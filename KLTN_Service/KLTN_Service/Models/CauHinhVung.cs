using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace KLTN_Service.Models
{
    [Table("cauhinhvung")] 
    public class CauHinhVung
    {
        [Key]
        public int Id { get; set; }
        public int CameraId { get; set; } = 1;
        public string LoaiVung { get; set; } 
        public string ToaDoJson { get; set; } 
    }
}