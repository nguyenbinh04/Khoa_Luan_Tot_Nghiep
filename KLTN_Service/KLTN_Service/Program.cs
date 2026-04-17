using KLTN_Service.Models;
using Microsoft.EntityFrameworkCore;
using Microsoft.AspNetCore.Http.Features; // BẮT BUỘC THÊM: Để xử lý form upload dung lượng lớn
using Microsoft.Extensions.FileProviders; // BẮT BUỘC THÊM: Để đọc file từ ổ đĩa ngoài (D:, E:...)

namespace KLTN_Service
{
    public class Program
    {
        public static void Main(string[] args)
        {
            var builder = WebApplication.CreateBuilder(args);

            // =========================================================
            // CẤU HÌNH MỞ KHÓA GIỚI HẠN UPLOAD FILE LÊN 500MB
            // =========================================================
            builder.Services.Configure<FormOptions>(options =>
            {
                options.ValueLengthLimit = int.MaxValue;
                options.MultipartBodyLengthLimit = 524288000; // 500 MB
                options.MultipartHeadersLengthLimit = int.MaxValue;
            });

            builder.WebHost.ConfigureKestrel(serverOptions =>
            {
                serverOptions.Limits.MaxRequestBodySize = 524288000; // 500 MB
            });
            // =========================================================

            var connectionString = builder.Configuration.GetConnectionString("DefaultConnection");
            builder.Services.AddDbContext<AppDbContext>(options =>
                options.UseMySql(connectionString, ServerVersion.AutoDetect(connectionString))
            );

            // Add services to the container.
            builder.Services.AddControllersWithViews();

            var app = builder.Build();

            // Configure the HTTP request pipeline.
            if (!app.Environment.IsDevelopment())
            {
                app.UseExceptionHandler("/Home/Error");
                // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
                app.UseHsts();
            }

            app.UseHttpsRedirection();
            app.UseRouting();

            app.UseAuthorization();

            // =========================================================
            // CẤU HÌNH MAP THƯ MỤC Ổ ĐĨA NGOÀI VÀO WEB (ẢO HÓA ĐƯỜNG DẪN)
            // =========================================================
            string storageFolder = @"D:\DuLieu_GiaoThong_KLTN";

            // 1. Map thư mục ảnh vi phạm
            string imagesPath = Path.Combine(storageFolder, "images");
            if (!Directory.Exists(imagesPath)) Directory.CreateDirectory(imagesPath);
            app.UseStaticFiles(new StaticFileOptions
            {
                FileProvider = new PhysicalFileProvider(imagesPath),
                RequestPath = "/images" // Khi web gọi /images/... nó sẽ tự động chui vào ổ D tìm
            });

            // 2. Map thư mục Video
            string videosPath = Path.Combine(storageFolder, "videos");
            if (!Directory.Exists(videosPath)) Directory.CreateDirectory(videosPath);
            app.UseStaticFiles(new StaticFileOptions
            {
                FileProvider = new PhysicalFileProvider(videosPath),
                RequestPath = "/videos" // Khi web gọi /videos/... nó sẽ tự động chui vào ổ D tìm
            });
            // =========================================================

            // Map các file tĩnh mặc định trong wwwroot (CSS, JS...)
            app.MapStaticAssets();

            app.MapControllerRoute(
                name: "default",
                pattern: "{controller=Home}/{action=Index}/{id?}")
                .WithStaticAssets();

            app.Run();
        }
    }
}