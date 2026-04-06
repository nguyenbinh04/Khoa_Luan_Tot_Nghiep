using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace KLTN_Service.Models
{
    [Table("lichsuvipham")] // Viết thường để khớp chuẩn MySQL
    public class LichSuViPham
    {
        [Key]
        public int Id { get; set; }
        public int CameraId { get; set; } = 1; // Tạm thời mặc định là Camera số 1
        public string? BienSo { get; set; }
        public string? LoaiViPham { get; set; }
        public DateTime ThoiGian { get; set; }
        public string? DuongDanAnh { get; set; }
        public string? DuongDanAnhBienSo { get; set; } // Cột mới để lưu đường dẫn ảnh biển số
        public string? TrangThaiXuLy { get; set; } = "Chờ duyệt";
    }
}