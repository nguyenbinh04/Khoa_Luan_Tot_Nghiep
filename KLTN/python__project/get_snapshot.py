import cv2
import sys


def main():
    video_path = sys.argv[1]
    output_path = sys.argv[2]

    # Mở video/stream
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        exit(1)

    # Đọc frame đầu tiên hoặc frame sau 1 giây để ảnh rõ nét
    for _ in range(5):
        ret, frame = cap.read()

    if ret:
        cv2.imwrite(output_path, frame)
        print("Success")

    cap.release()


if __name__ == "__main__":
    main()