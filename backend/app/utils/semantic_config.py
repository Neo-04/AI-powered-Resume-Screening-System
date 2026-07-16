SEMANTIC_ENABLED = True
SEMANTIC_MODEL_NAME = "all-MiniLM-L6-v2"

# credit for one semantic match relative to a rule match (1.0)
SEMANTIC_MATCH_WEIGHT = 0.75

# cosine thresholds
SKILL_SIMILARITY_THRESHOLD = 0.60
KEYWORD_SIMILARITY_THRESHOLD = 0.45
QUALIFICATION_SIMILARITY_THRESHOLD = 0.55
EXPERIENCE_SIMILARITY_THRESHOLD = 0.45

# qualification points awarded on a semantic match (below the rule related-branch of score 6)
SEMANTIC_QUALIFICATION_SCORE = 4
