import requests

# 1. Điền chính xác đường link từ trình duyệt C# của bạn vào đây
# LƯU Ý: Thay port 7123 bằng số port thực tế trên máy bạn
API_URL = "https://localhost:7114/api/api/violations/report"

# 2. Chuẩn bị thông tin vi phạm giả lập
data_vi_pham = {
    "bienSo": "30G-999.99",
    "loaiViPham": "Vuot den do (TEST)"
}

# 3. Mở file ảnh để chuẩn bị gửi đi (Nhớ đổi tên file cho đúng với ảnh của bạn)
# 'rb' nghĩa là read binary (đọc ảnh dưới dạng mã nhị phân)
file_anh = "ket_qua_bien_bao.jpg"

try:
    with open(file_anh, "rb") as image_file:
        files = {
            "anhViPham": (file_anh, image_file, "image/jpeg")
        }

        print("Đang bắn dữ liệu sang C#... Chờ một chút...")

        # 4. Nhấn nút GỬI (POST)
        # verify=False để bỏ qua lỗi chứng chỉ bảo mật HTTPS khi test ở localhost
        response = requests.post(API_URL, data=data_vi_pham, files=files, verify=False)

        # 5. Xem C# trả lời gì
        print("MÃ TRẠNG THÁI:", response.status_code)
        print("NỘI DUNG C# TRẢ LỜI:", response.json())

except FileNotFoundError:
    print(f"LỖI: Không tìm thấy bức ảnh '{file_anh}'. Bạn đã để nó cùng chỗ với file code chưa?")
except Exception as e:
    print("LỖI KẾT NỐI:", e)