import cv2
import easyocr
from ultralytics import YOLO

print("Đang tải mô hình YOLO và EasyOCR...")
import cv2
from ultralytics import YOLO
import tkinter as tk
from tkinter import filedialog
import os


def select_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Chọn file ảnh hoặc video",
        filetypes=[
            ("Tất cả định dạng", "*.mp4 *.avi *.jpg *.jpeg *.png"),
            ("Video", "*.mp4 *.avi"),
            ("Ảnh", "*.jpg *.jpeg *.png")
        ]
    )
    return file_path


def main():
    #TẢI MÔ HÌNH
    model_path = "D:/Khóa luận tốt nghiệp/KLTN/python__project/runs/detect/LPR_Project/model_bien_so/weights/lpr_model.pt"

    if not os.path.exists(model_path):
        print(f"LỖI: Không tìm thấy file mô hình tại {model_path}")
        return

    model = YOLO(model_path)

    #CHỌN FILE
    input_path = select_file()
    if not input_path:
        print("Đã hủy chọn file. Thoát chương trình.")
        return

    is_image = input_path.lower().endswith(('.png', '.jpg', '.jpeg'))

    if is_image:
        frame = cv2.imread(input_path)
        print("Đang xử lý ảnh... Vui lòng đợi.")

        results = model.predict(frame, conf=0.5, verbose=False)

        for box in results[0].boxes:
            x1, y1, x2, y2 = [int(i) for i in box.xyxy[0]]

            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(frame, "Bien so", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        output_img = "D:/Khóa luận tốt nghiệp/KLTN/datasets/anh/ket_qua_bien_so.jpg"
        cv2.imwrite(output_img, frame)

        cv2.imshow("Nhan dien Bien So - KLTN", cv2.resize(frame, (1024, 576)))
        print(f"Đã lưu ảnh kết quả tại: {output_img}")

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    else:
        cap = cv2.VideoCapture(input_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))

        output_vid = "D:/Khóa luận tốt nghiệp/KLTN/datasets/videos/ket_qua_bien_so.avi"
        out = cv2.VideoWriter(output_vid, cv2.VideoWriter_fourcc(*'XVID'), fps, (width, height))

        print("Đang xử lý video... Bấm 'q'để thoát")
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            results = model.predict(frame, conf=0.5, verbose=False)

            for box in results[0].boxes:
                x1, y1, x2, y2 = [int(i) for i in box.xyxy[0]]

                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(frame, "Bien so", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            out.write(frame)
            cv2.imshow("Nhan Dien Bien So", cv2.resize(frame, (1024, 576)))

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        out.release()
        cv2.destroyAllWindows()
        print(f"Đã lưu video kết quả tại: {output_vid}")


if __name__ == "__main__":
    main()
duong_dan_model_yolo = "D:/Khóa luận tốt nghiệp/KLTN/python__project/runs/detect/LPR_Project/model_bien_so/weights/lpr_model.pt"

try:
    plate_model = YOLO(duong_dan_model_yolo)
except Exception as e:
    print(f"LỖI: Không tìm thấy mô hình YOLO tại {duong_dan_model_yolo}.")
    exit()

reader = easyocr.Reader(['en'], gpu=False)

image_path = "D:/Khóa luận tốt nghiệp/KLTN/datasets/anh/bs.jpg"
img = cv2.imread(image_path)

if img is None:
    print(f"Lỗi: Không đọc được ảnh tại {image_path}")
    exit()

print("Đang tìm kiếm biển số trên ảnh...")
results = plate_model.predict(img)


for r in results:
    boxes = r.boxes
    for box in boxes:
        x1, y1, x2, y2 = [int(i) for i in box.xyxy[0]]

        plate_img = img[y1:y2, x1:x2]

        plate_img = cv2.resize(plate_img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        gray_plate = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
        _, thresh_plate = cv2.threshold(gray_plate, 120, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        ky_tu_cho_phep = '0123456789ABCDEFGHJKLMNPRSTUVWXYZ.-'
        ocr_results = reader.readtext(thresh_plate, allowlist=ky_tu_cho_phep)


        ocr_results = sorted(ocr_results, key=lambda r: r[0][0][1])

        bien_so_text = ""
        for ocr_res in ocr_results:
            text = ocr_res[1]
            confidence = ocr_res[2]

            if confidence > 0.2:
                text_clean = ''.join(e for e in text if e.isalnum())
                bien_so_text += text_clean + "-"

        bien_so_text = bien_so_text.strip("-").upper()
        if bien_so_text == "":
            bien_so_text = "KHONG_DOC_DUOC"

        print(f"=> Phát hiện biển số: {bien_so_text}")

        color = (0, 255, 0)
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        (w, h), _ = cv2.getTextSize(bien_so_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
        cv2.rectangle(img, (x1, y1 - 30), (x1 + w, y1), color, -1)
        cv2.putText(img, bien_so_text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

output_path = "ket_qua_lpr_hoan_chinh.jpg"
cv2.imwrite(output_path, img)
print(f"\nĐã lưu ảnh kết quả thành công vào: {output_path}")