def test_fastapi_application_imports() -> None:
    from app.main import app

    assert app.title
