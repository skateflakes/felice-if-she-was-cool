import re

def contains_delete_template(content: str) -> bool:
    return bool(re.search(r"\{\{\s*delete\s*[\|}]", content, re.IGNORECASE))
