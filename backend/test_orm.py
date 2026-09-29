from database import SessionLocal
from models import Problem

db = SessionLocal()

problems = db.query(Problem).filter(Problem.difficulty=="Easy").all()

for problem in problems:
    print(problem.id, problem.problem, problem.difficulty)

db.close()