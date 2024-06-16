import string, random

def random_tag(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))