def is_question_allowed(text):
    allowed_keywords = ["ریاضی", "علوم", "فیزیک", "تاریخ"]  # قابل تغییر
    return any(word in text for word in allowed_keywords)
