
# Airtable Field Schema for AWS D1.1 Exam Questions

| Field Name             | Field Type     | Required | Description |
|------------------------|----------------|----------|-------------|
| question_id            | Single line text | ✅       | Unique ID (e.g., CWI-2025-001) |
| question               | Long text       | ✅       | The question stem |
| choice_a               | Single line text | ✅     | Option A |
| choice_b               | Single line text | ✅     | Option B |
| choice_c               | Single line text | ✅     | Option C |
| choice_d               | Single line text | ✅     | Option D |
| correct_answer         | Single select (A–D) | ✅  | One correct choice |
| clause_reference       | Single line text | ✅     | AWS D1.1:2025 Clause/Table (e.g., 4.3.7) |
| clause_type            | Single select   | ✅       | General / Design / Qualification / Fabrication / Inspection |
| difficulty             | Single select   | ✅       | Easy / Medium / Hard |
| bloom_level            | Single select   | ✅       | Knowledge / Comprehension / Application / Analysis / Evaluation |
| primary_keyword        | Single line text | ✅     | Main technical term |
| secondary_keywords     | Multi-select    | ✅       | Conditions/exceptions |
| distractor_type_a      | Single select   | Optional| Type of error in choice A |
| distractor_type_b      | Single select   | Optional| Type of error in choice B |
| distractor_type_c      | Single select   | Optional| Type of error in choice C |
| distractor_type_d      | Single select   | Optional| Type of error in choice D |
| drift_alert            | Checkbox        | Optional| True if clause changed from previous versions |
| answer_rationale       | Long text       | ✅       | Explanation for correct answer and distractors |
| lookup_recipe          | Long text       | Optional| Steps to locate answer in AWS D1.1:2025 |
