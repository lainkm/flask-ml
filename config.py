import os

basedir = os.path.abspath(os.path.dirname(__file__))

# 栗子
SQLALCHEMY_DATABASE_URL = 'mssql+pymssql://user:password@localhost:3306/dbname'
