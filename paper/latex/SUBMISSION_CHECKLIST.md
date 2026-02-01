# FJCAI 2026 Camera-Ready Submission Checklist
## Paper ID: 157

### Deadline: February 15, 2026

---

## Pre-Submission Checklist

### ✓ Content Review (COMPLETED)
- [x] All Review 1 concerns addressed
- [x] All Review 2 concerns addressed  
- [x] All Review 3 concerns addressed (8/8 questions)
- [x] Threat model added (Section 3.1)
- [x] Feature selection justification added (Section 4.5)
- [x] Ablation study table added (Table 2)
- [x] Attack pattern examples added (Section 7.3)
- [x] Failure case analysis added (Section 7.3)
- [x] Cloud-based comparison added (Section 6.7)
- [x] Language model discussion added (Section 6.8)
- [x] Practical deployment guidelines added (Section 9)
- [x] Related work updated with 2022-2024 references
- [x] Section IX reorganized into Results section

---

## Pre-Compilation Tasks (TODO)

### [ ] LaTeX Compilation
```bash
cd /home/dtu/project_URL/Edge-AI-URL-Detection/paper/latex
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

### [ ] Document Verification
- [ ] Check total page count ≤ 10 pages
- [ ] Verify all figures render correctly
- [ ] Verify all tables render correctly
- [ ] Check all citations resolve (no [?] in text)
- [ ] Verify no compilation errors or warnings

### [ ] Content Quality Checks
- [ ] Proofread abstract for typos
- [ ] Verify all author names and affiliations correct
- [ ] Check all section/subsection numbering consistent
- [ ] Verify all table/figure references correct (e.g., "Table~\ref{tab:...}")
- [ ] Ensure all URLs in text are properly formatted

### [ ] Bibliography Verification
- [ ] All 9 new references compile correctly
- [ ] Citation style matches IEEE format
- [ ] No duplicate entries in references.bib
- [ ] All in-text citations have corresponding bibliography entries

---

## Camera-Ready Preparation (TODO)

### [ ] Final PDF Generation
1. Compile LaTeX to generate main.pdf
2. Verify PDF is IEEE conference format
3. Check PDF file size < 10 MB
4. Verify PDF contains embedded fonts
5. Test PDF opens correctly in Adobe Reader

### [ ] Copyright Form (if required)
- [ ] Complete IEEE copyright transfer form
- [ ] Insert copyright notice in PDF footer (per FJCAI instructions)

### [ ] Supplementary Materials (optional)
- [ ] Prepare source code repository link
- [ ] Prepare dataset access instructions
- [ ] Create README for reproducibility

---

## Conference Registration (TODO before Feb 15)

### [ ] Register at: https://fjcai.ctu.edu.vn/registration
- [ ] Select appropriate registration category
- [ ] Pay registration fee
- [ ] Receive confirmation email

### [ ] Review Registration Info: https://fjcai.ctu.edu.vn/#dang-ky

---

## Submission (TODO before Feb 15)

### [ ] Upload Camera-Ready PDF
1. Log into FJCAI submission system
2. Navigate to Paper ID 157
3. Upload final PDF (main.pdf)
4. Upload supplementary materials (if any)
5. Verify upload successful
6. Download and review uploaded PDF

### [ ] Submit Additional Materials
- [ ] Upload source files (if required by conference)
- [ ] Upload copyright form
- [ ] Submit presentation slides (if early submission encouraged)

---

## Post-Submission

### [ ] Confirmation
- [ ] Receive camera-ready acceptance email
- [ ] Save confirmation email
- [ ] Note presentation date/time/session

### [ ] Presentation Preparation
- [ ] Create PowerPoint/Beamer slides
- [ ] Prepare 15-20 minute talk
- [ ] Practice presentation timing
- [ ] Prepare Q&A responses

---

## Key Dates Reminder

| Event | Date | Status |
|-------|------|--------|
| Acceptance Notification | Feb 1, 2026 | ✓ Done |
| Camera-Ready Deadline | **Feb 15, 2026** | ⏳ Pending |
| Registration Deadline | Feb 15, 2026 | ⏳ Pending |
| Conference Date | TBD (check https://fjcai.ctu.edu.vn) | ⏳ Pending |

---

## Compilation Commands Quick Reference

```bash
# Navigate to latex folder
cd /home/dtu/project_URL/Edge-AI-URL-Detection/paper/latex

# Full compilation with bibliography
pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex

# Quick recompile (after minor changes)
pdflatex main.tex

# Check for errors
grep -i "error\|warning" main.log

# Verify page count
pdfinfo main.pdf | grep Pages
```

---

## Contact Information

**Conference Email:** (check https://fjcai.ctu.edu.vn for contact)  
**Conference Website:** https://fjcai.ctu.edu.vn  
**Registration:** https://fjcai.ctu.edu.vn/registration  

---

## Notes

- **Important:** FJCAI emphasizes authors' responsibility for academic integrity regarding AI tool usage
- Ensure all AI-assisted content (if any) complies with ethical guidelines
- Declare AI tool usage transparently if required by conference policy
- Maintain scientific rigor and honesty in all content

---

**Last Updated:** February 1, 2026  
**Status:** Ready for LaTeX compilation and final PDF generation
