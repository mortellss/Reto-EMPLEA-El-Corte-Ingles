from sqlalchemy import create_engine

engine = create_engine(
    "mysql+pymysql://root:emplea@localhost/emplea"
)