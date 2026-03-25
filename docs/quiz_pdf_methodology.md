# Quiz PDF Generation Methodology

This document explains exactly how the `quiz.pdf` answer sheet was produced so the same process can be reused for other exam sheets.

## 1. Source Input

- Original question source used for this run: `/Users/nursultan/Desktop/desktop/nur_vault/SET course/SWP.md`
- Working LaTeX template: `/Users/nursultan/Developer/quiz_template.tex`
- Generated PDF output: `/Users/nursultan/Desktop/desktop/nur_vault/SET course/quiz.pdf`

## 2. Why LaTeX Was Used Instead of Direct Markdown-to-PDF

The original Markdown file contains only the question text. A plain Markdown-to-PDF conversion would preserve the questions, but it would not reliably create:

- fixed-height answer boxes under each question
- a compact exam-sheet layout
- precise page-count control
- a fill-in header for student information

To control those details, the Markdown content was manually transferred into a small LaTeX template.

## 3. LaTeX Structure

The template uses these packages:

- `geometry` for page size and margins
- `enumitem` for tight numbered-question layout
- `tcolorbox` for drawing fixed-height answer boxes
- `needspace` to keep a question and its answer box from splitting awkwardly across pages

The document is configured as:

- paper size: `a4paper`
- font size: `10pt`
- margins: `1.2cm`

## 4. Header Added

The PDF includes:

- a title: `Retake Exam Questions`
- a line for `Name`
- a line for `Email`
- a boxed note: `Write clearly. Handwriting must be legible because responses will be transcribed by AI.`

This was added directly in the TeX file before the question list.

## 5. Answer Box Method

A reusable LaTeX macro was defined:

```tex
\newcommand{\answerbox}[1]{%
  \begin{tcolorbox}[... height=#1]
  \mbox{}\vfill
  \end{tcolorbox}
}
```

How it works:

- each question is followed by `\answerbox{...}`
- the height parameter is set per question
- longer questions get taller boxes
- short factual questions get shorter boxes

Example usage:

```tex
\item What is an MVP? Provide a proper definition.
\answerbox{2.2cm}
```

## 6. Page-Fit Tuning Process

The first version compiled to 3 pages. To reduce it to 2 pages, these changes were made:

1. Reduced the base font size from `11pt` to `10pt`.
2. Reduced page margins from `1.5cm` to `1.2cm`.
3. Tightened list spacing with `enumitem`.
4. Removed extra paragraph spacing.
5. Reduced padding inside answer boxes.
6. Reduced answer-box heights question by question.
7. Kept the largest box for the taxi-app use case diagram question.

The current box heights are:

- Q1: `4.1cm`
- Q2: `2.1cm`
- Q3: `3.3cm`
- Q4: `2.9cm`
- Q5: `3.8cm`
- Q6: `7.1cm`
- Q7: `3.5cm`
- Q8: `2.9cm`
- Q9: `2.4cm`
- Q10: `2.4cm`

These were intentionally increased on page 2 because that page had visible spare space, and the added room is most useful for:

- the taxi-app use case diagram question
- the requirements-engineering explanation question
- the short-definition questions that benefit from a little more writing room

## 7. Compilation Command

The PDF was compiled with XeLaTeX:

```bash
/Library/TeX/texbin/xelatex -interaction=nonstopmode -halt-on-error -output-directory=/tmp /Users/nursultan/Developer/quiz_template.tex
```

Why this command:

- `xelatex` is installed on this machine
- `-interaction=nonstopmode` keeps logs readable
- `-halt-on-error` stops immediately on LaTeX errors
- `-output-directory=/tmp` keeps auxiliary build files out of the working directory

The generated file is:

- `/tmp/quiz_template.pdf`

## 8. Final Save Step

After compilation, the PDF was copied to the destination path:

```bash
cp /tmp/quiz_template.pdf '/Users/nursultan/Desktop/desktop/nur_vault/SET course/quiz.pdf'
```

## 9. How To Reuse This Method

For another exam sheet:

1. Copy `quiz_template.tex` to a new TeX filename.
2. Replace the title and header note if needed.
3. Replace the numbered question text with the new questions.
4. Adjust each `\answerbox{...}` height based on expected answer length.
5. Compile with the same `xelatex` command.
6. If the document is too long, first reduce:
   - box heights
   - list spacing
   - margins
   - font size
7. If the document is too compressed, increase those values in the reverse order.

## 10. Practical Rules For Future Sheets

- Use larger boxes for diagram or explanation questions.
- Use smaller boxes for definition or list questions.
- Keep the student-info header compact.
- Keep one source TeX template and only swap question text plus box heights.
- Verify final page count with:

```bash
pdfinfo /tmp/quiz_template.pdf | sed -n '1,20p'
```

- Verify the text content with:

```bash
pdftotext /tmp/quiz_template.pdf - | sed -n '1,120p'
```
