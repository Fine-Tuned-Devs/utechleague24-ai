import os
import fitz  # PyMuPDF
from langchain_core.messages import HumanMessage
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

from application.pinecone_lib import PineconeHelper
from db.repositories.text_file_repository import find_text_by_title
from db.repositories.user_repository import get_last_n_messages, join_messages

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


def get_best_fit_user_idx(prompt: str, username):
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


def truncate_history(conversation_history, max_tokens=4096):
    total_tokens = 0
    truncated_history = []
    for message in reversed(conversation_history):
        message_tokens = len(message.split()) + 1
        total_tokens += message_tokens
        if total_tokens > max_tokens:
            break
        truncated_history.insert(0, message)
    return truncated_history


async def process_user_prompt(prompt: str, user_name: str):
    history_revrsed = truncate_history(join_messages(await get_last_n_messages(user_name, 2)))
    best_fit = get_best_fit(prompt)
    if best_fit is None or best_fit['id'] not in files_config:
        assistant_reply = "I'm sorry, I don't have the information you need. Please contact our live support for further assistance."
        return {"result": assistant_reply, "source": None}
    file = files_config[best_fit]
    source = sources[best_fit]
    context_f = (await find_text_by_title(file)).content
    """
    Process the user's prompt and generate a response using GPT-3.

    Args:
        prompt (str): The user's prompt.
        user_name (str): The username.

    Returns:
        str: The generated response.
    """
    prompt_template = """ Prompt Template:
You are a customer support representative at Jawwal, a leading mobile network provider. Your role involves assisting customers with their inquiries, providing accurate and helpful responses. Maintain a friendly, professional, and empathetic tone throughout the interaction. Use your knowledge and resources effectively to address customer concerns. If additional information is needed, request it politely from the customer. Aim to make every customer feel valued and understood.

- Keep your response concise, aiming for no more than 30 words.
- Refer to conversation history when relevant to provide context-specific support.
- If a topic from past interactions is relevant to the current question, incorporate that information into your response.

Template Details:
Context: {context}

Conversation History: {conversation_history}

Customer's Question: {user_prompt}

Your Task:
Provide a clear, concise, and relevant response based on the customer’s question and the provided context and history.
"""

    formatted_prompt = prompt_template.format(user_prompt=prompt, conversation_history=history_revrsed,
                                              context=context_f)
    message = HumanMessage(content=formatted_prompt)

    result = await gpt.ainvoke([message])
    return {"result": result, "source": source}


files_config = {"files-vector-0-0": "ESim", "files-vector-1-1": "Internet Packages",
                "files-vector-1-0": "Internet Packages",
                "files-vector-2-0": "Missed Call Alert", "files-vector-3-0": "Parental control",
                "files-vector-4-0": "Ranili"}

sources = {"files-vector-0-0": "https://drive.google.com/file/d/1nxm5jH11UnL26hXK3_wm3P1DSXqWbVFA/view",
           "files-vector-1-1": "https://drive.google.com/file/d/14BVangb9i4MSkc0b7fuuqTmozxP2rcKi/view",
           "files-vector-1-0": "https://drive.google.com/file/d/14BVangb9i4MSkc0b7fuuqTmozxP2rcKi/view",
           "files-vector-2-0": "https://drive.google.com/file/d/1-gsFIxo0vuo4SUghdNQvaAt3ccpdUfIj/view",
           "files-vector-3-0": "https://drive.google.com/file/d/1-gsFIxo0vuo4SUghdNQvaAt3ccpdUfIj/view",
           "files-vector-4-0": "https://drive.google.com/file/d/1-wU9lPl0ZufFyU9jBMNh1V4OcAUx3lIl/view"}
