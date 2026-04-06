import os
import sys

def resource_path(relative_path):
    ## Get absolute path to resource for dev and py installer
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_db_name():
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(sys.executable), "scemas.db")
    return "scemas.db"