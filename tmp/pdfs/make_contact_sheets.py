from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
import sys


def make_sheets(source: Path, destination: Path, per_sheet: int = 4) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    pages = sorted(source.glob("page-*.png"))
    for start in range(0, len(pages), per_sheet):
        batch = pages[start : start + per_sheet]
        thumbs = []
        for page in batch:
            with Image.open(page) as image:
                image = image.convert("RGB")
                image.thumbnail((900, 1165), Image.Resampling.LANCZOS)
                canvas = Image.new("RGB", (940, 1235), "white")
                canvas.paste(image, ((940 - image.width) // 2, 35))
                ImageDraw.Draw(canvas).text((20, 10), page.stem, fill="black")
                thumbs.append(ImageOps.expand(canvas, border=2, fill="gray"))
        sheet = Image.new("RGB", (1884, 2478), "white")
        for index, thumb in enumerate(thumbs):
            x = (index % 2) * 942
            y = (index // 2) * 1239
            sheet.paste(thumb, (x, y))
        sheet.save(destination / f"contact-{start // per_sheet + 1:02d}.png")


if __name__ == "__main__":
    make_sheets(Path(sys.argv[1]), Path(sys.argv[2]))
