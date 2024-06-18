from fastapi import FastAPI, Depends
from application.langchain_app import process_text
from api.auth import get_current_user
from api.auth import router as auth_router

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI and LangChain application"}


@app.post("/process/", dependencies=[Depends(get_current_user)])
def process(input_text: str):
    result = process_text(input_text)
    return {"processed_text": result}


app.include_router(auth_router, prefix="/auth", tags=["auth"])
