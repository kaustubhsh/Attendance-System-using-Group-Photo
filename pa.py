import hashlib
import os

salt = os.urandom(32) # Remember this
password = 'password123'

key = hashlib.pbkdf2_hmac(
    'sha256', # The hash digest algorithm for HMAC
    password.encode('utf-8'), # Convert the password to bytes
    salt, # Provide the salt
    100000, # It is recommended to use at least 100,000 iterations of SHA-256 
    #dklen=128 # Get a 128 byte key
)
print(key)
#password_to_check = 'password246' # The password provided by the user to check

# Use the exact same setup you used to generate the key, but this time put in the password to check
new_key = hashlib.pbkdf2_hmac(
    'sha256',password.encode('utf-8'), # Convert the password to bytes
    salt,100000
)
print(new_key)
if new_key == key:
    print('Password is correct')
else:
    print('Password is incorrect')
