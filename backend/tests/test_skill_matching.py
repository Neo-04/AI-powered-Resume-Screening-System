import pytest

from backend.app.schemas.jd import JobDescription, ParsedJD
from backend.app.schemas.matching import MatchResult
from backend.app.schemas.resume import ParsedResume
from backend.app.services import (jd_parser, jd_service, matching_service,
                                  resume_parser, semantic_matcher,
                                  skill_matcher)
from backend.app.utils import skills_normalizer

WEIGHT = 0.75


def _seed(monkeypatch, resume_skills, required_skills):
    resume = ParsedResume(
        resume_id="r1",
        skills=resume_skills,
        degree="B.Tech",
        branch="Computer Science",
        education=["B.Tech Computer Science"],
    )
    jd = ParsedJD(
        jd_id="j1",
        required_skills=required_skills,
        preferred_qualification=[],
        experience="0-2 years",
        keywords=[],
    )
    monkeypatch.setitem(resume_parser.structured_resume_store, "r1", resume)
    monkeypatch.setitem(jd_parser.structured_jd_store, "j1", jd)
    monkeypatch.setitem(
        jd_service._jd_store,
        "j1",
        JobDescription(jd_id="j1", filename="jd.txt", char_count=1, text="Engineer"),
    )


def _semantic(monkeypatch, skill_hits=()):
    monkeypatch.setattr(
        semantic_matcher, "match_skills", lambda *a, **k: list(skill_hits)
    )
    monkeypatch.setattr(semantic_matcher, "match_keywords", lambda *a, **k: [])
    monkeypatch.setattr(
        semantic_matcher, "qualification_matches", lambda *a, **k: (False, 0.0)
    )
    monkeypatch.setattr(
        semantic_matcher, "experience_matches", lambda *a, **k: (False, 0.0)
    )


# 1. exact
def test_exact_match(monkeypatch):
    _seed(monkeypatch, ["Python", "SQL"], ["Python", "SQL"])
    _semantic(monkeypatch)
    r = matching_service.run_match("r1", "j1")
    assert r.missing_skills == []
    assert r.additional_skills == []
    assert r.skill_score == 50


# 2. alias / normalized
@pytest.mark.parametrize(
    "resume_skill,jd_skill",
    [
        ("Machine Learning", "ML"),
        ("NodeJS", "Node.js"),
        ("Postgres", "PostgreSQL"),
        ("JS", "JavaScript"),
    ],
)
def test_alias_match_gets_full_credit(monkeypatch, resume_skill, jd_skill):
    _seed(monkeypatch, [resume_skill], [jd_skill])
    _semantic(monkeypatch)
    r = matching_service.run_match("r1", "j1")
    assert r.missing_skills == []
    assert r.additional_skills == []
    assert r.skill_score == 50  # full weight, not 0.75


# 3 + 12. related-skill match (JS on resume, TS in JD)
def test_related_skill_match_reconciles_all_three_lists(monkeypatch):
    _seed(monkeypatch, ["JavaScript"], ["TypeScript"])
    _semantic(monkeypatch)
    r = matching_service.run_match("r1", "j1")
    assert "TypeScript" in r.matched_skills
    assert "TypeScript" not in r.missing_skills
    assert "JavaScript" not in r.additional_skills  # resume side consumed


@pytest.mark.parametrize(
    "resume_skill,jd_skill",
    [
        ("JavaScript", "TypeScript"),
        ("TypeScript", "JavaScript"),
        ("PyTorch", "TensorFlow"),
        ("MySQL", "PostgreSQL"),
        ("React", "Angular"),
    ],
)
def test_related_pairs_generic_and_bidirectional(monkeypatch, resume_skill, jd_skill):
    _seed(monkeypatch, [resume_skill], [jd_skill])
    _semantic(monkeypatch)
    r = matching_service.run_match("r1", "j1")
    assert r.missing_skills == []
    assert r.additional_skills == []


# 4 + 5 + 6. semantic match reconciles both sides
def test_semantic_match_removes_from_missing_and_additional(monkeypatch):
    _seed(monkeypatch, ["Containerization"], ["Docker"])
    _semantic(monkeypatch, [("Docker", "Containerization", 0.71)])
    r = matching_service.run_match("r1", "j1")
    assert "Docker" in r.matched_skills
    assert r.missing_skills == []
    assert r.additional_skills == []


# 7. rejected semantic match leaves both lists untouched
def test_rejected_semantic_match_leaves_lists_unchanged(monkeypatch):
    _seed(monkeypatch, ["Cooking"], ["Docker"])
    _semantic(monkeypatch, [])
    r = matching_service.run_match("r1", "j1")
    assert r.missing_skills == ["Docker"]
    assert r.additional_skills == ["Cooking"]
    assert r.skill_score == 0


# 8. related / semantic use 0.75, exact uses 1.0
def test_related_match_uses_partial_weight(monkeypatch):
    _seed(
        monkeypatch,
        ["Python", "SQL", "Docker", "JavaScript"],
        ["Python", "SQL", "Docker", "TypeScript"],
    )
    _semantic(monkeypatch)
    r = matching_service.run_match("r1", "j1")
    assert r.skill_score == round((3 + WEIGHT) / 4 * 50)  # 47, not 50


def test_semantic_match_uses_partial_weight(monkeypatch):
    _seed(
        monkeypatch,
        ["Python", "SQL", "Docker", "Containerization"],
        ["Python", "SQL", "Docker", "Podman"],
    )
    _semantic(monkeypatch, [("Podman", "Containerization", 0.8)])
    r = matching_service.run_match("r1", "j1")
    assert r.skill_score == round((3 + WEIGHT) / 4 * 50)


# 9. one resume skill is not consumed twice
def test_resume_skill_not_reused_across_jd_skills(monkeypatch):
    _seed(monkeypatch, ["JavaScript"], ["TypeScript", "Angular"])
    _semantic(monkeypatch)
    r = matching_service.run_match("r1", "j1")
    assert r.matched_skills.count("TypeScript") + r.matched_skills.count("Angular") == 1
    assert len(r.missing_skills) == 1
    assert r.additional_skills == []


def test_semantic_matcher_does_not_reuse_either_side():
    pairs = [("TS", "JS", 0.9), ("Angular", "JS", 0.8)]
    matched, missing, additional = ["x"], ["TS", "Angular"], ["JS"]
    accepted = matching_service._consume_pairs(
        [(j, r) for j, r, _ in pairs], matched, missing, additional
    )
    assert accepted == 1
    assert missing == ["Angular"]
    assert additional == []


# 10. same behaviour when scored repeatedly (ranking / batch flow)
def test_consistent_across_repeated_scoring(monkeypatch):
    _seed(monkeypatch, ["JavaScript"], ["TypeScript"])
    _semantic(monkeypatch)
    results = [matching_service.run_match("r1", "j1") for _ in range(3)]
    assert (
        len(
            {
                (
                    tuple(r.matched_skills),
                    tuple(r.missing_skills),
                    tuple(r.additional_skills),
                    r.match_score,
                )
                for r in results
            }
        )
        == 1
    )


# 11. unrelated skills still behave as before
def test_unrelated_skills_unchanged(monkeypatch):
    _seed(monkeypatch, ["Python", "Excel"], ["Python", "Kubernetes"])
    _semantic(monkeypatch)
    r = matching_service.run_match("r1", "j1")
    assert r.matched_skills == ["Python"]
    assert r.missing_skills == ["Kubernetes"]
    assert r.additional_skills == ["Excel"]


def test_related_skills_are_not_aliases():
    assert skills_normalizer.canonical_skill(
        "JavaScript"
    ) != skills_normalizer.canonical_skill("TypeScript")
    assert skills_normalizer.are_related_skills("JavaScript", "TypeScript")
    assert not skills_normalizer.are_related_skills("JavaScript", "Python")
    assert not skills_normalizer.are_related_skills(
        "React", "ReactJS"
    )  # identical, not related


def test_no_example_specific_conditionals_in_source():
    import inspect

    for module in (skill_matcher, matching_service, semantic_matcher):
        source = inspect.getsource(module)
        assert "JavaScript" not in source
        assert "TypeScript" not in source


def test_response_schema_unchanged(monkeypatch):
    _seed(monkeypatch, ["JavaScript"], ["TypeScript"])
    _semantic(monkeypatch)
    r = matching_service.run_match("r1", "j1")
    assert isinstance(r, MatchResult)
    assert set(r.model_dump().keys()) == {
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
