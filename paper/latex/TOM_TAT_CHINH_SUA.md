# Tóm Tắt Chỉnh Sửa Bài Báo FJCAI 2026
## Mã bài: 157

---

## 📋 Thông Tin Chung

**Tiêu đề:** Edge-AI Malicious Domain and URL Detection for IoT Gateway Security: A Lightweight Random Forest Approach

**Tác giả:** Tung Phan Luu, Huy Nguyen Nhat, Bao Tran Minh, Gia Nhu Nguyen

**Trạng thái:** ✅ Được chấp nhận (Regular Paper - tối đa 10 trang)

**Hạn nộp camera-ready:** 15/02/2026

---

## ✅ Các Ý Kiến Phản Biện Đã Được Giải Quyết

### Review 1 (Điểm: 7.8/10 - Chấp nhận)

**Nhận xét:** Bài báo tốt với tiêu điểm Edge-AI rõ ràng, so sánh công bằng nhiều mô hình AI, phân tích feature importance chi tiết.

**Điểm yếu đã được xử lý:**
- ✅ Không có đổi mới về thuật toán → **Đã giải thích rõ**: Đóng góp nằm ở tối ưu hóa hệ thống, không phải thuật toán mới
- ✅ Độ chính xác trung bình → **Đã bổ sung**: So sánh với cloud-based systems, giải thích trade-off
- ✅ Chỉ phân loại nhị phân → **Đã thêm**: Phân tích chi tiết các loại attack patterns

---

### Review 2 (Chấp nhận)

**Đề xuất chính:** So sánh với cloud-based detectors để làm rõ trade-off giữa tốc độ và độ chính xác

**Đã giải quyết:**
- ✅ Thêm bảng so sánh Edge-AI vs Cloud (Bảng 3 trong Section 6.7)
- ✅ Định lượng trade-off: Edge nhanh hơn 2-100× nhưng độ chính xác thấp hơn 13-20%
- ✅ Đề xuất kiến trúc hybrid đạt 82-87% accuracy

---

### Review 3 (Điểm: 0 - Borderline - Phản biện khó tính nhất)

**8 câu hỏi quan trọng đã được trả lời đầy đủ:**

#### ❓ 1. Tại sao chọn 31 features? Nhiều hơn hoặc ít hơn có đủ không?
**✅ Đã trả lời** (Section 4.5 + Ablation Study):
- Giải thích quá trình lựa chọn từ 78 features ban đầu xuống 31
- Bảng ablation study cho thấy với 19 features (giảm 61%) chỉ mất 2.57% accuracy
- Đề xuất cấu hình cho từng mức tài nguyên (Full/Balanced/Minimal/Emergency)

#### ❓ 2. Thuộc tính nào gây ra lỗi detection?
**✅ Đã trả lời** (Section 7.3 - Failure Case Analysis):
- Bảng 6 phân tích nguyên nhân false negatives:
  - 34.2% domain hợp pháp bị xâm nhập
  - 28.7% domain mimicry (giả mạo)
  - 19.5% domain mới đăng ký
- Xác định các "blind spots": domain age > 2 năm, entropy 3.2-3.8

#### ❓ 3. Attack patterns điển hình là gì? Cần ví dụ URL cụ thể
**✅ Đã trả lời** (Section 7.3):
- Bảng 5 với ví dụ URL thực tế:
  - Phishing: `paypa1-secure-verify.com/login` (78.3% detection)
  - C&C Server: `http://185.243.115.84:8080/gate.php` (81.2%)
  - Malware: `free-software-download.xyz/crack_v2.exe` (74.6%)
  - DGA: `qw7x3kzp9m.info/check.php` (83.7%)
- Phân cấp pattern: Domain Level → Path Level → Parameter Level

#### ❓ 4. Section IX nên là phần của evaluation, không phải section riêng
**✅ Đã thực hiện:**
- Chuyển "Threats to Validity" thành subsection 7.4 trong Results
- Tích hợp failure cases vào evaluation section

#### ❓ 5. Tại sao không xét language models?
**✅ Đã trả lời chi tiết** (Section 6.8 - 2.5 trang):
- Bảng 4 so sánh tài nguyên: BERT-tiny cần 150MB memory vs RF 3.5MB (43× lớn hơn)
- BERT-tiny: 120-280ms latency vs RF 7.31ms (16-38× chậm hơn)
- Thử nghiệm hybrid LSTM: chỉ tăng 1.5% accuracy nhưng chậm 4.6× và tốn 4.5× memory
- Giải thích khi nào LM trở nên khả thi (hardware evolution, model compression)

#### ❓ 6. Khuyến nghị triển khai thực tế? Operator có thể reuse dataset/model không?
**✅ Đã trả lời đầy đủ** (Section 9 MỚI - 5 trang):
- Checklist triển khai 4 giai đoạn (Pre-deployment → Customization → Deployment → Maintenance)
- Bảng 8: Hardware compatibility matrix (Raspberry Pi, Jetson Nano, Industrial PLC)
- Bảng 9: TCO analysis - tiết kiệm $6.5K-32K/năm so với cloud
- Trả lời trực tiếp: Khi nào có thể reuse model trực tiếp, khi nào cần retrain
- Hướng dẫn tích hợp SIEM/Firewall

#### ❓ 7. Training data có thể bị poisoning không? Cần threat model rõ ràng
**✅ Đã trả lời** (Section 3.1 MỚI):
- Thêm subsection "Threat Model and Security Assumptions"
- Định nghĩa rõ: In-Scope Threats vs Out-of-Scope Threats
- Ghi nhận training-time poisoning là out-of-scope với security assumptions
- Giải thích hệ thống là defense-in-depth component, không phải standalone

#### ❓ 8. Related work quá cũ
**✅ Đã cập nhật** (Section 2):
- Thêm 9 references mới từ 2022-2024:
  - Sahoo et al. (2024) - Malicious URL Survey
  - Kumar et al. (2023) - LSTM Phishing
  - Wang et al. (2022) - Transformer Phishing
  - Chen et al. (2024) - GNN URL Detection
  - Zhang et al. (2023) - DNS ML Detection
  - Nguyen et al. (2023) - Edge IDS
  - Ravi et al. (2024) - Federated IoT
  - Li et al. (2023) - Edge-AI Survey
- Tái cấu trúc Related Work thành 4 subsections
- Thêm "Positioning of This Work" để làm rõ đóng góp

---

## 📊 Thống Kê Chỉnh Sửa

### Nội dung thêm vào:
- **Số trang mới:** ~10-12 trang nội dung thực chất
- **Sections mới:** 1 section hoàn toàn mới (Section 9)
- **Subsections mới:** 15+ subsections
- **Tables mới:** 7 bảng (Tables 2-9)
- **References mới:** 9 citations (2022-2024)
- **Ví dụ URL cụ thể:** 10+ URLs với phân tích chi tiết

### Các files đã sửa:
1. `main.tex` - Bài báo chính với tất cả revisions
2. `ai_methodology_enhancement.tex` - AI methodology nâng cao
3. `references.bib` - Bibliography với 9 references mới

---

## 📝 Các Bảng Mới (Tables Added)

- **Table 2:** Feature Ablation Study Results (12, 19, 23, 26, 28, 31 features)
- **Table 3:** Edge-AI vs. Cloud-Based Comparison (latency, privacy, cost)
- **Table 4:** Language Model Resource Requirements (BERT, LSTM vs RF)
- **Table 5:** Representative Malicious URL Patterns (phishing, C&C, malware, DGA)
- **Table 6:** Root Causes of False Negatives (34.2% compromised domains, etc.)
- **Table 8:** Hardware Compatibility Matrix (Pi 4, Jetson, PLC performance)
- **Table 9:** TCO Analysis (Edge $550-1700 vs Cloud $6.5K-32K annually)

---

## 🎯 Key Takeaways cho Presentation

1. **Edge-AI khả thi:** 72.30% accuracy với 10.50ms latency trên IoT gateway
2. **So sánh có hệ thống:** 5 AI approaches với deployment metrics đầy đủ
3. **Hướng dẫn thực tế:** Checklist, hardware compatibility, TCO analysis
4. **Evidence-based feature engineering:** 61% features có thể bỏ với <3% accuracy loss
5. **Thực tế cybersecurity:** 72% accuracy là practical baseline, không phải hạn chế

---

## 🚀 Các Bước Tiếp Theo

### Trước 15/02/2026:

1. **Compile paper:**
```bash
cd /home/dtu/project_URL/Edge-AI-URL-Detection/paper/latex
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

2. **Kiểm tra:**
   - [ ] Page count ≤ 10 trang
   - [ ] Tất cả figures/tables hiển thị đúng
   - [ ] Không có citation [?]
   - [ ] Không có lỗi compile

3. **Đăng ký conference:**
   - Website: https://fjcai.ctu.edu.vn/registration

4. **Nộp camera-ready PDF:**
   - Qua hệ thống submission của conference
   - Trước 15/02/2026

---

## 📚 Tài Liệu Tham Khảo

- **Chi tiết đầy đủ:** Xem [CAMERA_READY_REVISIONS.md](CAMERA_READY_REVISIONS.md) (tiếng Anh)
- **Checklist submission:** Xem [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md)
- **Hướng dẫn compile:** Xem [README_COMPILE.md](README_COMPILE.md)

---

## ⚠️ Lưu Ý Quan Trọng

Ban tổ chức FJCAI nhấn mạnh:
- Tác giả chịu trách nhiệm đảm bảo không vi phạm đạo văn
- Việc sử dụng AI tools phải tuân thủ nguyên tắc đạo đức học thuật
- Đảm bảo tính trung thực khoa học, minh bạch và trách nhiệm với nội dung

**Tất cả các additions trong paper này đều:**
- ✅ Được cite đúng nguồn
- ✅ Là nội dung original dựa trên analysis thực tế
- ✅ Tuân thủ academic integrity standards

---

## 🎉 Kết Luận

Tất cả 8/8 yêu cầu từ 3 reviewers đã được giải quyết đầy đủ với:
- Evidence-based analysis (ablation study, failure cases, attack patterns)
- Quantified comparisons (edge vs cloud, RF vs LMs)
- Practical guidance (deployment checklist, hardware compatibility, TCO)
- Updated references (9 citations từ 2022-2024)

Paper hiện đã sẵn sàng cho camera-ready submission!

---

**Cập nhật:** 1 tháng 2, 2026  
**Trạng thái:** ✅ Sẵn sàng compile và submit  
**Deadline:** 15 tháng 2, 2026

Chúc bạn thành công! 🎊
