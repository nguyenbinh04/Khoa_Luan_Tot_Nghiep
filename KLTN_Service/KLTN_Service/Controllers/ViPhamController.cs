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
        public IActionResult Index()
        {
            // ĐÃ SỬA: Không bắt Database tải toàn bộ dữ liệu ở đây nữa để tránh nghẽn RAM.
            // Chỉ cần trả về giao diện rỗng, DataTables sẽ tự động gọi hàm LoadData bên dưới để lấy dữ liệu.
            return View();
        }

        // =========================================================
        // API CẤP DỮ LIỆU TỪNG PHẦN CHO BẢNG DATATABLES
        // =========================================================
        [HttpPost]
        public async Task<IActionResult> LoadData()
        {
            try
            {
                // 1. Nhận các tham số mà thư viện DataTables tự động gửi lên
                var draw = Request.Form["draw"].FirstOrDefault();
                var start = Request.Form["start"].FirstOrDefault();
                var length = Request.Form["length"].FirstOrDefault();
                var searchValue = Request.Form["search[value]"].FirstOrDefault();

                int pageSize = length != null ? Convert.ToInt32(length) : 10;
                int skip = start != null ? Convert.ToInt32(start) : 0;

                // 2. Tạo câu truy vấn gốc
                var query = _context.LichSuViPhams.AsQueryable();

                // 3. Xử lý tính năng Tìm kiếm
                if (!string.IsNullOrEmpty(searchValue))
                {
                    query = query.Where(v => v.BienSo.Contains(searchValue)
                                          || v.LoaiViPham.Contains(searchValue));
                }

                // 4. Đếm tổng số dòng (để vẽ các nút phân trang 1, 2, 3...)
                int recordsTotal = await query.CountAsync();

                // 5. Lấy đúng số lượng cần thiết (Skip & Take)
                var data = await query.OrderByDescending(v => v.ThoiGian)
                                      .Skip(skip)
                                      .Take(pageSize)
                                      .ToListAsync();

                // 6. Trả về chuẩn JSON của DataTables
                return Json(new
                {
                    draw = draw,
                    recordsFiltered = recordsTotal,
                    recordsTotal = recordsTotal,
                    data = data
                });
            }
            catch (Exception ex)
            {
                // Bắt lỗi an toàn
                return Json(new { error = ex.Message });
            }
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