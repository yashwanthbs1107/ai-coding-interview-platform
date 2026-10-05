from database import SessionLocal
from models import Problem
from database import engine
from models import Base,Submission
Base.metadata.create_all(bind=engine)

print("Tables created!")
# db = SessionLocal()

# problems = db.query(Problem).filter(Problem.difficulty=="Easy").all()
# new_problem=Problem(problem="valid parentheses",difficulty="Easy")
# db.add(new_problem)
# db.commit()
# print("problem inserted")
# for problem in problems:
#     print(problem.id, problem.problem, problem.difficulty)
# problem=db.query(Problem).filter(Problem.problem=="valid parentheses").first()
# problem.difficulty="Medium"
# db.commit()

# problem=db.query(Problem).filter(Problem.problem=='valid parentheses').first()
# db.delete(problem)
# db.commit()
# db.close()


db=SessionLocal()

new_submission=Submission(
    problem_id=1,
    code="print('Hello')",
    language="python",
    status="pending"
)

db.add(new_submission)
db.commit()
db.close()