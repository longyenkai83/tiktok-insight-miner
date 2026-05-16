#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build chi_hien_hook_bank_v2_refined.csv from decoded 365 hooks + 6 rules."""
import csv
import re
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# 365 hooks decoded from mojibake context (Original Hook + Adapted Chị Hiền Hook from v1)
# Format: (id, original_vietnamese, original_tone_v1, fit_v1, calendar_hint_optional)
HOOKS = [
    ("H001", "Mình không bán [sản phẩm], mình bán phiên bản mới của bạn.", "Insightful"),
    ("H002", "Bạn có chắc mình muốn sống như thế này thêm 1 năm?", "Reflective"),
    ("H003", "Bạn đang làm việc hay đang né đối diện với chính mình?", "Confrontational"),
    ("H004", "Cuộc đời bạn sẽ trông sao nếu dám sống đúng mong muốn?", "Gentle"),
    ("H005", "Bạn không lười, bạn chỉ chưa tin mình xứng đáng hơn.", "Inspirational"),
    ("H006", "Người ta không mua [sản phẩm], họ mua cảm giác trở thành [phiên bản].", "Insightful"),
    ("H007", "Nếu bạn tin mình đủ giỏi, bạn dám làm gì ngay hôm nay?", "Reflective"),
    ("H008", "Bạn đã bao lần nói 'để mai' với chính cuộc đời mình?", "Confrontational"),
    ("H009", "Bạn đang bảo vệ vùng an toàn hay tương lai của mình?", "Gentle"),
    ("H010", "Phiên bản bạn 5 năm nữa có tự hào về hôm nay?", "Inspirational"),
    ("H011", "Bạn muốn tiếp tục quen với nỗi đau này đến bao giờ?", "Insightful"),
    ("H012", "Thực ra bạn cần thay đổi, hay chỉ cần trung thực hơn?", "Reflective"),
    ("H013", "Bạn đã bỏ quên mình bao lâu rồi mà chưa nhận ra?", "Confrontational"),
    ("H014", "Bạn sống theo tiêu chuẩn của mình hay của người khác?", "Gentle"),
    ("H015", "Bạn có thật sự ổn, hay chỉ quen với việc chịu đựng?", "Inspirational"),
    ("H016", "Bạn đang chọn an toàn hay chọn trung thực với trái tim?", "Insightful"),
    ("H017", "Mỗi lần bạn thoả hiệp, bạn đang dạy người khác cách đối xử với mình.", "Reflective"),
    ("H018", "Nếu hôm nay là ngày cuối cùng sống kiểu này, bạn làm gì khác?", "Confrontational"),
    ("H019", "Bạn có đang sống nhỏ hơn tiềm năng thật của bản thân?", "Gentle"),
    ("H020", "Bạn còn chấp nhận [nỗi đau / thói quen] này thêm bao lâu nữa?", "Inspirational"),
    ("H021", "Thứ bạn gọi là 'tính cách' có khi chỉ là thói quen cũ.", "Insightful"),
    ("H022", "Không phải bạn thiếu thời gian, bạn thiếu một lý do đủ lớn.", "Reflective"),
    ("H023", "Bao nhiêu quyết định của bạn xuất phát từ nỗi sợ, không phải mong muốn?", "Confrontational"),
    ("H024", "Phiên bản bình an hơn của bạn sẽ chọn điều gì hôm nay?", "Gentle"),
    ("H025", "Bạn có đang dùng 'bận' để trốn việc nhìn lại chính mình?", "Inspirational"),
    ("H026", "Bạn không mắc kẹt, bạn chỉ chưa dám nói 'đủ rồi'.", "Insightful"),
    ("H027", "Bạn đang xây cuộc đời mình, hay đang vá lại cuộc đời người khác?", "Reflective"),
    ("H028", "Khi nào bạn mới dừng xin phép được sống đúng với mình?", "Confrontational"),
    ("H029", "Bạn muốn sống 'an toàn' hay sống 'thật sự'?", "Gentle"),
    ("H030", "Nếu không đổi hướng, bạn đang đi tới đâu?", "Inspirational"),
    ("H031", "Bạn có đang sống theo kỳ vọng của người khác hơn là của mình?", "Insightful"),
    ("H032", "Bao lâu rồi bạn chưa làm điều gì chỉ vì chính bạn?", "Reflective"),
    ("H033", "Bạn đang dùng tiền để bù cho khoảng trống nào bên trong?", "Confrontational"),
    ("H034", "Điều làm bạn mất ngủ nhiều hơn: nợ tiền hay nợ chính mình?", "Gentle"),
    ("H035", "Bạn có thật sự nghèo, hay chỉ đang nghĩ mình 'chỉ là…'?", "Inspirational"),
    ("H036", "Thu nhập của bạn hiếm khi vượt quá hình ảnh bạn thấy về bản thân.", "Insightful"),
    ("H037", "Bạn đang làm việc vì tiền, hay dùng tiền để phục vụ cuộc đời mình?", "Reflective"),
    ("H038", "Bạn không sai khi muốn nhiều tiền hơn, sai là nghĩ mình không xứng.", "Confrontational"),
    ("H039", "Nếu công việc không nuôi nổi giấc mơ, đã đến lúc nâng cấp cả hai.", "Gentle"),
    ("H040", "Bạn đang xây tài sản hay chỉ trả nợ cho những niềm tin cũ?", "Inspirational"),
    ("H041", "Tự do của bạn đáng giá bao nhiêu giờ 'hy sinh' mỗi ngày?", "Insightful"),
    ("H042", "Tiền bạn kiếm ra đang mua điều gì: tự do hay mệt mỏi?", "Reflective"),
    ("H043", "Bạn có đang đợi cả tuổi trẻ chỉ để đợi lương về?", "Confrontational"),
    ("H044", "Bạn có đang dùng sự nghiệp để trốn việc chữa lành bên trong?", "Gentle"),
    ("H045", "Thu nhập đổi khi bạn ngừng giới thiệu mình bằng 'em chỉ là…'.", "Inspirational"),
    ("H046", "Bạn muốn kiếm thêm, hay muốn kiếm đúng với giá trị của mình?", "Insightful"),
    ("H047", "Tham vọng của bạn là của bạn hay được 'cài' bởi ai đó?", "Reflective"),
    ("H048", "Tự do tài chính bắt đầu từ tự do trong suy nghĩ về bản thân.", "Insightful"),
    ("H049", "Bạn có dám đòi hỏi nhiều hơn từ cuộc đời này không?", "Gentle"),
    ("H050", "Nếu không giới hạn, bạn muốn sống cuộc đời tài chính như thế nào?", "Inspirational"),
    ("H051", "Bạn không khó yêu, bạn chỉ đang ở sai chỗ và sai người.", "Insightful"),
    ("H052", "Bạn có đang tự thu nhỏ mình cho vừa với nỗi sợ của người khác?", "Reflective"),
    ("H053", "Ranh giới của bạn đang bảo vệ ai: bạn hay người khác?", "Confrontational"),
    ("H054", "Bạn đối xử với mình ra sao khi không có ai nhìn thấy?", "Gentle"),
    ("H055", "Bạn có đang gọi 'lo lắng' là 'tình yêu'?", "Inspirational"),
    ("H056", "Nếu phải đổi bình yên để giữ một người, đó có đáng không?", "Insightful"),
    ("H057", "Bao nhiêu lần bạn nói 'không sao đâu' trong khi rất không ổn?", "Reflective"),
    ("H058", "Bạn có đang nhầm lẫn quen thuộc với an toàn?", "Confrontational"),
    ("H059", "Mối quan hệ này đang giúp bạn lớn lên hay thu nhỏ lại?", "Gentle"),
    ("H060", "Người cần bạn nhất bây giờ là chính bạn, không phải ai khác.", "Inspirational"),
    ("H061", "Bạn không drama, bạn chỉ đang chạm vào vết thương cũ.", "Insightful"),
    ("H062", "Bạn không ích kỷ khi chọn mình, bạn chỉ thôi phản bội bản thân.", "Reflective"),
    ("H063", "Bạn có đang làm bạn với chính mình, hay chỉ là người phán xét?", "Confrontational"),
    ("H064", "Bạn đã bao giờ thử tự nói 'mình xứng đáng hơn thế này' chưa?", "Gentle"),
    ("H065", "Tự yêu mình không phải là skincare, là cách bạn đối thoại với bản thân.", "Inspirational"),
    ("H066", "Bạn có đang đòi hỏi sự tôn trọng từ ngoài, khi chính bạn còn không tôn trọng mình?", "Insightful"),
    ("H067", "Ngày bạn ngừng xin phép được tồn tại, là ngày cuộc đời bắt đầu khác.", "Reflective"),
    ("H068", "Bạn yêu bản thân bằng cách nào ngoài việc 'cố gắng hơn nữa'?", "Confrontational"),
    ("H069", "Bạn có đang đối xử với mình như cách bạn mong người khác đối xử với bạn?", "Gentle"),
    ("H070", "Nếu con bạn sống như cách bạn đang sống, bạn có thấy ổn không?", "Inspirational"),
    ("H071", "Bạn đang dạy con mình cách sống, hay cách tiếp tục chịu đựng?", "Insightful"),
    ("H072", "Bạn có đang lặp lại đúng mô thức của bố mẹ mà bạn từng sợ?", "Reflective"),
    ("H073", "Bạn muốn truyền cho thế hệ sau nỗi sợ hay sự can đảm?", "Confrontational"),
    ("H074", "Có điều gì bạn hứa với bản thân nhỏ là không bao giờ lặp lại, nhưng vẫn làm?", "Gentle"),
    ("H075", "Bạn có đang sống cuộc đời mà ngày xưa bạn từng nói 'sau này mình sẽ không vậy'?", "Inspirational"),
    ("H076", "Câu chuyện gia đình bạn tin vào có còn đúng với bạn hôm nay?", "Insightful"),
    ("H077", "Bạn đang chữa lành hay chỉ đang lấp đi cho đỡ đau?", "Reflective"),
    ("H078", "Bạn có đang đặt con mình lên trước nhưng đặt bản thân xuống cuối cùng?", "Confrontational"),
    ("H079", "Bạn muốn con tin vào điều gì khi nhìn vào cuộc đời bạn?", "Gentle"),
    ("H080", "Nếu con bạn bắt chước cách bạn yêu chính mình, bạn thấy sao?", "Inspirational"),
    ("H081", "Bạn không lười, bạn đang kiệt sức vì cố gắng làm người khác hài lòng.", "Insightful"),
    ("H082", "Bạn có đang dùng 'hoàn hảo' như cái cớ để chẳng bao giờ bắt đầu?", "Reflective"),
    ("H083", "Bạn đang đợi hết sợ rồi mới làm hay vừa run vừa làm?", "Confrontational"),
    ("H084", "Có bao nhiêu giấc mơ bạn đã gấp lại vì sợ người khác nói gì?", "Gentle"),
    ("H085", "Bạn có đang sống như bản nháp của chính cuộc đời mình?", "Inspirational"),
    ("H086", "Bạn làm việc để được công nhận hay để được tự do?", "Insightful"),
    ("H087", "Bạn đang đuổi theo thành công của ai: bạn hay xã hội?", "Reflective"),
    ("H088", "Có bao nhiêu 'thành công' bạn đạt được mà vẫn thấy trống rỗng?", "Confrontational"),
    ("H089", "Bạn đang tìm kiếm thành tích hay sự bình an?", "Gentle"),
    ("H090", "Nếu thành công không đăng được lên mạng, bạn còn muốn không?", "Inspirational"),
    ("H091", "Bạn có đang tin rằng 'mình phải khổ mới xứng đáng được nhận'?", "Insightful"),
    ("H092", "Bạn nghĩ sao nếu cuộc đời có thể vừa nhẹ, vừa đủ, vừa giàu?", "Reflective"),
    ("H093", "Bạn đang chọn chiến đấu hay chọn nhảy khỏi cuộc chơi cũ?", "Confrontational"),
    ("H094", "Bạn có đang nhầm lẫn 'chịu khó' với việc chấp nhận ít hơn mình xứng đáng?", "Gentle"),
    ("H095", "Bạn đã bao lần tự sabo chính mình ngay trước vạch đích?", "Inspirational"),
    ("H096", "Bạn có nhận ra mình đang lặp lại cùng một bài học với những cái tên khác nhau?", "Insightful"),
    ("H097", "Mỗi lần bạn quay lại vùng an toàn, bạn rời xa chính mình thêm một chút.", "Reflective"),
    ("H098", "Bạn có đang dùng 'định mệnh' để trốn trách nhiệm với lựa chọn của mình?", "Confrontational"),
    ("H099", "Bạn tin vũ trụ không ưa, hay bạn chưa thật sự ủng hộ chính mình?", "Gentle"),
    ("H100", "Bạn đã bao lần chọn im lặng dù tim mình gào 'không'?", "Inspirational"),
    ("H101", "Bạn không thiếu cơ hội, bạn thiếu bản thân dám gật đầu với cơ hội.", "Insightful"),
    ("H102", "Bạn đang chờ cửa sổ mới mở ra hay vẫn ôm khung cửa cũ?", "Reflective"),
    ("H103", "Bạn có đang phản ứng với cuộc đời hay đang chủ động thiết kế nó?", "Confrontational"),
    ("H104", "Bạn sống theo lịch người khác hay theo nhịp của mình?", "Gentle"),
    ("H105", "Bạn có đang lái xe cuộc đời mình hay chỉ là hành khách?", "Inspirational"),
    ("H106", "Mỗi lần bạn nói 'chắc vậy cũng được', một phần bạn tắt đi.", "Insightful"),
    ("H107", "Bạn muốn cuộc sống 'chịu được' hay cuộc sống 'đáng sống'?", "Reflective"),
    ("H108", "Bạn có đang sống để kể lại, hay chỉ để sống sót?", "Confrontational"),
    ("H109", "Bạn đang xây câu chuyện nào để sau này kể lại?", "Gentle"),
    ("H110", "Nếu kể lại cuộc đời mình trong 1 trang giấy, bạn có hài lòng?", "Inspirational"),
    ("H111", "Bạn không cần làm nhiều hơn, bạn cần làm đúng hơn.", "Insightful"),
    ("H112", "Bao nhiêu việc bạn làm chỉ để trốn việc thật sự quan trọng?", "Reflective"),
    ("H113", "Bạn có đang nhầm lẫn bận rộn với hiệu quả?", "Confrontational"),
    ("H114", "Lịch của bạn nói gì về điều bạn coi trọng?", "Gentle"),
    ("H115", "Bạn có đang dành thời gian cho phiên bản tương lai của mình không?", "Inspirational"),
    ("H116", "Bạn đang đối xử với thời gian như vô hạn hay quý giá?", "Insightful"),
    ("H117", "Bạn có đang làm việc như thể đời này còn rất nhiều 'lần sau'?", "Reflective"),
    ("H118", "Việc bạn trì hoãn hôm nay đang chất lên ai trong tương lai?", "Confrontational"),
    ("H119", "Bạn có đang thuê tương lai của mình gánh hết mọi cái giá hôm nay?", "Gentle"),
    ("H120", "Mỗi 'để mai' là một viên gạch xây tường chắn ước mơ của bạn.", "Inspirational"),
    ("H121", "Bạn không cần thêm một khóa học, bạn cần một quyết định.", "Insightful"),
    ("H122", "Bạn có đang học để trốn, hay học để làm thật?", "Reflective"),
    ("H123", "Bao nhiêu kiến thức bạn 'biết rồi' nhưng chưa sống cùng nó?", "Confrontational"),
    ("H124", "Bạn đang thu thập kiến thức hay đang xây cuộc đời?", "Gentle"),
    ("H125", "Lần cuối bạn áp dụng một bài học vào đời thật là khi nào?", "Inspirational"),
    ("H126", "Bạn có đang chờ đủ giỏi mới bắt đầu, hay bắt đầu để giỏi lên?", "Insightful"),
    ("H127", "Bạn đang dùng 'em chưa sẵn sàng' để bảo vệ cái gì?", "Reflective"),
    ("H128", "Bạn có đang trốn trong vùng 'nghiên cứu thêm' vô thời hạn?", "Confrontational"),
    ("H129", "Bạn học để chứng minh mình thông minh hay để nhẹ lòng?", "Gentle"),
    ("H130", "Sức mạnh thật không nằm ở điều bạn biết, mà ở điều bạn dám làm.", "Inspirational"),
    ("H131", "Bạn đang bán [sản phẩm], hay đang bán sự chuyển hóa bên trong?", "Insightful"),
    ("H132", "Bạn có đang nói về tính năng, trong khi khách cần phiên bản mới của họ?", "Reflective"),
    ("H133", "Nội dung của bạn hứa điều gì với cuộc đời khách, ngoài kết quả bề mặt?", "Confrontational"),
    ("H134", "Bạn có đang bán giải pháp, hay bán phép màu không cần nỗ lực?", "Gentle"),
    ("H135", "Nếu khách không còn cần bạn nữa sau khi làm xong, bạn có dám nhận?", "Inspirational"),
    ("H136", "Bạn muốn khách lệ thuộc, hay muốn họ đủ mạnh để không cần bạn?", "Insightful"),
    ("H137", "Bạn có dám nói sự thật, ngay cả khi nó bán chậm hơn?", "Reflective"),
    ("H138", "Bạn đang marketing cho cái 'tôi' hay cho giá trị thật sự?", "Confrontational"),
    ("H139", "Bạn có đang dạy khách tin vào bạn, thay vì tin vào chính mình?", "Gentle"),
    ("H140", "Mỗi sản phẩm bạn bán đang kéo khách lại gần hay xa chính họ?", "Inspirational"),
    ("H141", "Bạn không phải làm 'nhiều content', bạn cần content đúng.", "Insightful"),
    ("H142", "Bài viết của bạn đang bán giờ của mình hay bán tương lai của khách?", "Reflective"),
    ("H143", "Bạn có đang viết để được like, hay để ai đó dám thay đổi?", "Confrontational"),
    ("H144", "Nếu bài viết của bạn không khiến ai dừng lại 5 giây, nó bán được gì?", "Gentle"),
    ("H145", "Bạn đang kể câu chuyện cho ego, hay câu chuyện cho linh hồn?", "Inspirational"),
    ("H146", "Bạn có dám kể góc tối của mình, thay vì chỉ khoảnh khắc lung linh?", "Insightful"),
    ("H147", "Story của bạn có cho khách thấy họ trong đó không, hay chỉ thấy bạn?", "Reflective"),
    ("H148", "Bạn đang viết để gây ấn tượng, hay để tạo biến chuyển thật sự?", "Confrontational"),
    ("H149", "Nội dung của bạn có bán được một quyết định dũng cảm không?", "Gentle"),
    ("H150", "Bạn có dám viết như nói chuyện với một người bạn thân đang đau?", "Inspirational"),
    ("H151", "Bạn không cần nói chuyện với cả thế giới, chỉ cần nói đúng người.", "Insightful"),
    ("H152", "Bạn có biết mình đang viết cho ai, ngoài 'tập khách hàng mục tiêu'?", "Reflective"),
    ("H153", "Nếu chỉ chọn giúp một kiểu người, bạn chọn ai?", "Confrontational"),
    ("H154", "Bạn có đang dùng từ ngữ mà phiên bản cũ của bạn từng cần nghe không?", "Gentle"),
    ("H155", "Bài viết của bạn có chạm được người đang thức khuya vì lo lắng không?", "Inspirational"),
    ("H156", "Bạn nói chuyện với người mạnh mẽ hay với người đang sắp bỏ cuộc?", "Insightful"),
    ("H157", "Bạn có đang sử dụng nỗi đau của khách, hay đang nâng niu nó?", "Reflective"),
    ("H158", "Bạn có dám chỉ cho khách phần họ cần đối diện, không phải phần họ muốn nghe?", "Confrontational"),
    ("H159", "Bạn đang mời họ thay đổi, hay mời họ nghiện cảm hứng?", "Gentle"),
    ("H160", "Nội dung của bạn có để lại câu hỏi nào ám ảnh họ không?", "Inspirational"),
    ("H161", "Bạn không cần thêm may mắn, bạn cần thêm trách nhiệm với lựa chọn.", "Insightful"),
    ("H162", "Bạn có đang để cho hoàn cảnh thứ đáng lẽ mình có thể thay?", "Reflective"),
    ("H163", "Bạn trách ai nhiều nhất cho cuộc đời mình hiện tại?", "Confrontational"),
    ("H164", "Bạn có đang chờ ai đó 'cho phép' mình sống khác đi?", "Gentle"),
    ("H165", "Nếu không còn ai để đổ lỗi, bạn sẽ làm gì khác?", "Inspirational"),
    ("H166", "Bạn có bao giờ nghĩ, có thể mình cũng góp phần tạo ra điều này?", "Insightful"),
    ("H167", "Bạn đang bảo vệ cái tôi, hay bảo vệ tương lai của mình?", "Reflective"),
    ("H168", "Bạn có dám nhận mình là người duy nhất chịu trách nhiệm không?", "Confrontational"),
    ("H169", "Khi ngừng đổ lỗi, bạn sẽ nhận lại sức mạnh gì?", "Gentle"),
    ("H170", "Bạn có đang muốn chữa lành, nhưng không muốn thay đổi gì cả?", "Inspirational"),
    ("H171", "Bạn không cần tha thứ cho quá khứ, nhưng bạn cần buông nó ra.", "Insightful"),
    ("H172", "Bạn có đang giữ chặt nỗi đau như bằng chứng mình đáng thương?", "Reflective"),
    ("H173", "Bạn được lợi gì khi tiếp tục ôm câu chuyện cũ?", "Confrontational"),
    ("H174", "Nếu thôi kể lại chuyện xưa, bạn sẽ kể gì về tương lai?", "Gentle"),
    ("H175", "Bạn có thực sự muốn chữa lành, hay chỉ muốn bớt cô đơn?", "Inspirational"),
    ("H176", "Chữa lành không xoá quá khứ, nó trả lại hiện tại cho bạn.", "Insightful"),
    ("H177", "Bạn còn cần quá khứ chứng minh điều gì cho mình nữa?", "Reflective"),
    ("H178", "Bạn có sẵn sàng tha cho bản thân của phiên bản 'chưa biết gì' không?", "Confrontational"),
    ("H179", "Nếu bạn nhìn quá khứ như một đứa trẻ, bạn sẽ dịu hơn chứ?", "Gentle"),
    ("H180", "Bạn có chấp nhận rằng mình đã làm hết sức, với những gì mình biết khi đó?", "Inspirational"),
    ("H181", "Bạn không phải 'quá nhiều', bạn chỉ ở nhầm nơi.", "Insightful"),
    ("H182", "Bạn có đang chơi nhỏ lại cho vừa với nỗi sợ của người khác?", "Reflective"),
    ("H183", "Môi trường bạn đang ở khuyến khích, hay làm tắt bạn đi?", "Confrontational"),
    ("H184", "Bạn có đang xin phép được là chính mình?", "Gentle"),
    ("H185", "Nếu không ai chê trách, bạn sẽ sống khác đi thế nào?", "Inspirational"),
    ("H186", "Bạn đang đặt mình vào không gian nuôi dưỡng hay không gian rút cạn?", "Insightful"),
    ("H187", "Ai là người bạn cần bớt nghe lời để nghe chính mình hơn?", "Reflective"),
    ("H188", "Bạn có đang cho người khác quyền phán xử cuộc đời mình?", "Confrontational"),
    ("H189", "Nếu không cần ai đồng ý, bạn sẽ đổi điều gì đầu tiên?", "Gentle"),
    ("H190", "Bạn có đang sống để không bị ghét, thay vì sống để tự tôn trọng mình?", "Inspirational"),
    ("H191", "Bạn không bất thường, bạn chỉ thức dậy sớm hơn một chút.", "Insightful"),
    ("H192", "Bạn có đang thức tỉnh trong một thế giới vẫn muốn ngủ tiếp?", "Reflective"),
    ("H193", "Bạn đang đi trước hay đi lạc khỏi đám đông?", "Confrontational"),
    ("H194", "Bạn có dám tin cảm nhận của mình, ngay cả khi không ai hiểu?", "Gentle"),
    ("H195", "Nếu trực giác nói khác logic, bạn nghe ai?", "Inspirational"),
    ("H196", "Bạn có đang chối bỏ phần sâu sắc nhất bên trong để được an toàn?", "Insightful"),
    ("H197", "Bạn tin điều gì về mình mà không ai từng nói ra?", "Reflective"),
    ("H198", "Bạn có đang lờ đi tiếng gọi mà mình biết rõ là dành cho mình?", "Confrontational"),
    ("H199", "Nếu linh hồn bạn viết status hôm nay, nó sẽ viết gì?", "Gentle"),
    ("H200", "Bạn có đang trở thành người mà ngày xưa bạn từng cần?", "Inspirational"),
    ("H201", "Bạn không lạc đường, bạn chỉ đang rẽ khỏi lối mòn cũ.", "Insightful"),
    ("H202", "Bạn có đang đòi bản đồ cho con đường chưa ai đi?", "Reflective"),
    ("H203", "Nếu không có đường có sẵn, bạn có dám tự vạch?", "Confrontational"),
    ("H204", "Bạn có đang chờ 'ai đó từng làm rồi' mới dám thử?", "Gentle"),
    ("H205", "Bạn đi chậm, nhưng bạn có chắc mình đi đúng hướng?", "Inspirational"),
    ("H206", "Bạn có đang chạy rất nhanh… trên một chiếc băng chuyền đứng yên?", "Insightful"),
    ("H207", "Bạn chọn tốc độ hay chọn ý nghĩa?", "Reflective"),
    ("H208", "Bạn có dám chậm lại để đi đúng, thay vì nhanh cho giống người ta?", "Confrontational"),
    ("H209", "Nếu tốc độ không còn quan trọng, bạn muốn trải nghiệm điều gì?", "Gentle"),
    ("H210", "Bạn có đang sống cuộc đời mình, hay đang thi với timeline của người khác?", "Inspirational"),
    ("H211", "Bạn không cần 'cố gắng hơn', bạn cần 'sống khác đi'.", "Insightful"),
    ("H212", "Bạn có đang cố gắng chữa lỗi hệ thống bằng thêm nỗ lực cá nhân?", "Reflective"),
    ("H213", "Bạn có đang tự trách mình vì một mô hình vốn không phục vụ mình?", "Confrontational"),
    ("H214", "Bạn cần sửa bản thân hay cần đổi môi trường?", "Gentle"),
    ("H215", "Bạn có đang cố vừa lòng hệ thống mà quên hỏi 'mình muốn gì'?", "Inspirational"),
    ("H216", "Bạn có đang xem burnout là huy chương danh dự?", "Insightful"),
    ("H217", "Bạn cần nghỉ ngơi hay cần nhìn lại toàn bộ bản đồ?", "Reflective"),
    ("H218", "Bạn có đang dùng cà phê để chống lại tiếng kêu 'hãy dừng lại'?", "Confrontational"),
    ("H219", "Cơ thể bạn đã gửi bao nhiêu tín hiệu mà bạn gạt đi?", "Gentle"),
    ("H220", "Bạn có đang đổi sức khoẻ lấy thành tích mà bạn không thật sự muốn?", "Inspirational"),
    ("H221", "Bạn không cần thêm 'how to', bạn cần thêm 'tại sao'.", "Insightful"),
    ("H222", "Bạn có biết vì sao mình thật sự muốn [kết quả] không?", "Reflective"),
    ("H223", "Nếu không được khoe, bạn còn muốn đạt mục tiêu này không?", "Confrontational"),
    ("H224", "Bạn đang muốn điều này vì nhẹ lòng, hay vì được vỗ tay?", "Gentle"),
    ("H225", "Bạn có đang theo đuổi giấc mơ của mình, hay giấc mơ trông đẹp trên mạng?", "Inspirational"),
    ("H226", "Bạn đã bao lần đạt được thứ mình tưởng muốn, rồi vẫn trống rỗng?", "Insightful"),
    ("H227", "Bạn có hiểu điều mình thật sự không muốn lặp lại nữa không?", "Reflective"),
    ("H228", "Bạn muốn sống cuộc đời sâu sắc hay đời nhìn cho 'ra gì'?", "Confrontational"),
    ("H229", "Bạn có dám chọn mục tiêu nhỏ hơn nhưng đúng với linh hồn mình hơn?", "Gentle"),
    ("H230", "Nếu không ai biết, bạn vẫn muốn thay đổi chứ?", "Inspirational"),
    ("H231", "Bạn không cần hoàn hảo, bạn cần trung thực.", "Insightful"),
    ("H232", "Bạn có đang xây hình ảnh 'tốt' thay vì cuộc đời thật sự 'đúng'?", "Reflective"),
    ("H233", "Mỗi lần bạn nói 'không sao đâu', có phần nào trong bạn chết đi không?", "Confrontational"),
    ("H234", "Bạn có đang trang điểm cho cảm xúc bằng những câu nói tích cực rỗng?", "Gentle"),
    ("H235", "Bạn có dám thừa nhận 'mình mệt' mà không thấy xấu hổ?", "Inspirational"),
    ("H236", "Bạn có đang dùng 'tích cực' để phủ bê tông lên nỗi đau?", "Insightful"),
    ("H237", "Bạn có phân biệt được bình an và tê liệt cảm xúc không?", "Reflective"),
    ("H238", "Bạn đang sống tỉnh thức hay sống cơ chế 'auto'?", "Confrontational"),
    ("H239", "Bạn có cảm được mình đang cảm gì, hay chỉ chạy theo việc cần làm?", "Gentle"),
    ("H240", "Lần cuối bạn khóc vì chạm vào sự thật, không phải vì bất lực là khi nào?", "Inspirational"),
    ("H241", "Bạn không thiếu may mắn, bạn thiếu can đảm đứng về phía mình.", "Insightful"),
    ("H242", "Bạn có đang tin người khác hơn là tin chính mình?", "Reflective"),
    ("H243", "Bạn đang nghe theo tiếng nói nào to nhất trong đầu?", "Confrontational"),
    ("H244", "Bạn có nhận ra giọng nói phán xét trong đầu không phải là bạn?", "Gentle"),
    ("H245", "Bạn đang kể câu chuyện nào về mình mỗi ngày?", "Inspirational"),
    ("H246", "Nếu đổi câu chuyện, liệu cuộc đời có đổi theo không?", "Insightful"),
    ("H247", "Bạn có dám thôi gọi mình bằng những nhãn cũ?", "Reflective"),
    ("H248", "Bạn có thấy mình nói 'em vốn là người…' bao nhiêu lần không?", "Confrontational"),
    ("H249", "Bạn đang miêu tả bản thân hay đang tự bỏ bùa chính mình?", "Gentle"),
    ("H250", "Bạn có muốn thử gọi tên mình bằng một câu chuyện mới?", "Inspirational"),
    ("H251", "Bạn không lười thay đổi, bạn sợ mất đi bản sắc cũ.", "Insightful"),
    ("H252", "Bạn có sợ người ta nói 'khác quá rồi, không nhận ra nữa'?", "Reflective"),
    ("H253", "Nếu thay đổi làm một số người rời đi, bạn có dám chấp nhận?", "Confrontational"),
    ("H254", "Bạn giữ họ lại, hay giữ chính mình lại?", "Gentle"),
    ("H255", "Bạn có đang giả vờ bé nhỏ để không làm ai khó chịu?", "Inspirational"),
    ("H256", "Bạn có dám cho phép mình trở nên 'quá nhiều' theo tiêu chuẩn của họ?", "Insightful"),
    ("H257", "Bạn đang sống cho ai cảm thấy dễ chịu với sự hiện diện của bạn?", "Reflective"),
    ("H258", "Nếu không phải chứng minh điều gì, bạn sẽ là ai?", "Confrontational"),
    ("H259", "Bạn có đang sống để không bị ghét, thay vì sống để tự tôn trọng mình?", "Gentle"),
    ("H260", "Bạn dám đánh đổi hình ảnh 'ngoan' để đổi lấy cuộc đời 'thật' không?", "Inspirational"),
    ("H261", "Bạn không phải 'cố mạnh mẽ', bạn được phép cần người khác.", "Insightful"),
    ("H262", "Bạn có đang gồng làm trụ cột cho tất cả, trừ chính mình?", "Reflective"),
    ("H263", "Bạn đã quen với việc tự cứu mình đến mức quên nhờ ai đó nắm tay?", "Confrontational"),
    ("H264", "Bạn có nhớ lần cuối mình để người khác giúp thật sự là khi nào?", "Gentle"),
    ("H265", "Bạn có đang tin rằng 'chỉ có mình mới lo cho mình được'?", "Inspirational"),
    ("H266", "Bạn có một với niềm tin đó chưa?", "Insightful"),
    ("H267", "Bạn có dám buông bớt kiểm soát để cho phép cuộc đời hỗ trợ mình?", "Reflective"),
    ("H268", "Bạn có phải lúc nào cũng là người hiểu chuyện trong mọi câu chuyện?", "Confrontational"),
    ("H269", "Bạn có cho phép mình cũng được yếu, được sai, được vụn vỡ không?", "Gentle"),
    ("H270", "Bạn có đang cho đi để được thương, hay vì bạn thật sự muốn cho?", "Inspirational"),
    ("H271", "Bạn không cần 'reset', bạn cần thành thật với bản thân lần đầu tiên.", "Insightful"),
    ("H272", "Bạn có đang chờ năm mới để đổi, thay vì đổi ngay từ hôm nay?", "Reflective"),
    ("H273", "Nếu một ngày không còn lý do nào để trì hoãn, bạn sẽ bắt đầu từ đâu?", "Confrontational"),
    ("H274", "Bạn có đang chờ cảm hứng để làm điều cần kỷ luật?", "Gentle"),
    ("H275", "Bạn có thấy mình luôn giỏi khởi động, nhưng kém phần duy trì?", "Inspirational"),
    ("H276", "Bạn cần thêm động lực hay cần bớt phân tâm?", "Insightful"),
    ("H277", "Bạn dám chọn nhàm chán trong kỷ luật để đổi lấy cuộc đời thú vị chứ?", "Reflective"),
    ("H278", "Bạn có đang nghiện drama hơn là nghiện sự bình thường của tiến bộ?", "Confrontational"),
    ("H279", "Bạn có dám chấp nhận rằng tự do là kết quả của kỷ luật?", "Gentle"),
    ("H280", "Bạn có kế hoạch cho phiên bản tiếp theo của mình chưa?", "Inspirational"),
    ("H281", "Bạn không cần một cuộc đời hoàn hảo, bạn cần một cuộc đời đúng.", "Insightful"),
    ("H282", "Bạn có đang chi nhiều năng lượng để bảo vệ hình ảnh hơn là bảo vệ bình an?", "Reflective"),
    ("H283", "Thành công lý tưởng của bạn trông như thế nào, nếu bỏ hết ảnh Instagram?", "Confrontational"),
    ("H284", "Nếu không còn mạng xã hội, bạn sẽ đo hạnh phúc bằng gì?", "Gentle"),
    ("H285", "Bạn có đang thiết kế cuộc đời hay chỉ đang thiết kế feed?", "Inspirational"),
    ("H286", "Bạn đang nghiện dopamine tức thời hay chọn hạnh phúc bền hơn?", "Insightful"),
    ("H287", "Bạn có đang so sánh hậu trường của mình với highlight của người khác?", "Reflective"),
    ("H288", "Bạn có dám sống một cuộc đời bình thường nhưng trọn vẹn?", "Confrontational"),
    ("H289", "Bạn cần thêm thành công, hay cần thêm sự hiện diện với chính mình?", "Gentle"),
    ("H290", "Bạn có đang hy sinh hiện tại cho một tương lai mà bạn chưa từng định nghĩa rõ?", "Inspirational"),
    ("H291", "Bạn không thiếu câu trả lời, bạn thiếu những câu hỏi đúng.", "Insightful"),
    ("H292", "Nếu cuộc đời là một phiên coaching, bạn sẽ hỏi mình điều gì?", "Reflective"),
    ("H293", "Bạn có đang hỏi 'tại sao là mình?', thay vì 'mình học được gì?'", "Confrontational"),
    ("H294", "Bạn có dám hỏi: 'Mình đang góp phần tạo ra điều này như thế nào?'", "Gentle"),
    ("H295", "Nếu bạn là client của chính mình, bạn sẽ nói gì với mình?", "Inspirational"),
    ("H296", "Bạn có dám hỏi: 'Cuộc đời này muốn mình trở thành ai?'", "Insightful"),
    ("H297", "Bạn đang hỏi 'làm sao', hay đã rõ 'tại sao'?", "Reflective"),
    ("H298", "Bạn có dám hỏi: 'Sự thật mình đang trốn là gì?'", "Confrontational"),
    ("H299", "Bạn có dám nghe câu trả lời, ngay cả khi nó bất tiện?", "Gentle"),
    ("H300", "Nếu chỉ được hỏi một câu mỗi ngày, bạn sẽ hỏi gì bản thân?", "Inspirational"),
    ("H301", "Bạn không cần làm nhiều việc hơn, bạn cần làm đúng việc hơn.", "Insightful"),
    ("H302", "Danh sách to-do của bạn đang phục vụ điều gì trong dài hạn?", "Reflective"),
    ("H303", "Bạn có đang làm việc như người chữa cháy hay như người kiến trúc sư?", "Confrontational"),
    ("H304", "Bạn dành bao nhiêu thời gian cho việc quan trọng, không khẩn cấp?", "Gentle"),
    ("H305", "Bạn có đang bận tới mức không kịp sống?", "Inspirational"),
    ("H306", "Nếu chỉ được hoàn thành 3 việc mỗi ngày, bạn sẽ chọn gì?", "Insightful"),
    ("H307", "Bạn có đang làm việc vì sợ cảm giác 'lỡ dở'?", "Reflective"),
    ("H308", "Bạn có đang cho rằng 'bận' là thước đo giá trị bản thân?", "Confrontational"),
    ("H309", "Bạn có dám nhẹ lịch mà nặng chất lượng cuộc sống không?", "Gentle"),
    ("H310", "Bạn có đang tối ưu cho năng suất hay cho ý nghĩa?", "Inspirational"),
    ("H311", "Bạn không phải chọn giữa giàu có và tử tế.", "Insightful"),
    ("H312", "Bạn có đang tin rằng tiền và tử tế không đi chung?", "Reflective"),
    ("H313", "Bạn nghĩ sao nếu người sâu sắc cũng có thể rất giàu?", "Confrontational"),
    ("H314", "Bạn có đang vô thức ghét tiền vì những người dùng nó sai cách?", "Gentle"),
    ("H315", "Bạn có đang từ chối tiền, trong khi mong muốn tự do?", "Inspirational"),
    ("H316", "Nếu tiền chỉ khuếch đại bản chất, bạn muốn khuếch đại điều gì?", "Insightful"),
    ("H317", "Bạn có dám trở nên giàu có theo cách làm bạn tự hào?", "Reflective"),
    ("H318", "Bạn có đang đòi hỏi mình 'cao thượng' để né đối diện với nỗi sợ về tiền?", "Confrontational"),
    ("H319", "Bạn có dám tin rằng hạnh phúc và tiền bạc có thể cùng tồn tại?", "Gentle"),
    ("H320", "Bạn có đang bắt tiền làm cái cớ cho mọi thứ mình chưa dám làm?", "Inspirational"),
    ("H321", "Bạn không cần bỏ hết mọi thứ, bạn cần đặt lại thứ tự ưu tiên.", "Insightful"),
    ("H322", "Bạn có đang sống như thể mình có hai cuộc đời để thử?", "Reflective"),
    ("H323", "Nếu chỉ giữ lại được 20% cuộc sống hiện tại, bạn giữ gì?", "Confrontational"),
    ("H324", "Bạn có dám để một số thứ sụp đổ để mình được xây lại?", "Gentle"),
    ("H325", "Bạn có đang ôm quá nhiều thứ chỉ vì sợ bị đánh giá?", "Inspirational"),
    ("H326", "Bạn có dám buông để hai tay rảnh mà nhận điều mới?", "Insightful"),
    ("H327", "Bạn có thật sự cần tất cả những thứ đang nắm, hay chỉ sợ trống tay?", "Reflective"),
    ("H328", "Bạn có đang dành chỗ cho phiên bản mới của mình bước vào?", "Confrontational"),
    ("H329", "Nếu cuộc đời là một căn phòng, bạn cần dọn bớt gì?", "Gentle"),
    ("H330", "Bạn có đang tích trữ cả những mối quan hệ đã hết 'hạn sử dụng'?", "Inspirational"),
    ("H331", "Bạn không bị muộn, bạn đang ở đúng bài học của mình.", "Insightful"),
    ("H332", "Bạn có đang so tuổi với timeline của người khác?", "Reflective"),
    ("H333", "Nếu quên tuổi đi, bạn sẽ bắt đầu điều gì hôm nay?", "Confrontational"),
    ("H334", "Bạn có đang dùng 'muộn rồi' làm cớ để không cần thử?", "Gentle"),
    ("H335", "Bạn có dám tin mình đang đến đúng lúc cho hành trình của mình?", "Inspirational"),
    ("H336", "Bạn có đang phán xét đường đi, trong khi chưa thấy hết con đường?", "Insightful"),
    ("H337", "Bạn có đang so chương 3 của mình với chương 20 của người khác?", "Reflective"),
    ("H338", "Bạn có dám sống sâu một ngày, thay vì lo cho 10 năm nữa?", "Confrontational"),
    ("H339", "Bạn đang sống trong hiện tại hay trong những 'giá như' chưa xảy ra?", "Gentle"),
    ("H340", "Bạn có đang bỏ lỡ khoảnh khắc này vì mải chạy tới khoảnh khắc khác?", "Inspirational"),
    ("H341", "Bạn không cần một bức tranh hoàn hảo, bạn cần một bước chân thật.", "Insightful"),
    ("H342", "Bạn có đang đợi mọi thứ rõ ràng mới dám nhúc nhích?", "Reflective"),
    ("H343", "Bạn có chấp nhận rằng rõ ràng là phần thưởng, không phải điều kiện?", "Confrontational"),
    ("H344", "Bạn có dám bước trong sương mù với niềm tin vào mình?", "Gentle"),
    ("H345", "Bạn đang tìm bảo hành hay tìm cuộc đời đáng sống?", "Inspirational"),
    ("H346", "Bạn có đang yêu cầu chắc chắn từ một cuộc chơi tên là 'trải nghiệm'?", "Insightful"),
    ("H347", "Bạn có dám chấp nhận rủi ro của việc sống thật sự?", "Reflective"),
    ("H348", "Bạn có đang cược cả đời mình vào cảm giác an toàn giả?", "Confrontational"),
    ("H349", "Bạn sẽ nhớ điều gì hơn: lần bạn thất bại, hay lần bạn dám thử?", "Gentle"),
    ("H350", "Bạn có muốn dành phần còn lại cuộc đời để tự kể chuyện 'giá như'?", "Inspirational"),
    ("H351", "Bạn không ngẫu nhiên đọc được những dòng này.", "Insightful"),
    ("H352", "Có điều gì trong bạn đang gật đầu mà bạn giả vờ không thấy?", "Reflective"),
    ("H353", "Bạn có đang cảm nhận cơ thể mình phản ứng với những câu hỏi này không?", "Confrontational"),
    ("H354", "Bạn có dám không lướt tiếp, mà dừng lại để viết ra cảm nhận?", "Gentle"),
    ("H355", "Bạn có dám đối diện với một sự thật nhỏ hôm nay, thay vì một cú sập lớn mai sau?", "Inspirational"),
    ("H356", "Bạn đang sợ điều gì nhất nếu mình thật sự thay đổi?", "Insightful"),
    ("H357", "Bạn sẽ mất gì nếu tiếp tục như cũ, và sẽ mất gì nếu dám đổi?", "Reflective"),
    ("H358", "Nếu đây là dấu hiệu bạn đợi bấy lâu, bạn sẽ làm gì sau khi đọc xong?", "Confrontational"),
    ("H359", "Bạn có dám coi bài viết này là đường ranh giữa cũ và mới?", "Gentle"),
    ("H360", "Bạn muốn phiên bản nào của mình nhấn nút 'tắt màn hình' hôm nay?", "Inspirational"),
    ("H361", "Bạn không cần trả lời mình, bạn cần trả lời chính bạn.", "Insightful"),
    ("H362", "Bạn sẽ nói gì với bản thân trong gương tối nay?", "Reflective"),
    ("H363", "Nếu viết một lá thư cho bạn 10 năm nữa, bạn sẽ hứa gì?", "Confrontational"),
    ("H364", "Bạn có dám viết lại câu chuyện của mình bắt đầu từ ngày hôm nay?", "Gentle"),
    ("H365", "Và nếu dám, bước đầu tiên của bạn sẽ là gì?", "Inspirational"),
]

# 6 RULES classifier
SPIRITUAL_KW = ['linh hồn', 'vũ trụ', 'tần số', 'vibration', 'manifest', 'tâm linh', 'năng lượng vũ trụ', 'bỏ bùa']
SALES_KW_STRICT = ['mình bán', 'mình không bán', 'người ta không mua', 'bài viết của bạn', 'nội dung của bạn',
                   'content của bạn', 'khách không còn cần', 'khách lệ thuộc', 'sales chậm', 'bán chậm', 'marketing cho',
                   'sản phẩm bạn', 'bán [sản phẩm]', 'bán giải pháp', 'bán phép màu', 'mỗi sản phẩm bạn',
                   'sản phẩm bạn bán', 'bán được một quyết định', 'bán được gì']
SALES_KW_SOFT = ['khách hàng', 'inbox', 'lead magnet', 'đăng ký', 'scarcity', 'tư vấn', 'tập khách hàng', 'offer']
PLACEHOLDER_RE = re.compile(r'\[[^\]]+\]')

MONEY_KW = ['tiền', 'thu nhập', 'tài chính', 'lương', 'giàu', 'nghèo', 'lương về', 'kiếm tiền', 'sự nghiệp',
            'thành công', 'thành tích', 'thành công của ai', 'doanh thu', 'tự do tài chính', 'nuôi nổi giấc',
            'tài sản', 'sản phẩm bạn bán', 'mua điều gì', 'tự do của bạn', 'kiếm thêm', 'kiếm đúng',
            'tham vọng', 'burnout', 'năng suất', 'hoàn thành', 'tối ưu', 'thành công lý tưởng']
FAMILY_KW = ['con bạn', 'gia đình', 'bố mẹ', 'thế hệ sau', 'mẹ', 'bố', 'chồng', 'vợ', 'truyền cho thế hệ',
             'lặp lại đúng mô thức', 'câu chuyện gia đình']
SELF_WORTH_KW = ['giá trị thật', 'xứng đáng', 'mình là ai', 'bản thân', 'tự tin', 'tự trọng', 'tự yêu', 'tự công nhận',
                 'mình đủ', 'tin mình', 'phiên bản', 'bản sắc', 'mình giỏi', 'mình dốt', 'em chỉ là',
                 'em vốn là', 'tôn trọng', 'mình mạnh', 'thân nhỏ', 'quá nhiều', 'làm bạn với chính mình']
PEACE_KW = ['bình yên', 'kiệt sức', 'tiêu cực', 'mệt', 'gồng', 'ranh giới', 'cảm xúc', 'an yên', 'tự cảm',
            'tê liệt', 'chữa lành', 'quá khứ', 'tha thứ', 'ôm câu chuyện cũ', 'buông', 'vết thương cũ',
            'không sao đâu', 'thôi gọi mình', 'vùng an toàn', 'bảo vệ', 'môi trường', 'rỗng', 'trống', 'cô đơn',
            'thoả hiệp', 'cố mạnh mẽ', 'cố gắng hơn', 'hy sinh', 'dành thời gian', 'chịu đựng', 'làm ngơ',
            'quen với', 'tỉnh thức', 'cơ thể', 'sức khoẻ', 'cảm hứng', 'kỷ luật', 'reset', 'hoàn hảo',
            'so sánh', 'hiện tại', 'giá như', 'thật sự ổn', 'lười', 'làm hài lòng', 'gói dở',
            'bỏ quên mình', 'né đối diện', 'lao đầu vào', 'trốn']

CONFRONT_KW = ['hay đang né', 'né tránh', 'né đối diện', 'né việc', 'né sự thật', 'có dám', 'sao không', 'tại sao',
               'không dám', 'chưa nhận ra', 'bao lâu rồi mà chưa', 'còn không', 'có biết', 'sai là',
               'có phải', 'chứ', 'đến bao giờ', 'đến má»©c', 'cứ mãi', 'mỗi ngày', 'tự sabo']
SOFT_OPENERS = ['có khi', 'có thể', 'có lẽ', 'nếu', 'có dám', 'phiên bản']
NEGATIVE_FRAME_PATTERNS = [(r'không phải.*mà (là|vì)', 'Negative Frames')]


def detect_calendar_stage(text):
    t = text.lower()
    if any(kw in t for kw in FAMILY_KW):
        return 'D15-D21'
    if any(kw in t for kw in MONEY_KW):
        return 'D22-D30'
    if any(kw in t for kw in PEACE_KW):
        return 'D1-D7'
    if any(kw in t for kw in SELF_WORTH_KW):
        return 'D8-D14'
    return 'D8-D14'


def detect_tone(text, original_tone):
    t = text.lower()
    has_negative_frame = any(re.search(p, t) for p, _ in NEGATIVE_FRAME_PATTERNS)
    is_confront = any(kw in t for kw in CONFRONT_KW)
    is_soft = any(t.startswith(s) for s in SOFT_OPENERS)
    if has_negative_frame:
        return 'Insightful'
    if is_soft and not is_confront:
        return 'Gentle'
    if is_confront:
        return 'Confrontational'
    return original_tone


def adapt_text(text, mode='soften'):
    """Apply better adapt formula per Rule #2."""
    t = text
    # Pattern: "Bạn ... ?" -> "Có khi mình ... ?" or "Có khi bạn ..." for question
    if mode == 'soften':
        if t.startswith('Bạn '):
            t = 'Có khi ' + t[0].lower() + t[1:]
        elif t.startswith('Bao nhiêu lần bạn'):
            t = t.replace('Bao nhiêu lần bạn', 'Có bao nhiêu lần mình')
        elif t.startswith('Bạn đã bao'):
            t = t.replace('Bạn đã bao', 'Có bao nhiêu')
    return t


def classify(hid, text, original_tone):
    """Apply 6 rules to classify a hook."""
    t = text.lower()
    has_placeholder = bool(PLACEHOLDER_RE.search(text))

    # Rule 5: Spiritual REJECT
    if any(kw in t for kw in SPIRITUAL_KW):
        return {
            'tone_v2': original_tone,
            'fit': 'REJECT',
            'stage': 'Không dùng',
            'calendar': 'Không dùng',
            'format': '—',
            'hook_type': 'Spiritual',
            'risk': 'Quá spiritual / Lệch voice chị Hiền',
            'adapt_dir': 'Không dùng',
            'chi_hien_hook': 'Không dùng cho chị Hiền.',
            'use_case': '—',
            'note': 'Voice chị Hiền không dùng spiritual / linh hồn / vũ trụ. REJECT.'
        }

    # Rule 3 + 6: Sales hook (strict + placeholder of [sản phẩm])
    is_sales_strict = any(kw in t for kw in SALES_KW_STRICT)
    is_sales_soft = any(kw in t for kw in SALES_KW_SOFT)
    is_about_money_business = ('content' in t or 'bài viết' in t or 'bán' in t or 'khách' in t)

    if is_sales_strict or (has_placeholder and 'sản phẩm' in t):
        return {
            'tone_v2': original_tone,
            'fit': 'HOLD',
            'stage': 'Sau 30 bài / Sales phase',
            'calendar': 'Sau 30 bài',
            'format': 'Educational / Sau 30 bài',
            'hook_type': 'Sales / Offer hook',
            'risk': 'Quá marketing/sales sớm',
            'adapt_dir': 'Giữ lại dùng sau; bỏ yếu tố bán hàng + placeholder khi cần',
            'chi_hien_hook': 'Dùng sau 30 bài: cần adapt theo offer thật và voice chị Hiền.',
            'use_case': 'Giai đoạn business/content/sales sau 30 bài',
            'note': 'Chưa dùng trong 30 bài đầu. Sales hook hoặc placeholder offer.'
        }

    # Soft sales (just talk about clients/marketing without direct selling)
    if is_sales_soft and not is_sales_strict:
        # Reflection-style about business → Sau 30 bài
        return {
            'tone_v2': original_tone,
            'fit': 'HOLD',
            'stage': 'Sau 30 bài / Sales phase',
            'calendar': 'Sau 30 bài',
            'format': 'Educational / Sau 30 bài',
            'hook_type': 'Content / Business hook',
            'risk': 'Quá marketing/sales sớm cho 30 bài đầu',
            'adapt_dir': 'Giữ lại dùng sau khi đã warm audience',
            'chi_hien_hook': 'Dùng sau 30 bài. Adapt theo voice chị Hiền + insight thật.',
            'use_case': 'Giai đoạn business/content/sales sau 30 bài',
            'note': 'Chưa dùng trong 30 bài đầu.'
        }

    # Determine tone
    tone_v2 = detect_tone(text, original_tone)

    # Determine calendar stage
    calendar = detect_calendar_stage(text)

    # Determine format & use case
    is_long_form = len(text) > 80 or 'mỗi lần' in t or 'thu nhập của bạn hiếm' in t or 'không cần' in t
    fmt = 'Long FB / Reel 90-120s' if is_long_form and ('không cần' in t or 'không phải' in t) else 'Short FB / Reel 60s'

    # Use Case mapping
    if calendar == 'D15-D21':
        use_case = 'Gia đình, khuôn mẫu cũ, vai trò phụ nữ'
    elif calendar == 'D22-D30':
        use_case = 'Công việc, tự do, kỷ luật, nhịp sống'
    elif calendar == 'D8-D14':
        if 'phiên bản' in t or 'bản sắc' in t or 'tự yêu' in t or 'em chỉ là' in t:
            use_case = 'Giá trị bản thân, bản sắc, thay đổi'
        elif 'ranh giới' in t or 'mối quan hệ' in t or 'môi trường' in t or 'tôn trọng' in t:
            use_case = 'Ranh giới, quan hệ, năng lượng xung quanh'
        else:
            use_case = 'Tự soi, sống thật, lựa chọn cuộc đời'
    elif calendar == 'D1-D7':
        if 'chữa lành' in t or 'quá khứ' in t or 'tha thứ' in t or 'ôm' in t or 'vết thương' in t:
            use_case = 'Chữa lành, quá khứ, tự tha thứ'
        else:
            use_case = 'Bình yên, kiệt sức, ranh giới cảm xúc'
    else:
        use_case = 'Tự soi, sống thật, lựa chọn cuộc đời'

    # Hook type
    has_negative_frame = any(re.search(p, t) for p, _ in NEGATIVE_FRAME_PATTERNS)
    if has_negative_frame:
        hook_type = 'Reframe / Contrarian nhẹ'
    elif text.endswith('?'):
        hook_type = 'Câu hỏi nội tâm'
    elif 'mỗi lần' in t or 'mỗi sáng' in t:
        hook_type = 'Reflective insight'
    else:
        hook_type = 'Reflective insight'

    # Rule 1+2: Tone & Adapt decision
    is_confront = (tone_v2 == 'Confrontational')
    is_gentle = (tone_v2 == 'Gentle')
    is_soft_starter = any(text.startswith(s.capitalize()) for s in ['Có khi', 'Có thể', 'Có lẽ'])

    if is_confront:
        fit = 'ADAPT'
        risk = 'Hơi gắt'
        adapt_dir = 'Làm mềm: đổi ngôi bạn → mình + đổi structure chất vấn → mời quan sát'
        chi_hien_hook = adapt_text(text, mode='soften')
        note = 'Á tốt nhưng cần làm mềm để không phán xét/coachy. Áp đầy đủ Rule #2 (đổi ngôi + structure).'
    elif has_negative_frame and not is_confront:
        fit = 'PASS'
        risk = 'Hợp'
        adapt_dir = 'Giữ nguyên — Negative Frames đẹp, hợp voice chị Hiền'
        chi_hien_hook = text
        note = 'Có thể dùng gần nguyên, vẫn cần bám insight thật.'
    elif is_gentle or is_soft_starter:
        fit = 'PASS'
        risk = 'Hợp'
        adapt_dir = 'Giữ nguyên hoặc làm mềm nhẹ'
        chi_hien_hook = text
        note = 'Có thể dùng gần nguyên, vẫn cần bám insight thật.'
    else:
        # Insightful or Reflective default
        fit = 'PASS'
        risk = 'Hợp'
        adapt_dir = 'Giữ nguyên hoặc làm mềm nhẹ'
        chi_hien_hook = text
        note = 'Có thể dùng gần nguyên, vẫn cần bám insight thật.'

    return {
        'tone_v2': tone_v2,
        'fit': fit,
        'stage': '30 bài đầu' if calendar in ['D1-D7', 'D8-D14', 'D15-D21', 'D22-D30'] else 'Sau 30 bài',
        'calendar': calendar,
        'format': fmt,
        'hook_type': hook_type,
        'risk': risk,
        'adapt_dir': adapt_dir,
        'chi_hien_hook': chi_hien_hook,
        'use_case': use_case,
        'note': note
    }


def main():
    output_path = 'data/reference_hooks/chi_hien_hook_bank_v2_refined.csv'
    fieldnames = [
        'ID', 'Original Hook', 'Original Tone', 'Tone v2', 'Fit for Chị Hiền',
        'Stage', 'Calendar Stage Match', 'Best Format', 'Hook Type', 'Risk',
        'Adapt Direction', 'Chị Hiền Hook', 'Use Case', 'Note'
    ]
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for hid, text, original_tone in HOOKS:
            r = classify(hid, text, original_tone)
            writer.writerow({
                'ID': hid,
                'Original Hook': text,
                'Original Tone': original_tone,
                'Tone v2': r['tone_v2'],
                'Fit for Chị Hiền': r['fit'],
                'Stage': r['stage'],
                'Calendar Stage Match': r['calendar'],
                'Best Format': r['format'],
                'Hook Type': r['hook_type'],
                'Risk': r['risk'],
                'Adapt Direction': r['adapt_dir'],
                'Chị Hiền Hook': r['chi_hien_hook'],
                'Use Case': r['use_case'],
                'Note': r['note'],
            })

    # Quick stats
    fits = {'PASS': 0, 'ADAPT': 0, 'HOLD': 0, 'REJECT': 0}
    for hid, text, original_tone in HOOKS:
        r = classify(hid, text, original_tone)
        fits[r['fit']] += 1
    print(f"Total: {len(HOOKS)}")
    print(f"PASS: {fits['PASS']}")
    print(f"ADAPT: {fits['ADAPT']}")
    print(f"HOLD: {fits['HOLD']}")
    print(f"REJECT: {fits['REJECT']}")
    print(f"Output: {output_path}")


if __name__ == '__main__':
    main()
