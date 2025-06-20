from decouple import Config, RepositoryEnv
from backend.utils.timedelta import parse_timespan
import os
import logging

config = Config(RepositoryEnv("local.env"))

if os.getenv("ENVIRONMENT") == "STAGE":
    config = Config(RepositoryEnv("stage.env"))

if os.getenv("ENVIRONMENT") == "PRODUCTION":
    config = Config(RepositoryEnv("production.env"))

CORS_ORIGIN = config.get("CORS_ORIGIN", default="*")
MONGO_URI = config.get("MONGO_URI")
PORT = config.get("PORT", default=5000, cast=int)

JWT_ACCESS_EXPIRY = parse_timespan(config.get("JWT_ACCESS_EXPIRY"))
JWT_REFRESH_EXPIRY = parse_timespan(config.get("JWT_REFRESH_EXPIRY"))
JWT_ACCESS_KEY = config.get("JWT_ACCESS_KEY", cast=str)
JWT_REFRESH_KEY = config.get("JWT_REFRESH_KEY", cast=str)

SECRET_OR_KEY = config.get("SECRET_OR_KEY", cast=str)

STORE_DIR = os.path.join(os.path.dirname(__file__), "..", "store")

ASTRA_DB_SECRET_KEY = config.get("ASTRA_DB_SECRET_KEY", cast=str)
ASTRA_DB_ENDPOINT = config.get("ASTRA_DB_ENDPOINT", cast=str)
ASTRA_DB_KEYSPACE  = config.get("ASTRA_DB_KEYSPACE", cast=str)
GEMINI_API_KEY = config.get("GEMINI_API_KEY", cast=str)

