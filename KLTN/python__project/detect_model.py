from ultralytics import YOLO

model = YOLO("D:/Khóa luận tốt nghiệp/KLTN/python__project/runs/detect/traffic_results/run_01/weights/traffic_model.pt")

results = model.predict(
    source="D:/Khóa luận tốt nghiệp/KLTN/datasets/videos/test1.mp4",
    show=True,
    save=True
)