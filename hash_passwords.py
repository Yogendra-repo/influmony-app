# hash_passwords.py
from streamlit_authenticator import Hasher

passwords = ["admin123", "demo123"]          # put your test passwords here
hashed_passwords = Hasher.hash_list(passwords)
print(hashed_passwords)
