#!/usr/bin/env python3
"""Build a blue revision PDF against the preserved submitted manuscript."""

import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / "Paper_original"
NEW = ROOT / "Paper"
TEXBIN = Path("/Library/TeX/texbin")
INPUTS = {}


def flatten(root, relative, stack=()):
    path = root / relative
    if path in stack:
        raise ValueError(f"Recursive input: {path}")
    content = path.read_text()
    INPUTS[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()

    def include(match):
        name = match.group(1)
        target = name if Path(name).suffix else name + ".tex"
        return "\n" + flatten(root, target, stack + (path,)) + "\n"

    # These manuscript inputs all resolve relative to the paper's build directory.
    # Keep bibliography commands so BibTeX, rather than latexdiff, handles the BBL.
    return re.sub(r"\\input\{([^}]+)\}", include, content)


def run(command, cwd, log):
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    log.write_text(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError(f"Command failed; diagnostics: {log}")
    return result.stdout


def unwrap_inactive_revision_markup(content):
    # Both manuscripts disable the older yellow revision macros. Removing
    # transparent wrappers avoids unbreakable strikethrough boxes in the diff.
    pattern = re.compile(r"\\(rev|revmath)\{")
    cursor, pieces = 0, []
    while match := pattern.search(content, cursor):
        depth, end = 1, match.end()
        while depth:
            if content[end] == "\\" and content[end + 1:end + 2] in ("{", "}"):
                end += 2
                continue
            depth += (content[end] == "{") - (content[end] == "}")
            end += 1
        argument = unwrap_inactive_revision_markup(content[match.end():end - 1])
        pieces.append(content[cursor:match.start()])
        pieces.append(argument if match.group(1) == "rev" else r"\ensuremath{" + argument + "}")
        cursor = end
    pieces.append(content[cursor:])
    return "".join(pieces)


def main():
    output = NEW / "LAMP_diff.tex"
    pdf = NEW / "LAMP_diff.pdf"
    with tempfile.TemporaryDirectory(prefix="lamp-revision-diff-") as temp:
        work = Path(temp)
        (work / "old.tex").write_text(unwrap_inactive_revision_markup(flatten(OLD, "main.tex")))
        (work / "new.tex").write_text(unwrap_inactive_revision_markup(flatten(NEW, "main.tex")))
        generation_log = ROOT / "Revision" / "diff-generation-20261001.log"
        diff = run([
            str(TEXBIN / "latexdiff"), "--math-markup=coarse",
            "--graphics-markup=none", "--add-to-config", r"PICTUREENV=table;table\*",
            "--label=Submitted first revision", "--label=EPYC comparison revision",
            "old.tex", "new.tex",
        ], work, generation_log)
        # The full generated source lives in LAMP_diff.tex, not in the diagnostic log.
        generation_log.write_text(generation_log.read_text().removeprefix(diff))
        style = r'''
% Requested review colors; body additions have no underline.
\definecolor{DiffBlue}{RGB}{0,65,190}
\definecolor{DiffDeleted}{RGB}{115,115,115}
\renewcommand{\DIFaddtex}[1]{{\protect\color{DiffBlue}#1}}
\renewcommand{\DIFdeltex}[1]{{\protect\color{DiffDeleted}\sout{#1}}}
'''
        diff = diff.replace(r"\begin{document}", style + "\n" + r"\begin{document}", 1)
        legend = r'''
\noindent{\footnotesize Compared with the submitted first revision:
\textcolor{DiffBlue}{blue = added/revised or relocated};
\textcolor{DiffDeleted}{\sout{gray = removed}}.
Tables relocated to Appendix F retain their original measurements.}
\par\smallskip
'''
        diff = diff.replace(r"\maketitle", r"\maketitle" + "\n" + legend, 1)
        diff = diff.replace(r"\DIFdelend \DIFaddbegin",
                            r"\DIFdelend\allowbreak \DIFaddbegin")
        diff = diff.replace(r"\url{https://github.com/lysias9049/LAMP-artifact}",
                            r"\textcolor{DiffBlue}{\url{https://github.com/lysias9049/LAMP-artifact}}")

        # A table is atomic for the diff. Color inserted/relocated tables inside
        # their float group, including numeric rows expanded from row macros.
        blue_tables = {"tab:epyc-zkmatrix-square", "tab:epyc-zkmatrix-batch",
                       "tab:lamp-breakdown", "tab:lamp-batch"}

        def color_table(match):
            prefix = diff[diff.rfind("\n", 0, match.start()) + 1:match.start()]
            if "%" not in prefix and any(r"\label{" + label + "}" in match.group(2)
                                         for label in blue_tables):
                return match.group(1) + "\n" + r"\color{DiffBlue}" + match.group(2)
            return match.group(0)

        diff = re.sub(r"(\\begin\{table\*?\}(?:\[[^\]]*\])?)"
                      r"([\s\S]*?\\end\{table\*?\})", color_table, diff)
        output.write_text(diff)
        (work / output.name).write_text(diff)
        shutil.copytree(NEW / "Styles", work / "Styles")
        build_log = ROOT / "Revision" / "diff-build-20261001.log"
        run([str(TEXBIN / "latexmk"), "-pdf", "-interaction=nonstopmode",
             "-halt-on-error", output.name], work, build_log)
        shutil.copy2(work / pdf.name, pdf)
        report = {
            "baseline": "Paper_original/main.tex (submitted first revision)",
            "new": "Paper/main.tex",
            "diff_source": str(output.relative_to(ROOT)),
            "diff_pdf": str(pdf.relative_to(ROOT)),
            "additions": "blue; includes relocated tables",
            "deletions": "gray strikethrough",
            "input_sha256": INPUTS,
            "diff_tex_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
            "diff_pdf_sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
            "page_count": int(re.findall(r"Output written on LAMP_diff.pdf \((\d+) pages",
                                         build_log.read_text())[-1]),
        }
        (ROOT / "Revision" / "diff-validation-20261001.json").write_text(
            json.dumps(report, indent=2) + "\n")
        print("Created Paper/LAMP_diff.tex and Paper/LAMP_diff.pdf.")
        print("Submitted baseline and current manuscript are unchanged.")


if __name__ == "__main__":
    main()
