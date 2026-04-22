import cv2
from ultralytics import YOLO

def main():
    # 1. TẢI CÁC MÔ HÌNH
    print("Đang tải mô hình AI...")
    traffic_model = YOLO("D:/Khóa luận tốt nghiệp/KLTN/python__project/models/traffic_model.pt")
    helmet_model = YOLO("D:/Khóa luận tốt nghiệp/KLTN/python__project/models/helmet_model1.pt")

    # 2. KHỞI TẠO VIDEO ĐẦU VÀO VÀ ĐẦU RA
    video_path = "D:/DATA/datasets/videos/vd xịn/KhacTam0028.MP4"
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Lỗi: Không thể mở video!")
        return

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    out = cv2.VideoWriter("D:/DATA/datasets/videos/vd xịn/ket_qua_mu_bao_hiem.mp4",
                          cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    print("Đang xử lý video... Vui lòng đợi...")

    # 3. VÒNG LẶP XỬ LÝ
    frame_count = 0
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame_count += 1
        if frame_count % 30 == 0:
            print(f"Đã xử lý được {frame_count} frames...")

        # --- BƯỚC A: TÌM VÀ THEO DÕI XE TRONG TOÀN BỘ FRAME ---
        results = traffic_model.track(frame, persist=True, tracker="bytetrack.yaml", verbose=False)

        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.int().cpu().tolist()
            class_ids = results[0].boxes.cls.int().cpu().tolist()

            # Chuẩn bị danh sách để xử lý Mũ bảo hiểm theo Lô (Batch)
            motorcycle_crops = []
            crop_coords = []
            track_infos = []

            for box, track_id, class_id in zip(boxes, track_ids, class_ids):
                x1_xe, y1_xe, x2_xe, y2_xe = [int(i) for i in box]

                if class_id == 5: # Nếu là xe máy
                    # Vẽ khung xe máy màu Cyan nhạt
                    cv2.rectangle(frame, (x1_xe, y1_xe), (x2_xe, y2_xe), (255, 255, 0), 2)

                    # CẮT ẢNH XE MÁY RA
                    y1_crop, y2_crop = max(0, y1_xe), min(height, y2_xe)
                    x1_crop, x2_crop = max(0, x1_xe), min(width, x2_xe)
                    crop_img = frame[y1_crop:y2_crop, x1_crop:x2_crop]

                    if crop_img.size > 0:
                        motorcycle_crops.append(crop_img)
                        crop_coords.append((x1_crop, y1_crop)) # Lưu lại tọa độ góc trái trên để bù trừ
                        track_infos.append((track_id, x1_xe, y1_xe)) # Lưu ID và tọa độ để ghi chữ

            # --- BƯỚC B: NHẬN DIỆN MŨ BẢO HIỂM BẰNG BATCH INFERENCE ---
            # Chỉ gọi hàm predict 1 LẦN cho TẤT CẢ các xe máy trong frame
            if motorcycle_crops:
                helmet_results = helmet_model.predict(motorcycle_crops, verbose=False, conf=0.4)

                # Duyệt qua kết quả trả về tương ứng với từng xe máy
                for idx, h_res in enumerate(helmet_results):
                    offset_x, offset_y = crop_coords[idx]
                    t_id, txt_x, txt_y = track_infos[idx]

                    status_text = "OK"
                    color_status = (0, 255, 0) # Xanh lá mặc định

                    for h_box in h_res.boxes:
                        h_class = int(h_box.cls[0])
                        hx1, hy1, hx2, hy2 = [int(i) for i in h_box.xyxy[0]]

                        # Cộng dồn tọa độ cắt để vẽ đúng vị trí trên khung hình gốc
                        hx1_abs, hy1_abs = offset_x + hx1, offset_y + hy1
                        hx2_abs, hy2_abs = offset_x + hx2, offset_y + hy2

                        if h_class == 0:
                            # Có đội mũ -> Vẽ khung xanh lá
                            cv2.rectangle(frame, (hx1_abs, hy1_abs), (hx2_abs, hy2_abs), (0, 255, 0), 2)
                        elif h_class == 1:
                            # KHÔNG ĐỘI MŨ -> Vẽ khung đỏ cảnh báo
                            cv2.rectangle(frame, (hx1_abs, hy1_abs), (hx2_abs, hy2_abs), (0, 0, 255), 2)
                            status_text = "VI PHAM: KHONG MU"
                            color_status = (0, 0, 255) # Chuyển text xe sang đỏ

                    # IN THÔNG TIN LÊN ĐẦU XE (In sau khi đã quét xong các đầu trong xe)
                    label = f"ID: {t_id} - {status_text}"
                    cv2.putText(frame, label, (txt_x, txt_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_status, 2)

        # 4. GHI KHUNG HÌNH VIDEO MỚI
        out.write(frame)

    # 5. DỌN DẸP
    cap.release()
    out.release()
    print("HOÀN THÀNH! Hãy mở file 'ket_qua_mu_bao_hiem.mp4' để xem.")

if __name__ == '__main__':
    main()