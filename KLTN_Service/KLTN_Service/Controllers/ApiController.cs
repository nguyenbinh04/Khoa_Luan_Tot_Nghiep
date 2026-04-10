using KLTN_Service.Models;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using System.Diagnostics;

namespace KLTN_Service.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class ApiController : ControllerBase
    {
        private readonly IWebHostEnvironment _env;
        private readonly AppDbContext _context;

        // Biến lưu trữ tiến trình Python đang chạy ngầm
        private static Process? _pythonProcess;

        public ApiController(IWebHostEnvironment env, AppDbContext context)
        {
            _env = env;
            _context = context;
        }

        [HttpPost("violations/report")]
        public async Task<IActionResult> ReportViolation(
            [FromForm] string bienSo,
            [FromForm] string loaiViPham,
            [FromForm] int cameraId, // <-- ĐÃ SỬA: Thêm biến hứng CameraId từ Python
            [FromForm] IFormFile anhViPham,
            [FromForm] IFormFile? anhBienSo)
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
                CameraId = cameraId, // <-- ĐÃ SỬA: Gắn CameraId vào Database
                ThoiGian = DateTime.Now,
                DuongDanAnh = fullPath,
                DuongDanAnhBienSo = platePath,
                TrangThaiXuLy = "Chưa xử lý"
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

        // =========================================================
        // API QUẢN LÝ CAMERA TỪ DATABASE
        // =========================================================
        [HttpGet("camera/list")]
        public async Task<IActionResult> GetCameras()
        {
            try
            {
                var cameras = await _context.Cameras.ToListAsync();
                return Ok(new { status = "success", data = cameras });
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { status = "error", message = ex.Message });
            }
        }

        [HttpPost("camera/update")]
        public async Task<IActionResult> UpdateCameraName([FromForm] int id, [FromForm] string newName)
        {
            try
            {
                var cam = await _context.Cameras.FindAsync(id);
                if (cam == null) return NotFound(new { status = "error", message = "Không tìm thấy Camera" });

                cam.TenCamera = newName;
                _context.Cameras.Update(cam);
                await _context.SaveChangesAsync();

                return Ok(new { status = "success", message = "Đã lưu tên Camera mới vào Database!" });
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { status = "error", message = ex.Message });
            }
        }

        // =========================================================
        // API CẤU HÌNH VẠCH KẺ
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
        // UPLOAD VIDEO VÀ BẬT AI CHẠY NGẦM
        // =========================================================
        [HttpPost("ai/start")]
        [DisableRequestSizeLimit]
        public async Task<IActionResult> StartAI([FromForm] IFormFile? videoFile, [FromForm] int cameraId)
        {
            try
            {
                KillZombiePythons();

                // 1. Kiểm tra xem Camera có tồn tại trong Database không
                var cam = await _context.Cameras.FindAsync(cameraId);
                if (cam == null) return BadRequest(new { status = "error", message = "Không tìm thấy Camera trong hệ thống!" });

                string uploadsFolder = Path.Combine(_env.WebRootPath, "videos");
                if (!Directory.Exists(uploadsFolder)) Directory.CreateDirectory(uploadsFolder);

                string filePath = "";

                // 2. NẾU NGƯỜI DÙNG CÓ CHỌN FILE MỚI -> Lưu file và cập nhật vào DB
                if (videoFile != null && videoFile.Length > 0)
                {
                    string fileExtension = Path.GetExtension(videoFile.FileName).ToLower();
                    if (string.IsNullOrEmpty(fileExtension)) fileExtension = ".mp4";

                    // Đặt tên file mới và tránh trùng lặp
                    string fileName = $"cam_{cameraId}_video_{DateTime.Now.Ticks}{fileExtension}";
                    filePath = Path.Combine(uploadsFolder, fileName);

                    using (var stream = new FileStream(filePath, FileMode.Create))
                    {
                        await videoFile.CopyToAsync(stream);
                    }

                    // Lưu tên file mới vào cột DuongDan của MySQL
                    cam.DuongDan = fileName;
                    cam.LoaiNguon = "Video";
                    cam.TrangThai = 1;
                    _context.Cameras.Update(cam);
                    await _context.SaveChangesAsync();
                }
                // 3. NẾU KHÔNG CHỌN FILE -> Lấy video cũ từ DB ra chạy
                else
                {
                    if (!string.IsNullOrEmpty(cam.DuongDan))
                    {
                        filePath = Path.Combine(uploadsFolder, cam.DuongDan);
                        if (!System.IO.File.Exists(filePath))
                        {
                            return BadRequest(new { status = "error", message = $"Video '{cam.DuongDan}' không còn tồn tại trên server. Vui lòng tải lên file mới!" });
                        }
                    }
                    else
                    {
                        return BadRequest(new { status = "error", message = $"Bạn chưa gán video nào cho Camera này cả. Vui lòng tải lên một file!" });
                    }
                }

                // 4. Khởi chạy AI Python với file tương ứng
                string pythonExePath = @"C:\Users\84339\AppData\Local\Microsoft\WindowsApps\python.exe";
                string scriptPath = @"D:\Khóa luận tốt nghiệp\KLTN\python__project\main_system.py";

                ProcessStartInfo startInfo = new ProcessStartInfo
                {
                    FileName = pythonExePath,
                    Arguments = $"\"{scriptPath}\" \"{filePath}\" {cameraId}",
                    WorkingDirectory = Path.GetDirectoryName(scriptPath),
                    UseShellExecute = false,
                    CreateNoWindow = true,
                    RedirectStandardOutput = false,
                    RedirectStandardError = false
                };

                _pythonProcess = new Process { StartInfo = startInfo };
                _pythonProcess.Start();

                return Ok(new { status = "success", message = $"Đã khởi động AI cho '{cam.TenCamera}' thành công!" });
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
                try
                {
                    using (var client = new HttpClient())
                    {
                        client.Timeout = TimeSpan.FromSeconds(2);
                        await client.PostAsync("http://127.0.0.1:5000/shutdown", null);
                    }
                }
                catch { }

                if (_pythonProcess != null && !_pythonProcess.HasExited)
                {
                    try { _pythonProcess.Kill(true); } catch { }
                    _pythonProcess.Dispose();
                    _pythonProcess = null;
                }

                KillZombiePythons();

                return Ok(new { status = "success", message = "Đã dập tắt hoàn toàn hệ thống AI và giải phóng Camera!" });
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { status = "error", message = ex.Message });
            }
        }

        private void KillZombiePythons()
        {
            try
            {
                ProcessStartInfo psi = new ProcessStartInfo
                {
                    FileName = "cmd.exe",
                    Arguments = "/c taskkill /F /IM python.exe /T",
                    CreateNoWindow = true,
                    UseShellExecute = false
                };

                var process = Process.Start(psi);
                process?.WaitForExit();
            }
            catch
            {
            }
        }

        [HttpPost("camera/create")]
        [DisableRequestSizeLimit]
        public async Task<IActionResult> CreateCamera([FromForm] string tenCamera, [FromForm] IFormFile? videoFile)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(tenCamera))
                    return BadRequest(new { status = "error", message = "Tên Camera không được để trống!" });

                // 1. Tạo Camera mới
                var newCam = new Camera { TenCamera = tenCamera };

                // 2. Nếu có gán luôn video thì lưu file và lưu đường dẫn
                if (videoFile != null && videoFile.Length > 0)
                {
                    string uploadsFolder = Path.Combine(_env.WebRootPath, "videos");
                    if (!Directory.Exists(uploadsFolder)) Directory.CreateDirectory(uploadsFolder);

                    string fileExtension = Path.GetExtension(videoFile.FileName).ToLower();
                    if (string.IsNullOrEmpty(fileExtension)) fileExtension = ".mp4";

                    string fileName = $"cam_new_{DateTime.Now.Ticks}{fileExtension}";
                    string filePath = Path.Combine(uploadsFolder, fileName);

                    using (var stream = new FileStream(filePath, FileMode.Create))
                    {
                        await videoFile.CopyToAsync(stream);
                    }

                    newCam.DuongDan = fileName;
                    newCam.LoaiNguon = "Video";
                    newCam.TrangThai = 1;
                }

                _context.Cameras.Add(newCam);
                await _context.SaveChangesAsync();

                return Ok(new { status = "success", message = "Đã thêm Camera mới thành công!", newId = newCam.Id });
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { status = "error", message = ex.Message });
            }
        }
    }
}