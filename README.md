# 1.Them loc ngay thang nam

//lọc tháng cần xem xét lại

# 2.Them phan trang pagination

# 3.Coi lai cho phan trang

# 4.Đang tiến hàng xóa db vì hôm qua làm sai tiến trình

# 5.Đưa thằng app text xún trc main

<Các thứ cần khắc phục trên phương diện người dùng>
1.Chưa có của "riêng"
2.Thiếu sự thông minh ở cái app này có cái j (tháng này chi tiêu quá 50%...)
3.Chưa có Unit test -> kiểm thử phần mềm
4.Trải nghiệm người dùng cần một số thứ cần mượt hơn//chi tiết sau

Điều một nhà tuyển dụng muốn thấy là TƯ DUY, KHẢ NĂNG HỌC HỎI VÀ SỰ TỈ MỈ
-- Đi từ bên trong trc:
<Cải thiện bản đồ? biểu đồ ch có thay đổi khi người dùng lọc dữ liệu nên phải làm thế nào để khi lọc thì dữ liệu cũng sẽ vẽ lại, ví dụ khi mình lọc tháng 5 với danh mục đồ ăn thì nó phải lọc ra tháng 5 đồ ăn
--thằng rout api phải có khả năng đọc và xử lý tham số lọc(month,category) giống với thằng route.hàm home>

--> coi lai cho sua cua ban do

<thêm empty state ví dụ như thông báo khi mình bấm "lọc" thì có hiện thông báo dữ liệu k, có sự khác biệt giữa chưa có dữ liệu và không tìm thấy kết quả lọc>
<thêm phần có thể sửa danh mục khi chọn nhầm thì route.edit nó phải lấy được danh sách của category và truyền nó vào edit html, khi nhận dữ liệu post thì nó sẽ cập nhật cả category_id, ở phần frontend thì template phải có dropdown list cho danh mục và phải tự động chọn sẵn danh mục hiện tại của danh mục đó>
