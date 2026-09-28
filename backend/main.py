from fastapi import FastAPI,HTTPException
from pydantic import BaseModel

app=FastAPI()

class Submission(BaseModel):
    problem_id: int
    code: str
    language: str

problems_list = [
    {
        "id": 1,
        "problem": "Two Sum",
        "difficulty": "Easy"
    },
    {
        "id": 2,
        "problem": "Binary Search",
        "difficulty": "Easy"
    },
    {
        "id": 3,
        "problem": "Maximum Subarray",
        "difficulty": "Medium"
    }
]
@app.get("/")
def root():
    return {"message":"Namaste backend is running"}


@app.get("/problems")
def get_problems():
    return{
        "problems":problems_list
    }


@app.get("/problems/{id}")
def get_problems(id:int):
    for problem in problems_list:
        if problem["id"]==id:
            return problem
    raise HTTPException(
        status_code=404,
        detail="No found"
    )

@app.get("/problem")
def get_problem(difficulty: str):

    matching_problem=[]
    for problem in problems_list:
        if problem["difficulty"]==difficulty:
            matching_problem.append(problem)

    if len(matching_problem)==0:
         return {"message": "This type is not present"} 

    return matching_problem


@app.post('/submissions',status_code=201)
def create_submissions(submission:Submission):
    return{
        "message":"Sumitted successfully",
        
    }
