from ultralytics import YOLO
import torch

def main():
    device = '0' if torch.cuda.is_available() else 'cpu'
    print(f"Đang tiến hành huấn luyện sử dụng: {device}")

    model = YOLO("yolo11s.pt")
    results = model.train(
        data="traffic_data.yaml",
        epochs=5,
        imgsz=640,
        batch=16,
        device=device,
        project="traffic_results",
        name="run_01"
    )

if __name__ == '__main__':
    main()