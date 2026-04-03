import cv2
from ultralytics import YOLO
import tkinter as tk
from tkinter import filedialog



def select_file():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(
        title="HỆ THỐNG GIÁM SÁT GIAO THÔNG TOÀN DIỆN",
        filetypes=[("Tất cả định dạng", "*.mp4 *.avi *.jpg *.jpeg *.png"),
                   ("Video", "*.mp4 *.avi"), ("Ảnh", "*.jpg *.jpeg *.png")]
    )


def main():
    # Thay đổi True False
    ENABLE_VEHICLE = True  # Nhận diện và tracking Xe( luôn bật)
    ENABLE_SIGN = False  # Nhận diện biển báo
    ENABLE_PLATE = False  # Nhận diện biển số
    ENABLE_HELMET = False  # Nhận diện mũ bảo hiểm

    print("Đang khởi động ... tải mô hình ...")
    base_dir = "models/"

    # 1. TẢI MÔ HÌNH
    if ENABLE_VEHICLE: traffic_model = YOLO(base_dir + "traffic_model.pt")
    if ENABLE_SIGN:    sign_model = YOLO(base_dir + "sign_model.pt")
    if ENABLE_HELMET:  helmet_model = YOLO(base_dir + "helmet_model.pt")
    if ENABLE_PLATE:   plate_model = YOLO(base_dir + "plate_model.pt")

    # 2. CHỌN FILE
    input_path = select_file()
    if not input_path: return
    is_image = input_path.lower().endswith(('.png', '.jpg', '.jpeg'))

    if is_image:
        frame_source = cv2.imread(input_path)
    else:
        cap = cv2.VideoCapture(input_path)
        width, height = int(cap.get(3)), int(cap.get(4))
        fps = int(cap.get(5))
        out = cv2.VideoWriter("D:/Khóa luận tốt nghiệp/KLTN/datasets/videos/ket_qua_Full.avi",
                              cv2.VideoWriter_fourcc(*'XVID'), fps, (width, height))

    print("Bắt đầu xử lý! Bấm phím 'q' để thoát.")

    # 3. VÒNG LẶP XỬ LÝ
    while True:
        if is_image:
            frame = frame_source.copy()
        else:
            success, frame = cap.read()
            if not success: break

        height, width = frame.shape[:2]

        #MODULE 1: BIỂN BÁO
        if ENABLE_SIGN:
            sign_results = sign_model.predict(frame, conf=0.5, verbose=False)
            for s_box in sign_results[0].boxes:
                sx1, sy1, sx2, sy2 = [int(i) for i in s_box.xyxy[0]]
                s_name = sign_model.names[int(s_box.cls[0])]
                cv2.rectangle(frame, (sx1, sy1), (sx2, sy2), (0, 165, 255), 2)
                cv2.putText(frame, f"Bien: {s_name}", (sx1, sy1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 2)

        # MODULE 2: PHƯƠNG TIỆN
        if ENABLE_VEHICLE:
            if is_image:
                traffic_results = traffic_model.predict(frame, conf=0.4, verbose=False)
            else:
                traffic_results = traffic_model.track(frame, persist=True, tracker="bytetrack.yaml", verbose=False)

            if len(traffic_results[0].boxes) > 0:
                boxes = traffic_results[0].boxes.xyxy.cpu().numpy()
                class_ids = traffic_results[0].boxes.cls.int().cpu().tolist()

                if not is_image and traffic_results[0].boxes.id is not None:
                    track_ids = traffic_results[0].boxes.id.int().cpu().tolist()
                else:
                    track_ids = [-1] * len(boxes)

                for box, track_id, class_id in zip(boxes, track_ids, class_ids):
                    vx1, vy1, vx2, vy2 = [int(i) for i in box]
                    v_name = traffic_model.names[class_id]

                    cv2.rectangle(frame, (vx1, vy1), (vx2, vy2), (0, 255, 0), 2)
                    id_text = f" ID:{track_id}" if track_id != -1 else ""
                    cv2.putText(frame, f"{v_name}{id_text}", (vx1, vy1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                (0, 255, 0), 2)

                    crop_img = frame[max(0, vy1):min(height, vy2), max(0, vx1):min(width, vx2)]
                    if crop_img.size == 0: continue

                    # MODULE 3: BIỂN SỐ
                    if ENABLE_PLATE:
                        plate_results = plate_model.predict(crop_img, conf=0.5, verbose=False)
                        for p_box in plate_results[0].boxes:
                            px1, py1, px2, py2 = [int(i) for i in p_box.xyxy[0]]
                            cv2.rectangle(frame, (vx1 + px1, vy1 + py1), (vx1 + px2, vy1 + py2), (255, 0, 0), 2)
                            cv2.putText(frame, "Bien So", (vx1 + px1, vy1 + py1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                        (255, 0, 0), 2)

                    # MODULE 4: MŨ BẢO HIỂM
                    if ENABLE_HELMET and class_id == 5:
                        helmet_results = helmet_model.predict(crop_img, conf=0.4, verbose=False)
                        for h_box in helmet_results[0].boxes:
                            h_class = int(h_box.cls[0])
                            hx1, hy1, hx2, hy2 = [int(i) for i in h_box.xyxy[0]]
                            color = (0, 255, 0) if h_class == 0 else (0, 0, 255)
                            cv2.rectangle(frame, (vx1 + hx1, vy1 + hy1), (vx1 + hx2, vy1 + hy2), color, 2)

                            if h_class == 1:
                                cv2.putText(frame, "KHONG MU", (vx1, vy1 - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                                            (0, 0, 255), 2)

        # 4. HIỂN THỊ
        h_goc, w_goc = frame.shape[:2]
        h_hien_thi = 700
        w_hien_thi = int(w_goc * (h_hien_thi / h_goc))

        if is_image:
            cv2.imshow("He Thong Tong Hop", cv2.resize(frame, (w_hien_thi, h_hien_thi)))
            cv2.imwrite("D:/Khóa luận tốt nghiệp/KLTN/datasets/anh/ket_qua_Full.jpg", frame)
            cv2.waitKey(0)
            break
        else:
            out.write(frame)
            cv2.imshow("He Thong Tong Hop", cv2.resize(frame, (w_hien_thi, h_hien_thi)))
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    if not is_image:
        cap.release()
        out.release()
    cv2.destroyAllWindows()
    print("HOÀN THÀNH!")


if __name__ == "__main__":
    main()