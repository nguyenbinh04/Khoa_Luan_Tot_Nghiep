using KLTN_Service.Models;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using System.Diagnostics;
using System.IO;
using System.Net.Http;

namespace KLTN_Service.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class ApiController : ControllerBase
    {
        private readonly IWebHostEnvironment _env;
        private readonly AppDbContext _context;
        // Tiến trình chạy chính cho trang Live
        private static Process? _pythonProcess;

        private readonly string _storageFolder = @"D:\DuLieu_GiaoThong_KLTN";

        public ApiController(IWebHostEnvironment env, AppDbContext context)
        {
            _env = env;
            _context = context;
        }

        private string GetCleanFileName(string originalName, string? customName)
        {
            string ext = Path.GetExtension(originalName).ToLower();
            if (string.IsNullOrEmpty(ext)) ext = ".mp4";
            string finalName = !string.IsNullOrWhiteSpace(customName) ? customName.Trim().Replace(" ", "_") : Path.GetFileName(originalName).Replace(" ", "_");
            if (!finalName.EndsWith(ext)) finalName += ext;
            var invalidChars = Path.GetInvalidFileNameChars();
            return new string(finalName.Where(ch => !invalidChars.Contains(ch)).ToArray());
        }

        [HttpPost("violations/report")]
        public async Task<IActionResult> ReportViolation([FromForm] string bienSo, [FromForm] string loaiViPham, [FromForm] int cameraId, [FromForm] IFormFile anhViPham, [FromForm] IFormFile? anhBienSo)
        {
            string fullPath = await SaveFile(anhViPham, "vi_pham");
            string platePath = anhBienSo != null ? await SaveFile(anhBienSo, "plates") : "";
            var record = new LichSuViPham { BienSo = bienSo, LoaiViPham = loaiViPham, CameraId = cameraId, ThoiGian = DateTime.Now, DuongDanAnh = fullPath, DuongDanAnhBienSo = platePath, TrangThaiXuLy = "Chưa xử lý" };
            _context.LichSuViPhams.Add(record);
            await _context.SaveChangesAsync();
            return Ok(new { status = "success" });
        }

        private async Task<string> SaveFile(IFormFile file, string folder)
        {
            string path = Path.Combine(_storageFolder, "images", folder);
            if (!Directory.Exists(path)) Directory.CreateDirectory(path);
            string fileName = Guid.NewGuid().ToString() + ".jpg";
            using (var stream = new FileStream(Path.Combine(path, fileName), FileMode.Create)) { await file.CopyToAsync(stream); }
            return fileName;
        }

        [HttpGet("camera/list")]
        public async Task<IActionResult> GetCameras()
        {
            var cameras = await _context.Cameras.ToListAsync();
            return Ok(new { status = "success", data = cameras });
        }

        [HttpPost("camera/update")]
        [DisableRequestSizeLimit]
        public async Task<IActionResult> UpdateCamera([FromForm] int id, [FromForm] string newName, [FromForm] string? newPath, [FromForm] IFormFile? newVideo, [FromForm] string? customFileName)
        {
            var cam = await _context.Cameras.FindAsync(id);
            if (cam == null) return NotFound();
            cam.TenCamera = newName;
            if (newVideo != null && newVideo.Length > 0)
            {
                string uploadsFolder = Path.Combine(_storageFolder, "videos");
                if (!Directory.Exists(uploadsFolder)) Directory.CreateDirectory(uploadsFolder);
                string fileName = GetCleanFileName(newVideo.FileName, customFileName);
                using (var stream = new FileStream(Path.Combine(uploadsFolder, fileName), FileMode.Create)) { await newVideo.CopyToAsync(stream); }
                cam.DuongDan = fileName; cam.LoaiNguon = "Video";
            }
            else if (!string.IsNullOrWhiteSpace(newPath)) { cam.DuongDan = newPath.Trim(); cam.LoaiNguon = (newPath.StartsWith("http") || newPath.StartsWith("rtsp")) ? "Stream" : "Khác"; }
            _context.Cameras.Update(cam); await _context.SaveChangesAsync();
            return Ok(new { status = "success", message = "Đã cập nhật!" });
        }
        [HttpPost("camera/delete")]
        public async Task<IActionResult> DeleteCamera([FromForm] int id)
        {
            var cam = await _context.Cameras.FindAsync(id);
            if (cam == null) return NotFound(new { status = "error", message = "Không tìm thấy Camera." });

            try
            {
                // 1. Xóa các cấu hình vùng liên quan đến Camera này
                var configs = _context.CauHinhVungs.Where(x => x.CameraId == id);
                if (configs.Any())
                {
                    _context.CauHinhVungs.RemoveRange(configs);
                }

                // 2. Xóa các lịch sử vi phạm liên quan đến Camera này (Đây là nguyên nhân gây lỗi)
                var viPhams = _context.LichSuViPhams.Where(x => x.CameraId == id);
                if (viPhams.Any())
                {
                    _context.LichSuViPhams.RemoveRange(viPhams);
                }

                // Lưu lại các thay đổi xóa bảng con (configs, viPhams) trước
                await _context.SaveChangesAsync();

                // 3. Cuối cùng mới xóa Camera
                _context.Cameras.Remove(cam);
                await _context.SaveChangesAsync();

                return Ok(new { status = "success", message = "Đã xóa Camera và dữ liệu liên quan thành công!" });
            }
            catch (DbUpdateConcurrencyException ex)
            {
                // Xử lý dự phòng nếu EF Core vẫn bị kẹt tracking (Hiếm khi xảy ra nếu đã gọi SaveChangesAsync cho bảng con trước)
                return StatusCode(500, new { status = "error", message = "Lỗi đồng bộ dữ liệu. Không thể xóa Camera ngay lúc này.", details = ex.Message });
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { status = "error", message = "Lỗi Server khi xóa Camera.", details = ex.Message });
            }
        }

        [HttpPost("camera/create")]
        [DisableRequestSizeLimit]
        public async Task<IActionResult> CreateCamera([FromForm] string tenCamera, [FromForm] string? duongDan, [FromForm] IFormFile? videoFile, [FromForm] string? customFileName)
        {
            if (string.IsNullOrWhiteSpace(tenCamera)) return BadRequest();
            var newCam = new Camera { TenCamera = tenCamera };
            if (videoFile != null && videoFile.Length > 0)
            {
                string uploadsFolder = Path.Combine(_storageFolder, "videos");
                if (!Directory.Exists(uploadsFolder)) Directory.CreateDirectory(uploadsFolder);
                string fileName = GetCleanFileName(videoFile.FileName, customFileName);
                using (var stream = new FileStream(Path.Combine(uploadsFolder, fileName), FileMode.Create)) { await videoFile.CopyToAsync(stream); }
                newCam.DuongDan = fileName; newCam.LoaiNguon = "Video"; newCam.TrangThai = 1;
            }
            else if (!string.IsNullOrWhiteSpace(duongDan)) { newCam.DuongDan = duongDan.Trim(); newCam.LoaiNguon = "Stream"; newCam.TrangThai = 1; }
            _context.Cameras.Add(newCam); await _context.SaveChangesAsync();
            return Ok(new { status = "success", newId = newCam.Id });
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
                return Ok(new { status = "success" });
            }
            if (existingConfig != null) { existingConfig.ToaDoJson = toaDoJson; _context.CauHinhVungs.Update(existingConfig); }
            else { _context.CauHinhVungs.Add(new CauHinhVung { CameraId = cameraId, LoaiVung = loaiVung, ToaDoJson = toaDoJson }); }
            await _context.SaveChangesAsync();
            return Ok(new { status = "success" });
        }

        [HttpPost("violations/approve")]
        public async Task<IActionResult> ApproveViolation([FromForm] int id, [FromForm] string bienSoMoi)
        {
            var record = await _context.LichSuViPhams.FindAsync(id);
            if (record == null) return NotFound();
            record.BienSo = bienSoMoi.ToUpper(); record.TrangThaiXuLy = "Đã duyệt";
            _context.LichSuViPhams.Update(record); await _context.SaveChangesAsync();
            return Ok(new { status = "success" });
        }

        [HttpPost("ai/start")]
        public async Task<IActionResult> StartAI([FromForm] int cameraId)
        {
            try
            {
                KillZombiePythons();
                var cam = await _context.Cameras.FindAsync(cameraId);
                if (cam == null) return BadRequest();
                string filePath = cam.DuongDan;
                if (!filePath.StartsWith("http") && !filePath.Contains("://")) filePath = Path.Combine(_storageFolder, "videos", filePath);

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
                _pythonProcess = Process.Start(startInfo);
                return Ok(new { status = "success", message = $"Đã khởi động AI cho '{cam.TenCamera}'!" });
            }
            catch (Exception ex) { return StatusCode(500, new { status = "error", message = ex.Message }); }
        }

        [HttpPost("ai/stop")]
        public async Task<IActionResult> StopAI()
        {
            try
            {
                try { using (var client = new HttpClient() { Timeout = TimeSpan.FromSeconds(1) }) { await client.PostAsync("http://127.0.0.1:5000/shutdown", null); } } catch { }
                if (_pythonProcess != null)
                {
                    try { if (!_pythonProcess.HasExited) _pythonProcess.Kill(true); } catch { }
                    _pythonProcess.Dispose(); _pythonProcess = null;
                }
                KillZombiePythons();
                return Ok(new { status = "success" });
            }
            catch (Exception ex) { return StatusCode(500, new { status = "error", message = ex.Message }); }
        }

        private void KillZombiePythons()
        {
            try { Process.Start(new ProcessStartInfo { FileName = "cmd.exe", Arguments = "/c taskkill /F /IM python.exe /T", CreateNoWindow = true, UseShellExecute = false })?.WaitForExit(); } catch { }
        }

        [HttpGet("images/vi_pham/{fileName}")]
        public IActionResult GetViPhamImage(string fileName)
        {
            string path = Path.Combine(_storageFolder, "images", "vi_pham", fileName);
            if (!System.IO.File.Exists(path)) return NotFound();
            return PhysicalFile(path, "image/jpeg");
        }

        [HttpGet("images/plates/{fileName}")]
        public IActionResult GetPlateImage(string fileName)
        {
            string path = Path.Combine(_storageFolder, "images", "plates", fileName);
            if (!System.IO.File.Exists(path)) return NotFound();
            return PhysicalFile(path, "image/jpeg");
        }

        // =========================================================
        // CHỨC NĂNG CHỤP ẢNH TĨNH ĐỘC LẬP CHO TRANG CẤU HÌNH
        // =========================================================
        [HttpGet("ai/take-snapshot/{cameraId}")]
        public async Task<IActionResult> TakeSnapshot(int cameraId)
        {
            try
            {
                var cam = await _context.Cameras.FindAsync(cameraId);
                if (cam == null) return NotFound();

                string filePath = cam.DuongDan;
                if (!filePath.StartsWith("http") && !filePath.Contains("://"))
                    filePath = Path.Combine(_storageFolder, "videos", filePath);

                // Script python này chỉ mở camera, chụp 1 frame rồi thoát ngay lập tức
                // Nó KHÔNG dùng chung biến _pythonProcess nên không làm sập trang Live
                string pythonExePath = @"C:\Users\84339\AppData\Local\Microsoft\WindowsApps\python.exe";
                string snapshotScript = @"D:\Khóa luận tốt nghiệp\KLTN\python__project\get_snapshot.py";

                // Thư mục lưu ảnh tạm cho Web hiển thị (lưu vào wwwroot/temp)
                string tempFolder = Path.Combine(_env.WebRootPath, "temp");
                if (!Directory.Exists(tempFolder)) Directory.CreateDirectory(tempFolder);
                string outputImg = Path.Combine(tempFolder, $"snapshot_{cameraId}.jpg");

                ProcessStartInfo startInfo = new ProcessStartInfo
                {
                    FileName = pythonExePath,
                    Arguments = $"\"{snapshotScript}\" \"{filePath}\" \"{outputImg}\"",
                    UseShellExecute = false,
                    CreateNoWindow = true
                };

                using (Process? proc = Process.Start(startInfo))
                {
                    // Chờ tối đa 10 giây để nó chụp xong ảnh
                    if (proc != null) proc.WaitForExit(10000);
                }

                if (System.IO.File.Exists(outputImg))
                    return Ok(new { status = "success", imageUrl = $"/temp/snapshot_{cameraId}.jpg" });

                return BadRequest(new { status = "error", message = "Không thể chụp ảnh từ luồng này." });
            }
            catch (Exception ex) { return StatusCode(500, new { status = "error", message = ex.Message }); }
        }
    }
}