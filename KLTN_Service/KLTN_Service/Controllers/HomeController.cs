using Microsoft.AspNetCore.Mvc;
using KLTN_Service.Models;
using System.Linq;
using System;
using System.Collections.Generic;

namespace KLTN_Service.Controllers
{
    public class HomeController : Controller
    {
        private readonly AppDbContext _context;

        public HomeController(AppDbContext context)
        {
            _context = context;
        }

        // Trả về giao diện trang chủ (Index.cshtml)
        public IActionResult Index()
        {
            return View();
        }

        // ========================================================
        // API TRẢ VỀ DỮ LIỆU THẬT TỪ MYSQL DATABASE CHO DASHBOARD
        // ========================================================
        [HttpGet]
        public IActionResult GetDashboardData()
        {
            var today = DateTime.Today;

            // 1. THỐNG KÊ HÔM NAY
            var totalToday = _context.LichSuViPhams.Count(v => v.ThoiGian.Date == today);
            var vuotDenDo = _context.LichSuViPhams.Count(v => v.ThoiGian.Date == today && v.LoaiViPham.Contains("Vuot Den Do"));
            var saiLan = _context.LichSuViPhams.Count(v => v.ThoiGian.Date == today && v.LoaiViPham.Contains("Sai Lan"));
            var khongMu = _context.LichSuViPhams.Count(v => v.ThoiGian.Date == today && v.LoaiViPham.Contains("Khong Mu Bao Hiem"));

            // 2. THỐNG KÊ TẤT CẢ (TOÀN THỜI GIAN)
            var totalAllTime = _context.LichSuViPhams.Count();
            var vuotDenDoAllTime = _context.LichSuViPhams.Count(v => v.LoaiViPham.Contains("Vuot Den Do"));
            var saiLanAllTime = _context.LichSuViPhams.Count(v => v.LoaiViPham.Contains("Sai Lan"));
            var khongMuAllTime = _context.LichSuViPhams.Count(v => v.LoaiViPham.Contains("Khong Mu Bao Hiem"));

            // 3. BIỂU ĐỒ 7 NGÀY QUA
            var last7Days = Enumerable.Range(0, 7).Select(i => today.AddDays(-i)).Reverse().ToList();
            var labels7Days = last7Days.Select(d => d.ToString("dd/MM")).ToList();
            var data7Days = new List<int>();

            foreach (var day in last7Days)
            {
                data7Days.Add(_context.LichSuViPhams.Count(v => v.ThoiGian.Date == day));
            }

            // 4. DANH SÁCH 5 VI PHẠM MỚI NHẤT
            var recentViolations = (from v in _context.LichSuViPhams
                                    join c in _context.Cameras on v.CameraId equals c.Id
                                    orderby v.ThoiGian descending
                                    select new
                                    {
                                        id = v.Id,
                                        hinhAnh = v.DuongDanAnh,
                                        hinhAnhBienSo = v.DuongDanAnhBienSo, // <-- THÊM DÒNG NÀY
                                        bienSo = v.BienSo,
                                        loaiViPham = v.LoaiViPham,
                                        tenCamera = c.TenCamera,
                                        thoiGian = v.ThoiGian.ToString("HH:mm - dd/MM/yyyy"),
                                        trangThai = v.TrangThaiXuLy
                                    }).Take(5).ToList();

            // Trả về một khối JSON tổng hợp tất cả
            return Json(new
            {
                today = new { total = totalToday, denDo = vuotDenDo, saiLan = saiLan, khongMu = khongMu },
                allTime = new { total = totalAllTime, denDo = vuotDenDoAllTime, saiLan = saiLanAllTime, khongMu = khongMuAllTime },
                chart7Days = new { labels = labels7Days, data = data7Days },
                recentList = recentViolations
            });
        }
    }
}