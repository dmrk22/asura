from daari_core.interview import review


def test_feedback_is_always_a_verbatim_transcript_quote():
    transcript = "I built a dashboard for our team. It reduced reporting time by 20%."
    result = review("Tell me about a project.", transcript)
    assert result.feedback
    assert all(item.quote in transcript for item in result.feedback)
    assert result.star["action"] is True
    assert result.star["result"] is True


def test_interview_requires_candidate_words():
    try:
        review("Question", "")
    except ValueError as exc:
        assert "transcript" in str(exc)
    else:
        raise AssertionError("empty transcript must not produce invented feedback")
