import os


def get_abspath():
    return os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
