from ultralytics import YOLO

def main():

    model = YOLO("yolo11s.pt")

    print("Bắt đầu huấn luyện mô hình bắt mũ bảo hiểm...")
    results = model.train(
        data="helmet.yaml",
        epochs=2,
        imgsz=640,
        batch=16,
        device='cpu',
        project="KLTN_Helmet",
        name="model_helmet"
    )

if __name__ == '__main__':
    main()