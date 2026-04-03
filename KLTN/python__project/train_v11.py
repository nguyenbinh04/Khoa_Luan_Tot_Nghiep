from ultralytics import YOLO
import torch

def main():

    device = 0 if torch.cuda.is_available() else 'cpu'
    print(f"Đang sử dụng thiết bị: {device}")

    model = YOLO("yolo11s.pt")

    results = model.train(
        data="traffic_data.yaml",
        epochs=1,
        imgsz=640,
        batch=16,
        device=device,
        project="KLTN_V11",
        name="train_from_scratch",
        exist_ok=True
    )

if __name__ == '__main__':
    main()