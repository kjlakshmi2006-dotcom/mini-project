import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "adaptlearn.db")
SECRET_KEY = os.environ.get("SECRET_KEY", "adaptlearn-super-secret-key-2026")
DEBUG = True
