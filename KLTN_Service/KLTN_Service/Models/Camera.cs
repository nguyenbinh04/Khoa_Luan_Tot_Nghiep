using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace KLTN_Service.Models
{
    [Table("cameras")] // Tên bảng trong MySQL của bạn đang viết thường
    public class Camera
    {
        [Key]
        public int Id { get; set; }
        public string? TenCamera { get; set; }
        public string? LoaiNguon { get; set; }
        public string? DuongDan { get; set; }
        public int? TrangThai { get; set; }
    }
}