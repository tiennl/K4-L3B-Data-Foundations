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

Chạy `ChunkingStrategyComparator().compare(text, chunk_size=300)` trên 3 tài liệu (nội dung sau front matter, không tính khối YAML):

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `warranty-seller-general-tiki` (3304 ký tự) | FixedSizeChunker (`fixed_size`) | 13 | 281.8 | Không — cắt cứng theo ký tự, có thể đứt giữa câu/giữa "Câu hỏi — trả lời" |
| `warranty-seller-general-tiki` | SentenceChunker (`by_sentences`) | 11 | 298.0 | Một phần — giữ trọn câu, nhưng 1 "Câu hỏi" gốc thường gồm 2-4 câu nên vẫn có thể bị tách sang 2 chunk |
| `warranty-seller-general-tiki` | RecursiveChunker (`recursive`) | 19 | 172.0 | Một phần — ưu tiên tách theo `\n\n`/`\n` nên bám sát đoạn văn hơn fixed-size, nhưng vẫn không biết ranh giới "Câu X." là một đơn vị |
| `warranty-seller-fbt-tiki` (1641 ký tự) | FixedSizeChunker | 6 | 298.5 | Không |
| `warranty-seller-fbt-tiki` | SentenceChunker | 5 | 326.0 | Một phần |
| `warranty-seller-fbt-tiki` | RecursiveChunker | 9 | 180.7 | Một phần |
| `warranty-buyer-shopee` (2897 ký tự) | FixedSizeChunker | 11 | 290.6 | Không |
| `warranty-buyer-shopee` | SentenceChunker | 9 | 320.0 | Một phần |
| `warranty-buyer-shopee` | RecursiveChunker | 14 | 205.2 | Một phần |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Ngô Lê Thuỳ Tiên**
- **Loại chiến lược:** custom — `HeadingChunker` (chunk theo tiêu đề `##`/`###`), đáp ứng yêu cầu bắt buộc của K4_VARIANT.md ("ít nhất một thành viên chunk theo tiêu đề/mục của điều khoản/chính sách gốc").
- **Mô tả & lý do chọn cho chủ đề này:** Mọi file trong `data/warranty-policy/` đều là Markdown có `##` đánh dấu rõ từng điều khoản gốc (`## Câu 4. ...`, `## II. Quy trình xử lý bảo hành FBT`). Một câu hỏi benchmark gần như luôn ứng với đúng **một** heading — chunk theo heading giữ nguyên vẹn cả điều kiện lẫn hậu quả của điều khoản đó trong cùng 1 chunk, trong khi 3 chiến lược có sẵn (dựa trên ký tự/câu) có thể cắt đứt chúng ra hai chunk khác nhau nếu ranh giới rơi giữa chừng.
- **Code snippet:**
```python
# scripts/heading_chunker.py
class HeadingChunker:
    """Chunk theo tiêu đề `##`/`###` — mỗi điều khoản gốc thành 1 chunk."""

    def __init__(self, heading_pattern: str = r"^#{2,3}\s+.+$") -> None:
        self.heading_re = re.compile(heading_pattern, re.MULTILINE)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        matches = list(self.heading_re.finditer(text))
        if not matches:
            return [text.strip()]

        chunks: list[str] = []
        preamble = text[: matches[0].start()].strip()
        if preamble:
            chunks.append(preamble)
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            section = text[start:end].strip()
            if section:
                chunks.append(section)
        return chunks
```
- **Kết quả trên baseline (3 tài liệu trên):** `warranty-seller-general-tiki` → 9 chunk (avg 365.3 ký tự), `warranty-seller-fbt-tiki` → 3 chunk (avg 545.7), `warranty-buyer-shopee` → 5 chunk (avg 577.8). Ít chunk hơn hẳn 3 chiến lược kia nhưng mỗi chunk là **một đơn vị chính sách hoàn chỉnh**, không cắt dở.
- **Chạy thử 5 câu benchmark (mục 3) với `HeadingChunker` + `_mock_embed`, so với baseline "1 file = 1 Document" (không chunk):**

| | Top-1 đúng | Có gold trong top-3 |
|---|---|---|
| Baseline (không chunk, `REPORT_CANHAN.md` mục 5) | 1/5 | 2/5 |
| `HeadingChunker` (23 chunk cho 5 file) | **3/5** | **4/5** |

  Chi tiết: câu 1 (filter buyer), 3 (FBT), 4 (Dropship) đúng top-1; câu 2 (general-tiki) có gold ở top-2; chỉ câu 5 (SD) vẫn miss hoàn toàn.
- **⚠️ Diễn giải — đừng vội kết luận "heading chunking thắng vì hiểu ngữ nghĩa":** `_mock_embed` băm MD5 toàn bộ chuỗi ký tự, không có khái niệm từ/ngữ nghĩa dù chunk to hay nhỏ. Một phần cải thiện 1/5→3/5 rất có thể chỉ là hiệu ứng thống kê: tách 5 tài liệu thành 23 chunk độc lập nghĩa là có **nhiều lượt "rút thăm" hơn**, nên xác suất một chunk đúng tình cờ có điểm dot-product cao hơn cũng tăng theo, không hẳn vì chunk nhỏ "đúng ngữ nghĩa" hơn. Muốn kết luận chắc chắn heading-chunking có lợi thật, cần chạy lại đúng bảng so sánh này với một embedder ngữ nghĩa thật (`LocalEmbedder`/`OpenAIEmbedder`/`GeminiEmbedder`) — việc này để lại cho các thành viên còn lại khi họ thêm chiến lược của mình.

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
| Ngô Lê Thuỳ Tiên | `HeadingChunker` (theo `##`/`###`) | 3/5 top-1, 4/5 top-3 (trên `_mock_embed`) | Giữ nguyên vẹn từng điều khoản; ít chunk hơn nên dễ đọc lại khi debug; cải thiện rõ so với baseline không chunk | Chunk to nhỏ không đều (219–1147 ký tự) vì phụ thuộc độ dài mục gốc; nếu 1 heading gộp nhiều ý (như `warranty-seller-fbt-tiki` mục II dài 1147 ký tự) thì vẫn có nguy cơ chunk quá lớn; cải thiện đo được có thể một phần do hiệu ứng thống kê của `_mock_embed`, chưa chắc là do hiểu ngữ nghĩa |
| | | | | |
| | | | | |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Chờ các thành viên còn lại điền chiến lược của họ rồi mới so sánh công bằng — hiện chỉ có 1/3 (tối thiểu) chiến lược được thử.*

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Người mua cần chuẩn bị giấy tờ gì để được bảo hành miễn phí trên Shopee? *(cần `metadata_filter={"audience": "buyer"}` — nếu không lọc, câu hỏi dễ bị 4 tài liệu phía seller "lấn" vì cùng dùng từ "bảo hành")* | Có hóa đơn điện tử (khi Người Mua có yêu cầu) hoặc mã đơn hàng (ID đơn hàng); sản phẩm còn trong thời hạn bảo hành và lỗi do nhà sản xuất; riêng đồ điện gia dụng cần phiếu/tem bảo hành còn nguyên vẹn. | `warranty-buyer-shopee.md`, mục "1. Điều kiện bảo hành" |
| 2 | Nếu Nhà Bán trên Tiki không xác nhận phương án xử lý bảo hành trong 2 ngày làm việc thì Tiki xử lý thế nào? | Tiki chủ động xử lý theo yêu cầu của khách hàng (hoàn tiền hoặc tạo đơn hàng mới để đổi hàng), đồng thời có quyền từ chối tiếp nhận các khiếu nại về đơn hàng liên quan của Nhà Bán phát sinh sau thời hạn này. | `warranty-seller-general-tiki.md`, "Câu 4" |
| 3 | Theo mô hình FBT, nếu hàng hóa bảo hành không đủ điều kiện nhập kho thì Nhà Bán có bao nhiêu ngày để rút hàng? | 32 ngày làm việc kể từ khi phiếu trả hàng được Tiki tạo. | `warranty-seller-fbt-tiki.md`, mục "II. Quy trình xử lý yêu cầu bảo hành FBT" (Bước 1–2) |
| 4 | Ở mô hình Dropship, nếu Nhà Bán từ chối xử lý đổi–trả–bảo hành thì phải cung cấp bằng chứng hợp lệ trong bao lâu? | Trong vòng 02 ngày làm việc kể từ khi nhận được yêu cầu hoàn tiền hoặc kể từ khi nhận sản phẩm từ đối tác vận chuyển (bằng chứng gồm biên bản bàn giao, biên bản đồng kiểm, hình ảnh/video đóng gói). | `warranty-seller-dropship-tiki.md`, mục "I. Quy định chung" |
| 5 | Ở mô hình SD, nếu Nhà Bán từ chối phương án xử lý, Tiki mất bao lâu để xác minh và ra quyết định cuối cùng? | 02–07 ngày làm việc (Tiki kiểm tra, xác minh chứng cứ/biên bản trước khi quyết định). | `warranty-seller-sd-tiki.md`, mục "II. Quy trình xử lý yêu cầu bảo hành" |

> Đã chạy thử cả 5 câu trên corpus thật với `_mock_embed` (xem `REPORT_CANHAN.md` mục 5) — kết quả: câu 1 (có filter) đúng ngay top-1; câu 3 đúng nhưng ở top-2; câu 2, 4, 5 **hoàn toàn không** có tài liệu đúng trong top-3 dù store chỉ có 5 tài liệu. Đây chính là "chất liệu" cho phần Failure Analysis (mục dưới) — nguyên nhân là `_mock_embed` không mang ngữ nghĩa (băm MD5) cộng với việc 4/5 tài liệu seller dùng chung rất nhiều từ vựng ("Nhà Bán", "bảo hành", "ngày làm việc"). Mỗi thành viên chạy lại đúng 5 câu này với chiến lược chunking + embedder riêng của mình để so sánh cải thiện được bao nhiêu so với baseline này.

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
