import random
import string

def generate_random_string(n):
    characters = string.ascii_letters + string.digits  # a-zA-Z0-9
    return ''.join(random.choices(characters, k=n)).upper()
