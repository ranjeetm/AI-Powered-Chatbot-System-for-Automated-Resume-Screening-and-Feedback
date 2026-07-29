"""Structured extraction accuracy evaluation.

Measures skill F1, experience-years MAE, name/email exact match, degree F1,
and profile completeness on synthetic resumes. Acceptance thresholds: skill
macro-F1 >= 0.65, experience MAE <= 2.0 years, name exact match >= 80%, email
exact match >= 90%, degree macro-F1 >= 0.60, mean completeness >= 0.75.
"""

from __future__ import annotations

import statistics

from backend.extraction.structured_parser import StructuredResumeParser


def _normalize_values(values):
    normalized = set()
    for value in values or []:
        text = str(value).strip().lower()
        if not text:
            continue
        if "master of science" in text or "m.sc" in text:
            normalized.add("m.sc")
        elif "bachelor of science" in text or "b.sc" in text:
            normalized.add("b.sc")
        elif "b.tech" in text or "bachelor of technology" in text:
            normalized.add("b.tech")
        elif "mba" in text:
            normalized.add("mba")
        else:
            normalized.add(text)
    return normalized


def _f1(predicted, expected):
    predicted_set = _normalize_values(predicted)
    expected_set = _normalize_values(expected)
    tp = len(predicted_set & expected_set)
    precision = tp / len(predicted_set) if predicted_set else 0.0
    recall = tp / len(expected_set) if expected_set else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return precision, recall, f1


def _parse_resume(parser, resume_text, case_id):
    if hasattr(parser, "parse"):
        return parser.parse(resume_text)

    return parser.build_candidate_profile(
        {
            "file_name": f"{case_id}.txt",
            "category": "evaluation",
            "text": resume_text,
            "embedding": None,
        }
    )


class TestExtractionAccuracy:
    def test_skill_f1(self, eval_dataset):
        parser = StructuredResumeParser()
        f1_scores = []
        for case in eval_dataset["extraction_cases"]:
            profile = _parse_resume(parser, case["resume_text"], case["id"])
            precision, recall, f1 = _f1(
                profile.get("skills"),
                case["expected"]["skills"],
            )
            f1_scores.append(f1)
            print(
                f"{case['id']} skill_precision={precision:.2f} "
                f"skill_recall={recall:.2f} skill_f1={f1:.2f}"
            )

        macro_f1 = statistics.mean(f1_scores)
        print(f"skill_macro_f1={macro_f1:.2f}")
        assert macro_f1 >= 0.65

    def test_experience_years_mae(self, eval_dataset):
        parser = StructuredResumeParser()
        errors = []
        for case in eval_dataset["extraction_cases"]:
            profile = _parse_resume(parser, case["resume_text"], case["id"])
            predicted = profile.get("experience_years") or 0
            expected = case["expected"]["experience_years"]
            error = abs(predicted - expected)
            errors.append(error)
            print(
                f"{case['id']} predicted_years={predicted} "
                f"expected_years={expected} abs_error={error}"
            )

        mae = statistics.mean(errors)
        print(f"experience_years_mae={mae:.2f}")
        assert mae <= 2.0

    def test_name_email_exact_match(self, eval_dataset):
        parser = StructuredResumeParser()
        name_matches = 0
        email_matches = 0
        total = len(eval_dataset["extraction_cases"])

        for case in eval_dataset["extraction_cases"]:
            profile = _parse_resume(parser, case["resume_text"], case["id"])
            predicted_name = str(profile.get("candidate_name") or "").strip().lower()
            expected_name = case["expected"]["candidate_name"].strip().lower()
            predicted_email = str(profile.get("email") or "").strip().lower()
            expected_email = case["expected"]["email"].strip().lower()
            name_ok = predicted_name == expected_name
            email_ok = predicted_email == expected_email
            name_matches += int(name_ok)
            email_matches += int(email_ok)
            print(
                f"{case['id']} name_ok={name_ok} email_ok={email_ok} "
                f"predicted_name={predicted_name!r} predicted_email={predicted_email!r}"
            )

        name_accuracy = name_matches / total
        email_accuracy = email_matches / total
        print(f"name_accuracy={name_accuracy:.2f} email_accuracy={email_accuracy:.2f}")
        assert name_accuracy >= 0.80
        assert email_accuracy >= 0.90

    def test_degree_extraction(self, eval_dataset):
        parser = StructuredResumeParser()
        f1_scores = []
        for case in eval_dataset["extraction_cases"]:
            profile = _parse_resume(parser, case["resume_text"], case["id"])
            precision, recall, f1 = _f1(
                profile.get("degrees"),
                case["expected"]["degrees"],
            )
            f1_scores.append(f1)
            print(
                f"{case['id']} degree_precision={precision:.2f} "
                f"degree_recall={recall:.2f} degree_f1={f1:.2f}"
            )

        macro_f1 = statistics.mean(f1_scores)
        print(f"degree_macro_f1={macro_f1:.2f}")
        assert macro_f1 >= 0.60

    def test_completeness_score(self, eval_dataset):
        parser = StructuredResumeParser()
        fields = [
            "candidate_name",
            "email",
            "skills",
            "experience_years",
            "degrees",
            "job_titles",
        ]
        scores = []
        for case in eval_dataset["extraction_cases"]:
            profile = _parse_resume(parser, case["resume_text"], case["id"])
            filled = 0
            for field in fields:
                value = profile.get(field)
                if field == "experience_years":
                    filled += int(value is not None)
                else:
                    filled += int(bool(value))
            completeness = filled / len(fields)
            scores.append(completeness)
            print(f"{case['id']} completeness={completeness:.2f}")

        mean_completeness = statistics.mean(scores)
        print(f"mean_completeness={mean_completeness:.2f}")
        assert mean_completeness >= 0.75
