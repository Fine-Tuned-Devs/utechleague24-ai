from fastapi import FastAPI, Depends
from starlette.middleware.cors import CORSMiddleware

from api.models.requests import ProcessRequest
from application.langchain_lib import process_user_prompt
from api.auth import get_current_user
from api.auth import router as auth_router
from db.database import initialize_database
from db.models.user import User
from db.repositories.user_repository import create_message

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.on_event("startup")
async def on_startup():
    await initialize_database()


@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI and RAG backend application"}


@app.post("/process/")
async def process(input_data: ProcessRequest, user: User = Depends(get_current_user)):
    message_id = await create_message(user.username, input_data.input_text)
    result = await process_user_prompt(input_data.input_text, user.username, message_id)
    return {"processed_text": result}


app.include_router(auth_router, prefix="/auth", tags=["auth"])
