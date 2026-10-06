
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from auth import hash_password, verify_password
from database import get_db
from models import Problem, Submission, Users
from jwt_utils import create_access_token, verify_access_token
import json
import subprocess
import tempfile
import os
from rag_service import get_rag_context
app = FastAPI()


# -------------------------
# Security
# -------------------------

security = HTTPBearer()


# -------------------------
# JWT - Current User
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


# -------------------------
# Pydantic Schemas
# -------------------------

class SubmissionCreate(BaseModel):
    problem_id: int
    code: str
    language: str


class RunRequest(BaseModel):
    input: str = ""

class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


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
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
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
        user_id=current_user.id,
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

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# -------------------------
# Protected /me
# -------------------------

@app.get("/me")
def get_me(
    current_user: Users = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }


@app.get("/submissions")
def get_my_submissions(
    db:Session=Depends(get_db),
    current_user:Users=Depends(get_current_user)
):
    submissions=db.query(Submission).filter(
        Submission.user_id==current_user.id
    ).all()
    if not submissions:
        raise HTTPException(
            status_code=404,
            detail="No Submissions Found"
        )
    return submissions


@app.post("/submissions/{submission_id}/run")
def run_submission(
    submission_id: int,
    request: RunRequest,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    submission = db.query(Submission).filter(
        Submission.id == submission_id
    ).first()

    if not submission:
        raise HTTPException(
            status_code=404,
            detail="Submission not found"
        )

    if submission.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to run this submission"
        )

    with tempfile.TemporaryDirectory() as temp_dir:

        source_file = os.path.join(temp_dir, "main.py")

        with open(source_file, "w") as file:
            file.write(submission.code)

        submission.status = "running"
        db.commit()

        try:
            result = subprocess.run(
                ["python", source_file],
                input=request.input,
                capture_output=True,
                text=True,
                timeout=5
            )

            output = result.stdout
            error = result.stderr

            if error:
                lines = error.splitlines()

                if lines and lines[0].startswith("  File"):
                    lines.pop(0)

                error = "\n".join(lines)

            if result.returncode == 0:
                submission.status = "completed"
            else:
                submission.status = "failed"

            submission.output = output
            submission.error = error

            db.commit()
            db.refresh(submission)

            return {
                "id": submission.id,
                "status": submission.status,
                "output": submission.output,
                "error": submission.error
            }

        except subprocess.TimeoutExpired:
            submission.status = "timeout"
            submission.output = ""
            submission.error = "Execution timed out after 5 seconds."

            db.commit()
            db.refresh(submission)

            return {
                "id": submission.id,
                "status": submission.status,
                "output": submission.output,
                "error": submission.error
            }


@app.post("/submissions/{submission_id}/analyze")
def analyze_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    submission = db.query(Submission).filter(
        Submission.id == submission_id
    ).first()

    if not submission:
        raise HTTPException(
            status_code=404,
            detail="Submission not found"
        )

    if submission.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to analyze this submission"
        )

    problem = db.query(Problem).filter(
        Problem.id == submission.problem_id
    ).first()

    if not problem:
        raise HTTPException(
            status_code=404,
            detail="Problem not found"
        )

    # Retrieve relevant knowledge from Pinecone
    rag_context = get_rag_context(problem.problem)

    prompt = f"""
You are an AI coding interview assistant.

Analyze the user's coding solution using the problem
and the relevant knowledge retrieved from the knowledge base.

Problem:
{problem.problem}

User's Code:
{submission.code}

Relevant Knowledge:
{rag_context}

Return ONLY valid JSON in exactly this format:

{{
    "approach": "...",
    "time_complexity": "...",
    "space_complexity": "...",
    "issues": "...",
    "suggestions": "..."
}}

Rules:
- Keep each field concise.
- Analyze the user's actual code.
- Use the relevant knowledge when helpful.
- Do not include markdown.
- Do not include ```json.
"""

    from ai_service import ask_gemini

    analysis = ask_gemini(prompt)

    # Convert Gemini's JSON string into a Python dictionary
    try:
        analysis_json = json.loads(analysis)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="AI returned invalid JSON"
        )

    # Save AI feedback to database
    submission.ai_feedback = json.dumps(analysis_json)

    db.commit()
    db.refresh(submission)

    return {
        "submission_id": submission.id,
        "analysis": analysis_json
    }




@app.post("/submissions/{submission_id}/hint")
def get_hint(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    submission = db.query(Submission).filter(
        Submission.id == submission_id
    ).first()

    if not submission:
        raise HTTPException(
            status_code=404,
            detail="Submission not found"
        )

    if submission.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to get a hint"
        )

    problem = db.query(Problem).filter(
        Problem.id == submission.problem_id
    ).first()

    if not problem:
        raise HTTPException(
            status_code=404,
            detail="Problem not found"
        )

    rag_context = get_rag_context(problem.problem)

    prompt = f"""
You are a coding interview mentor.

Problem:
{problem.problem}

User's Code:
{submission.code}

Relevant Knowledge:
{rag_context}

Give the user ONE useful hint.

Rules:
- Do NOT provide the complete solution.
- Do NOT provide complete code.
- Do NOT reveal the final answer.
- Point the user toward the next idea they should consider.
- Keep the hint under 3 sentences.
- Return ONLY the hint text.
- Do not use JSON.
- Do not use markdown.
"""
    from ai_service import ask_gemini

    hint = ask_gemini(prompt)

    return {
        "submission_id": submission.id,
        "hint": hint
    }