from app.utils.auth import hash_password, verify_password


def test_password_hash_round_trip() -> None:
    password = "open-vg-password"

    password_hash = hash_password(password)

    assert password_hash != password
    assert verify_password(password, password_hash)
    assert not verify_password("wrong-password", password_hash)
