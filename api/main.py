from fastapi import FastAPI
from application.langchain_app import process_text

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI and LangChain application"}


@app.post("/process/")
def process(input_text: str):
    result = process_text(input_text)
    return {"processed_text": result}
