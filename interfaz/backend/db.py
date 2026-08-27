#from sqlalchemy import create_engine

#engine = create_engine(
#    "mysql+pymysql://root:emplea@localhost/emplea"
#)

import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_SSL_CA = os.path.join(BASE_DIR, "ca.pem")

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    connect_args={
        "ssl": {
            "ca": DB_SSL_CA
        }
    },
    pool_pre_ping=True
)