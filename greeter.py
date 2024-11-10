import os

def greet(username=None):
    username = username or os.environ.get('USER', 'UNKNOWN')
    print(f'Hello, {username}!')