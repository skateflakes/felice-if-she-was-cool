def contains_delete_template(content: str) -> bool:
    return "{{Delete" in content
