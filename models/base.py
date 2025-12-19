
from typing import Annotated
import uuid
from sqlalchemy import Integer, MetaData, String
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


int_pk = Annotated[int, mapped_column(Integer, primary_key=True, autoincrement=True)]
str_255 = Annotated[str, mapped_column(String(255))]

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


mysql_url = "mysql+pymysql://root:User1234@localhost:3306/hotel"
engine = create_engine(mysql_url)

My_session = sessionmaker(engine)

def generate_uuid():
    return str(uuid.uuid4())

uuid_pk = Annotated[str, mapped_column(String(36), primary_key= True, default= generate_uuid)]

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    })