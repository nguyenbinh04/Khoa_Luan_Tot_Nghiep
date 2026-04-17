import cv2
from ultralytics import YOLO


def main():
    #TẢI CÁC MÔ HÌNH
    traffic_model = YOLO("D:/Khóa luận tốt nghiệp/KLTN/python__project/models/traffic_model.pt")  # Mô hình Hutech (xe máy là số 5)
    helmet_model = YOLO("D:/Khóa luận tốt nghiệp/KLTN/python__project/models/helmet_model.pt")  # Mô hình Mũ bảo hiểm (0: Mũ, 1: Không mũ)

    # VIDEO ĐẦU VÀO VÀ ĐẦU RA
    video_path = "D:/Khóa luận tốt nghiệp/KLTN/datasets/videos/test13.mp4"
    cap = cv2.VideoCapture(video_path)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    out = cv2.VideoWriter("D:/Khóa luận tốt nghiệp/KLTN/datasets/videos/ket_qua_mu_bao_hiem.mp4",
                          cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    print("Đang xử lý video... Vui lòng đợi...")


    #VÒNG LẶP XỬ LÝ
    frame_count = 0
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame_count += 1
        if frame_count % 30 == 0:
            print(f"Đã xử lý được {frame_count} frames...")

        # TÌM VÀ THEO DÕI XE
        results = traffic_model.track(frame, persist=True, tracker="bytetrack.yaml", verbose=False)

        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.int().cpu().tolist()
            class_ids = results[0].boxes.cls.int().cpu().tolist()

            for box, track_id, class_id in zip(boxes, track_ids, class_ids):
                # Tọa độ của chiếc xe
                x1_xe, y1_xe, x2_xe, y2_xe = [int(i) for i in box]

                if class_id == 5:
                    # Vẽ khung xe máy
                    cv2.rectangle(frame, (x1_xe, y1_xe), (x2_xe, y2_xe), (255, 255, 0), 2)

                    # CẮT ẢNH XE MÁY RA
                    y1_crop, y2_crop = max(0, y1_xe), min(height, y2_xe)
                    x1_crop, x2_crop = max(0, x1_xe), min(width, x2_xe)
                    motorcycle_crop = frame[y1_crop:y2_crop, x1_crop:x2_crop]

                    #Tránh cắt ảnh rỗng
                    if motorcycle_crop.size == 0:
                        continue

                    #QUÉT MŨ BẢO HIỂM ẢNH VỪA CẮT
                    helmet_results = helmet_model.predict(motorcycle_crop, verbose=False, conf=0.4)

                    status_text = "OK"
                    color_status = (0, 255, 0)

                    for h_res in helmet_results:
                        for h_box in h_res.boxes:
                            h_class = int(h_box.cls[0])

                            #Tọa độ của đầu người
                            hx1, hy1, hx2, hy2 = [int(i) for i in h_box.xyxy[0]]

                            hx1_abs = x1_crop + hx1
                            hy1_abs = y1_crop + hy1
                            hx2_abs = x1_crop + hx2
                            hy2_abs = y1_crop + hy2

                            if h_class == 0:
                                #Có đội mũ -> Vẽ khung xanh lá
                                cv2.rectangle(frame, (hx1_abs, hy1_abs), (hx2_abs, hy2_abs), (0, 255, 0), 2)
                            elif h_class == 1:
                                # KHÔNG ĐỘI MŨ ->Vẽ khung đỏ cảnh báo
                                cv2.rectangle(frame, (hx1_abs, hy1_abs), (hx2_abs, hy2_abs), (0, 0, 255), 2)
                                status_text = "VI PHAM: KHONG MU"
                                color_status = (0, 0, 255)

                    #IN THÔNG TIN LÊN ĐẦU XE
                    label = f"ID: {track_id} - {status_text}"
                    cv2.putText(frame, label, (x1_xe, y1_xe - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_status, 2)

        #GHI KHUNG HÌNH VIDEO MỚI
        out.write(frame)

    cap.release()
    out.release()
    print("HOÀN THÀNH!mở file 'ket_qua_mu_bao_hiem.mp4'.")


if __name__ == '__main__':
    main()