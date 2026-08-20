from app.utils.text import clean_text, extract_keywords


def test_clean_text_collapses_spaces_and_blank_lines():
    raw = "Hello     world\n\n\nThis is a test"
    assert clean_text(raw) == "Hello world\nThis is a test"


def test_extract_keywords_counts_and_drops_single_chars():
    result = extract_keywords("The engine engine a torque")
    by_word = {item["word"]: item["count"] for item in result}
    assert by_word["engine"] == 2
    assert by_word["torque"] == 1
    assert "a" not in by_word
