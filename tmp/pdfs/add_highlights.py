import sys
import types

# pdfminer only needs charset_normalizer.detect() for malformed byte strings.
# Avoid loading its optional native extension in this bundled Windows runtime.
sys.modules["charset_normalizer"] = types.SimpleNamespace(
    detect=lambda _: {"encoding": "utf-8"}
)

import pdfplumber
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Highlight
from pypdf.generic import ArrayObject, FloatObject, NameObject


def is_added_color(value: object) -> bool:
    if not isinstance(value, tuple) or len(value) != 3:
        return False
    target = (17 / 255, 34 / 255, 51 / 255)
    return all(abs(float(a) - b) < 0.002 for a, b in zip(value, target))


def merge_chars(chars: list[dict]) -> list[tuple[float, float, float, float]]:
    segments: list[dict] = []
    for char in chars:
        if not is_added_color(char.get("non_stroking_color")):
            continue
        if not char.get("text", "").strip() and not segments:
            continue
        if segments:
            current = segments[-1]
            same_line = abs(char["top"] - current["top"]) < 1.8
            close = char["x0"] <= current["x1"] + max(2.5, char["size"] * 0.45)
            if same_line and close:
                current["x1"] = max(current["x1"], char["x1"])
                current["bottom"] = max(current["bottom"], char["bottom"])
                current["has_text"] |= bool(char.get("text", "").strip())
                continue
        segments.append(
            {
                "x0": char["x0"],
                "x1": char["x1"],
                "top": char["top"],
                "bottom": char["bottom"],
                "has_text": bool(char.get("text", "").strip()),
            }
        )
    return [
        (s["x0"] - 0.6, s["top"] + 0.5, s["x1"] + 0.6, s["bottom"] - 0.2)
        for s in segments
        if s["has_text"]
    ]


def main(source: str, destination: str) -> None:
    reader = PdfReader(source)
    writer = PdfWriter()
    writer.append(reader)
    rectangles = 0
    highlighted_pages = 0

    with pdfplumber.open(source) as document:
        for page_number, page in enumerate(document.pages):
            boxes = merge_chars(page.chars)
            if boxes:
                highlighted_pages += 1
            for x0, top, x1, bottom in boxes:
                y0 = page.height - bottom
                y1 = page.height - top
                quad_points = ArrayObject(
                    [
                        FloatObject(x0), FloatObject(y1),
                        FloatObject(x1), FloatObject(y1),
                        FloatObject(x0), FloatObject(y0),
                        FloatObject(x1), FloatObject(y0),
                    ]
                )
                annotation = Highlight(
                    rect=(x0, y0, x1, y1),
                    quad_points=quad_points,
                    highlight_color="ffe84d",
                    printing=True,
                )
                annotation[NameObject("/CA")] = FloatObject(0.42)
                writer.add_annotation(page_number=page_number, annotation=annotation)
                rectangles += 1

    with open(destination, "wb") as output:
        writer.write(output)
    print(f"highlighted_pages={highlighted_pages} rectangles={rectangles}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
