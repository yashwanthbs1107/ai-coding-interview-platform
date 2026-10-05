from jwt_utils import create_access_token, verify_access_token

token = create_access_token({
    "sub": "2"
})

print("TOKEN:")
print(token)

print("\nDECODED:")
print(verify_access_token(token))