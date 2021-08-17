from datetime import date
from os import environ

from sqlalchemy import Column, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import (
	BigInteger, Boolean, Date, Integer, SmallInteger, String
)

from .grades import Grades

Base = declarative_base()


class Fucker(Base):
	"""Rock fucking person."""

	__tablename__ = 'fuckers'

	tg_id = Column(BigInteger, primary_key=True, autoincrement=False)
	username = Column(String, nullable=False)
	league = Column(Integer, nullable=False, default=Grades.white.value)
	rating = Column(Integer, nullable=False, default=0)


class Problem(Base):
	"""A rock."""

	__tablename__ = 'problems'

	MAX_NUMBER = 200

	id = Column(Integer, primary_key=True)
	number = Column(SmallInteger, nullable=False)
	grade = Column(Integer, nullable=False)
	active = Column(Boolean, default=True)


class Solution(Base):
	"""A fuck."""

	__tablename__ = 'solutions'

	id = Column(Integer, primary_key=True)
	date_solved = Column(Date, nullable=False, default=date.today)
	with_style = Column(Boolean, nullable=False, default=False)
	problem_id = Column(Integer, ForeignKey(Problem.id), nullable=False)
	fucker_id = Column(BigInteger, ForeignKey(Fucker.tg_id), nullable=False)
	witness_1_id = Column(BigInteger, ForeignKey(Fucker.tg_id))
	witness_2_id = Column(BigInteger, ForeignKey(Fucker.tg_id))

	@hybrid_property
	def confirmed(self):
		return self.witness_1_id and self.witness_2_id

	@confirmed.expression
	def confirmed(self):
		return self.witness_1_id.isnot(None) & self.witness_2_id.isnot(None)


engine = create_engine(
	'sqlite:///fuckers.db', connect_args={'check_same_thread': False}
)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
