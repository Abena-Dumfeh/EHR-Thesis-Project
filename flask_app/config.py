import os
from dotenv import load_dotenv

# Load variables from .env into environment
load_dotenv()

class Config:
    # Flask secret key
    SECRET_KEY = os.getenv('SECRET_KEY') or 'fallback-dev-key'

    # MySQL database config
    DB_HOST = os.getenv('DB_HOST')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_NAME = os.getenv('DB_NAME')

    # IPFS config (optional)
    IPFS_HOST = os.getenv('IPFS_HOST', 'localhost')
    IPFS_PORT = os.getenv('IPFS_PORT', 5001)

    # Other services (e.g., Fabric CLI paths, log levels) can also go here
