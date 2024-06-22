import os
import fitz  # PyMuPDF
from langchain_core.messages import HumanMessage
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

from application.pinecone_lib import PineconeHelper
from db.repositories.text_file_repository import find_text_by_title

# Set environment variables for API keys and endpoints
os.environ["AZURE_OPENAI_API_KEY"] = "70acd5849bdd4aaaa8560815c4d929de"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://uleague-openai.openai.azure.com/"
os.environ["AZURE_OPENAI_API_VERSION"] = "2024-02-01"
os.environ["CONNECTION_STRINGS_PINECONE"] = "a89ce7f5-0a4f-4c82-a7c2-5e4046753349"


def extract_text_from_pdf(pdf_path, chunk_size=5):
    """
    Extract text from PDF in chunks.

    Args:
        pdf_path (str): Path to the PDF file.
        chunk_size (int): Number of pages to process in each chunk.

    Returns:
        list: List of text chunks.
    """
    doc = fitz.open(pdf_path)
    text_chunks = []

    for page_num in range(0, len(doc), chunk_size):
        chunk_text = ""
        for page in doc[page_num:page_num + chunk_size]:
            chunk_text += page.get_text()
        text_chunks.append(chunk_text)

    return text_chunks


class EmbeddingsUtils:
    def __init__(self, api_key, endpoint, deployment, api_version):
        """
        Initialize Azure OpenAI Embeddings.
        """
        self.embeddings = AzureOpenAIEmbeddings(
            openai_api_key=api_key,
            azure_endpoint=endpoint,
            deployment=deployment,
            openai_api_version=api_version
        )

    def process_text_and_get_embeddings(self, text):
        """
        Process text and get embeddings using Azure OpenAI API.

        Args:
            text (str): Text to process.

        Returns:
            list: Embedding result.
        """
        embedding_result = self.embeddings.embed_query(text)
        return embedding_result


# Initialize utilities
utils = EmbeddingsUtils(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    deployment="emb_model",
    api_version=os.environ["AZURE_OPENAI_API_VERSION"]
)

gpt = AzureChatOpenAI(
    openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    azure_deployment="gpt3",
    model_version="0613",
)

ph = PineconeHelper()


def get_best_fit(prompt: str):
    vector = utils.process_text_and_get_embeddings(prompt)
    score = ph.query_vector("files", vector, 3, 3072)
    highest_scoring_match_id = ""
    highest_scoring_match = None
    for match in score.matches:
        # If highest_scoring_match is None or current match's score is higher, update it
        if highest_scoring_match is None or match['score'] > highest_scoring_match['score']:
            highest_scoring_match = match
            highest_scoring_match_id = match["id"]
    return highest_scoring_match_id


def get_best_fit_user_idx(prompt: str,username):
    vector = utils.process_text_and_get_embeddings(prompt)
    score = ph.query_vector("username", vector, 3, 3072)
    highest_scoring_match_id = ""
    highest_scoring_match = None
    for match in score.matches:
        # If highest_scoring_match is None or current match's score is higher, update it
        if highest_scoring_match is None or match['score'] > highest_scoring_match['score']:
            highest_scoring_match = match
            highest_scoring_match_id = match["id"]
    return highest_scoring_match_id


async def process_user_prompt(prompt: str, user_name: str,message_id: str):
    #ph.create_user_index(user_name+"--s--"+str(message_id), 3072)
    best_fit = get_best_fit(prompt)
    #best_fit_user_idx = get_best_fit_user_idx(prompt, user_name)
    #user_id, message_id = best_fit.split("--s--")
    user_context=""
    file = files_config[best_fit]
    context_f = (await find_text_by_title(file)).content
    """
    Process the user's prompt and generate a response using GPT-3.

    Args:
        prompt (str): The user's prompt.
        user_name (str): The username.

    Returns:
        str: The generated response.
    """
    prompt_template = """You are a customer support representative at Jawwal, a leading mobile network provider. Your primary role is to assist customers with their inquiries, ensuring they receive accurate and helpful responses. You should always maintain a friendly, professional, and empathetic tone. Use your knowledge and available resources to address their concerns effectively. If additional information is required, ask the customer politely to provide it. Always aim to make the customer feel valued and understood. The answer must be straight with no additional details.The answer should be 30 words or less.
 
    Context: {context}
    Customer's Question: {user_prompt}
 
    Please provide a detailed and helpful response to the customer.
    """
    formatted_prompt = prompt_template.format(user_prompt=prompt, context=context_f+"---"+user_context)
    message = HumanMessage(content=formatted_prompt)

    result = await gpt.ainvoke([message])
    return {"result": result, "file": file}


files_config = {"files-vector-0-0": "ESim", "files-vector-1-1": "Internet Packages",
                "files-vector-1-0": "Internet Packages",
                "files-vector-2-0": "Missed Call Alert", "files-vector-3-0": "Parental control",
                "files-vector-4-0": "Ranili"}
