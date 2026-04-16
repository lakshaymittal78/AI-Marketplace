import os
os.environ["SECRET_KEY"] = "testsecret"
from app.utils.hashing import hash_password, verify_password
from app.utils.jwt import create_access_token, decode_access_token
def test_hashing():
    hashed = hash_password("password123")
    assert hashed != "password123"
    assert len(hashed) > 0
def test_verify_password():
    hashed = hash_password("password123")
    assert verify_password("password123", hashed) == True
    assert verify_password("wrongpassword", hashed) == False
def test_create_access_token():
    token = create_access_token(data={"user_id": 1})
    assert token is not None
    assert len(token) > 0
def test_decode_access_token():
    token = create_access_token(data={"user_id": 1})
    decoded = decode_access_token(token)
    assert decoded["user_id"] == 1