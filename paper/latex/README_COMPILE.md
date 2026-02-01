# Camera-Ready Paper Compilation Guide
## FJCAI 2026 - Paper ID 157

This guide helps you compile and verify the camera-ready paper after addressing all reviewer comments.

---

## Quick Start

### 1. Compile the Paper

```bash
cd /home/dtu/project_URL/Edge-AI-URL-Detection/paper/latex

# Full compilation (run this first time or after bibliography changes)
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex

# The final PDF will be: main.pdf
```

### 2. Verify Output

```bash
# Check page count (must be ≤ 10 pages)
pdfinfo main.pdf | grep Pages

# Check for errors
grep -i error main.log

# Open PDF to review
xdg-open main.pdf  # Linux
# or
open main.pdf      # macOS
```

---

## What Was Changed

All reviewer comments have been systematically addressed. See [CAMERA_READY_REVISIONS.md](CAMERA_READY_REVISIONS.md) for complete details.

### Major Additions:
1. **Threat Model** (Section 3.1) - Explicit security assumptions and attack scenarios
2. **Feature Selection Justification** (Section 4.5) - Why 31 features with ablation study
3. **Attack Pattern Analysis** (Section 7.3) - Typical malicious URL patterns with examples
4. **Failure Case Analysis** (Section 7.3) - Root causes of misclassifications
5. **Cloud vs Edge Comparison** (Section 6.7) - Quantified trade-off analysis
6. **Language Model Discussion** (Section 6.8) - Why LMs were excluded with evidence
7. **Practical Deployment Guidelines** (Section 9) - Complete deployment checklist and TCO analysis
8. **Updated Related Work** (Section 2) - 9 new references from 2022-2024

### Files Modified:
- `main.tex` - Main paper with all revisions (~10 pages)
- `ai_methodology_enhancement.tex` - Enhanced AI methodology sections
- `references.bib` - 9 new contemporary citations added

---

## Troubleshooting

### Issue: "Undefined references" or citations showing as [?]

**Solution:** Make sure you run the full compilation sequence:
```bash
pdflatex main.tex
bibtex main       # This processes the bibliography
pdflatex main.tex # This resolves citations
pdflatex main.tex # This ensures everything is correct
```

### Issue: "Package ... not found"

**Solution:** Install missing LaTeX packages:
```bash
# On Ubuntu/Debian
sudo apt-get install texlive-full

# Or install specific packages
sudo apt-get install texlive-latex-extra texlive-science
```

### Issue: Page count exceeds 10 pages

**Solution:** Adjust formatting in main.tex:
- Reduce figure sizes slightly
- Adjust table font sizes (\small or \footnotesize)
- Compress section spacing
- Move some examples to appendix (if allowed)

### Issue: Compilation takes too long

**Solution:** For quick edits, use:
```bash
pdflatex main.tex  # Just one pass, faster
```
Only run the full bibtex sequence when bibliography changes.

---

## Verification Checklist

Before submission, verify:

- [ ] PDF compiles without errors
- [ ] Page count ≤ 10 pages
- [ ] All figures appear correctly
- [ ] All tables are readable and formatted properly
- [ ] No citation appears as [?]
- [ ] Author names and emails are correct
- [ ] Abstract accurately reflects revised content
- [ ] All URLs in text are properly formatted (clickable if applicable)

---

## Next Steps

1. **Compile and verify PDF** (follow steps above)
2. **Review SUBMISSION_CHECKLIST.md** for complete pre-submission tasks
3. **Register for conference** at https://fjcai.ctu.edu.vn/registration
4. **Submit camera-ready PDF** before February 15, 2026

---

## File Structure

```
paper/latex/
├── main.tex                          # Main paper (compile this)
├── ai_methodology_enhancement.tex    # AI methodology section (included by main.tex)
├── references.bib                    # Bibliography with new references
├── main.pdf                          # Compiled output (generated)
├── CAMERA_READY_REVISIONS.md         # Detailed revision summary
├── SUBMISSION_CHECKLIST.md           # Step-by-step submission guide
└── README_COMPILE.md                 # This file
```

---

## Support

If you encounter issues:
1. Check main.log for detailed error messages
2. Review [CAMERA_READY_REVISIONS.md](CAMERA_READY_REVISIONS.md) for context
3. Consult FJCAI conference website for formatting guidelines

---

**Important Dates:**
- Camera-Ready Deadline: **February 15, 2026**
- Registration Deadline: **February 15, 2026**

**Conference Website:** https://fjcai.ctu.edu.vn

---

Good luck with the submission! 🎉
