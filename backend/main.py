from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from auth import hash_password, verify_password
from database import get_db
from models import Problem, Submission, Users
from jwt_utils import create_access_token, verify_access_token


app = FastAPI()


# -------------------------
# OAuth2
# -------------------------

security = HTTPBearer()

# -------------------------
# Pydantic Schemas
# -------------------------

class SubmissionCreate(BaseModel):
    problem_id: int
    code: str
    language: str


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


# -------------------------
# JWT - Current User
# -------------------------



# -------------------------
# Root
# -------------------------

@app.get("/")
def root():
    return {
        "message": "Namaste backend is running"
    }


# -------------------------
# Problems
# -------------------------

@app.get("/problems")
def get_problems(
    difficulty: str | None = None,
    db: Session = Depends(get_db)
):
    if difficulty:
        problems = db.query(Problem).filter(
            Problem.difficulty == difficulty
        ).all()
    else:
        problems = db.query(Problem).all()

    if not problems:
        raise HTTPException(
            status_code=404,
            detail="No problems found"
        )

    return problems


@app.get("/problems/{id}")
def get_problem(
    id: int,
    db: Session = Depends(get_db)
):
    problem = db.query(Problem).filter(
        Problem.id == id
    ).first()

    if not problem:
        raise HTTPException(
            status_code=404,
            detail="Problem not found"
        )

    return problem


# -------------------------
# Submissions
# -------------------------

@app.post("/submissions", status_code=201)
def create_submission(
    submission: SubmissionCreate,
    db: Session = Depends(get_db)
):
    problem = db.query(Problem).filter(
        Problem.id == submission.problem_id
    ).first()

    if not problem:
        raise HTTPException(
            status_code=404,
            detail="Problem not found"
        )

    new_submission = Submission(
        problem_id=submission.problem_id,
        code=submission.code,
        language=submission.language,
        status="pending"
    )

    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)

    return new_submission


# -------------------------
# Register
# -------------------------

@app.post("/register", status_code=201)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    users = db.query(Users).filter(
        Users.email == user.email
    ).first()

    if users:
        raise HTTPException(
            status_code=409,
            detail="User already exists"
        )

    new_user = Users(
        username=user.username,
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully"
    }


# -------------------------
# Login
# -------------------------

@app.post("/login")
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    user = db.query(Users).filter(
        Users.email == login_data.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        login_data.password,
        user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token({
        "sub": str(user.id)
    })
    print("LOGIN TOKEN:")
    print(token)

    print("LOGIN TOKEN DECODE:")
    print(verify_access_token(token))
    return {
        "access_token": token,
        "token_type": "bearer"
    }


# -------------------------
# Protected /me
# -------------------------
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    payload = verify_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user = db.query(Users).filter(
        Users.id == int(user_id)
    ).first()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User doesn't exist"
        )

    return user


@app.get("/me")
def get_me(
    current_user: Users = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }