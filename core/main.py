from fastapi import FastAPI, status, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

expenses_db = [
    {
        "id": 1,
        "description": "Lunch",
        "amount": 12.5
    },
    {
        "id": 2,
        "description": "Bus ticket",
        "amount": 2.0
    },
    {
        "id": 3,
        "description": "Notebook",
        "amount": 5.75
    }
]

@app.get("/")
async def read_root():
    return {"Hello": "World"}

