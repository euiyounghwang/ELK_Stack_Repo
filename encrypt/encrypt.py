
import bcrypt

''' bcrypt is a password-hashing function '''

def encrypt(my_password):
    ''' encrypt'''
    # Generating Salt
    salt = bcrypt.gensalt(10)

    # Hashing Password
    hash_password = bcrypt.hashpw(
        password=my_password,
        salt=salt
    )
    
    print(f"Actual Password: {my_password.decode('utf-8')}")
    # Print Hashed Password
    print(f"Hashed Password: {hash_password.decode('utf-8')}")

    return hash_password


def comapre_decrypt(plain, hash_password):
    ''' comapre_decrypt'''
    result = bcrypt.checkpw(
        password=plain, 
        hashed_password=hash_password)
    print(result)


if __name__ == "__main__":
    encrypted_password = encrypt(b'1')
    comapre_decrypt(plain=b'11', hash_password=encrypted_password)
