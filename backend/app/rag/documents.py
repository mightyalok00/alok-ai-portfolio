from pathlib import Path


def load_documents(directory: str) -> list[str]:
    """WHY: Keep portfolio evidence in maintainable Markdown files."""
    root = Path(directory)
    if not root.is_absolute():
        root = Path(__file__).resolve().parents[1] / root
    return [p.read_text(encoding="utf-8") for p in sorted(root.glob("*.md"))] if root.exists() else []
