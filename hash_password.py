from werkzeug.security import generate_password_hash

# ✅ Enter your password
plain_text_password = "Mehek123"

# ✅ Hash the password
hashed_password = generate_password_hash(plain_text_password)

# ✅ Print the hashed password
print("Hashed Password:", hashed_password)
