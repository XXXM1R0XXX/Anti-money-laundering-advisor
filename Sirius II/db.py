import hashlib

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
import random
import string
import uuid
Base = declarative_base()
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    api_key = Column(String(64), unique=True, autoincrement=False)
    login = Column(String(64), unique=True)
    password = Column(String(128))
class Database:
    def __init__(self):
        self.engine = create_engine('postgresql+psycopg2://postgres:postgres@localhost:5436/siriusii')
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def check_api_key(self, login, paaword):
        session = self.SessionLocal()
        password = self.hashing_password(paaword).hexdigest()
        user = session.query(User).filter(User.login == login, User.password == password).first()
        session.close()
        print(user.api_key)
        if user is None:
            return None
        return user.api_key
    def create_random_api_key(self):
        api_key = uuid.uuid4().hex
        print(api_key)
        return api_key
    def create_api_key(self, login, password):
        session = self.SessionLocal()
        password = self.hashing_password(password).hexdigest()
        user = session.query(User).filter(User.login == login, User.password == password).first()
        print(user)
        if user is None:
            return None
        else:
            api_key = self.create_random_api_key()
            user.api_key = api_key
            session.commit()
        return api_key
    def write_log(self, api_key, transaction_info):
        pass
    def register(self, login, password):
        session = self.SessionLocal()
        password = self.hashing_password(password).hexdigest()
        user = User(login=login, password=password)
        session.add(user)
        session.commit()
        session.close()
        return user
    def hashing_password(self, password):
        salt = 'devatdvasem'
        dataBase_password = password + salt
        hashed = hashlib.md5(dataBase_password.encode())
        return hashed
    def login(self, login, password):
        session = self.SessionLocal()
        password = self.hashing_password(password).hexdigest()
        user = session.query(User).filter(User.login == login, User.password == password).first()
        session.close()
        return user
    def auto_migrate(self):
        Base.metadata.create_all(self.engine)
