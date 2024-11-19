document.addEventListener("DOMContentLoaded", function () {
    const loginLinks = document.querySelectorAll('.product-name, .btn.btn-xs.btn-outline.btn-primary');

    loginLinks.forEach(link => {
        link.addEventListener('click', function (event) {
            event.preventDefault(); // Ngăn chặn hành động mặc định của thẻ <a>
            
            // Hiển thị hộp thoại xác nhận
            const confirmLogin = confirm("Bạn cần đăng nhập để tiếp tục. Bạn có muốn đăng nhập không?");
            
            if (confirmLogin) {
                // Điều hướng đến trang đăng nhập
                window.location.href = "login"; // Thay bằng URL của trang đăng nhập của bạn
            }
            // Nếu chọn "Hủy", sẽ không có hành động gì
        });
    });
});
