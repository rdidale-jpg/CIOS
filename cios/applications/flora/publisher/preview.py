"""Generate PNG previews for the latest Flora Morning Edition PDF."""
from __future__ import annotations

from pathlib import Path

from cios.applications.flora.publisher.morning_edition import PUBLICATIONS_DIR, write_pilot_package

OPTIONAL_DEPENDENCY_MESSAGE = (
    "PDF preview generation requires the optional dependency PyMuPDF. "
    "Install it with `pip install PyMuPDF` to enable PNG rendering."
)


def latest_morning_edition_pdf(publications_dir: Path = PUBLICATIONS_DIR) -> Path:
    pdfs = sorted(publications_dir.glob("Morning_Edition_*.pdf"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not pdfs:
        raise FileNotFoundError(f"No Morning Edition PDF found in {publications_dir}")
    return pdfs[0]


def generate_previews(pdf_path: Path | None = None, publications_dir: Path = PUBLICATIONS_DIR) -> list[Path]:
    pdf_path = pdf_path or latest_morning_edition_pdf(publications_dir)
    previews_dir = publications_dir / "previews"
    previews_dir.mkdir(parents=True, exist_ok=True)

    try:
        import fitz  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError(OPTIONAL_DEPENDENCY_MESSAGE) from exc

    created: list[Path] = []
    document = fitz.open(str(pdf_path))
    try:
        for index, page in enumerate(document, start=1):
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            output_path = previews_dir / f"page-{index:02d}.png"
            pixmap.save(str(output_path))
            created.append(output_path)
    finally:
        document.close()

    write_pilot_package(publications_dir, pdf_path.stem)
    return created


def main() -> None:
    try:
        created = generate_previews()
    except (FileNotFoundError, RuntimeError) as exc:
        print(str(exc))
        raise SystemExit(1) from exc

    print("Preview images created:")
    for path in created:
        print(path.name)


if __name__ == "__main__":
    main()
