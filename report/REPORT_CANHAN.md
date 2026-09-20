# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Ngô Lê Thuỷ Tiên

**Nhóm:** Skynet

**Ngày:** 2026-09-20

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector embedding trỏ gần như cùng một hướng trong không gian nhiều chiều — nói cách khác, hai đoạn văn bản mang **ý nghĩa/ngữ cảnh gần giống nhau** theo cách mô hình embedding biểu diễn, dù cách dùng từ có thể khác nhau (paraphrase).

**Ví dụ có độ tương tự CAO:**
- Câu A: "Nhà Bán phải phản hồi yêu cầu bảo hành trong 2 ngày làm việc."
- Câu B: "Người bán cần trả lời khiếu nại bảo hành trong vòng hai ngày làm việc."
- Tại sao tương đồng: Cùng một sự kiện (nghĩa vụ phản hồi bảo hành) và cùng một con số (2 ngày), chỉ khác cách diễn đạt — với một embedder ngữ nghĩa thật, hai câu này nên có cosine similarity rất gần 1.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Chính sách bảo hành áp dụng cho sản phẩm điện tử được mua trên Shopee."
- Câu B: "Hôm nay thời tiết Hà Nội khá lạnh."
- Tại sao khác: Không có chủ đề, thực thể hay ý định chung nào — một embedder ngữ nghĩa thật nên cho cosine similarity gần 0.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine chỉ so sánh **hướng** của vector, bỏ qua độ dài (magnitude) — mà độ dài của embedding thường bị ảnh hưởng bởi độ dài văn bản/tần suất từ chứ không phản ánh ý nghĩa. Euclidean distance lại nhạy với độ dài này, nên hai đoạn văn dài-ngắn khác nhau dù cùng ý nghĩa vẫn có thể bị coi là "xa nhau" một cách sai lệch.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Trình bày phép tính: `số chunk = ceil((10000 − 50) / (500 − 50)) = ceil(9950 / 450) = ceil(22.11) = 23`
> Đáp án: **23 chunks**.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> `ceil((10000 − 100) / (500 − 100)) = ceil(9900 / 400) = ceil(24.75) = 25` chunks — tăng từ 23 lên **25** (nhiều hơn 2 chunk). Overlap lớn hơn giúp giảm rủi ro một câu/thông tin quan trọng bị cắt đúng vào ranh giới giữa hai chunk (mất ngữ cảnh cho cả hai phía); đánh đổi là nhiều chunk hơn → tốn thêm dung lượng lưu trữ và có nội dung trùng lặp giữa các chunk liền kề.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng `re.split(r"(?<=[.!?])\s+", text)` — lookbehind giữ lại dấu câu ở cuối mỗi câu thay vì tách rời nó ra (đã kiểm chứng: `"Đây là câu một. Đây là câu hai!"` → `["Đây là câu một.", "Đây là câu hai!"]`, không mất dấu chấm/chấm than), rồi `strip()` và loại bỏ phần tử rỗng (edge case: văn bản mẫu kết thúc bằng dấu cách sau dấu chấm sinh ra một phần tử rỗng ở cuối nếu không lọc). Sau đó nhóm `max_sentences_per_chunk` câu liên tiếp lại bằng cách duyệt theo bước nhảy (`range(0, len(sentences), max_sentences_per_chunk)`) và nối bằng khoảng trắng.
>
> **Edge case chưa xử lý được (đã kiểm chứng, không giấu):** chữ viết tắt có dấu chấm theo sau bởi khoảng trắng + chữ hoa sẽ bị tách nhầm thành "câu" riêng — test thực tế: `SentenceChunker(max_sentences_per_chunk=1).chunk("TS. Nguyễn Văn A là tác giả.")` trả về `["TS.", "Nguyễn Văn A là tác giả."]` thay vì giữ nguyên một câu. Ngược lại, số thập phân kiểu `"19.99"` **không** bị ảnh hưởng trong cách viết thông thường vì không có khoảng trắng ngay sau dấu chấm nội bộ của số (regex chỉ tách khi có `\s+` theo sau `[.!?]`) — đã kiểm chứng với câu `"Giá sản phẩm là 19.99 USD, khá cao."` không bị cắt sai. Rủi ro thật sự nằm ở các chữ viết tắt tiếng Việt/tiếng Anh có dấu chấm (`TS.`, `ThS.`, `Q.3`, `TP.HCM`, `vs.`...), không phải số thập phân như suy đoán ban đầu.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> `chunk()` trả về ngay `[text]` nếu văn bản đã đủ ngắn (base case), ngược lại gọi `_split` với danh sách separator gốc. `_split` cũng có base case tương tự (đoạn đủ ngắn) và base case khi hết separator hoặc gặp separator rỗng `""` (cắt cứng theo `chunk_size`). Với separator hiện tại, nó `split()` văn bản rồi **gộp các phần liền kề lại** (nối bằng đúng separator đã tách) cho tới sát `chunk_size`; phần nào tự nó vẫn quá dài mới đệ quy tiếp với `separators[1:]` — danh sách separator co dần đảm bảo đệ quy luôn kết thúc. Việc gộp lại (thay vì giữ nguyên từng mảnh nhỏ do `split()` sinh ra) là điểm quan trọng để chunk không bị vụn thành từng từ một.

### Lớp EmbeddingStore

> `EmbeddingStore` chỉ dùng **in-memory** (`self._store: list[dict]`) — bản đầu có thử khởi tạo `chromadb.Client()` khi thư viện có sẵn, nhưng đã **bỏ hẳn nhánh đó** ở checkpoint 4: không test nào cần Chroma, `requirements.txt` không cài nó, và vì `search`/`search_with_filter`/`delete_document` chỉ đọc từ `self._store` nên nhánh Chroma dù có khởi tạo thành công cũng là code chết — chỉ thêm rủi ro nếu máy chấm tình cờ có `chromadb` cài sẵn (import chậm hơn, có thể lỗi ghi file cục bộ trong môi trường sandbox) mà không mang lại lợi ích gì.

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi `Document` được embed một lần qua `self._embedding_fn` và đóng gói thành một record `{id, content, embedding, metadata}` rồi append vào `self._store` — `id` nội bộ là `f"{doc.id}#{self._next_index}"` (tăng dần) để **không dedupe** khi add cùng `doc.id` nhiều lần (test `test_add_more_increases_further` yêu cầu size cộng dồn), còn `metadata["doc_id"]` được gán lại từ `doc.id` để `delete_document` sau này có chỗ khớp — quan trọng ở CP5 khi một file được chunk thành nhiều `Document` dạng `"file#0"`, `"file#1"`... thì `doc_id` phải luôn trỏ về **file gốc**, không phải id riêng của từng chunk. `search` embed câu hỏi một lần, tính `_dot(query_embedding, record["embedding"])` cho từng record qua helper dùng chung `_search_records`, sort giảm dần theo score rồi cắt `top_k`; kết quả trả về **không** kèm vector embedding (chỉ `id/content/metadata/score`) để không làm bẩn output khi in ra terminal.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> **Lọc trước, tìm kiếm sau** — đây là câu hỏi checkpoint 4 cảnh báo trước, nên giải thích rõ lý do: `search_with_filter` duyệt `self._store`, giữ lại record nào khớp **mọi** cặp key/value trong `metadata_filter`, rồi mới chạy `_search_records` (search + cắt `top_k`) trên tập **đã lọc**. Nếu làm ngược lại — `search()` lấy top-k trước rồi mới lọc bỏ record không khớp — thì có thể mất trắng kết quả dù store vẫn còn tài liệu hợp lệ: ví dụ `top_k=3` mà cả 3 vị trí đầu bảng xếp hạng đều thuộc `audience: seller`, trong khi tài liệu `audience: buyer` phù hợp lại xếp hạng 4 trở đi — lọc sau khi đã cắt top-3 sẽ trả về danh sách rỗng thay vì tài liệu buyer đó. `search_with_filter(..., metadata_filter=None)` bỏ qua bước lọc, dùng toàn bộ `self._store` (test `test_no_filter_returns_all_candidates` yêu cầu kết quả bằng `search()` bình thường). `delete_document` so `len(self._store)` trước/sau khi lọc bỏ mọi record có `metadata["doc_id"] == doc_id`, trả `True` nếu size giảm.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Ba nhịp đúng theo docstring: (1) `store.search(question, top_k)` lấy các chunk liên quan; (2) build prompt dạng đánh số `[1] (source: doc_id) nội dung chunk`, `[2] ...` — gắn nhãn nguồn vào mỗi đoạn **và** yêu cầu model trích dẫn lại đúng số `[n]` đó cho từng luận điểm trong câu trả lời, để câu trả lời truy vết ngược được về đúng chunk/đúng file (tiêu chí "Source Traceability" trong `docs/EVALUATION.md`); (3) gọi `llm_fn(prompt)`. Prompt còn có ràng buộc chống bịa: "chỉ trả lời dựa trên context, không có thì nói rõ, không được tự suy đoán thêm". Nếu `store.search` trả về rỗng (chưa nạp tài liệu nào), trả thẳng một câu báo không có context thay vì gọi `llm_fn` vô ích với prompt trống.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
$ pytest tests/ -v
============================= test session starts ==============================
platform darwin -- Python 3.11.4, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/thuytien/Code/vinai/K4-L3B-Data-Foundations
collecting ... collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED

============================== 42 passed in 0.03s ==============================
```

**Số lượng bài test vượt qua (pass):** **42** / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Chạy `compute_similarity()` (dùng `_mock_embed`, backend mặc định của lab) trên 5 cặp câu tự chọn quanh chủ đề bảo hành, dự đoán trước rồi mới chạy:

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Người bán phải bảo hành sản phẩm trong tối đa 30 ngày. | Thời gian bảo hành tối đa của người bán là 30 ngày. | cao (paraphrase) | **0.1083** | Đúng hướng — là điểm cao nhất trong 5 cặp |
| 2 | Người mua có quyền yêu cầu bảo hành khi sản phẩm lỗi kỹ thuật. | Con mèo của tôi rất thích ngủ trên ghế sofa. | thấp (không liên quan) | **0.0808** | Sai — cao hơn cả cặp 3 và 4 dù chủ đề hoàn toàn khác nhau |
| 3 | Nhà Bán phải phản hồi trong 2 ngày làm việc. | Nhà Bán cần trả lời trong vòng hai ngày làm việc. | cao (paraphrase gần như y hệt) | **-0.1648** | Sai hoàn toàn — là điểm **thấp nhất** trong cả 5 cặp |
| 4 | Chính sách bảo hành áp dụng cho sản phẩm điện tử. | Hôm nay thời tiết Hà Nội khá lạnh. | thấp (không liên quan) | **-0.1321** | Đúng hướng — điểm thấp thứ nhì |
| 5 | Thời hạn bảo hành được tính từ ngày mua hàng. | Thời hạn bảo hành được tính từ ngày nhận được sản phẩm. | cao (cùng chủ đề, khác chi tiết) | **0.0953** | Đúng hướng — điểm cao thứ nhì |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Bất ngờ nhất là **cặp 3**: hai câu gần như là bản dịch nguyên văn của nhau ("phản hồi trong 2 ngày" vs "trả lời trong vòng hai ngày") lại có cosine similarity **âm và thấp nhất trong cả 5 cặp** — thấp hơn cả cặp với "con mèo ngủ trên sofa" hoàn toàn lạc đề. Điều này cho thấy `_mock_embed` (dùng MD5 hash của chuỗi ký tự làm seed sinh vector giả ngẫu nhiên) **không mã hoá ngữ nghĩa** — nó chỉ tạo ra một vector "vân tay" khác nhau cho mỗi chuỗi ký tự khác nhau, kể cả khi hai chuỗi đó diễn đạt cùng một ý. Cosine similarity giữa hai vector ngẫu nhiên độc lập trong không gian 64 chiều dao động quanh 0 bất kể nội dung — đúng như 5 kết quả đo được (tất cả đều nằm trong khoảng [-0.17, 0.11], không có cặp nào tiệm cận 1.0 như một embedder ngữ nghĩa thật sẽ cho ra với cặp paraphrase). Đây là lời nhắc quan trọng cho Giai đoạn 2: benchmark chạy trên `_mock_embed` chỉ kiểm tra được **luồng code** (đúng interface, đúng kiểu dữ liệu), không kiểm tra được **chất lượng truy xuất** — muốn đánh giá chunking/metadata thật sự tốt hơn, nhóm cần bật `LocalEmbedder`/`OpenAIEmbedder`/`GeminiEmbedder`.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Người mua cần chuẩn bị giấy tờ gì để được bảo hành miễn phí trên Shopee? *(lọc `audience: buyer`)* | `warranty-buyer-shopee`: "...có hóa đơn điện tử (khi Người Mua có yêu cầu) hoặc mã đơn hàng..." | -0.0387 | ✅ Có — đúng tài liệu, nhờ filter chỉ còn 1 ứng viên | *(xem ghi chú bên dưới)* |
| 2 | Nếu người bán trên Tiki không xác nhận phương án xử lý bảo hành trong 2 ngày làm việc thì chuyện gì xảy ra? | `warranty-buyer-shopee`: "...Sản phẩm được bảo hành miễn phí nếu..." | 0.0587 | ❌ Không — tài liệu đúng (`warranty-seller-general-tiki`) vắng mặt hoàn toàn trong top-3 | *(xem ghi chú bên dưới)* |
| 3 | Theo mô hình FBT, nếu hàng hóa bảo hành không đủ điều kiện nhập kho thì người bán có bao nhiêu ngày để rút hàng? | `warranty-seller-sd-tiki`: "...Nhà Bán bảo hành hàng hóa đúng như quy định (15–30 ngày)..." | 0.1211 | 🟡 Một phần — tài liệu đúng (`warranty-seller-fbt-tiki`) có mặt nhưng ở **top-2**, không phải top-1 | *(xem ghi chú bên dưới)* |
| 4 | Ở mô hình Dropship, nếu người bán từ chối yêu cầu bảo hành thì phải cung cấp bằng chứng trong bao lâu? | `warranty-seller-fbt-tiki`: "...Nhà Bán cần sắp xếp rút hàng trong 32 ngày làm việc..." | 0.1503 | ❌ Không — tài liệu đúng (`warranty-seller-dropship-tiki`) vắng mặt hoàn toàn trong top-3 | *(xem ghi chú bên dưới)* |
| 5 | Ở mô hình SD, nếu người bán từ chối phương án xử lý, Tiki mất bao lâu để ra quyết định cuối cùng? | `warranty-seller-dropship-tiki`: "...cung cấp bằng chứng hợp lệ trong vòng 02 ngày làm việc..." | 0.0642 | ❌ Không — tài liệu đúng (`warranty-seller-sd-tiki`) vắng mặt hoàn toàn trong top-3 | *(xem ghi chú bên dưới)* |

> **Ghi chú về cột "Câu trả lời của Agent":** `llm_fn` dùng ở đây là hàm demo (`lambda prompt: f"[DEMO LLM] {prompt[:180]}..."`), không phải LLM thật — nó chỉ echo lại 180 ký tự đầu của prompt để xác nhận `KnowledgeBaseAgent.answer` build prompt đúng cấu trúc (đánh số, gắn nhãn nguồn). Bảng trên vì vậy chỉ đánh giá được **độ chính xác của bước retrieval**, chưa đánh giá được chất lượng câu trả lời cuối — muốn có cột "câu trả lời" thật cần cắm một LLM thật (`llm_fn` gọi OpenAI/Gemini) vào `Agent`.

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **2** / 5 (câu 1 và câu 3; câu 3 chỉ ở hạng 2 chứ không phải top-1)

**Phân tích nhanh (đầy đủ hơn ở `REPORT_NHOM.md` mục 3 — Failure analysis):**
> 3/5 câu hỏi (câu 2, 4, 5) truy xuất trật hoàn toàn dù kho chỉ có vỏn vẹn 5 tài liệu — tệ hơn xác suất ngẫu nhiên (top-3/5 tài liệu lẽ ra phải "trúng" ~60% theo lý thuyết nếu chọn ngẫu nhiên). Nguyên nhân kép: (1) `_mock_embed` không mang ngữ nghĩa (đã thấy rõ ở mục 4), và (2) 4/5 tài liệu đều là hướng dẫn xử lý bảo hành của Tiki cho 3 mô hình vận hành khác nhau (FBT/Dropship/SD) — dùng chung rất nhiều từ vựng ("Nhà Bán", "bảo hành", "ngày làm việc") nên ngay cả một embedder từ-khóa đơn giản cũng khó phân biệt; cần một embedder ngữ nghĩa thật và/hoặc chunk theo heading (tách rõ từng mô hình vận hành) mới có cơ hội truy đúng.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
- **Backend embedding quyết định nhiều hơn chiến lược chunking.** Cùng một `SentenceChunker`, điểm nhảy từ 1/10 với MockEmbedder lên 6/10 với Nemotron — khớp đúng điều tôi tự đo được ở mục 4: `_mock_embed` chỉ là "vân tay" của chuỗi ký tự, nên mọi kết luận về chunking rút ra trên mock đều không đáng tin.
- **So sánh chỉ có nghĩa khi mọi biến số khác được giữ cố định:** chung corpus, chung 5 câu hỏi, chung backend, chung cách chấm. Gom tất cả chiến lược về một harness duy nhất là điều kiện tiên quyết, không phải chi tiết kỹ thuật phụ.
- **Ranh giới heading nên đi kèm trần kích thước.** `HeadingChunker` thuần của tôi phải nhờ metadata filter mới lên 8/10 (7/10 khi không filter), trong khi bản heading có fallback recursive đạt 8/10 ngay cả khi không filter. Chunk của tôi trung bình 525,17 ký tự — dài nhất nhóm — nên một mục chính sách dài bị dồn nhiều ý vào cùng một vector và bị pha loãng.
- **"Lựa chọn an toàn" không tự động là lựa chọn đúng.** `RecursiveChunker` là default tổng quát hợp lý nhưng lại thấp nhất trên corpus này (3/10, lên 4/10 sau filter). Chiến lược nên bám cấu trúc thật của tài liệu — ở đây heading chính là ranh giới điều khoản — chứ không chọn theo thói quen.


---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 (42/42 test pass) |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 6 / 10 — chạy trên mã nguồn cá nhân với MockEmbedder: retrieval sai nhiều (2/5 đúng) nhưng đã chạy đủ 5 câu hỏi và phân tích đúng nguyên nhân |
| **Tổng phần cá nhân** | **56 / 60** |
