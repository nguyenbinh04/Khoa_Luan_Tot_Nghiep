using KLTN_Service.Models;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using System.Diagnostics; // BẮT BUỘC THÊM: Để C# có thể ra lệnh cho hệ điều hành chạy file Python

namespace KLTN_Service.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class ApiController : ControllerBase
    {
        private readonly IWebHostEnvironment _env;
        private readonly AppDbContext _context;

        // BẮT BUỘC THÊM: Biến lưu trữ tiến trình Python đang chạy ngầm
        private static Process? _pythonProcess;

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
            string fullPath = await SaveFile(anhViPham, "vi_pham");
            string platePath = "";

            if (anhBienSo != null)
            {
                platePath = await SaveFile(anhBienSo, "plates");
            }

            var record = new LichSuViPham
            {
                BienSo = bienSo,
                LoaiViPham = loaiViPham,
                ThoiGian = DateTime.Now,
                DuongDanAnh = fullPath,
                DuongDanAnhBienSo = platePath,
                TrangThaiXuLy = "Chưa xử lý" // Thêm mặc định trạng thái
            };

            _context.LichSuViPhams.Add(record);
            await _context.SaveChangesAsync();

            return Ok(new { status = "success" });
        }

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

        [HttpPost("config/save")]
        public async Task<IActionResult> SaveConfig([FromForm] int cameraId, [FromForm] string loaiVung, [FromForm] string toaDoJson)
        {
            try
            {
                var existingConfig = await _context.CauHinhVungs
                    .FirstOrDefaultAsync(x => x.CameraId == cameraId && x.LoaiVung == loaiVung);

                if (string.IsNullOrEmpty(toaDoJson) || toaDoJson == "[]")
                {
                    if (existingConfig != null)
                    {
                        _context.CauHinhVungs.Remove(existingConfig);
                        await _context.SaveChangesAsync();
                    }
                    return Ok(new { status = "success", message = "Đã xóa vạch cấu hình cũ thành công!" });
                }

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

        [HttpPost("config/clear-all/{cameraId}")]
        public async Task<IActionResult> ClearAllConfig(int cameraId)
        {
            try
            {
                var configs = _context.CauHinhVungs.Where(x => x.CameraId == cameraId);
                if (configs.Any())
                {
                    _context.CauHinhVungs.RemoveRange(configs);
                    await _context.SaveChangesAsync();
                }
                return Ok(new { status = "success", message = "Đã dọn dẹp sạch cấu hình cũ cho Camera " + cameraId });
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { status = "error", message = ex.Message });
            }
        }

        [HttpPost("violations/approve")]
        public async Task<IActionResult> ApproveViolation([FromForm] int id, [FromForm] string bienSoMoi)
        {
            try
            {
                var record = await _context.LichSuViPhams.FindAsync(id);
                if (record == null)
                {
                    return NotFound(new { status = "error", message = "Không tìm thấy dữ liệu vi phạm này!" });
                }

                record.BienSo = bienSoMoi.ToUpper();
                record.TrangThaiXuLy = "Đã duyệt";

                _context.LichSuViPhams.Update(record);
                await _context.SaveChangesAsync();

                return Ok(new { status = "success", message = "Đã duyệt và cập nhật biển số thành công!" });
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { status = "error", message = ex.Message });
            }
        }



        // =========================================================
        // TÍNH NĂNG MỚI: UPLOAD VIDEO VÀ BẬT AI CHẠY NGẦM
        // =========================================================
        [HttpPost("ai/start")]
        public async Task<IActionResult> StartAI([FromForm] IFormFile videoFile)
        {
            try
            {
                // BƯỚC QUAN TRỌNG: Dọn dẹp sạch sẽ các Zombie Python từ phiên làm việc trước
                KillZombiePythons();

                if (videoFile == null || videoFile.Length == 0)
                {
                    return BadRequest(new { status = "error", message = "Vui lòng chọn một file video!" });
                }

                // Lưu file Video
                string uploadsFolder = Path.Combine(_env.WebRootPath, "videos");
                if (!Directory.Exists(uploadsFolder)) Directory.CreateDirectory(uploadsFolder);
                string filePath = Path.Combine(uploadsFolder, "current_test_video.mp4");

                using (var stream = new FileStream(filePath, FileMode.Create))
                {
                    await videoFile.CopyToAsync(stream);
                }

                // Cấu hình đường dẫn Python
                string pythonExePath = @"C:\Users\84339\AppData\Local\Microsoft\WindowsApps\python.exe";
                string scriptPath = @"D:\Khóa luận tốt nghiệp\KLTN\python__project\main_system.py";

                // Khởi động AI
                ProcessStartInfo startInfo = new ProcessStartInfo
                {
                    FileName = pythonExePath,
                    Arguments = $"\"{scriptPath}\" \"{filePath}\"",
                    WorkingDirectory = Path.GetDirectoryName(scriptPath),
                    UseShellExecute = false,
                    CreateNoWindow = true,
                    RedirectStandardOutput = false,
                    RedirectStandardError = false
                };

                _pythonProcess = new Process { StartInfo = startInfo };
                _pythonProcess.Start();

                return Ok(new { status = "success", message = "Đã tải video và khởi động AI thành công!" });
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { status = "error", message = "Không thể khởi động AI: " + ex.Message });
            }
        }

        [HttpPost("ai/stop")]
        public async Task<IActionResult> StopAI()
        {
            try
            {
                // 1. BẤM NÚT TỰ HỦY: Gửi lệnh sang API của Python
                try
                {
                    using (var client = new HttpClient())
                    {
                        client.Timeout = TimeSpan.FromSeconds(2);
                        await client.PostAsync("http://127.0.0.1:5000/shutdown", null);
                    }
                }
                catch { } // Bỏ qua nếu Python đã tắt trước đó rồi

                // 2. DỌN DẸP BỘ NHỚ TRONG C#
                if (_pythonProcess != null && !_pythonProcess.HasExited)
                {
                    try { _pythonProcess.Kill(true); } catch { }
                    _pythonProcess.Dispose();
                    _pythonProcess = null;
                }

                // 3. QUÉT RÁC PHÒNG HỜ BẰNG LỆNH WINDOWS
                KillZombiePythons();

                return Ok(new { status = "success", message = "Đã dập tắt hoàn toàn hệ thống AI và giải phóng Camera!" });
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { status = "error", message = ex.Message });
            }
        }

        // =========================================================
        // HÀM HỖ TRỢ: ĐI SĂN ZOMBIE BẰNG LỆNH WINDOWS CMD
        // =========================================================
        private void KillZombiePythons()
        {
            try
            {
                // Mở CMD ngầm và chạy lệnh taskkill
                // /F: Ép buộc tắt (Force)
                // /IM: Tìm theo tên file (Image Name)
                // /T: Diệt cả mẹ lẫn con (Kill Tree)
                ProcessStartInfo psi = new ProcessStartInfo
                {
                    FileName = "cmd.exe",
                    Arguments = "/c taskkill /F /IM python.exe /T",
                    CreateNoWindow = true,     // Chạy ngầm không văng cửa sổ
                    UseShellExecute = false
                };

                var process = Process.Start(psi);
                process?.WaitForExit(); // Chờ dọn dẹp xong mới cho Web chạy tiếp
            }
            catch
            {
                // Bỏ qua nếu không tìm thấy tiến trình nào để tắt
            }
        }
    }
}