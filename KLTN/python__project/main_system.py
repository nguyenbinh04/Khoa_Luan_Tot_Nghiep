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

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# CẤU HÌNH API
# ==========================================
API_REPORT = "https://localhost:7114/api/api/violations/report"
API_CONFIG = "https://localhost:7114/api/api/config/coordinates/1"
API_CLEAR = "https://localhost:7114/api/api/config/clear-all/1"

ENABLE_VEHICLE = True
ENABLE_SIGN = True  # Bật để nhận diện đèn giao thông
ENABLE_PLATE = True  # Bật để cắt biển số
ENABLE_HELMET = True  # Bật để soi mũ bảo hiểm

# ==========================================
# FLASK STREAMING (PHÁT LUỒNG LÊN WEB)
# ==========================================
app = Flask(__name__)
output_frame = None
lock = threading.Lock()


def generate():
    global output_frame, lock
    while True:
        with lock:
            if output_frame is None: continue
            (flag, encodedImage) = cv2.imencode(".jpg", output_frame)
            if not flag: continue
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')


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


# ==========================================
# HÀM HỖ TRỢ XỬ LÝ ẢNH & DATABASE
# ==========================================
def reset_system_config():
    try:
        requests.post(API_CLEAR, verify=False, timeout=3)
    except:
        pass


def fetch_all_zones():
    zones = {"Vach_DenDo": None, "Lan_XeMay": None, "Lan_Oto": None}
    try:
        res = requests.get(API_CONFIG, verify=False, timeout=2)
        if res.status_code == 200:
            for cfg in res.json().get("data", []):
                if cfg["loaiVung"] in zones:
                    pts = json.loads(cfg["toaDoJson"])
                    if len(pts) >= 3: zones[cfg["loaiVung"]] = np.array([[p["x"], p["y"]] for p in pts], np.int32)
    except:
        pass
    return zones


def detect_light_color(crop_img):
    hsv = cv2.cvtColor(crop_img, cv2.COLOR_BGR2HSV)
    lower_red1, upper_red1 = np.array([0, 100, 100]), np.array([10, 255, 255])
    lower_red2, upper_red2 = np.array([160, 100, 100]), np.array([179, 255, 255])
    mask_red = cv2.add(cv2.inRange(hsv, lower_red1, upper_red1), cv2.inRange(hsv, lower_red2, upper_red2))

    lower_green = np.array([40, 50, 50])
    upper_green = np.array([90, 255, 255])
    mask_green = cv2.inRange(hsv, lower_green, upper_green)

    red_pixels = cv2.countNonZero(mask_red)
    green_pixels = cv2.countNonZero(mask_green)

    if red_pixels > green_pixels and red_pixels > 15:
        return "RED"
    elif green_pixels > red_pixels and green_pixels > 15:
        return "GREEN"
    return "UNKNOWN"


# ==========================================
# HÀM CHÍNH
# ==========================================
def main():
    global output_frame, lock

    reset_system_config()
    threading.Thread(target=run_flask, daemon=True).start()

    print("[HỆ THỐNG] Đang tải các mô hình AI...")
    base_dir = "models/"
    traffic_model = YOLO(os.path.join(base_dir, "traffic_model.pt"))
    if ENABLE_SIGN:   sign_model = YOLO(os.path.join(base_dir, "sign_model.pt"))
    if ENABLE_PLATE:  plate_model = YOLO(os.path.join(base_dir, "plate_model.pt"))
    if ENABLE_HELMET: helmet_model = YOLO(os.path.join(base_dir, "helmet_model.pt"))

    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    else:
        print("[LỖI] Không nhận được đường dẫn video từ C#! Vui lòng chạy qua Web.")
        return

    if not os.path.exists(input_path):
        print(f"[LỖI] File video không tồn tại: {input_path}")
        return

    cap = cv2.VideoCapture(input_path)
    success, first_frame = cap.read()
    if not success: return

    zones = fetch_all_zones()
    print("[HỆ THỐNG] Đang chờ cấu hình vạch từ Web...")
    while all(v is None for v in zones.values()):
        temp = first_frame.copy()
        cv2.putText(temp, "DANG CHO CAU HINH TU WEB...", (50, temp.shape[0] // 2), 2, 1.2, (0, 255, 255), 3)
        with lock:
            output_frame = temp
        zones = fetch_all_zones()
        time.sleep(0.5)

    violation_ids = []
    frame_counter = 0

    # =======================================================
    # BIẾN CẤU HÌNH THỜI GIAN CHỜ (DELAY CONFIRMATION)
    # =======================================================
    tracker_frames = {}  # Dictionary lưu số frame vi phạm của từng xe
    FRAMES_TO_CONFIRM = 15  # Số frame chờ trước khi chụp (Tăng lên nếu muốn xe đi sâu hơn, Vd: 30)

    while True:
        if frame_counter == 0:
            frame = first_frame
        else:
            success, frame = cap.read()
            if not success: break

        frame_counter += 1
        h, w = frame.shape[:2]

        if frame_counter % 100 == 0:
            new_zones = fetch_all_zones()
            if any(v is not None for v in new_zones.values()): zones = new_zones

        current_traffic_light = "GREEN"

        if ENABLE_SIGN:
            s_results = sign_model.predict(frame, conf=0.4, verbose=False)
            for s_box in s_results[0].boxes:
                sx1, sy1, sx2, sy2 = map(int, s_box.xyxy[0])
                s_cls = int(s_box.cls[0])
                s_name = sign_model.names[s_cls].lower()

                if "light" in s_name or "den" in s_name or "đèn" in s_name or s_cls == 9:
                    crop_light = frame[max(0, sy1):min(h, sy2), max(0, sx1):min(w, sx2)]
                    if crop_light.size > 0:
                        detected_color = detect_light_color(crop_light)
                        if detected_color != "UNKNOWN": current_traffic_light = detected_color

                    l_color = (0, 0, 255) if current_traffic_light == "RED" else (0, 255, 0)
                    cv2.rectangle(frame, (sx1, sy1), (sx2, sy2), l_color, 2)
                    cv2.putText(frame, f"Traffic Light: {current_traffic_light}", (sx1, sy1 - 10), 1, 0.8, l_color, 2)
                else:
                    cv2.rectangle(frame, (sx1, sy1), (sx2, sy2), (0, 165, 255), 2)
                    cv2.putText(frame, s_name.upper(), (sx1, sy1 - 5), 1, 0.6, (0, 165, 255), 2)

        if zones["Vach_DenDo"] is not None:
            zone_color = (0, 0, 255) if current_traffic_light == "RED" else (0, 255, 0)
            cv2.polylines(frame, [zones["Vach_DenDo"]], True, zone_color, 2)
            cv2.putText(frame, f"TRANG THAI DEN: {current_traffic_light}",
                        (zones["Vach_DenDo"][0][0], zones["Vach_DenDo"][0][1] - 10), 1, 1, zone_color, 2)

        if zones["Lan_XeMay"] is not None: cv2.polylines(frame, [zones["Lan_XeMay"]], True, (0, 255, 255), 2)
        if zones["Lan_Oto"] is not None: cv2.polylines(frame, [zones["Lan_Oto"]], True, (255, 0, 0), 2)

        t_results = traffic_model.track(frame, persist=True, tracker="bytetrack.yaml", verbose=False)

        if t_results[0].boxes.id is not None:
            boxes = t_results[0].boxes.xyxy.cpu().numpy()
            tids = t_results[0].boxes.id.int().cpu().tolist()
            cids = t_results[0].boxes.cls.int().cpu().tolist()

            for box, tid, cid in zip(boxes, tids, cids):
                x1, y1, x2, y2 = map(int, box)
                cx, cy = (x1 + x2) // 2, y2

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
                in_any_zone = in_red_zone or in_moto_zone or in_car_zone

                danh_sach_loi = []

                if class_name not in nhom_uutien:
                    if in_red_zone and current_traffic_light == "RED":
                        danh_sach_loi.append("Vuot Den Do")
                    elif class_name in nhom_oto and in_moto_zone:
                        danh_sach_loi.append(f"Sai Lan ({class_name})")
                    elif class_name in nhom_xemay and in_car_zone:
                        danh_sach_loi.append(f"Sai Lan ({class_name})")

                if ENABLE_HELMET and class_name in nhom_xemay and in_any_zone:
                    crop_veh = frame[max(0, y1):min(h, y2), max(0, x1):min(w, x2)]
                    has_no_helmet = False

                    if crop_veh.size > 0:
                        h_results = helmet_model.predict(crop_veh, conf=0.4, verbose=False)
                        if len(h_results[0].boxes) > 0:
                            for h_box in h_results[0].boxes:
                                hx1, hy1, hx2, hy2 = map(int, h_box.xyxy[0])
                                h_cls = int(h_box.cls[0])
                                h_name = helmet_model.names[h_cls].lower()

                                if h_cls == 1 or "no" in h_name or "khong" in h_name:
                                    has_no_helmet = True
                                    cv2.rectangle(frame, (x1 + hx1, y1 + hy1), (x1 + hx2, y1 + hy2), (0, 0, 255), 2)
                                    cv2.putText(frame, "NO HELMET", (x1 + hx1, y1 + hy1 - 5), 1, 0.5, (0, 0, 255), 2)
                                else:
                                    cv2.rectangle(frame, (x1 + hx1, y1 + hy1), (x1 + hx2, y1 + hy2), (0, 255, 0), 2)

                    if has_no_helmet and class_name not in nhom_uutien: danh_sach_loi.append("Khong Mu Bao Hiem")

                # =======================================================
                # LOGIC XÁC NHẬN VI PHẠM (TRÌ HOÃN TRƯỚC KHI CHỤP)
                # =======================================================
                if len(danh_sach_loi) > 0 and tid not in violation_ids:
                    # Tăng biến đếm số frame chiếc xe này đã vi phạm
                    tracker_frames[tid] = tracker_frames.get(tid, 0) + 1

                    # Vẽ phần trăm xác nhận lên màn hình
                    progress = min(int((tracker_frames[tid] / FRAMES_TO_CONFIRM) * 100), 100)
                    cv2.putText(frame, f"XAC NHAN... {progress}%", (x1, max(y1 - 25, 20)), 1, 0.8, (0, 165, 255), 2)

                    # NẾU ĐÃ ĐỦ THỜI GIAN (ĐÃ ĐI SÂU VÀO VÙNG) => MỚI CHỤP ẢNH PHẠT
                    if tracker_frames[tid] >= FRAMES_TO_CONFIRM:
                        violation_ids.append(tid)
                        loi_tong_hop = " + ".join(danh_sach_loi)
                        print(f"\n[!] TÓM ĐƯỢC XE ID {tid} VI PHẠM: {loi_tong_hop}!")

                        crop_veh = frame[max(0, y1):min(h, y2), max(0, x1):min(w, x2)]
                        crop_plate_bytes = None

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

                        _, img_enc = cv2.imencode('.jpg', frame)
                        files = {"anhViPham": (f"full_{tid}.jpg", img_enc.tobytes(), "image/jpeg")}
                        if crop_plate_bytes is not None: files["anhBienSo"] = (
                        f"plate_{tid}.jpg", crop_plate_bytes, "image/jpeg")

                        try:
                            requests.post(API_REPORT, verify=False, timeout=2,
                                          data={"bienSo": f"ID {tid}", "loaiViPham": loi_tong_hop}, files=files)
                        except:
                            pass

                # Nếu không có lỗi (xe lùi lại, ra khỏi vùng) nhưng vẫn đang bị theo dõi -> Reset đếm
                elif len(danh_sach_loi) == 0 and tid in tracker_frames and tid not in violation_ids:
                    tracker_frames[tid] = 0

                # =======================================================
                # TÔ MÀU KHUNG XE THEO TRẠNG THÁI MỚI
                # =======================================================
                if class_name in nhom_uutien:
                    color = (0, 255, 255)  # Ưu tiên: Vàng
                else:
                    if tid in violation_ids:
                        color = (0, 0, 255)  # Đã chụp lỗi: Đỏ
                    elif tid in tracker_frames and tracker_frames[tid] > 0:
                        color = (0, 165, 255)  # Đang chờ xác nhận: Cam
                    else:
                        color = (0, 255, 0)  # Bình thường: Xanh

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, f"{class_name.upper()} ID:{tid}", (x1, y1 - 10), 1, 0.8, color, 1)

        with lock:
            output_frame = frame.copy()

        time.sleep(0.01)

    cap.release()


if __name__ == "__main__":
    main()