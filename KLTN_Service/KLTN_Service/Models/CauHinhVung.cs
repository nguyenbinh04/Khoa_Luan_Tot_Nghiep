using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace KLTN_Service.Models
{
    [Table("cauhinhvung")] // Phải khớp với tên bảng trong MySQL
    public class CauHinhVung
    {
        [Key]
        public int Id { get; set; }
        public int CameraId { get; set; } = 1;
        public string LoaiVung { get; set; } // Ví dụ: 'Vach_DenDo'
        public string ToaDoJson { get; set; } // Chứa mảng JSON tọa độ
    }
}