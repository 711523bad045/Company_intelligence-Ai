from llm.company_extractor import extract_company_profile
import json

sample_text = """
BGTS is a global IT services company providing digital transformation,
cloud solutions, and managed services to enterprise clients worldwide.
"""

result = extract_company_profile(sample_text)
print(json.dumps(result, indent=2))
