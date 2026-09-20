# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [Tên nhóm]
**Thành viên:** [Họ tên từng thành viên]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Chính sách bảo hành sản phẩm trên sàn thương mại điện tử (seller-warranty-policy)

**Tại sao nhóm chọn chủ đề này?**
> Bảo hành là điểm giao thoa rõ nhất giữa nghĩa vụ Người Bán và quyền lợi Người Mua trên sàn TMĐT, mỗi bên có tài liệu riêng với mốc thời gian, mức phạt cụ thể, rất phù hợp để kiểm tra `metadata_filter` theo `audience`. Nhóm chọn 2 sàn (Shopee cho phía người mua, Tiki cho phía người bán qua Học viện Tiki dành cho Nhà Bán) vì đây là hai nguồn chính thức duy nhất tìm được có nội dung server-side rendered (không rỗng do JavaScript) và đủ chi tiết số liệu.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Chính sách bảo hành cho sản phẩm mua tại Shopee (Người Mua) | [help.shopee.vn/.../79046](https://help.shopee.vn/4/article/79046-%5BQuy-%C4%91%E1%BB%8Bnh%5D-Ch%C3%ADnh-s%C3%A1ch-b%E1%BA%A3o-h%C3%A0nh-cho-s%E1%BA%A3n-ph%E1%BA%A9m-mua-t%E1%BA%A1i-Shopee) | 2026-09-20 / not-stated | 4212 | `audience: buyer`, `category: warranty-policy`, `language: vi`, `platform: shopee` |
| 2 | FAQ xử lý bảo hành dành cho Nhà Bán (Tiki) | [hocvien.tiki.vn/faq/cau-hoi-thuong-gap-ve-xu-ly-doi-tra-bao-hanh](https://hocvien.tiki.vn/faq/cau-hoi-thuong-gap-ve-xu-ly-doi-tra-bao-hanh/) | 2026-09-20 / not-stated | 4659 | `audience: seller`, `category: warranty-policy`, `language: vi`, `platform: tiki` |
| 3 | [Mô hình FBT] Hướng dẫn xử lý bảo hành (Tiki) | [hocvien.tiki.vn/faq/mo-hinh-fbt-...](https://hocvien.tiki.vn/faq/mo-hinh-fbt-huong-dan-quy-trinh-xu-ly-doi-tra-bao-hanh/) | 2026-09-20 / not-stated | 2516 | `audience: seller`, `category: warranty-policy`, `language: vi`, `platform: tiki`, `fulfillment_model: fbt` |
| 4 | [Mô hình Dropship] Hướng dẫn xử lý bảo hành (Tiki) | [hocvien.tiki.vn/faq/huong-dan-...-dropship](https://hocvien.tiki.vn/faq/huong-dan-quy-trinh-xu-ly-doi-tra-bao-hanh-mo-hinh-dropship/) | 2026-09-20 / not-stated | 3319 | `audience: seller`, `category: warranty-policy`, `language: vi`, `platform: tiki`, `fulfillment_model: dropship` |
| 5 | [Mô hình SD] Hướng dẫn xử lý bảo hành (Tiki) | [hocvien.tiki.vn/faq/huong-dan-...-sd](https://hocvien.tiki.vn/faq/huong-dan-quy-trinh-xu-ly-doi-tra-bao-hanh-mo-hinh-sd/) | 2026-09-20 / not-stated | 2990 | `audience: seller`, `category: warranty-policy`, `language: vi`, `platform: tiki`, `fulfillment_model: sd` |

> Toàn bộ 5 tài liệu đã qua bước làm sạch thủ công (bỏ menu điều hướng, banner, widget đánh giá bài viết, danh sách 60+ tên gian hàng phân phối) theo checklist `docs/DATA_COLLECTION.md` mục 2 — xem `data/warranty-policy/sources.csv` để đối chiếu 1-1 với từng file. Corpus được đặt trong thư mục riêng `data/warranty-policy/`, tách khỏi `data/ecommerce/` (nơi giữ nguyên 2 file mẫu gốc của repo — `return-refund-policy.md`, `seller-warranty-policy.md` — để tham khảo, không dùng làm dữ liệu chấm điểm). `document_version` ghi `not-stated` cho cả 5 file vì các trang nguồn không công bố số hiệu/ngày hiệu lực rõ ràng (khác với các trang đổi trả của Shopee có ghi ngày hiệu lực — nhưng các trang đó nằm ngoài phạm vi "chỉ bảo hành" nên nhóm không đưa vào corpus).

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng (help.shopee.vn, hocvien.tiki.vn — cả hai đều `Allow: /` trong `robots.txt`) và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata — đã xác nhận bằng script kiểm tra ở checkpoint 2 (`docs/DATA_COLLECTION.md` mục 6): 5/5 file OK, `sources.csv` khớp 1-1.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `audience` | enum | `buyer` \| `seller` | Bắt buộc theo K4_VARIANT — lọc đúng phía cần trả lời (vd. hỏi nghĩa vụ seller không bị lẫn với quyền lợi buyer, dù cả hai đều dùng chung từ "bảo hành"). |
| `category` | string | `warranty-policy` | Ở lab này mọi doc đều `warranty-policy` (đã cố tình thu hẹp phạm vi) — trường này để lại chỗ mở rộng nếu nhóm gộp thêm chủ đề khác sau này. |
| `platform` | string | `shopee` \| `tiki` | Phân biệt nguồn khi so sánh 2 sàn có số liệu khác nhau (vd. Shopee bảo hành nhà sản xuất 20–45 ngày vs Tiki 15–30 ngày). |
| `fulfillment_model` | string (chỉ có ở 3 file Tiki) | `fbt` \| `dropship` \| `sd` | Cùng là Tiki nhưng mốc thời gian/quy trình bảo hành khác nhau theo mô hình vận hành — filter theo trường này tránh trộn lẫn quy trình của 3 mô hình khi truy xuất. |
| `language` | string | `vi` | Toàn bộ corpus tiếng Việt; giữ trường này để nhất quán với `EmbeddingStore.search_with_filter` và mở rộng đa ngôn ngữ sau này. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| | FixedSizeChunker (`fixed_size`) | | | |
| | SentenceChunker (`by_sentences`) | | | |
| | RecursiveChunker (`recursive`) | | | |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — [Tên]**
- **Loại chiến lược:** [FixedSize / Sentence / Recursive / custom]
- **Mô tả & lý do chọn cho chủ đề này:** *(2-3 câu)*
- **Code snippet (nếu custom):**
```python
# Dán mã nguồn (implementation) vào đây
```

**Thành viên 2 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

**Thành viên 3 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| | | | | |
| | | | | |
| | | | | |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Viết 2-3 câu — đây là phần được đánh giá cao nhất (khả năng suy nghĩ & giải thích):*

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> *Viết 2-3 câu:*

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> *Liệt kê 2-3 ý:*

**Bài học rút ra khi so sánh trong nhóm:**
> *Viết 2-3 câu — cùng tài liệu nhưng chiến lược khác nhau dẫn tới khác biệt gì?*

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | / 10 |
| Thiết kế chiến lược (Strategy Design) | / 15 |
| Chất lượng truy xuất (Retrieval Quality) | / 10 |
| Thuyết trình (Demo) | / 5 |
| **Tổng phần nhóm** | **/ 40** |
