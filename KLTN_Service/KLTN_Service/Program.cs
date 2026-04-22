using KLTN_Service.Models;
using Microsoft.EntityFrameworkCore;
using Microsoft.AspNetCore.Http.Features; // BẮT BUỘC THÊM: Để xử lý form upload dung lượng lớn
using Microsoft.Extensions.FileProviders; // BẮT BUỘC THÊM: Để đọc file từ ổ đĩa ngoài (D:, E:...)
using Microsoft.AspNetCore.Server.IIS;    // Thêm thư viện này cho IIS

namespace KLTN_Service
{
    public class Program
    {
        public static void Main(string[] args)
        {
            var builder = WebApplication.CreateBuilder(args);

            // =========================================================
            // CẤU HÌNH MỞ KHÓA GIỚI HẠN UPLOAD FILE LÊN 2GB
            // (2GB = 2147483648 bytes. Thêm 'L' để chỉ định kiểu số Long)
            // =========================================================

            // 1. Mở khóa cho Form Data
            builder.Services.Configure<FormOptions>(options =>
            {
                options.ValueLengthLimit = int.MaxValue;
                options.MultipartBodyLengthLimit = 2147483648L; // 2 GB
                options.MultipartHeadersLengthLimit = int.MaxValue;
            });

            // 2. Mở khóa cho Kestrel Server
            builder.WebHost.ConfigureKestrel(serverOptions =>
            {
                serverOptions.Limits.MaxRequestBodySize = 2147483648L; // 2 GB
            });

            // 3. Mở khóa cho IIS Express (Khi chạy bằng Visual Studio)
            builder.Services.Configure<IISServerOptions>(options =>
            {
                options.MaxRequestBodySize = 2147483648L; // 2 GB
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