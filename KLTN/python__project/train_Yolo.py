from ultralytics import YOLO
import torch

def main():
    device = '0' if torch.cuda.is_available() else 'cpu'
    print(f"Đang tiến hành huấn luyện sử dụng: {device}")

    model = YOLO("yolov8x.pt")

    results = model.train(
        data="data.yaml",
        epochs=2,
        imgsz=640,
        batch=4,
        device=device,
        project="traffic_results_x",
        name="run_x_01"
    )

if __name__ == '__main__':
    main()