from passlib.hash import bcrypt

password = "granjacerdo"
hash_stored = "<>"

print("Verificación:", bcrypt.verify(password, hash_stored))
