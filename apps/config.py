import os
from pathlib import Path
import dotenv

dotenv.load_dotenv()
basedir = Path(__file__).parent.parent


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY")


class LocalConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    JSON_AS_ASCII = False
    JSONIFY_PRETTYPRINT_REGULAR = True


class TestingConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = str(Path(basedir, "tests", "detector", "images"))
    JSON_AS_ASCII = False


config = {
    "testing": TestingConfig,
    "local": LocalConfig,
}
