using KLTN_Service.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace KLTN_Service.Controllers
{
    public class ViPhamController : Controller
    {
        private readonly AppDbContext _context;

        // Tiêm DbContext để gọi Database
        public ViPhamController(AppDbContext context)
        {
            _context = context;
        }

        // Hàm này sẽ chạy khi người dùng vào trang /ViPham
        public async Task<IActionResult> Index()
        {
            // Lấy toàn bộ danh sách vi phạm, sắp xếp những ca mới nhất lên trên cùng
            var danhSachViPham = await _context.LichSuViPhams
                                               .OrderByDescending(x => x.ThoiGian)
                                               .ToListAsync();

            // Đẩy dữ liệu này sang trang View (HTML)
            return View(danhSachViPham);
        }

        public IActionResult Live()
        {
            return View();
        }
        public IActionResult Config()
        {
            return View();
        }
    }
}
