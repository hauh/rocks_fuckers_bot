from datetime import date

from sqlalchemy import Column, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.types import BigInteger, Boolean, Date, Integer, String, SmallInteger

from .grades import Grades

Base = declarative_base()


class Fuckers(Base):
	__tablename__ = 'fuckers'

	tg_id = Column(BigInteger, primary_key=True, autoincrement=False)
	username = Column(String, nullable=False)
	league = Column(Integer, nullable=False, default=Grades.white.value)
	rating = Column(Integer, nullable=False, default=0)


class Problems(Base):
	__tablename__ = 'problems'

	MAX_NUMBER = 200

	id = Column(Integer, primary_key=True)
	number = Column(SmallInteger, nullable=False)
	grade = Column(Integer, nullable=False)
	active = Column(Boolean, default=True)
	first_ascent = Column(Date, nullable=False, default=date.today)
	first_fucker = Column(BigInteger, ForeignKey(Fuckers.tg_id), nullable=False)


class Solutions(Base):
	__tablename__ = 'solutions'

	id = Column(Integer, primary_key=True)
	ascent = Column(Date, nullable=False, default=date.today)
	problem = Column(Integer, ForeignKey(Problems.id), nullable=False)
	fucker = Column(BigInteger, ForeignKey(Fuckers.tg_id), nullable=False)
	witness = Column(BigInteger, ForeignKey(Fuckers.tg_id))


engine = create_engine(
	'sqlite:///fuckers.db', connect_args={'check_same_thread': False}
)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
