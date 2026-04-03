from ultralytics import YOLO

def main():
    model = YOLO("yolo11s.pt")

    print("Bắt đầu huấn luyện mô hình cắt biển số...")
    results = model.train(
        data="plate.yaml",
        epochs=5,
        imgsz=640,
        batch=16,
        device='cpu',
        project="LPR_Project",
        name="model_bien_so"
    )

if __name__ == '__main__':
    main()