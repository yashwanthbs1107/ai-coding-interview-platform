from sqlalchemy import UniqueConstraint, Column, Integer, String, ForeignKey, Text

from database import Base




class Problem(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True)
    problem = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    examples = Column(Text, nullable=False)
    constraints = Column(Text, nullable=False)
    test_cases = Column(Text, nullable=False)

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    code = Column(Text, nullable=False)
    language = Column(String, nullable=False)
    status = Column(String, nullable=False)
    ai_feedback = Column(Text, nullable=True)

class Users(Base):
    __tablename__="users"
    id=Column(Integer,primary_key=True)
    username=Column(String,nullable=False)
    email=Column(String,nullable=False)
    password=Column(String,nullable=False)



class UserProblemProgress(Base):
    __tablename__ = "user_problem_progress"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "problem_id",
            name="uq_user_problem_progress_user_problem"
        ),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        index=True,
        nullable=False
    )
    problem_id = Column(
        Integer,
        ForeignKey("problems.id"),
        index=True,
        nullable=False
    )
    solved = Column(Integer, default=0, nullable=False)