from passlib.context import CryptContext
from passlib.hash import pbkdf2_sha256
# def encrypt_password(password):
#     return pwd_context.encrypt(password)


# def check_encrypted_password(password, hashed):
#     return pwd_context.verify(password, hashed)


# pwd_context = CryptContext(
#         schemes=["pbkdf2_sha256"],
#         default="pbkdf2_sha256",
#         pbkdf2_sha256__default_rounds=30000
# )

# encrypt_password('abd')

 
hash = pbkdf2_sha256.encrypt("password", rounds=200000, salt_size=16)

# check_encrypted_password('abd',hash)
# from passlib.hash import pbkdf2_sha256
 
pbkdf2_sha256.verify("password", hash)

