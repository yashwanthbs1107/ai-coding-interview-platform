
from fastapi import FastAPI, HTTPException, Depends,BackgroundTasks, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from redis_client import redis_client
from auth import hash_password, verify_password
from database import get_db,SessionLocal
from models import Problem, Submission, Users, UserProblemProgress
from jwt_utils import create_access_token, verify_access_token
import json
import subprocess
import tempfile
import redis
import os
from rag_service import get_rag_context
import time
from fastapi import Request
from worker import ai_queue
app = FastAPI()


# -------------------------
# Security
# -------------------------

security = HTTPBearer()


# -------------------------
# JWT - Current User
# -------------------------
def rate_limit(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    window = int(time.time() // 60)
    key = f"rate_limit:{client_ip}:{window}"

    try:
        requests = redis_client.incr(key)

        if requests == 1:
            redis_client.expire(key, 60)

        if requests > 60:
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again in a minute."
            )

    except redis.RedisError:
        # If Redis is unavailable, allow the request for now.
        # This keeps the API available but disables rate limiting temporarily.
        pass


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

@app.get("/",dependencies=[Depends(rate_limit)])
def root():
    return {
        "message": "Namaste backend is running"
    }


# -------------------------
# Problems
# -------------------------

@app.get("/problems",dependencies=[Depends(rate_limit)])
def get_problems(
    difficulty: str | None = None,
    topic: str | None = None,
    db: Session = Depends(get_db)
):
    cache_key = f"problems:{topic or 'all'}:{difficulty or 'all'}"

    # 1. Check Redis
    try:
        cached_data = redis_client.get(cache_key)

        if cached_data:
            return json.loads(cached_data)

    except redis.RedisError:
        cached_data = None

    # 2. Cache miss → query PostgreSQL
    query = db.query(Problem)

    if difficulty:
        query = query.filter(Problem.difficulty == difficulty)

    if topic:
        query = query.filter(Problem.topic == topic)

    problems = query.all()

    if not problems:
        raise HTTPException(
            status_code=404,
            detail="No problems found"
        )

    # 3. Convert SQLAlchemy objects to JSON-friendly data
    problems_data = [
        {
            "id": problem.id,
            "problem": problem.problem,
            "topic": problem.topic,
            "difficulty": problem.difficulty,
            "description": problem.description,
            "examples": problem.examples,
            "constraints": problem.constraints,
            "test_cases": problem.test_cases
        }
        for problem in problems
    ]

    # 4. Store in Redis for 5 minutes
    try:
        redis_client.setex(
            cache_key,
            300,
            json.dumps(problems_data)
        )
    except redis.RedisError:
        pass

    # 5. Return data
    return problems_data


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
    cursor: int | None = None,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 100"
        )

    if cursor is not None and cursor < 1:
        raise HTTPException(
            status_code=400,
            detail="Cursor must be greater than 0"
        )

    query = db.query(Submission).filter(
        Submission.user_id == current_user.id
    )

    if cursor is not None:
        query = query.filter(Submission.id < cursor)

    submissions = (
        query
        .order_by(Submission.id.desc())
        .limit(limit + 1)
        .all()
    )

    has_more = len(submissions) > limit
    submissions = submissions[:limit]

    next_cursor = (
        submissions[-1].id
        if has_more and submissions
        else None
    )

    return {
        "count": len(submissions),
        "limit": limit,
        "next_cursor": next_cursor,
        "has_more": has_more,
        "submissions": submissions
    }



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



def run_submission_analysis(submission_id: int):
    # Create a separate database session for the background task
    db = SessionLocal()

    try:
        submission = (
            db.query(Submission)
            .filter(Submission.id == submission_id)
            .first()
        )

        if not submission:
            return

        problem = (
            db.query(Problem)
            .filter(Problem.id == submission.problem_id)
            .first()
        )

        if not problem:
            return

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
        analysis_json = json.loads(analysis)

        submission.ai_feedback = json.dumps(analysis_json)
        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()



@app.post("/submissions/{submission_id}/analyze", status_code=202)
def analyze_submission(
    submission_id: int,
    background_tasks: BackgroundTasks,
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

    ai_queue.enqueue(
    "main.run_submission_analysis",
    submission_id
)

    return {
        "submission_id": submission_id,
        "status": "processing",
        "message": "AI analysis has been scheduled."
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


@app.post("/submissions/{submission_id}/submit")
def submit_solution(
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
            detail="You are not authorized to submit this solution"
        )

    problem = db.query(Problem).filter(
        Problem.id == submission.problem_id
    ).first()

    if not problem:
        raise HTTPException(
            status_code=404,
            detail="Problem not found"
        )

    try:
        test_cases = json.loads(problem.test_cases)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Invalid test case format"
        )

    submission.status = "running"
    db.commit()

    results = []

    with tempfile.TemporaryDirectory() as temp_dir:

        source_file = os.path.join(temp_dir, "main.py")

        with open(source_file, "w") as file:
            file.write(submission.code)

        for index, test_case in enumerate(test_cases, start=1):

            try:
                result = subprocess.run(
                    ["python", source_file],
                    input=test_case["input"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                actual_output = result.stdout.strip()
                expected_output = test_case["expected_output"].strip()

                passed = (
                    result.returncode == 0
                    and actual_output == expected_output
                )

                results.append({
                    "test_case": index,
                    "passed": passed,
                    "input": test_case["input"],
                    "expected_output": expected_output,
                    "actual_output": actual_output
                })

                if not passed:
                    submission.status = "failed"
                    db.commit()

                    return {
                        "submission_id": submission.id,
                        "status": "failed",
                        "solved": False,
                        "results": results
                    }

            except subprocess.TimeoutExpired:

                submission.status = "timeout"
                db.commit()

                return {
                    "submission_id": submission.id,
                    "status": "timeout",
                    "solved": False,
                    "results": results,
                    "error": "Execution timed out after 5 seconds."
                }

    # All test cases passed
    submission.status = "passed"

    progress = db.query(UserProblemProgress).filter(
        UserProblemProgress.user_id == current_user.id,
        UserProblemProgress.problem_id == submission.problem_id
    ).first()

    if progress:
        progress.solved = 1
    else:
        progress = UserProblemProgress(
            user_id=current_user.id,
            problem_id=submission.problem_id,
            solved=1
        )
        db.add(progress)

    db.commit()

    return {
        "submission_id": submission.id,
        "status": "passed",
        "solved": True,
        "results": results
    }



@app.get("/test-redis")
def test_redis():
    try:
        value = redis_client.get("test")
        return {"redis": value}
    except redis.RedisError as e:
        return {
            "redis": "unavailable",
            "error": type(e).__name__
        }