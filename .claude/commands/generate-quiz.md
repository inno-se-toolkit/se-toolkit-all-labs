Generate unique quiz variants as a PDF from the question bank.

Arguments: $ARGUMENTS (number of variants, e.g. `270`)

## Source

Questions are in `docs/Question bank.md`. The LaTeX template is at `scripts/quiz/template.tex`.

## Variant generation

1. Read questions from the question bank. Split into 3 groups of roughly equal size (e.g. first 7, middle 7, last 7). Exclude Q22 (system design diagram) unless told otherwise.
2. Generate N unique variants. Each variant picks one question from each group.
3. Use coprime strides so **adjacent pages never share any question** (e.g. group A stride 1, group B stride 2, group C stride 3).
4. Verify the adjacency constraint before proceeding.

## LaTeX structure

- Paper: A4, font size 11pt, margins 1.0cm top/bottom, 1.0cm sides
- One variant per page — every variant must fit on exactly one page
- Packages: `geometry`, `enumitem`, `tcolorbox`, `calc`
- No page numbers, no headers/footers (`\pagestyle{empty}`)

### Per-page layout

1. **Title line:** `Software Engineering Toolkit --- Theory Quiz` (left) + `Variant N` (right, bold)
2. **Horizontal rule**
3. **Fields:** `Full name: ___________    University email: ___________`
4. **Warning box** (framed, small text): `Answer at least 2 questions correctly. Write clearly and within the boxes. Mistakes in email or name, unclear writing, or writing outside of the boxes gets 0 without appeal.`
5. **Three numbered questions**, each followed by an answer box

### Answer boxes

Use `tcolorbox` with fixed height:

```tex
\newcommand{\answerbox}[1]{%
  \begin{tcolorbox}[colback=white, colframe=black!40, boxrule=0.4pt, arc=1pt,
    left=3pt, right=3pt, top=2pt, bottom=2pt, height=#1, valign=top]
  \mbox{}\vfill
  \end{tcolorbox}
}
```

Start with equal box heights (e.g. 7.0cm each). Adjust to fill the page.

## Page-fit tuning

If variants overflow to 2 pages:
1. Reduce answer box heights
2. Reduce list spacing (`enumitem` topsep/itemsep)
3. Reduce margins
4. Reduce font size (11pt → 10pt)

If too compressed, increase in reverse order.

## Compilation

```bash
/Library/TeX/texbin/xelatex -interaction=nonstopmode -halt-on-error -output-directory=/tmp <texfile>
```

## Verification

After compilation, check:
- Page count equals N: `pdfinfo /tmp/<file>.pdf | grep Pages`
- Content looks right: `pdftotext /tmp/<file>.pdf - | head -30`

## Output

Copy the PDF to `~/Downloads/quiz_<N>_variants.pdf`.
