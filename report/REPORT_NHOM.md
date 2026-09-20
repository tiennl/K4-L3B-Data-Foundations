# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Skynet

**Thành viên:**
- Phùng Trọng Chiến (`2A202602430`, thành viên 1)
- Ngô Lê Thuỳ Tiên (`2A202602614`, thành viên 2)
- Nguyễn Khánh Linh (`2A202602409`, thành viên 3)
- Nguyễn Hồng Khoa (`2A202602534`, thành viên 4)

**Ngày:** 2026-09-20

## 1. Lựa chọn tài liệu (10 điểm)

### Chủ đề và lý do chọn

**Chủ đề:** Chính sách bảo hành và quy trình xử lý bảo hành trên Shopee và Tiki.

Chủ đề có cấu trúc phân cấp rõ gồm điều kiện, thời hạn, quy trình và chế tài; đồng thời chứa nhiều mốc SLA cụ thể như 02, 15–30, 32 và 45 ngày. Corpus cũng phân tách rõ `buyer` và `seller`, cùng các mô hình FBT, Dropship và SD, phù hợp để đánh giá cả chunking lẫn metadata filtering.

### Data inventory

| # | Tài liệu | Nguồn | Ngày lấy / phiên bản | Số ký tự nội dung | Metadata chính |
|---|---|---|---|---:|---|
| 1 | Chính sách bảo hành cho sản phẩm mua tại Shopee | [Shopee Help Center](https://help.shopee.vn/4/article/79046-[Quy-định]-Chính-sách-bảo-hành-cho-sản-phẩm-mua-tại-Shopee) | 2026-09-20 / not-stated | 2.897 | `buyer`, `shopee`, `warranty-policy` |
| 2 | FAQ xử lý bảo hành dành cho Nhà Bán | [Học viện Tiki](https://hocvien.tiki.vn/faq/cau-hoi-thuong-gap-ve-xu-ly-doi-tra-bao-hanh/) | 2026-09-20 / not-stated | 3.304 | `seller`, `tiki`, `warranty-policy` |
| 3 | Quy trình bảo hành FBT | [Học viện Tiki](https://hocvien.tiki.vn/faq/mo-hinh-fbt-huong-dan-quy-trinh-xu-ly-doi-tra-bao-hanh/) | 2026-09-20 / not-stated | 1.641 | `seller`, `tiki`, `fbt` |
| 4 | Quy trình bảo hành Dropship | [Học viện Tiki](https://hocvien.tiki.vn/faq/huong-dan-quy-trinh-xu-ly-doi-tra-bao-hanh-mo-hinh-dropship/) | 2026-09-20 / not-stated | 2.244 | `seller`, `tiki`, `dropship` |
| 5 | Quy trình bảo hành SD | [Học viện Tiki](https://hocvien.tiki.vn/faq/huong-dan-quy-trinh-xu-ly-doi-tra-bao-hanh-mo-hinh-sd/) | 2026-09-20 / not-stated | 2.029 | `seller`, `tiki`, `sd` |

Corpus nằm tại `data/warranty-policy/`; nguồn được tổng hợp trong `sources.csv`.

### Data governance

- [x] Có 5 tài liệu công khai, không chứa dữ liệu cá nhân hoặc thông tin đăng nhập.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version`.
- [x] Mỗi tài liệu có `audience`, `category`, `language`, `platform`.
- [x] Tài liệu theo mô hình vận hành có thêm `fulfillment_model`.
- [x] Gold answer đều trích được từ corpus, không suy đoán chính sách.

### Metadata schema

| Trường | Kiểu | Ví dụ | Công dụng |
|---|---|---|---|
| `doc_id` | string | `warranty-seller-fbt-tiki` | Truy vết, cập nhật và xóa toàn bộ chunk của tài liệu. |
| `source_url` | string | URL trang chính sách | Kiểm chứng nguồn. |
| `retrieved_at` | ISO date | `2026-09-20` | Theo dõi độ mới. |
| `document_version` | string | `not-stated` | Ghi nhận phiên bản/hiệu lực mà nguồn công bố. |
| `audience` | enum | `buyer`, `seller` | Tránh truy xuất nhầm đối tượng. |
| `category` | string | `warranty-policy` | Phân loại nghiệp vụ. |
| `platform` | enum | `shopee`, `tiki` | Giới hạn theo sàn. |
| `fulfillment_model` | enum | `fbt`, `dropship`, `sd` | Giới hạn đúng quy trình vận hành. |
| `language` | string | `vi` | Định tuyến theo ngôn ngữ. |

## 2. Thiết kế chiến lược (15 điểm)

### Baseline trên ba tài liệu

Thông số chung: `chunk_size=500`; Fixed-size baseline dùng `overlap=0` trong comparator.

| Tài liệu | Chiến lược | Số chunk | Độ dài TB | Nhận xét |
|---|---|---:|---:|---|
| Shopee buyer | Fixed-size | 6 | 482,83 | Kích thước đều nhưng có thể cắt giữa câu. |
| Shopee buyer | Sentence | 9 | 320,00 | Mạch lạc theo câu, đôi lúc mang heading sang chunk khác. |
| Shopee buyer | Recursive | 8 | 360,38 | Ưu tiên đoạn/dòng/câu nên cân bằng độ dài và ngữ cảnh. |
| Tiki FAQ | Fixed-size | 7 | 472,00 | Có nguy cơ trộn hai câu hỏi FAQ. |
| Tiki FAQ | Sentence | 11 | 298,00 | Chunk nhỏ, dễ đọc. |
| Tiki FAQ | Recursive | 9 | 365,33 | Giữ đoạn tốt hơn fixed-size. |
| Tiki FBT | Fixed-size | 4 | 410,25 | Ít chunk nhưng có ranh giới cơ học. |
| Tiki FBT | Sentence | 5 | 326,00 | Giữ câu hoàn chỉnh. |
| Tiki FBT | Recursive | 4 | 408,75 | Giữ cấu trúc đoạn tương đối tốt. |

### Các cấu hình được so sánh

| Cấu hình | Chiến lược | Tham số | Lý do |
|---|---|---|---|
| A | Fixed-size | 500 ký tự, overlap 50 | Baseline có overlap để giảm mất ngữ cảnh ở biên. |
| B | Sentence | 3 câu/chunk | Phù hợp các điều khoản viết thành câu đầy đủ. |
| C | Recursive | 500 ký tự | Ưu tiên đoạn, dòng, câu rồi từ. |
| D | Heading custom | Tách heading, recursive nếu section >500 | Khai thác cấu trúc Markdown và đáp ứng yêu cầu chunk theo heading/section. |
| Thành viên 2 | `HeadingChunker` | Tách nguyên mục theo heading `##`/`###`, không fallback theo kích thước | Giữ mỗi điều khoản gốc thành một đơn vị hoàn chỉnh. |
| Thành viên 3 | `RecursiveChunker` | 500 ký tự, separator `\n\n`, `\n`, `. `, khoảng trắng, ký tự | Cân bằng ranh giới cấu trúc và kích thước; là lựa chọn mặc định được Nguyễn Khánh Linh kết luận trong báo cáo thử nghiệm. |

`HeadingChunker` được cài trong `bench.py`: regex tìm heading Markdown, tạo section rồi dùng `RecursiveChunker` làm fallback cho section quá dài.

### Kết quả chính bằng NVIDIA Nemotron

Backend retrieval: NVIDIA API, model `nvidia/nemotron-3-embed-1b`, vector 2048 chiều. Tài liệu được embed với `input_type=passage`, câu hỏi với `input_type=query`. Agent dùng Google `gemini-3.5-flash-lite`, chỉ trả lời từ top-3 context và trích số nguồn. Cách chấm: 2 điểm khi gold chunk ở top-1 và Agent đúng; 1 điểm khi gold chunk chỉ ở top-3 nhưng Agent vẫn đúng; 0 điểm khi không có gold chunk.

| Chiến lược | Chunk | Độ dài TB | Unfiltered | Filtered | Điểm mạnh | Điểm yếu |
|---|---:|---:|---:|---:|---|---|
| Fixed-size | 29 | 459,14 | 7/10 | 7/10 | Đơn giản, kích thước ổn định | Có thể cắt giữa từ/câu; thất bại ở Q1. |
| Sentence — thành viên 1 | 35 | 344,03 | 6/10 | 6/10 | Câu hoàn chỉnh, dễ đọc | Heading và nội dung có thể bị tách; Q1 thất bại. |
| Recursive | 34 | 354,62 | 3/10 | 4/10 | Cân bằng cấu trúc và kích thước | Một số gold chunk không lọt top-3. |
| Heading + recursive | 36 | 334,81 | 8/10 | 8/10 | Bám cấu trúc chính sách và giới hạn section dài | Q1 và Q5 chỉ đạt top-3, chưa top-1. |
| Heading — thành viên 2 | 23 | 525,17 | 7/10 | 8/10 | Ít chunk, giữ nguyên mục chính sách | Section dài có thể gộp nhiều ý. |
| Recursive — thành viên 3 | 34 | 354,62 | 3/10 | 4/10 | Giữ ranh giới đoạn/dòng trước khi tách nhỏ | Trùng cấu hình recursive baseline. |

Hai cấu hình heading cùng đạt 8/10 sau filter. `Heading + recursive` ổn định hơn một chút vì đạt 8/10 ngay cả khi không filter, trong khi Heading thành viên 2 tăng từ 7/10 lên 8/10 nhờ filter. Baseline MockEmbedder thấp hơn nhiều: điểm filtered tương ứng của sáu cấu hình là 2, 1, 0, 2, 4 và 0; chi tiết nằm trong `ket_qua_benchmark.txt`.

### Thành viên 2 — Ngô Lê Thuỳ Tiên (`2A202602614`)

- **Repo:** [K4-DAY07-NgoLeThuyTien-2A202602614](https://github.com/tiennl/K4-DAY07-NgoLeThuyTien-2A202602614)
- **Chiến lược:** custom `HeadingChunker`, tách theo heading Markdown cấp `##`/`###`.
- **Lý do:** tài liệu chính sách dùng heading làm ranh giới điều khoản; giữ heading và nội dung trong cùng chunk giúp bảo toàn điều kiện, thời hạn và hậu quả.
- **Kết quả chạy lại bằng Nemotron:** 23 chunk, độ dài trung bình 525,17; 7/10 không filter và 8/10 có filter.

### Thành viên 3 — Nguyễn Khánh Linh (2A202602409)

- **Repo:** [K4-L3B-Data-Foundations-Nguyen-Khanh-Linh](https://github.com/klinhnguyen2012/K4-L3B-Data-Foundations-Nguyen-Khanh-Linh)
- **Chiến lược:** `RecursiveChunker(chunk_size=500)` với thứ tự separator mặc định: đoạn trống, xuống dòng, dấu chấm, khoảng trắng rồi ký tự.
- **Lý do:** ưu tiên ranh giới cấu trúc lớn trước, chỉ tách nhỏ hơn khi cần; phù hợp tài liệu chính sách có cả đoạn văn, danh sách và FAQ.
- **Kết quả chạy lại bằng Nemotron:** 34 chunk, độ dài trung bình 354,62; 3/10 không filter và 4/10 có filter.
## 3. Benchmark queries và retrieval quality (10 điểm)

### Bộ câu hỏi và gold answer

| # | Query | Gold answer | Chunk nguồn |
|---|---|---|---|
| 1 | Người mua cần giấy tờ gì để được bảo hành miễn phí trên Shopee? | Hóa đơn điện tử hoặc mã đơn hàng; đồ điện gia dụng cần phiếu/tem bảo hành nguyên vẹn. | `warranty-buyer-shopee`, mục 1 |
| 2 | Nhà Bán Tiki không xác nhận phương án trong 02 ngày thì sao? | Tiki xử lý theo yêu cầu khách hàng và có thể từ chối khiếu nại phát sinh sau hạn. | `warranty-seller-general-tiki`, Câu 4 |
| 3 | Với FBT, Nhà Bán phải rút hàng lỗi không đủ điều kiện nhập kho trong bao lâu? | 32 ngày làm việc kể từ khi phiếu trả hàng được tạo. | `warranty-seller-fbt-tiki`, Bước 1–2 |
| 4 | Với Dropship, nếu từ chối xử lý thì Nhà Bán phải cung cấp bằng chứng trong bao lâu? | 02 ngày làm việc kể từ khi nhận yêu cầu hoàn tiền hoặc nhận sản phẩm. | `warranty-seller-dropship-tiki`, mục I |
| 5 | Với SD, Tiki xử lý và quyết định khiếu nại trong bao lâu? | 02–07 ngày làm việc. | `warranty-seller-sd-tiki`, mục II |


### Kết quả tốt nhất theo từng query bằng Nemotron

| # | Chiến lược tốt nhất hiện tại | Gold chunk trong top-3? | Điểm | Ghi chú |
|---|---|---|---:|---|
| 1 | Heading + recursive / Heading thành viên 2 | Có nhưng không ở top-1 | 1 | Gold chunk xuất hiện trong top-3 nhưng phần thời gian bảo hành được xếp trước. |
| 2 | Heading + recursive / Heading thành viên 2 / Sentence / Fixed-size | Có ở top-1 | 2 | Model đưa đúng Câu 4 của FAQ lên đầu. |
| 3 | Fixed-size / hai cấu hình Heading | Có ở top-1 | 2 | Chunk chứa “32 ngày làm việc” và “phiếu trả hàng” lên top-1. |
| 4 | Nhiều cấu hình | Có ở top-1 | 2 | Query và chunk cùng nêu từ chối xử lý, bằng chứng hợp lệ và 02 ngày. |
| 5 | Fixed-size / Sentence / hai cấu hình Heading | Có nhưng không ở top-1 | 1 | Gold chunk 02–07 ngày có trong top-3 nhưng chưa đứng đầu. |

**Tổng tốt nhất ghép theo query:** 8/10.

Gemini Agent của cấu hình Heading + recursive trả lời đúng cả 5 gold answer và trích nguồn `[1]`/`[2]`. Q1 và Q5 vẫn nhận 1 điểm vì gold chunk chỉ nằm trong top-3, không phải top-1. Output nguyên văn được lưu tại `ket_qua_agent_gemini.txt`.

### Phân tích A/B metadata filtering

Với Nemotron, query đã đủ cụ thể nên Fixed-size, Sentence và Heading + recursive không đổi điểm sau filter. Filter giúp Recursive và cấu hình thành viên 3 tăng từ 3 lên 4, đồng thời giúp Heading thành viên 2 tăng từ 7 lên 8 bằng cách loại tài liệu sai mô hình vận hành. Filter vẫn có rủi ro loại mất gold chunk nếu metadata sai hoặc điều kiện lọc quá hẹp.
### Failure analysis

- **Failure Q1:** model ưu tiên phần thời gian/liên hệ bảo hành thay vì điều kiện giấy tờ; gold chunk chỉ vào top-3 ở hai cấu hình heading.
- **Failure Q5:** model nhận đúng tài liệu SD nhưng xếp phần cam kết vận hành trước chunk 02–07 ngày.
- **Cải tiến:** gắn heading cha vào mọi subchunk, thêm `platform` vào filter khi query nêu rõ sàn, và thử chunk size 300–400 để giảm section chứa nhiều ý.

## 4. Demo và bài học nhóm (5 điểm)

### Kịch bản demo 6–8 phút

1. Giới thiệu corpus và metadata.
2. So sánh bốn chiến lược bằng số chunk và độ dài trung bình.
3. Chạy `bench.py` với Q5 để thể hiện filter cải thiện Heading thành viên 2 từ 0 lên 1 điểm ở query này.
4. Giải thích failure case Q1 và Q5 của Nemotron.
5. So sánh Nemotron với MockEmbedder trên cùng corpus/query.

### Insight chính

- Metadata tốt có thể cứu retrieval bằng cách loại bỏ sai đối tượng và sai mô hình vận hành.
- Chunk mạch lạc chưa đảm bảo retrieval tốt nếu embedding không biểu diễn ngữ nghĩa.
- Benchmark phải giữ corpus, query và backend cố định khi so sánh chunking.

### Nếu làm lại

Nhóm dùng hai tầng: MockEmbedder để kiểm thử contract và NVIDIA Nemotron để đánh giá retrieval thật. Metadata schema vẫn được giữ, nhưng filter sẽ bổ sung `platform` khi query nêu rõ Shopee/Tiki; heading chunker sẽ gắn tiêu đề vào mọi subchunk sau khi section bị chia.

## Tự đánh giá hiện tại

| Tiêu chí | Điểm hiện tại |
|---|---:|
| Lựa chọn tài liệu | 10 / 10 |
| Thiết kế chiến lược | 15 / 15 |
| Retrieval Nemotron + Gemini Agent | 8 / 10 |
| Demo thực tế | 5 |
| **Tổng trước demo** | **38 / 40** |