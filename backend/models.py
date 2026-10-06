from sqlalchemy import Column, Integer, String, ForeignKey, Text

from database import Base




class Problem(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True)
    problem = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    code = Column(Text, nullable=False)
    language = Column(String, nullable=False)
    status = Column(String, nullable=False)
    ai_feedback=Column(Text,nullable=True)

class Users(Base):
    __tablename__="users"
    id=Column(Integer,primary_key=True)
    username=Column(String,nullable=False)
    email=Column(String,nullable=False)
    password=Column(String,nullable=False)