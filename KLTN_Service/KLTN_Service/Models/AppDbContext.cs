using Microsoft.EntityFrameworkCore;

namespace KLTN_Service.Models
{
    public class AppDbContext : DbContext
    {
        public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

        // Đại diện cho bảng trong Database
        public DbSet<LichSuViPham> LichSuViPhams { get; set; }
        public DbSet<CauHinhVung> CauHinhVungs { get; set; }
        public DbSet<Camera> Cameras { get; set; }

    }
}