using KLTN_Service.Models;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using System.Diagnostics;
using System.IO;

namespace KLTN_Service.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class ApiController : ControllerBase
    {
        private readonly IWebHostEnvironment _env;
        private readonly AppDbContext _context;
        private static Process? _pythonProcess;

        // CẤU HÌNH THƯ MỤC LƯU TRỮ
        private readonly string _storageFolder = @"D:\DuLieu_GiaoThong_KLTN";

        public ApiController(IWebHostEnvironment env, AppDbContext context)
        {
            _env = env;
            _context = context;
        }

        // =========================================================
        // HÀM XỬ LÝ LÀM SẠCH VÀ ĐẶT TÊN FILE (MỚI)
        // =========================================================
        private string GetCleanFileName(string originalName, string? customName)
        {
            string ext = Path.GetExtension(originalName).ToLower();
            if (string.IsNullOrEmpty(ext)) ext = ".mp4";

            string finalName = "";
            if (!string.IsNullOrWhiteSpace(customName))
            {
                // Lấy tên tự chọn, tự động thêm đuôi file nếu người dùng quên
                finalName = customName.Trim().Replace(" ", "_");
                if (!finalName.EndsWith(ext)) finalName += ext;
            }
            else
            {
                // Nếu để trống, lấy nguyên bản tên file gốc từ máy tính
                finalName = Path.GetFileName(originalName).Replace(" ", "_");
            }

            // Xóa các ký tự đặc biệt bị cấm trên Windows (VD: <, >, :, ", /, \, |, ?, *)
            var invalidChars = Path.GetInvalidFileNameChars();
            return new string(finalName.Where(ch => !invalidChars.Contains(ch)).ToArray());
        }

        [HttpPost("violations/report")]
        public async Task<IActionResult> ReportViolation([FromForm] string bienSo, [FromForm] string loaiViPham, [FromForm] int cameraId, [FromForm] IFormFile anhViPham, [FromForm] IFormFile? anhBienSo)
        {
            string fullPath = await SaveFile(anhViPham, "vi_pham");
            string platePath = anhBienSo != null ? await SaveFile(anhBienSo, "plates") : "";

            var record = new LichSuViPham
            {
                BienSo = bienSo,
                LoaiViPham = loaiViPham,
                CameraId = cameraId,
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
            string path = Path.Combine(_storageFolder, "images", folder);
            if (!Directory.Exists(path)) Directory.CreateDirectory(path);

            string fileName = Guid.NewGuid().ToString() + ".jpg";
            using (var stream = new FileStream(Path.Combine(path, fileName), FileMode.Create))
            {
                await file.CopyToAsync(stream);
            }
            return fileName;
        }

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

        // ĐÃ NÂNG CẤP: Nhận thêm biến customFileName
        [HttpPost("camera/update")]
        [DisableRequestSizeLimit]
        public async Task<IActionResult> UpdateCamera([FromForm] int id, [FromForm] string newName, [FromForm] string? newPath, [FromForm] IFormFile? newVideo, [FromForm] string? customFileName)
        {
            try
            {
                var cam = await _context.Cameras.FindAsync(id);
                if (cam == null) return NotFound(new { status = "error", message = "Không tìm thấy Camera" });

                cam.TenCamera = newName;

                if (newVideo != null && newVideo.Length > 0)
                {
                    string uploadsFolder = Path.Combine(_storageFolder, "videos");
                    if (!Directory.Exists(uploadsFolder)) Directory.CreateDirectory(uploadsFolder);

                    // Sử dụng hàm làm sạch tên file mới
                    string fileName = GetCleanFileName(newVideo.FileName, customFileName);

                    using (var stream = new FileStream(Path.Combine(uploadsFolder, fileName), FileMode.Create))
                    {
                        await newVideo.CopyToAsync(stream);
                    }
                    cam.DuongDan = fileName;
                    cam.LoaiNguon = "Video";
                }
                else if (!string.IsNullOrWhiteSpace(newPath))
                {
                    cam.DuongDan = newPath.Trim();
                    cam.LoaiNguon = (newPath.StartsWith("http") || newPath.StartsWith("rtsp")) ? "Stream" : "Khác";
                }

                _context.Cameras.Update(cam);
                await _context.SaveChangesAsync();

                return Ok(new { status = "success", message = "Đã cập nhật thông tin Camera!" });
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { status = "error", message = ex.Message });
            }
        }

        [HttpPost("camera/delete")]
        public async Task<IActionResult> DeleteCamera([FromForm] int id)
        {
            try
            {
                var cam = await _context.Cameras.FindAsync(id);
                if (cam == null) return NotFound(new { status = "error", message = "Không tìm thấy Camera!" });

                var configs = _context.CauHinhVungs.Where(x => x.CameraId == id);
                _context.CauHinhVungs.RemoveRange(configs);

                _context.Cameras.Remove(cam);
                await _context.SaveChangesAsync();

                return Ok(new { status = "success", message = "Đã xóa Camera thành công!" });
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { status = "error", message = ex.Message });
            }
        }

        // ĐÃ NÂNG CẤP: Nhận thêm biến customFileName
        [HttpPost("camera/create")]
        [DisableRequestSizeLimit]
        public async Task<IActionResult> CreateCamera([FromForm] string tenCamera, [FromForm] string? duongDan, [FromForm] IFormFile? videoFile, [FromForm] string? customFileName)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(tenCamera)) return BadRequest(new { status = "error", message = "Tên không được để trống!" });

                var newCam = new Camera { TenCamera = tenCamera };

                if (videoFile != null && videoFile.Length > 0)
                {
                    string uploadsFolder = Path.Combine(_storageFolder, "videos");
                    if (!Directory.Exists(uploadsFolder)) Directory.CreateDirectory(uploadsFolder);

                    // Sử dụng hàm làm sạch tên file mới
                    string fileName = GetCleanFileName(videoFile.FileName, customFileName);

                    using (var stream = new FileStream(Path.Combine(uploadsFolder, fileName), FileMode.Create))
                    {
                        await videoFile.CopyToAsync(stream);
                    }
                    newCam.DuongDan = fileName;
                    newCam.LoaiNguon = "Video";
                    newCam.TrangThai = 1;
                }
                else if (!string.IsNullOrWhiteSpace(duongDan))
                {
                    newCam.DuongDan = duongDan.Trim();
                    newCam.LoaiNguon = "Stream";
                    newCam.TrangThai = 1;
                }

                _context.Cameras.Add(newCam);
                await _context.SaveChangesAsync();

                return Ok(new { status = "success", message = "Đã thêm Camera mới!", newId = newCam.Id });
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { status = "error", message = ex.Message });
            }
        }

        [HttpGet("config/coordinates/{cameraId}")]
        public async Task<IActionResult> GetCoordinates(int cameraId)
        {
            var configs = await _context.CauHinhVungs.Where(x => x.CameraId == cameraId).ToListAsync();
            return Ok(new { status = "success", data = configs });
        }

        [HttpPost("config/save")]
        public async Task<IActionResult> SaveConfig([FromForm] int cameraId, [FromForm] string loaiVung, [FromForm] string toaDoJson)
        {
            var existingConfig = await _context.CauHinhVungs.FirstOrDefaultAsync(x => x.CameraId == cameraId && x.LoaiVung == loaiVung);
            if (string.IsNullOrEmpty(toaDoJson) || toaDoJson == "[]")
            {
                if (existingConfig != null) { _context.CauHinhVungs.Remove(existingConfig); await _context.SaveChangesAsync(); }
                return Ok(new { status = "success", message = "Đã xóa vạch cấu hình cũ!" });
            }
            if (existingConfig != null) { existingConfig.ToaDoJson = toaDoJson; _context.CauHinhVungs.Update(existingConfig); }
            else { _context.CauHinhVungs.Add(new CauHinhVung { CameraId = cameraId, LoaiVung = loaiVung, ToaDoJson = toaDoJson }); }
            await _context.SaveChangesAsync();
            return Ok(new { status = "success", message = "Đã lưu tọa độ mới!" });
        }

        [HttpPost("violations/approve")]
        public async Task<IActionResult> ApproveViolation([FromForm] int id, [FromForm] string bienSoMoi)
        {
            var record = await _context.LichSuViPhams.FindAsync(id);
            if (record == null) return NotFound(new { status = "error", message = "Không tìm thấy dữ liệu!" });
            record.BienSo = bienSoMoi.ToUpper();
            record.TrangThaiXuLy = "Đã duyệt";
            _context.LichSuViPhams.Update(record);
            await _context.SaveChangesAsync();
            return Ok(new { status = "success", message = "Đã duyệt!" });
        }

        [HttpPost("ai/start")]
        public async Task<IActionResult> StartAI([FromForm] int cameraId)
        {
            try
            {
                KillZombiePythons();

                var cam = await _context.Cameras.FindAsync(cameraId);
                if (cam == null) return BadRequest(new { status = "error", message = "Không tìm thấy Camera!" });

                string filePath = cam.DuongDan;
                if (string.IsNullOrWhiteSpace(filePath))
                    return BadRequest(new { status = "error", message = "Camera này chưa được cấu hình Đường dẫn hoặc Video. Hãy bấm Sửa để thêm!" });

                if (!filePath.StartsWith("http") && !filePath.StartsWith("rtsp") && !filePath.Contains("://") && cameraId.ToString() != "0")
                {
                    string fullLocalPath = Path.Combine(_storageFolder, "videos", filePath);
                    if (!System.IO.File.Exists(fullLocalPath))
                        return BadRequest(new { status = "error", message = $"Không tìm thấy file video ({filePath}). Bạn hãy Sửa lại camera và tải lên video khác!" });
                    filePath = fullLocalPath;
                }

                string baseUrl = $"{Request.Scheme}://{Request.Host}";
                string pythonExePath = @"C:\Users\84339\AppData\Local\Microsoft\WindowsApps\python.exe";
                string scriptPath = @"D:\Khóa luận tốt nghiệp\KLTN\python__project\main_system.py";

                ProcessStartInfo startInfo = new ProcessStartInfo
                {
                    FileName = pythonExePath,
                    Arguments = $"\"{scriptPath}\" \"{filePath}\" {cameraId} \"{baseUrl}\"",
                    WorkingDirectory = Path.GetDirectoryName(scriptPath),
                    UseShellExecute = false,
                    CreateNoWindow = true
                };

                _pythonProcess = new Process { StartInfo = startInfo };
                _pythonProcess.Start();

                return Ok(new { status = "success", message = $"Đã khởi động AI cho '{cam.TenCamera}'!" });
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { status = "error", message = "Lỗi khởi động AI: " + ex.Message });
            }
        }

        [HttpPost("ai/stop")]
        public async Task<IActionResult> StopAI()
        {
            try
            {
                try { using (var client = new HttpClient() { Timeout = TimeSpan.FromSeconds(2) }) { await client.PostAsync("http://127.0.0.1:5000/shutdown", null); } } catch { }
                if (_pythonProcess != null && !_pythonProcess.HasExited)
                {
                    try { _pythonProcess.Kill(true); } catch { }
                    _pythonProcess.Dispose(); _pythonProcess = null;
                }
                KillZombiePythons();
                return Ok(new { status = "success", message = "Đã tắt AI thành công!" });
            }
            catch (Exception ex) { return StatusCode(500, new { status = "error", message = ex.Message }); }
        }

        private void KillZombiePythons()
        {
            try { Process.Start(new ProcessStartInfo { FileName = "cmd.exe", Arguments = "/c taskkill /F /IM python.exe /T", CreateNoWindow = true, UseShellExecute = false })?.WaitForExit(); } catch { }
        }
    }
}