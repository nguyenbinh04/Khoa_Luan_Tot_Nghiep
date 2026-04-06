import cv2
from ultralytics import YOLO
import tkinter as tk
from tkinter import filedialog
import os
import numpy as np
import requests
import urllib3
import threading
from flask import Flask, Response
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# CẤU HÌNH API
# ==========================================
API_REPORT = "https://localhost:7114/api/api/violations/report"
API_CONFIG = "https://localhost:7114/api/api/config/coordinates/1"
API_CLEAR = "https://localhost:7114/api/api/config/clear-all/1"

ENABLE_VEHICLE = True
ENABLE_SIGN = False
ENABLE_PLATE = True
ENABLE_HELMET = False

# ==========================================
# FLASK STREAMING
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


def run_flask():
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True, use_reloader=False)


# ==========================================
# HÀM HỖ TRỢ
# ==========================================
def reset_system_config():
    try:
        requests.post(API_CLEAR, verify=False, timeout=3)
    except:
        pass


def fetch_stop_zone():
    try:
        res = requests.get(API_CONFIG, verify=False, timeout=2)
        if res.status_code == 200:
            data = res.json().get("data", [])
            for cfg in data:
                if cfg["loaiVung"] == "Vach_DenDo":
                    return np.array([[p["x"], p["y"]] for p in json.loads(cfg["toaDoJson"])], np.int32)
    except:
        pass
    return None


def select_file():
    root = tk.Tk();
    root.withdraw()
    return filedialog.askopenfilename(title="HỆ THỐNG GIÁM SÁT", filetypes=[("Video", "*.mp4 *.avi")])


# ==========================================
# HÀM CHÍNH
# ==========================================
def main():
    global output_frame, lock

    reset_system_config()
    threading.Thread(target=run_flask, daemon=True).start()

    print("Đang tải các mô hình AI...")
    base_dir = "models/"
    traffic_model = YOLO(os.path.join(base_dir, "traffic_model.pt"))
    if ENABLE_SIGN:   sign_model = YOLO(os.path.join(base_dir, "sign_model.pt"))
    if ENABLE_PLATE:  plate_model = YOLO(os.path.join(base_dir, "plate_model.pt"))

    input_path = select_file()
    if not input_path: return
    cap = cv2.VideoCapture(input_path)

    success, first_frame = cap.read()
    if not success: return

    # VÒNG LẶP CHỜ VẼ VẠCH
    stop_zone = None
    print("[HỆ THỐNG] Đang chờ cấu hình vạch từ Web...")
    while stop_zone is None:
        temp = first_frame.copy()
        cv2.putText(temp, "DANG CHO CAU HINH TU WEB...", (50, temp.shape[0] // 2), 2, 1.2, (0, 255, 255), 3)
        with lock:
            output_frame = temp
        stop_zone = fetch_stop_zone()
        cv2.imshow("He Thong Giam Sat (CHO VE VACH)",
                   cv2.resize(temp, (int(temp.shape[1] * (700 / temp.shape[0])), 700)))
        if cv2.waitKey(500) & 0xFF == ord('q'): return

    cv2.destroyWindow("He Thong Giam Sat (CHO VE VACH)")
    violation_ids = []
    frame_counter = 0

    while True:
        if frame_counter == 0:
            frame = first_frame
        else:
            success, frame = cap.read()
            if not success: break

        frame_counter += 1
        h, w = frame.shape[:2]

        cv2.polylines(frame, [stop_zone], True, (0, 0, 255), 2)

        if ENABLE_SIGN:
            s_results = sign_model.predict(frame, conf=0.5, verbose=False)
            for s_box in s_results[0].boxes:
                sx1, sy1, sx2, sy2 = map(int, s_box.xyxy[0])
                cv2.rectangle(frame, (sx1, sy1), (sx2, sy2), (0, 165, 255), 2)

        t_results = traffic_model.track(frame, persist=True, tracker="bytetrack.yaml", verbose=False)

        if t_results[0].boxes.id is not None:
            boxes = t_results[0].boxes.xyxy.cpu().numpy()
            tids = t_results[0].boxes.id.int().cpu().tolist()
            cids = t_results[0].boxes.cls.int().cpu().tolist()

            for box, tid, cid in zip(boxes, tids, cids):
                x1, y1, x2, y2 = map(int, box)
                cx, cy = (x1 + x2) // 2, y2

                is_violating = cv2.pointPolygonTest(stop_zone, (float(cx), float(cy)), False) >= 0

                if is_violating and tid not in violation_ids:
                    violation_ids.append(tid)
                    print(f"\n[!] Xe {tid} vi phạm! Đang trích xuất dữ liệu...")

                    crop_veh = frame[max(0, y1):min(h, y2), max(0, x1):min(w, x2)]
                    crop_plate_bytes = None

                    # --- MODULE BIỂN SỐ HOÀN CHỈNH ---
                    if ENABLE_PLATE and crop_veh.size > 0:
                        p_results = plate_model.predict(crop_veh, conf=0.2, verbose=False)

                        if len(p_results[0].boxes) == 0:
                            print(f"   [-] Không tìm thấy biển số trên xe ID {tid}")
                        else:
                            # Lấy biển số đầu tiên tìm thấy
                            for p_box in p_results[0].boxes:
                                px1, py1, px2, py2 = map(int, p_box.xyxy[0])
                                print(f"   [+] Đã tìm thấy biển số! Đang cắt ảnh...")

                                # CẮT ẢNH BIỂN SỐ VÀ MÃ HÓA
                                plate_img = crop_veh[max(0, py1):min(crop_veh.shape[0], py2),
                                            max(0, px1):min(crop_veh.shape[1], px2)]

                                if plate_img.size > 0:
                                    _, p_enc = cv2.imencode('.jpg', plate_img)
                                    crop_plate_bytes = p_enc.tobytes()
                                    break  # Cắt được ảnh thì thoát vòng lặp tìm biển số

                    # --- CHUẨN BỊ GỬI API ---
                    _, img_enc = cv2.imencode('.jpg', frame)

                    files = {
                        "anhViPham": (f"full_{tid}.jpg", img_enc.tobytes(), "image/jpeg")
                    }
                    if crop_plate_bytes is not None:
                        files["anhBienSo"] = (f"plate_{tid}.jpg", crop_plate_bytes, "image/jpeg")
                        print(f"   [+] Đã đính kèm file ảnh biển số vào báo cáo.")

                    try:
                        requests.post(API_REPORT, verify=False, timeout=2,
                                      data={"bienSo": f"Xe ID {tid}", "loaiViPham": "Vuot Den Do"},
                                      files=files)
                        print(f"   [API] Đã đẩy dữ liệu thành công lên Web C#!")
                    except:
                        pass

                color = (0, 0, 255) if tid in violation_ids else (0, 255, 0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, f"ID:{tid}", (x1, y1 - 10), 1, 0.8, color, 1)

        with lock:
            output_frame = frame.copy()

        cv2.imshow("KLTN ACTIVE", cv2.resize(frame, (int(w * (700 / h)), 700)))
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()