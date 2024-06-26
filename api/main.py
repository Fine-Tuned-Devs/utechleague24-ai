from fastapi import FastAPI, Depends
from starlette.middleware.cors import CORSMiddleware

from api.models.requests import ProcessRequest
from application.langchain_lib import process_user_prompt
from api.auth import get_current_user
from api.auth import router as auth_router
from db.database import initialize_database
from db.models.user import User
from db.repositories.user_repository import create_message, get_last_n_messages, get_all_messages_by_username

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
    return {"message": "Welcome"}


@app.post("/process/")
async def process(input_data: ProcessRequest, user: User = Depends(get_current_user)):
    await create_message(user.username, input_data.input_text, True)
    result = await process_user_prompt(input_data.input_text, user.username)
    await create_message(user.username, result['result'].content, False)
    return {"processed_text": result}


@app.get("/user/last_messages/{n}")
async def get_last_messages_n(n: int, user: User = Depends(get_current_user)):
    return {"messages": await get_last_n_messages(user.username, n)}


@app.get("/user/last_messages/")
async def get_last_messages(user: User = Depends(get_current_user)):
    return {"messages": await get_all_messages_by_username(user.username)}


app.include_router(auth_router, prefix="/auth", tags=["auth"])
