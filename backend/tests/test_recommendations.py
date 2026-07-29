from app.analytics.insights import get_recommendation, SEGMENT_RECOMMENDATIONS, DEFAULT_RECOMMENDATION


def test_known_segment_returns_its_recommendation():
    for segment_name, expected_text in SEGMENT_RECOMMENDATIONS.items():
        assert get_recommendation(segment_name) == expected_text


def test_unknown_segment_returns_default():
    assert get_recommendation("Some Made Up Segment") == DEFAULT_RECOMMENDATION


def test_none_segment_returns_default():
    assert get_recommendation(None) == DEFAULT_RECOMMENDATION


def test_empty_string_segment_returns_default():
    assert get_recommendation("") == DEFAULT_RECOMMENDATION
