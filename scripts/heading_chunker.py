"""Custom chunking strategy for the warranty-policy corpus (Phase 2, K4-L3B).

Splits a markdown policy document on its `##` headings, so each clause of
the original policy (a numbered question, a "Bước", a "Điều") stays whole
in exactly one chunk instead of being cut at an arbitrary character or
sentence boundary.

Not part of the graded `src/` package (that only requires the 3 built-in
strategies + ChunkingStrategyComparator) — this is the "at least one member
must chunk by heading/section" strategy required by K4_VARIANT.md, run
standalone against the real corpus for Phase 2 comparison.
"""

from __future__ import annotations

import re


class HeadingChunker:
    """Chiến lược chia nhỏ tùy chỉnh cho corpus chính sách bảo hành.

    Lý do thiết kế: mọi file trong `data/warranty-policy/` đều là Markdown
    có tiêu đề `##` đánh dấu rõ từng điều khoản/câu hỏi gốc của chính sách
    (vd. "## Câu 4. ...", "## II. Quy trình xử lý bảo hành FBT"). Một câu
    hỏi benchmark thường ứng với đúng MỘT heading ("Nếu Nhà Bán không phản
    hồi trong 2 ngày thì sao?" == đúng "Câu 4"). Chunk theo `FixedSizeChunker`
    hay `SentenceChunker` có nguy cơ cắt đứt điều kiện khỏi hậu quả của nó
    (vd. tách "trong 02 ngày làm việc" khỏi phần "Tiki sẽ xử lý ra sao" ngay
    sau đó) nếu ranh giới rơi giữa chừng một điều khoản. Chunk theo heading
    giữ nguyên vẹn từng điều khoản, đúng đơn vị ngữ nghĩa mà benchmark cần.
    """

    def __init__(self, heading_pattern: str = r"^#{2,3}\s+.+$") -> None:
        self.heading_re = re.compile(heading_pattern, re.MULTILINE)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        matches = list(self.heading_re.finditer(text))
        if not matches:
            # No heading found (e.g. plain-text doc) -> whole text is one chunk.
            return [text.strip()]

        chunks: list[str] = []

        # Content before the first heading (title/intro paragraph) is its
        # own chunk if it carries anything beyond whitespace.
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
