import pytest

from backend.app.schemas.jd import JobDescription, ParsedJD
from backend.app.schemas.matching import MatchResult
from backend.app.schemas.resume import ParsedResume
from backend.app.services import (jd_parser, jd_service, matching_service,
                                  qualification_matcher, resume_parser,
                                  score_calculator, semantic_matcher)
from backend.app.utils import qualifications

W = qualification_matcher.QUALIFICATION_WEIGHT


def _assess(degree, branch, jd_text):
    quals = qualifications.extract_qualifications(jd_text)
    return qualification_matcher.assess(degree, branch, quals, jd_text)


# 1. degree missing, branch present -> full degree credit, branch evaluated
@pytest.mark.parametrize(
    "degree,branch,jd_text,branch_pts",
    [
        ("B.Sc", "Statistics", "Candidates from Statistics or Mathematics", 6),
        ("MBA", "Marketing", "Open to Human Resources backgrounds", 4),
        ("B.Tech", "Civil Engineering", "Mechanical Engineering only", 0),
    ],
)
def test_degree_missing_branch_present(degree, branch, jd_text, branch_pts):
    a = _assess(degree, branch, jd_text)
    assert a.degree_score == 9
    assert a.branch_score == branch_pts
    assert a.score == 9 + branch_pts


# 2. branch missing, degree present -> full branch credit, degree evaluated
@pytest.mark.parametrize(
    "degree,jd_text,degree_pts",
    [
        ("MBA", "MBA required", 9),
        ("B.Com", "Bachelor's degree required", 6),
        ("BCA", "M.Tech required", 0),
    ],
)
def test_branch_missing_degree_present(degree, jd_text, degree_pts):
    a = _assess(degree, "Finance", jd_text)
    assert a.branch_score == 6
    assert a.degree_score == degree_pts
    assert a.score == degree_pts + 6


# 3. both missing
def test_both_missing_scores_full():
    a = _assess("B.A.", "Psychology", "We are hiring a analyst for our team.")
    assert (a.degree_score, a.branch_score, a.score) == (9, 6, 15)
    assert a.matched is True


# 4. both present and matching, across unrelated domains
@pytest.mark.parametrize(
    "degree,branch,jd_text",
    [
        ("B.Tech", "Computer Science", "B.Tech in Computer Science"),
        ("M.Com", "Accounting", "M.Com in Accounting"),
        ("B.Sc", "Physics", "B.Sc in Physics"),
        ("MBA", "Marketing", "MBA in Marketing"),
        ("B.E.", "Civil Engineering", "B.E. in Civil Engineering"),
    ],
)
def test_both_present_and_matching(degree, branch, jd_text):
    a = _assess(degree, branch, jd_text)
    assert a.score == W
    assert a.matched is True


# 5. degree matches, branch does not
@pytest.mark.parametrize(
    "degree,branch,jd_text",
    [
        ("B.Tech", "Civil Engineering", "B.Tech in Computer Science"),
        ("M.Sc", "Chemistry", "M.Sc in Economics"),
        ("MBA", "Finance", "MBA in Psychology"),
    ],
)
def test_degree_matches_branch_does_not(degree, branch, jd_text):
    a = _assess(degree, branch, jd_text)
    assert a.degree_score == 9
    assert a.branch_score == 0
    assert a.score == 9


# 6. branch matches, degree does not
@pytest.mark.parametrize(
    "degree,branch,jd_text",
    [
        ("B.Sc", "Data Science", "M.Tech in Data Science"),
        ("B.Com", "Finance", "MBA in Finance"),
        ("BCA", "Computer Science", "B.Tech in Computer Science"),
    ],
)
def test_branch_matches_degree_does_not(degree, branch, jd_text):
    a = _assess(degree, branch, jd_text)
    assert a.degree_score == 0
    assert a.branch_score == 6
    assert a.score == 6
    assert a.matched is True


# 7. related branches get the partial score, in several unrelated groups
@pytest.mark.parametrize(
    "branch,jd_text",
    [
        ("Information Technology", "B.Tech in Computer Science"),
        (
            "Electronics and Communication Engineering",
            "B.Tech in Electrical Engineering",
        ),
        ("Aerospace Engineering", "B.Tech in Mechanical Engineering"),
        ("Chemistry", "B.Tech in Chemical Engineering"),
        ("Statistics", "B.Tech in Mathematics"),
    ],
)
def test_related_branch_partial_score(branch, jd_text):
    a = _assess("B.Tech", branch, jd_text)
    assert a.branch_score == 4
    assert a.score == 13


# 8. completely unrelated qualification
@pytest.mark.parametrize(
    "degree,branch,jd_text",
    [
        ("B.Com", "Finance", "M.Tech in Mechanical Engineering"),
        ("B.A.", "Psychology", "B.Tech in Computer Science"),
        ("BCA", "Computer Science", "M.Com in Accounting"),
    ],
)
def test_unrelated_qualification_scores_zero(degree, branch, jd_text):
    a = _assess(degree, branch, jd_text)
    assert a.score == 0
    assert a.matched is False


# 9. degree equivalence and hierarchy stay generic
@pytest.mark.parametrize(
    "degree,jd_text,expected",
    [
        ("B.E.", "B.Tech required", 9),  # equivalence group
        ("M.E.", "M.Tech required", 9),
        ("B.Tech", "Bachelor's degree", 6),  # generic level match
        ("MBA", "Master's degree", 6),
        ("B.Sc", "Master's degree", 0),  # level mismatch
    ],
)
def test_degree_rules_generic(degree, jd_text, expected):
    a = _assess(degree, "", jd_text)
    assert a.degree_score == expected


def test_score_always_within_weight_across_domains():
    degrees = [
        "B.Tech",
        "B.E.",
        "B.Sc",
        "BCA",
        "B.Com",
        "B.A.",
        "M.Tech",
        "M.Sc",
        "MCA",
        "MBA",
        "",
    ]
    branches = [
        "Computer Science",
        "Information Technology",
        "Electrical Engineering",
        "Mechanical Engineering",
        "Civil Engineering",
        "Mathematics",
        "Statistics",
        "Finance",
        "Commerce",
        "Psychology",
        "",
    ]
    for jd_text in [
        "B.Tech in Computer Science",
        "MBA in Finance",
        "Bachelor's degree",
        "Nothing stated",
    ]:
        for d in degrees:
            for b in branches:
                a = _assess(d, b, jd_text)
                assert 0 <= a.score <= W
                assert a.score == a.degree_score + a.branch_score


def test_no_branch_specific_conditions_in_matcher_source():
    import inspect

    source = inspect.getsource(qualification_matcher)
    for literal in (
        "Electrical",
        "Computer Science",
        "Information Technology",
        "Software Engineering",
        "Electronics",
        "Mechanical",
    ):
        assert literal not in source


def test_components_sum_to_match_score():
    scores = score_calculator.calculate_scores(
        skill_credit=2,
        required_skill_count=4,
        experience_match=True,
        qualification_score=9,
        soft_credit=2,
        jd_keyword_count=5,
    )
    assert scores.qualification == 9
    assert (
        scores.skill + scores.experience + scores.qualification + scores.soft
        == scores.total
    )


def test_qualification_component_not_scaled():
    scores = score_calculator.calculate_scores(
        skill_credit=4,
        required_skill_count=4,
        experience_match=True,
        qualification_score=15,
        soft_credit=5,
        jd_keyword_count=5,
    )
    assert (scores.skill, scores.experience, scores.qualification, scores.soft) == (
        50,
        30,
        15,
        5,
    )
    assert scores.total == 100


def _seed(monkeypatch, jd_text, degree, branch):
    quals = qualifications.extract_qualifications(jd_text)
    resume = ParsedResume(
        resume_id="r1",
        skills=["Python"],
        education=[f"{degree} {branch}"],
        degree=degree,
        branch=branch,
    )
    jd = ParsedJD(
        jd_id="j1",
        required_skills=["Python"],
        preferred_qualification=quals,
        experience="0-2 years",
        keywords=[],
    )
    monkeypatch.setitem(resume_parser.structured_resume_store, "r1", resume)
    monkeypatch.setitem(jd_parser.structured_jd_store, "j1", jd)
    monkeypatch.setitem(
        jd_service._jd_store,
        "j1",
        JobDescription(
            jd_id="j1", filename="jd.txt", char_count=len(jd_text), text=jd_text
        ),
    )


def _no_semantic(monkeypatch):
    monkeypatch.setattr(semantic_matcher, "match_skills", lambda *a, **k: [])
    monkeypatch.setattr(semantic_matcher, "match_keywords", lambda *a, **k: [])
    monkeypatch.setattr(
        semantic_matcher, "qualification_matches", lambda *a, **k: (False, 0.0)
    )


@pytest.mark.parametrize(
    "jd_text,degree,branch,expected",
    [
        ("M.Com in Accounting", "M.Com", "Accounting", 15),
        ("MBA in Finance", "B.Com", "Finance", 6),
        ("Mechanical Engineering graduates", "B.Tech", "Aerospace Engineering", 13),
        ("We are hiring an analyst.", "B.A.", "Psychology", 15),
    ],
)
def test_response_score_matches_assessment_across_domains(
    monkeypatch, jd_text, degree, branch, expected
):
    _seed(monkeypatch, jd_text, degree, branch)
    _no_semantic(monkeypatch)
    r = matching_service.run_match("r1", "j1")
    assert r.qualification_score == expected
    assert (
        r.skill_score + r.experience_score + r.qualification_score + r.soft_skill_score
        == r.match_score
    )


def test_semantic_runs_only_when_stated_requirement_scores_zero(monkeypatch):
    _seed(monkeypatch, "M.Tech in Mechanical Engineering", "B.Com", "Finance")
    calls = []
    monkeypatch.setattr(semantic_matcher, "match_skills", lambda *a, **k: [])
    monkeypatch.setattr(semantic_matcher, "match_keywords", lambda *a, **k: [])
    monkeypatch.setattr(
        semantic_matcher,
        "qualification_matches",
        lambda *a, **k: (calls.append(1), (True, 0.9))[1],
    )
    r = matching_service.run_match("r1", "j1")
    assert calls == [1]
    assert r.qualification_score == 4


def test_semantic_skipped_when_requirement_already_scores(monkeypatch):
    _seed(monkeypatch, "M.Com in Accounting", "M.Com", "Accounting")
    calls = []
    monkeypatch.setattr(semantic_matcher, "match_skills", lambda *a, **k: [])
    monkeypatch.setattr(semantic_matcher, "match_keywords", lambda *a, **k: [])
    monkeypatch.setattr(
        semantic_matcher,
        "qualification_matches",
        lambda *a, **k: (calls.append(1), (True, 0.9))[1],
    )
    matching_service.run_match("r1", "j1")
    assert calls == []


def test_semantic_never_runs_when_not_mentioned(monkeypatch):
    _seed(monkeypatch, "We are hiring an analyst.", "B.A.", "Psychology")
    calls = []
    monkeypatch.setattr(semantic_matcher, "match_skills", lambda *a, **k: [])
    monkeypatch.setattr(semantic_matcher, "match_keywords", lambda *a, **k: [])
    monkeypatch.setattr(
        semantic_matcher,
        "qualification_matches",
        lambda *a, **k: (calls.append(1), (True, 0.9))[1],
    )
    matching_service.run_match("r1", "j1")
    assert calls == []


def test_response_schema_unchanged(monkeypatch):
    _seed(monkeypatch, "Bachelor's degree required", "B.Com", "Finance")
    _no_semantic(monkeypatch)
    result = matching_service.run_match("r1", "j1")
    assert isinstance(result, MatchResult)
    assert set(result.model_dump().keys()) == {
        "match_score",
        "skill_score",
        "experience_score",
        "qualification_score",
        "soft_skill_score",
        "matched_skills",
        "missing_skills",
        "additional_skills",
        "qualification_match",
        "matching_reason",
        "experience_match",
        "matched_keywords",
        "recommendation",
    }
