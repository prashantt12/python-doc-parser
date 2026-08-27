from app.services.document_service import _clamp_pagination


def test_clamp_pagination_enforces_limits() -> None:
    page, limit = _clamp_pagination(page=0, limit=500)
    assert page == 1
    assert limit == 100

    page, limit = _clamp_pagination(page=3, limit=0)
    assert page == 3
    assert limit == 1
