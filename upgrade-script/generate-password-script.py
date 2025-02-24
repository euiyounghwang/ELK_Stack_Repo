
import random
import string

def generate_password():
    # length = random.randint(8, 16)
    length = 12
    # characters = string.ascii_letters + string.digits + string.punctuation
    characters = string.ascii_letters + string.digits + '@'
    password = ''.join(random.choice(characters) for i in range(length))
    return password


if __name__ == "__main__":
    
    '''
    (.venv) ➜  python ./upgrade-script/generate-password-script.py
    '''
    print("Random password is:", generate_password())