import cv2
from ultralytics import YOLO
import os
import numpy as np
import requests
import urllib3
import threading
from flask import Flask, Response
import json
import sys
import time
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# CẤU HÌNH API TOÀN CỤC
# ==========================================
API_BASE = "https://localhost:7114"
CAMERA_ID = "1"

ENABLE_VEHICLE = True
ENABLE_SIGN = False
ENABLE_PLATE = True
ENABLE_HELMET = True

# ==========================================
# FLASK STREAMING (CHỐNG TREO CPU)
# ==========================================
app = Flask(__name__)
output_frame = None
lock = threading.Lock()


def generate():
    global output_frame, lock
    while True:
        frame_to_yield = None
        with lock:
            if output_frame is not None:
                frame_to_yield = output_frame.copy()

        if frame_to_yield is None:
            time.sleep(0.1)
            continue

        (flag, encodedImage) = cv2.imencode(".jpg", frame_to_yield)
        if not flag:
            continue

        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')
        time.sleep(0.03)


@app.route("/video_feed")
def video_feed():
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/shutdown", methods=['POST'])
def shutdown():
    print("[HỆ THỐNG] Nhận lệnh tự hủy từ Web. Đang tắt AI...")
    os._exit(0)
    return "OK"


def run_flask():
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True, use_reloader=False)


def fetch_all_zones():
    global CAMERA_ID, API_BASE
    zones = {"Vach_DenDo": None, "Lan_XeMay": None, "Lan_Oto": None, "Vung_DenGiaoThong": None}
    try:
        url = f"{API_BASE}/api/api/config/coordinates/{CAMERA_ID}"
        res = requests.get(url, verify=False, timeout=2)
        if res.status_code == 200:
            for cfg in res.json().get("data", []):
                lv = cfg.get("loaiVung") or cfg.get("LoaiVung")
                tj = cfg.get("toaDoJson") or cfg.get("ToaDoJson")
                if lv in zones and tj and tj != "[]":
                    pts = json.loads(tj)
                    if len(pts) >= 3:
                        zones[lv] = np.array([[p.get("x", p.get("X")), p.get("y", p.get("Y"))] for p in pts], np.int32)
    except Exception as e:
        pass
    return zones


# =======================================================
# THUẬT TOÁN ĐỌC MÀU
# =======================================================
def detect_light_color(crop_img):
    hsv = cv2.cvtColor(crop_img, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 40, 150])
    upper_red1 = np.array([5, 255, 255])
    lower_red2 = np.array([170, 40, 150])
    upper_red2 = np.array([180, 255, 255])
    mask_red = cv2.add(cv2.inRange(hsv, lower_red1, upper_red1), cv2.inRange(hsv, lower_red2, upper_red2))

    lower_yellow = np.array([12, 40, 150])
    upper_yellow = np.array([35, 255, 255])
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)

    lower_green = np.array([36, 30, 150])
    upper_green = np.array([100, 255, 255])
    mask_green = cv2.inRange(hsv, lower_green, upper_green)

    r_count = cv2.countNonZero(mask_red)
    y_count = cv2.countNonZero(mask_yellow)
    g_count = cv2.countNonZero(mask_green)

    max_color = max(r_count, y_count, g_count)

    if max_color > 15:
        if max_color == g_count: return "GREEN"
        if max_color == y_count: return "YELLOW"
        if max_color == r_count: return "RED"

    h, w = crop_img.shape[:2]
    if h > w and h > 20:
        gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
        _, bright_mask = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY)

        top_bright = cv2.countNonZero(bright_mask[0:h // 3, :])
        mid_bright = cv2.countNonZero(bright_mask[h // 3:2 * h // 3, :])
        bot_bright = cv2.countNonZero(bright_mask[2 * h // 3:h, :])

        max_bright = max(top_bright, mid_bright, bot_bright)

        if max_bright > 10:
            if max_bright == top_bright: return "RED"
            if max_bright == bot_bright: return "GREEN"
            if max_bright == mid_bright: return "YELLOW"

    return "UNKNOWN"


def main():
    global output_frame, lock, CAMERA_ID, API_BASE

    if len(sys.argv) > 3:
        input_path = sys.argv[1]
        CAMERA_ID = sys.argv[2]
        API_BASE = sys.argv[3]
    elif len(sys.argv) > 2:
        input_path = sys.argv[1]
        CAMERA_ID = sys.argv[2]
    elif len(sys.argv) > 1:
        input_path = sys.argv[1]
    else:
        return

    if not os.path.exists(input_path): return

    threading.Thread(target=run_flask, daemon=True).start()

    print(f"[HỆ THỐNG] Đang tải mô hình AI cho CAMERA {CAMERA_ID} tại {API_BASE} ...")
    base_dir = "models/"
    traffic_model = YOLO(os.path.join(base_dir, "traffic_model.pt"))
    if ENABLE_SIGN:   sign_model = YOLO(os.path.join(base_dir, "sign_model.pt"))

    if ENABLE_PLATE:
        plate_model = YOLO(os.path.join(base_dir, "plate_model.pt"))

    if ENABLE_HELMET: helmet_model = YOLO(os.path.join(base_dir, "helmet_model1.pt"))

    is_image = input_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.webp'))
    cap = cv2.VideoCapture(input_path)
    success, first_frame = cap.read()
    if not success: return

    zones = fetch_all_zones()
    while all(v is None for v in zones.values()):
        temp = first_frame.copy()
        cv2.putText(temp, "DANG CHO CAU HINH TU WEB...", (50, temp.shape[0] // 2), 2, 1.2, (0, 255, 255), 3)
        with lock: output_frame = temp
        zones = fetch_all_zones()
        time.sleep(0.5)

    violation_ids = []
    frame_counter = 0
    tracker_frames = {}
    FRAMES_TO_CONFIRM = 8
    vehicle_paths = {}

    while True:
        if is_image:
            frame = first_frame.copy()
        else:
            if frame_counter == 0:
                frame = first_frame
            else:
                success, frame = cap.read()
                if not success:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue

        frame_counter += 1
        h, w = frame.shape[:2]

        if frame_counter % 100 == 0:
            new_zones = fetch_all_zones()
            if any(v is not None for v in new_zones.values()): zones = new_zones

        t_results = traffic_model.track(frame, persist=True, tracker="bytetrack.yaml", verbose=False)
        current_traffic_light = "GREEN"
        light_detected = False

        if zones["Vach_DenDo"] is not None:
            if zones.get("Vung_DenGiaoThong") is not None:
                bx, by, bw, bh = cv2.boundingRect(zones["Vung_DenGiaoThong"])
                roi_x1, roi_x2 = bx, bx + bw
                roi_y1, roi_y2 = by, by + bh
                crop_light = frame[max(0, roi_y1):min(h, roi_y2), max(0, roi_x1):min(w, roi_x2)]
                if crop_light.size > 0:
                    detected_color = detect_light_color(crop_light)
                    if detected_color != "UNKNOWN": current_traffic_light = detected_color
                    cv2.rectangle(frame, (roi_x1, roi_y1), (roi_x2, roi_y2), (255, 0, 255), 2)
                    cv2.putText(frame, f"USER SCAN: {current_traffic_light}", (roi_x1, max(20, roi_y1 - 10)), 1, 1,
                                (255, 0, 255), 2)
                    light_detected = True

            if not light_detected:
                if t_results[0].boxes.id is not None:
                    for t_box in t_results[0].boxes:
                        if int(t_box.cls[0]) == 9:
                            tx1, ty1, tx2, ty2 = map(int, t_box.xyxy[0])
                            crop_light = frame[max(0, ty1):min(h, ty2), max(0, tx1):min(w, tx2)]
                            if crop_light.size > 0:
                                detected_color = detect_light_color(crop_light)
                                if detected_color != "UNKNOWN": current_traffic_light = detected_color
                            l_color = (0, 0, 255) if current_traffic_light == "RED" else (
                                (0, 255, 255) if current_traffic_light == "YELLOW" else (0, 255, 0))
                            cv2.rectangle(frame, (tx1, ty1), (tx2, ty2), l_color, 2)
                            cv2.putText(frame, f"Traffic Light: {current_traffic_light}", (tx1, ty1 - 10), 1, 0.8,
                                        l_color, 2)
                            light_detected = True
                            break

                if not light_detected and ENABLE_SIGN:
                    s_results = sign_model.predict(frame, conf=0.1, imgsz=1024, verbose=False)
                    for s_box in s_results[0].boxes:
                        sx1, sy1, sx2, sy2 = map(int, s_box.xyxy[0])
                        s_cls = int(s_box.cls[0])
                        s_name = sign_model.names[s_cls].lower()
                        if "light" in s_name or "den" in s_name or "đèn" in s_name or s_cls == 9:
                            crop_light = frame[max(0, sy1):min(h, sy2), max(0, sx1):min(w, sx2)]
                            if crop_light.size > 0:
                                detected_color = detect_light_color(crop_light)
                                if detected_color != "UNKNOWN": current_traffic_light = detected_color
                            l_color = (0, 0, 255) if current_traffic_light == "RED" else (
                                (0, 255, 255) if current_traffic_light == "YELLOW" else (0, 255, 0))
                            cv2.rectangle(frame, (sx1, sy1), (sx2, sy2), l_color, 2)
                            cv2.putText(frame, f"Traffic Light: {current_traffic_light}", (sx1, sy1 - 10), 1, 0.8,
                                        l_color, 2)
                            light_detected = True
                            break

                if not light_detected:
                    roi_x1, roi_x2 = int(w * 0.75), w
                    roi_y1, roi_y2 = 0, int(h * 0.45)
                    crop_light = frame[roi_y1:roi_y2, roi_x1:roi_x2]
                    if crop_light.size > 0:
                        detected_color = detect_light_color(crop_light)
                        if detected_color != "UNKNOWN": current_traffic_light = detected_color
                        cv2.rectangle(frame, (roi_x1, roi_y1), (roi_x2, roi_y2), (0, 255, 255), 2)
                        cv2.putText(frame, f"AUTO SCAN: {current_traffic_light}", (roi_x1 + 10, roi_y1 + 30), 1, 1,
                                    (0, 255, 255), 2)

        if zones["Vach_DenDo"] is not None:
            zone_color = (0, 0, 255) if current_traffic_light == "RED" else (
                (0, 255, 255) if current_traffic_light == "YELLOW" else (0, 255, 0))
            cv2.polylines(frame, [zones["Vach_DenDo"]], True, zone_color, 2)
            cv2.putText(frame, f"TRANG THAI DEN: {current_traffic_light}",
                        (zones["Vach_DenDo"][0][0], zones["Vach_DenDo"][0][1] - 10), 1, 1, zone_color, 2)

        if zones["Lan_XeMay"] is not None: cv2.polylines(frame, [zones["Lan_XeMay"]], True, (0, 255, 255), 2)
        if zones["Lan_Oto"] is not None: cv2.polylines(frame, [zones["Lan_Oto"]], True, (255, 0, 0), 2)

        if t_results[0].boxes.id is not None:
            boxes = t_results[0].boxes.xyxy.cpu().numpy()
            tids = t_results[0].boxes.id.int().cpu().tolist()
            cids = t_results[0].boxes.cls.int().cpu().tolist()

            # =================================================================
            # BƯỚC 1: BATCH INFERENCE MŨ BẢO HIỂM
            # =================================================================
            helmet_status_dict = {}
            if ENABLE_HELMET:
                moto_crops = []
                moto_tids = []
                moto_offsets = []

                for box, tid, cid in zip(boxes, tids, cids):
                    class_name = traffic_model.names[cid].lower()
                    if class_name in ['xe may', 'xe dap']:
                        x1, y1, x2, y2 = map(int, box)

                        box_h = y2 - y1
                        box_w = x2 - x1

                        crop_y1 = max(0, int(y1 - 1.7 * box_h))
                        crop_y2 = min(h, int(y2 + 0.1 * box_h))

                        crop_x1 = max(0, int(x1 - 0.1 * box_w))
                        crop_x2 = min(w, int(x2 + 0.1 * box_w))

                        crop_veh = frame[crop_y1:crop_y2, crop_x1:crop_x2]

                        if crop_veh.size > 0:
                            moto_crops.append(crop_veh)
                            moto_tids.append(tid)
                            moto_offsets.append((crop_x1, crop_y1, crop_veh.shape[0]))



                if moto_crops:
                    h_batch_results = helmet_model.predict(moto_crops, conf=0.50, verbose=False)

                    for tid, h_res, (ox, oy, crop_h) in zip(moto_tids, h_batch_results, moto_offsets):
                        has_no_helmet = False
                        draw_boxes = []

                        for h_box in h_res.boxes:
                            hx1, hy1, hx2, hy2 = map(int, h_box.xyxy[0])
                            h_cls = int(h_box.cls[0])
                            h_name = helmet_model.names[h_cls].lower()

                            if hy1 > crop_h * 0.85:
                                continue

                            if "no" in h_name or "khong" in h_name or "without" in h_name or "head" in h_name or h_cls == 1:
                                has_no_helmet = True
                                draw_boxes.append((ox + hx1, oy + hy1, ox + hx2, oy + hy2, "NO HELMET", (0, 0, 255)))
                            else:
                                draw_boxes.append((ox + hx1, oy + hy1, ox + hx2, oy + hy2, "", (0, 255, 0)))

                        helmet_status_dict[tid] = {"violation": has_no_helmet, "draw": draw_boxes}

            # =================================================================
            # BƯỚC 2: XỬ LÝ VI PHẠM TỔNG HỢP VÀ VẼ LÊN KHUNG HÌNH CHÍNH
            # =================================================================
            for box, tid, cid in zip(boxes, tids, cids):
                x1, y1, x2, y2 = map(int, box)
                cx, cy = (x1 + x2) // 2, y2

                if tid not in vehicle_paths: vehicle_paths[tid] = []
                vehicle_paths[tid].append((cx, cy))
                if len(vehicle_paths[tid]) > 30: vehicle_paths[tid].pop(0)

                class_name = traffic_model.names[cid].lower()
                nhom_oto = ['xe buyt', 'xe container', 'xe con', 'xe tai', 'xe van']
                nhom_xemay = ['xe may', 'xe dap']
                nhom_uutien = ['xe cuu hoa']

                in_red_zone = zones["Vach_DenDo"] is not None and cv2.pointPolygonTest(zones["Vach_DenDo"],
                                                                                       (float(cx), float(cy)),
                                                                                       False) >= 0
                in_moto_zone = zones["Lan_XeMay"] is not None and cv2.pointPolygonTest(zones["Lan_XeMay"],
                                                                                       (float(cx), float(cy)),
                                                                                       False) >= 0
                in_car_zone = zones["Lan_Oto"] is not None and cv2.pointPolygonTest(zones["Lan_Oto"],
                                                                                    (float(cx), float(cy)), False) >= 0

                danh_sach_loi = []
                is_turning_right = False

                if class_name not in nhom_uutien:
                    if in_red_zone and current_traffic_light == "RED":
                        if len(vehicle_paths[tid]) > 5:
                            old_cx = vehicle_paths[tid][0][0]
                            if (cx - old_cx) > 15 and cx > (w * 0.5):
                                is_turning_right = True
                                cv2.putText(frame, "RE PHAI", (x1, y1 - 25), 1, 0.8, (255, 255, 0), 2)
                        if not is_turning_right: danh_sach_loi.append("Vuot Den Do")

                    elif class_name in nhom_oto and in_moto_zone:
                        danh_sach_loi.append(f"Sai Lan ({class_name})")
                    elif class_name in nhom_xemay and in_car_zone:
                        danh_sach_loi.append(f"Sai Lan ({class_name})")

                if ENABLE_HELMET and class_name in nhom_xemay:
                    h_info = helmet_status_dict.get(tid)
                    if h_info:
                        for (bx1, by1, bx2, by2, label, color) in h_info["draw"]:
                            cv2.rectangle(frame, (bx1, by1), (bx2, by2), color, 2)
                            if label:
                                cv2.putText(frame, label, (bx1, max(by1 - 5, 10)), 1, 0.6, color, 2)

                        if h_info["violation"] and class_name not in nhom_uutien:
                            danh_sach_loi.append("Khong Mu Bao Hiem")

                if len(danh_sach_loi) > 0 and tid not in violation_ids:
                    tracker_frames[tid] = tracker_frames.get(tid, 0) + 1
                    progress = min(int((tracker_frames[tid] / FRAMES_TO_CONFIRM) * 100), 100)
                    cv2.putText(frame, f"XAC NHAN... {progress}%", (x1, max(y1 - 25, 20)), 1, 0.8, (0, 165, 255), 2)

                    if tracker_frames[tid] >= FRAMES_TO_CONFIRM:
                        violation_ids.append(tid)
                        loi_tong_hop = " + ".join(danh_sach_loi)
                        print(f"\n[!] TÓM ĐƯỢC XE ID {tid} VI PHẠM: {loi_tong_hop}!")

                        snapshot = frame.copy()
                        cv2.rectangle(snapshot, (x1, y1), (x2, y2), (0, 0, 255), 3)
                        cv2.putText(snapshot, f"VI PHAM: {loi_tong_hop.upper()}", (x1, max(y1 - 10, 20)), 1, 1,
                                    (0, 0, 255), 2)

                        crop_veh = frame[max(0, y1):min(h, y2), max(0, x1):min(w, x2)]
                        crop_plate_bytes = None
                        bien_so_text = "Không nhận diện"

                        if ENABLE_PLATE and crop_veh.size > 0:
                            p_results = plate_model.predict(crop_veh, conf=0.2, verbose=False)
                            if len(p_results[0].boxes) > 0:
                                for p_box in p_results[0].boxes:
                                    px1, py1, px2, py2 = map(int, p_box.xyxy[0])
                                    plate_img = crop_veh[max(0, py1):min(crop_veh.shape[0], py2),
                                                max(0, px1):min(crop_veh.shape[1], px2)]

                                    if plate_img.size > 0:
                                        _, p_enc = cv2.imencode('.jpg', plate_img)
                                        crop_plate_bytes = p_enc.tobytes()
                                        break

                        _, img_enc = cv2.imencode('.jpg', snapshot)
                        files = {"anhViPham": (f"full_{tid}.jpg", img_enc.tobytes(), "image/jpeg")}
                        if crop_plate_bytes is not None:
                            files["anhBienSo"] = (f"plate_{tid}.jpg", crop_plate_bytes, "image/jpeg")

                        try:
                            api_url = f"{API_BASE}/api/api/violations/report"
                            requests.post(api_url, verify=False, timeout=2,
                                          data={"bienSo": bien_so_text, "loaiViPham": loi_tong_hop,
                                                "cameraId": CAMERA_ID}, files=files)
                        except:
                            pass

                elif len(danh_sach_loi) == 0 and tid in tracker_frames and tid not in violation_ids:
                    tracker_frames[tid] = 0

                if class_name in nhom_uutien:
                    color = (0, 255, 255)
                else:
                    color = (0, 0, 255) if tid in violation_ids else (
                        (0, 165, 255) if tracker_frames.get(tid, 0) > 0 else (0, 255, 0))
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                if not is_turning_right: cv2.putText(frame, f"{class_name.upper()} ID:{tid}", (x1, y1 - 10), 1, 0.8,
                                                     color, 1)

        with lock:
            output_frame = frame.copy()
        time.sleep(0.05 if is_image else 0.01)
    cap.release()


if __name__ == "__main__":
    main()