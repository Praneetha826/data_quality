# Quality Detection Evaluation Report

**Generated:** 2026-09-23T15:45:35.891816

**Total Datasets Evaluated:** 11

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total True Positives | 18 |
| Total False Positives | 0 |
| Total False Negatives | 3 |
| Overall Precision | 1.000 |
| Overall Recall | 0.857 |
| Overall F1 Score | 0.923 |

## Detailed Results

### clean_dataset.csv

- **Format:** CSV
- **Category:** structured
- **Expected Issues:** ['date_as_string']
- **Detected Issues:** ['date_as_string']
- **Quality Score:** 95.0/100
- **Completeness:** 100.0/100
- **Consistency:** 100.0/100
- **Validity:** 100.0/100
- **Description:** Clean dataset with date_as_string issue (dates stored as strings, which is expected for CSV)

**Detection Metrics:**
- True Positives: 1
- False Positives: 0
- False Negatives: 0
- Precision: 1.0
- Recall: 1.0
- F1 Score: 1.0

**Performance:**
- Load Time: 0.006s
- Quality Time: 0.017s

---

### missing_values.csv

- **Format:** CSV
- **Category:** structured
- **Expected Issues:** ['missing_values', 'date_as_string']
- **Detected Issues:** ['missing_values', 'date_as_string']
- **Quality Score:** 75.0/100
- **Completeness:** 90.0/100
- **Consistency:** 100.0/100
- **Validity:** 100.0/100
- **Description:** Dataset with intentionally missing salary and email values and date_as_string

**Detection Metrics:**
- True Positives: 2
- False Positives: 0
- False Negatives: 0
- Precision: 1.0
- Recall: 1.0
- F1 Score: 1.0

**Performance:**
- Load Time: 0.005s
- Quality Time: 0.01s

---

### duplicate_records.csv

- **Format:** CSV
- **Category:** structured
- **Expected Issues:** ['duplicate_rows', 'date_as_string']
- **Detected Issues:** ['duplicate_rows', 'date_as_string']
- **Quality Score:** 85.0/100
- **Completeness:** 100.0/100
- **Consistency:** 85.0/100
- **Validity:** 100.0/100
- **Description:** Dataset with intentionally duplicated record (row 2 and row 6 are identical) and date_as_string

**Detection Metrics:**
- True Positives: 2
- False Positives: 0
- False Negatives: 0
- Precision: 1.0
- Recall: 1.0
- F1 Score: 1.0

**Performance:**
- Load Time: 0.004s
- Quality Time: 0.015s

---

### outlier_dataset.csv

- **Format:** CSV
- **Category:** structured
- **Expected Issues:** ['outliers', 'date_as_string']
- **Detected Issues:** ['outliers', 'date_as_string']
- **Quality Score:** 75.0/100
- **Completeness:** 100.0/100
- **Consistency:** 100.0/100
- **Validity:** 80.0/100
- **Description:** Dataset with intentionally introduced outliers (age=95, salary=450000) and date_as_string

**Detection Metrics:**
- True Positives: 2
- False Positives: 0
- False Negatives: 0
- Precision: 1.0
- Recall: 1.0
- F1 Score: 1.0

**Performance:**
- Load Time: 0.006s
- Quality Time: 0.015s

---

### type_inconsistency.csv

- **Format:** CSV
- **Category:** structured
- **Expected Issues:** ['inconsistent_type', 'date_as_string']
- **Detected Issues:** ['inconsistent_type', 'date_as_string']
- **Quality Score:** 85.0/100
- **Completeness:** 100.0/100
- **Consistency:** 85.0/100
- **Validity:** 100.0/100
- **Description:** Dataset with intentionally introduced type inconsistency (age as string 'twenty-nine') and date_as_string

**Detection Metrics:**
- True Positives: 2
- False Positives: 0
- False Negatives: 0
- Precision: 1.0
- Recall: 1.0
- F1 Score: 1.0

**Performance:**
- Load Time: 0.004s
- Quality Time: 0.008s

---

### mixed_quality_dataset.csv

- **Format:** CSV
- **Category:** structured
- **Expected Issues:** ['missing_values', 'outliers', 'inconsistent_type', 'partial_duplicates', 'date_as_string']
- **Detected Issues:** ['partial_duplicates', 'missing_values', 'inconsistent_type', 'date_as_string']
- **Quality Score:** 60.0/100
- **Completeness:** 90.0/100
- **Consistency:** 70.0/100
- **Validity:** 100.0/100
- **Description:** Dataset with multiple intentionally introduced quality issues: missing values, outliers, type inconsistency, partial duplicates, and date_as_string

**Detection Metrics:**
- True Positives: 4
- False Positives: 0
- False Negatives: 1
- Precision: 1.0
- Recall: 0.8
- F1 Score: 0.889

**Performance:**
- Load Time: 0.006s
- Quality Time: 0.014s

---

### clean_dataset.json

- **Format:** JSON
- **Category:** semi-structured
- **Expected Issues:** ['date_as_string']
- **Detected Issues:** ['date_as_string']
- **Quality Score:** 95.0/100
- **Completeness:** 100.0/100
- **Consistency:** 100.0/100
- **Validity:** 100.0/100
- **Description:** Clean JSON dataset with date_as_string issue

**Detection Metrics:**
- True Positives: 1
- False Positives: 0
- False Negatives: 0
- Precision: 1.0
- Recall: 1.0
- F1 Score: 1.0

**Performance:**
- Load Time: 0.004s
- Quality Time: 0.015s

---

### quality_issues.json

- **Format:** JSON
- **Category:** semi-structured
- **Expected Issues:** ['missing_values', 'date_as_string']
- **Detected Issues:** ['missing_values', 'date_as_string']
- **Quality Score:** 75.0/100
- **Completeness:** 90.0/100
- **Consistency:** 100.0/100
- **Validity:** 100.0/100
- **Description:** JSON dataset with missing value (null salary) and date_as_string

**Detection Metrics:**
- True Positives: 2
- False Positives: 0
- False Negatives: 0
- Precision: 1.0
- Recall: 1.0
- F1 Score: 1.0

**Performance:**
- Load Time: 0.006s
- Quality Time: 0.015s

---

### clean_dataset.xml

- **Format:** XML
- **Category:** semi-structured
- **Expected Issues:** ['date_as_string', 'inconsistent_type']
- **Detected Issues:** ['inconsistent_type', 'date_as_string']
- **Quality Score:** 65.0/100
- **Completeness:** 100.0/100
- **Consistency:** 55.0/100
- **Validity:** 100.0/100
- **Description:** Clean XML dataset with date_as_string and some type inconsistency from XML parsing

**Detection Metrics:**
- True Positives: 2
- False Positives: 0
- False Negatives: 0
- Precision: 1.0
- Recall: 1.0
- F1 Score: 1.0

**Performance:**
- Load Time: 0.004s
- Quality Time: 0.009s

---

### clean_document.txt

- **Format:** TXT
- **Category:** unstructured
- **Expected Issues:** []
- **Detected Issues:** []
- **Quality Score:** 100.0/100
- **Completeness:** 0.0/100
- **Consistency:** 0.0/100
- **Validity:** 0.0/100
- **Description:** Clean text document with no quality issues

**Detection Metrics:**
- True Positives: 0
- False Positives: 0
- False Negatives: 0
- Precision: 0
- Recall: 0
- F1 Score: 0

**Performance:**
- Load Time: 0.002s
- Quality Time: 0.0s

---

### poor_quality_document.txt

- **Format:** TXT
- **Category:** unstructured
- **Expected Issues:** ['special_characters', 'repetitive_content']
- **Detected Issues:** []
- **Quality Score:** 100.0/100
- **Completeness:** 0.0/100
- **Consistency:** 0.0/100
- **Validity:** 0.0/100
- **Description:** Poor quality text document with encoding issues, repetition, and special characters

**Detection Metrics:**
- True Positives: 0
- False Positives: 0
- False Negatives: 2
- Precision: 0
- Recall: 0.0
- F1 Score: 0

**Performance:**
- Load Time: 0.0s
- Quality Time: 0.0s

---

