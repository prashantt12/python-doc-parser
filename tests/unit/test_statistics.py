from app.utils.statistics import compute_statistics
from app.utils.text import clean_text


def test_compute_statistics_on_cleaned_text():
    text = clean_text("Hello     world\n\n\nThis is a test")
    stats = compute_statistics(text)
    assert stats.word_count == 6
    assert stats.line_count == 2
    assert stats.paragraph_count == 2
    assert stats.unique_word_count == 6
    assert stats.average_word_length > 0


def test_compute_statistics_empty_text():
    stats = compute_statistics("")
    assert stats.word_count == 0
    assert stats.line_count == 0
    assert stats.paragraph_count == 0
    assert stats.average_word_length == 0.0
