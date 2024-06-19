import os

import dotenv

dotenv_path = dotenv.find_dotenv(filename='.env', raise_error_if_not_found=False)
dotenv.load_dotenv(dotenv_path=dotenv_path)


class JwtSettings:
    SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    ALGORITHM: str = os.getenv("JWT_ALGORITHM")
    EXPIRATION_SECONDS: int = int(os.getenv("JWT_EXPIRATION_SECONDS"))


class MongoDbSettings:
    MONGODB_URL: str = os.getenv("CONNECTION_STRINGS_MONGODB")
    MONGODB_DATABASE: str = "utechleague24-db"


jwt_settings = JwtSettings()
mongodb_settings = MongoDbSettings()
