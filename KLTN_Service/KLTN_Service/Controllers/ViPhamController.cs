using KLTN_Service.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace KLTN_Service.Controllers
{
    public class ViPhamController : Controller
    {
        private readonly AppDbContext _context;
        public ViPhamController(AppDbContext context)
        {
            _context = context;
        }


        public IActionResult Index()
        {
            return View();
        }

        [HttpPost]
        public async Task<IActionResult> LoadData()
        {
            try
            {
                var draw = Request.Form["draw"].FirstOrDefault();
                var start = Request.Form["start"].FirstOrDefault();
                var length = Request.Form["length"].FirstOrDefault();
                var searchValue = Request.Form["search[value]"].FirstOrDefault();

                int pageSize = length != null ? Convert.ToInt32(length) : 10;
                int skip = start != null ? Convert.ToInt32(start) : 0;

                var query = _context.LichSuViPhams.AsQueryable();

                if (!string.IsNullOrEmpty(searchValue))
                {
                    query = query.Where(v => v.BienSo.Contains(searchValue)
                                          || v.LoaiViPham.Contains(searchValue));
                }

                int recordsTotal = await query.CountAsync();

                var data = await query.OrderByDescending(v => v.ThoiGian)
                                      .Skip(skip)
                                      .Take(pageSize)
                                      .ToListAsync();

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