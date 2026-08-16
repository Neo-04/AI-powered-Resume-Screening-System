import httpx
import fitz

doc = fitz.open()
page = doc.new_page()
text = """John Doe
Email: john@example.com
Skills: Python, JavaScript, React, FastAPI, SQL
Education: B.Tech Computer Science, IIT Delhi
Experience: 4 years as Software Engineer at TechCorp
Projects: Built AI resume screening system using Python and FastAPI
Achievements: Led team of 5 developers
"""
page.insert_text((72, 72), text)
doc.save("_test_resume.pdf")
doc.close()

jd_text = """Senior Software Engineer
Required Skills: Python, JavaScript, React, FastAPI, Docker
Preferred Qualification: B.Tech in Computer Science
Experience: 3+ years
Keywords: leadership, communication, teamwork
"""

base = "http://127.0.0.1:8000"
with httpx.Client(base_url=base, timeout=60.0) as client:
    health = client.get("/health")
    print("health", health.status_code, health.json())

    with open("_test_resume.pdf", "rb") as f:
        r = client.post(
            "/upload-resume",
            files={"file": ("resume.pdf", f, "application/pdf")},
        )
    print("upload-resume", r.status_code)
    resume = r.json()
    print("resume_id", resume["resume_id"])

    r = client.post(f"/parse-resume/{resume['resume_id']}")
    print("parse-resume", r.status_code)
    parsed_resume = r.json()
    print("parsed name", parsed_resume.get("name"))

    r = client.post("/upload-jd", data={"text": jd_text})
    print("upload-jd", r.status_code)
    jd = r.json()
    print("jd_id", jd["jd_id"])

    r = client.post(f"/parse-jd/{jd['jd_id']}")
    print("parse-jd", r.status_code)
    parsed_jd = r.json()
    print("parsed role", parsed_jd.get("role"))

    r = client.post(
        "/match",
        json={"resume_id": resume["resume_id"], "jd_id": jd["jd_id"]},
    )
    print("match", r.status_code)
    match = r.json()
    print("match_score", match["match_score"])
    print("recommendation", match["recommendation"])
    print("skill_score", match["skill_score"])
    print("matched_skills", match["matched_skills"][:5])
