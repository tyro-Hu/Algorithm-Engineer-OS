"""M1：数据清洗 + 分块，并比较不同 chunk size 的效果。

用法：
    python scripts/data_prep.py --docs data/docs --sizes 300 500 800

做了什么：
    - 读取 data/docs 下的 txt / md，折叠多余空白与换行
    - 用不同 chunk_size 分块，输出块数与平均字数
    - 把清洗后的文档和各组块落盘，供下一步 Embedding / 建库用
"""

import argparse
import json
from pathlib import Path


def read_docs(docs_dir: Path) -> list[dict]:
    """读取目录下所有 txt/md，做基础清洗，返回 [{source, text}]。"""
    out = []
    for p in docs_dir.rglob("*"):
        if p.suffix.lower() not in {".txt", ".md"}:
            continue
        raw = p.read_text(encoding="utf-8", errors="ignore")
        # 折叠所有连续空白/换行，让文档更规整（注意：会丢掉原有换行结构）
        cleaned = " ".join(raw.split())
        out.append({"source": str(p.relative_to(docs_dir)), "text": cleaned})
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="清洗并分块知识库文档")
    ap.add_argument("--docs", default="data/docs", help="原始文档目录")
    ap.add_argument("--sizes", type=int, nargs="+", default=[300, 500, 800],
                    help="要对比的 chunk_size 列表")
    args = ap.parse_args()

    docs = read_docs(Path(args.docs))
    print(f"清洗后共 {len(docs)} 篇文档")

    # 使用 LangChain 的分块器，按语义停顿（段落/换行/句号）优先切分
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    all_chunks: dict[int, list[str]] = {}
    for size in args.sizes:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=size,
            chunk_overlap=int(size * 0.15),  # 15% 重叠，避免切断关键句
            separators=["\n\n", "\n", "。", "！？", " "],
        )
        # 对每篇文档分块，再合并成这一组的所有块
        chunks = [c for d in docs for c in splitter.split_text(d["text"])]
        avg = sum(len(c) for c in chunks) / max(len(chunks), 1)
        all_chunks[size] = chunks
        print(f"chunk_size={size}: {len(chunks)} 块, 平均 {avg:.0f} 字")

    out_dir = Path("data")
    out_dir.mkdir(exist_ok=True)
    json.dump(docs, open(out_dir / "cleaned.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    for size, chunks in all_chunks.items():
        json.dump(chunks, open(out_dir / f"chunks_{size}.json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
    print(f"已输出 data/cleaned.json 与 data/chunks_*.json（共 {len(all_chunks)} 组）")


if __name__ == "__main__":
    main()
