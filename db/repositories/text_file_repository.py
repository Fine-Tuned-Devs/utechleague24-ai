from typing import Optional
from bson import ObjectId
from db.database import text_files_collection
from db.models.text_file import TextFile


async def create_text_file(title: str, content: str) -> str:
    pdf_file_dict = {
        "title": title,
        "content": content,
        "_id": ObjectId()
    }
    result = await text_files_collection.insert_one(pdf_file_dict)
    return str(result.inserted_id)


async def find_text_by_title(title: str) -> Optional[TextFile]:
    pdf_file = await text_files_collection.find_one({"title": title})
    if pdf_file:
        pdf_file['fileId'] = str(pdf_file.pop('_id'))
        return TextFile(**pdf_file)
    return None
