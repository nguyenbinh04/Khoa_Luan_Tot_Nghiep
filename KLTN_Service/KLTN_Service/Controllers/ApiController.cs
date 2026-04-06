using KLTN_Service.Models;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace KLTN_Service.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class ApiController : ControllerBase
    {
        private readonly IWebHostEnvironment _env;
        private readonly AppDbContext _context; // Khai báo ống kết nối DB

        // Tiêm (Inject) môi trường và DbContext vào Controller
        public ApiController(IWebHostEnvironment env, AppDbContext context)
        {
            _env = env;
            _context = context;
        }

        [HttpPost("violations/report")]
        public async Task<IActionResult> ReportViolation(
    [FromForm] string bienSo, [FromForm] string loaiViPham,
    [FromForm] IFormFile anhViPham, [FromForm] IFormFile? anhBienSo)
        {
            // 1. Lưu ảnh toàn cảnh
            string fullPath = await SaveFile(anhViPham, "vi_pham");

            // 2. Lưu ảnh biển số (nếu có)
            string platePath = "";
            if (anhBienSo != null)
            {
                platePath = await SaveFile(anhBienSo, "plates");
            }

            // 3. Lưu vào Database
            var record = new LichSuViPham
            {
                BienSo = bienSo,
                LoaiViPham = loaiViPham,
                ThoiGian = DateTime.Now,
                DuongDanAnh = fullPath,
                DuongDanAnhBienSo = platePath // Cột mới thêm
            };
            _context.LichSuViPhams.Add(record);
            await _context.SaveChangesAsync();

            return Ok(new { status = "success" });
        }

        // Hàm phụ để lưu file cho gọn code
        private async Task<string> SaveFile(IFormFile file, string folder)
        {
            string wwwRoot = _env.WebRootPath;
            string path = Path.Combine(wwwRoot, "images", folder);
            if (!Directory.Exists(path)) Directory.CreateDirectory(path);

            string fileName = Guid.NewGuid().ToString() + ".jpg";
            using (var stream = new FileStream(Path.Combine(path, fileName), FileMode.Create))
            {
                await file.CopyToAsync(stream);
            }
            return fileName;
        }
        // =========================================================
        // 1. API LẤY TỌA ĐỘ (Dành cho Python gọi để cập nhật vạch kẻ)
        // =========================================================
        [HttpGet("config/coordinates/{cameraId}")]
        public async Task<IActionResult> GetCoordinates(int cameraId)
        {
            try
            {
                var configs = await _context.CauHinhVungs
                                            .Where(x => x.CameraId == cameraId)
                                            .ToListAsync();
                return Ok(new { status = "success", data = configs });
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { status = "error", message = ex.Message });
            }
        }

        // =========================================================
        // 2. API LƯU HOẶC XÓA TỌA ĐỘ (Nâng cấp)
        // =========================================================
        [HttpPost("config/save")]
        public async Task<IActionResult> SaveConfig([FromForm] int cameraId, [FromForm] string loaiVung, [FromForm] string toaDoJson)
        {
            try
            {
                var existingConfig = await _context.CauHinhVungs
                    .FirstOrDefaultAsync(x => x.CameraId == cameraId && x.LoaiVung == loaiVung);

                // LOGIC MỚI: Nếu Web gửi mảng rỗng "[]" -> XÓA cấu hình cũ
                if (string.IsNullOrEmpty(toaDoJson) || toaDoJson == "[]")
                {
                    if (existingConfig != null)
                    {
                        _context.CauHinhVungs.Remove(existingConfig);
                        await _context.SaveChangesAsync();
                    }
                    return Ok(new { status = "success", message = "Đã xóa vạch cấu hình cũ thành công!" });
                }

                // CÒN LẠI: Lưu hoặc Cập nhật như bình thường
                if (existingConfig != null)
                {
                    existingConfig.ToaDoJson = toaDoJson;
                    _context.CauHinhVungs.Update(existingConfig);
                }
                else
                {
                    var newConfig = new CauHinhVung
                    {
                        CameraId = cameraId,
                        LoaiVung = loaiVung,
                        ToaDoJson = toaDoJson
                    };
                    _context.CauHinhVungs.Add(newConfig);
                }

                await _context.SaveChangesAsync();
                return Ok(new { status = "success", message = "Đã lưu tọa độ mới thành công!" });
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { status = "error", message = ex.Message });
            }
        }

        //xóa tất cả cấu hình của camera (nếu có)
        [HttpPost("config/clear-all/{cameraId}")]
        public async Task<IActionResult> ClearAllConfig(int cameraId)
        {
            try
            {
                // Tìm tất cả các vạch (vượt đèn đỏ, lấn làn...) của camera này
                var configs = _context.CauHinhVungs.Where(x => x.CameraId == cameraId);

                if (configs.Any())
                {
                    _context.CauHinhVungs.RemoveRange(configs); // Xóa sạch sành sanh
                    await _context.SaveChangesAsync();
                }

                return Ok(new { status = "success", message = "Đã dọn dẹp sạch cấu hình cũ cho Camera " + cameraId });
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { status = "error", message = ex.Message });
            }
        }
    }
}
