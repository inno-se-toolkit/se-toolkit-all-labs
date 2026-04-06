Generate unique quiz variants as a PDF from the question bank.

Arguments: $ARGUMENTS (format: `<number-of-variants>` e.g. `270`)

1. Read questions from `docs/Question bank.md`
2. Split into 3 groups (first 7, middle 7, last 7 — exclude Q22 unless told otherwise)
3. Generate N unique variants, each picking one question from each group
4. Use coprime strides so adjacent pages never share questions
5. Build a LaTeX document using `scripts/quiz/template.tex` as reference for styling:
   - One variant per page, A4, 11pt
   - Header: course title, variant number
   - Fields: Full name, University email
   - Note box: "Answer at least 2 questions correctly. Write clearly and within the boxes. Mistakes in email or name, unclear writing, or writing outside of the boxes gets 0 without appeal."
   - 3 answer boxes per page, sized to fill the page
6. Compile with `xelatex` (at `/Library/TeX/texbin/xelatex`)
7. Save PDF to `~/Downloads/quiz_<N>_variants.pdf`
