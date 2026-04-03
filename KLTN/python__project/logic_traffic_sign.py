import cv2
from ultralytics import YOLO
import tkinter as tk
from tkinter import filedialog
import os


def select_file():

    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Chọn file ảnh hoặc video để nhận diện biển báo",
        filetypes=[
            ("Tất cả định dạng hỗ trợ", "*.mp4 *.avi *.jpg *.jpeg *.png"),
            ("Video", "*.mp4 *.avi"),
            ("Ảnh", "*.jpg *.jpeg *.png")
        ]
    )
    return file_path


def main():
    #Tải mô hình
    model_path = "D:/Khóa luận tốt nghiệp/KLTN/python__project/runs/detect/sign_model/weights/sign_model.pt"
    if not os.path.exists(model_path):
        print(f"LỖI: Không tìm thấy file mô hình tại {model_path}")
        return
    model = YOLO(model_path)

    #Chọn file
    input_path = select_file()
    if not input_path:
        print("Bạn chưa chọn file nào. Thoát chương trình.")
        return

    is_image = input_path.lower().endswith(('.png', '.jpg', '.jpeg'))

    if is_image:
        frame = cv2.imread(input_path)
        results = model.predict(frame, conf=0.4, verbose=False)

        for box in results[0].boxes:
            x1, y1, x2, y2 = [int(i) for i in box.xyxy[0]]
            class_id = int(box.cls[0])
            label = f"Bien bao: {model.names[class_id]}"

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 165, 255), 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)

        cv2.imshow("Ket qua", cv2.resize(frame, (1024, 576)))
        cv2.imwrite("ket_qua_bien_bao.jpg", frame)
        print("Đã lưu ảnh kết quả: ket_qua_bien_bao.jpg")
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    else:
        cap = cv2.VideoCapture(input_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))

        out = cv2.VideoWriter("ket_qua_bien_bao.avi", cv2.VideoWriter_fourcc(*'XVID'), fps, (width, height))

        print("Đang xử lý video... Bấm 'q' để thoát.")
        while cap.isOpened():
            success, frame = cap.read()
            if not success: break

            results = model.predict(frame, conf=0.4, verbose=False)

            for box in results[0].boxes:
                x1, y1, x2, y2 = [int(i) for i in box.xyxy[0]]
                class_id = int(box.cls[0])
                label = f"Bien bao: {model.names[class_id]}"

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 165, 255), 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 2)

            out.write(frame)
            cv2.imshow("He thong nhan dien", cv2.resize(frame, (1024, 576)))

            if cv2.waitKey(1) & 0xFF == ord('q'): break

        cap.release()
        out.release()
        cv2.destroyAllWindows()
        print("Đã lưu video kết quả: ket_qua_bien_bao.avi")


if __name__ == "__main__":
    main()