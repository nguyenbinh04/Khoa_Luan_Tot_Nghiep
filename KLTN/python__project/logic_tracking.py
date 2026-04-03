import cv2
from ultralytics import YOLO

#Tải mô hình
model = YOLO("D:/Khóa luận tốt nghiệp/KLTN/python__project/runs/detect/traffic_results/run_01/weights/traffic_model.pt")
ten_xe_custom = {0:'xe buyt', 1: 'xe container', 2: 'xe cuu hoa', 3: 'xe dap', 4: 'xe con', 5: 'xe may', 6: 'xe tai', 7: 'xe van'}

#Mở video gốc
video_path = "D:/Khóa luận tốt nghiệp/KLTN/datasets/videos/lane.mp4"
cap = cv2.VideoCapture(video_path)

# Lấy thông số của video gốc
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

# Đường dẫn lưu file kết quả
output_path = "D:/Khóa luận tốt nghiệp/KLTN/datasets/videos/test9_ket_qua.mp4"

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break


    results = model.track(frame, persist=True, tracker="bytetrack.yaml", verbose=False)

    #Trích xuất dữ liệu và vẽ
    if results[0].boxes.id is not None:
        boxes = results[0].boxes.xyxy.cpu().numpy()
        track_ids = results[0].boxes.id.int().cpu().tolist()
        class_ids = results[0].boxes.cls.int().cpu().tolist()

        for box, track_id, class_id in zip(boxes, track_ids, class_ids):
            x1, y1, x2, y2 = [int(i) for i in box]
            ten_xe = ten_xe_custom.get(class_id, "Khong_xac_dinh")

            color = (0, 255, 0)
            # Vẽ hộp và chữ
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            label = f"{ten_xe} ID:{track_id}"
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(frame, (x1, y1 - 20), (x1 + w, y1), color, -1)
            cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

    out.write(frame)


    cv2.imshow("He thong giam sat", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
out.release()
cv2.destroyAllWindows()

print(f"Đã lưu video thành công tại: {output_path}")