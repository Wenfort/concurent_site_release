import random
import string


def generate_password(password_size = 8):
    generated_password = str()
    acceptable_letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    for letter in range(password_size):
        generated_password += random.choice(acceptable_letters)

    return generated_password
