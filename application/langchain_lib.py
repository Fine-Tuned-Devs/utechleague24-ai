import os
from langchain_core.messages import HumanMessage
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
import fitz  # PyMuPDF
from application.pinecone_lib import PineconeHelper

# Set environment variables for API keys and endpoints
os.environ["AZURE_OPENAI_API_KEY"] = "70acd5849bdd4aaaa8560815c4d929de"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://uleague-openai.openai.azure.com/"
os.environ["AZURE_OPENAI_API_VERSION"] = "2024-02-01"
os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"] = "gpt3"
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
    azure_deployment=os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"],
    model_version="0613",
)

ph = PineconeHelper()


async def process_user_prompt(prompt: str, user_name: str):
    """
    Process the user's prompt and generate a response using GPT-3.

    Args:
        prompt (str): The user's prompt.
        user_name (str): The username.

    Returns:
        str: The generated response.
    """
    vector = utils.process_text_and_get_embeddings(prompt)
    cosine_result = ph.query_vector("files", vector, 3, 3072)

    # Extract the id for the result with the highest score
    #highest_score_id = max(cosine_result, key=lambda x: x['score'])['id']
    #print(highest_score_id)
    prompt_template = """You are a customer support representative at Jawwal, a leading mobile network provider. Your primary role is to assist customers with their inquiries, ensuring they receive accurate and helpful responses. You should always maintain a friendly, professional, and empathetic tone. Use your knowledge and available resources to address their concerns effectively. If additional information is required, ask the customer politely to provide it. Always aim to make the customer feel valued and understood.The answer must be straight with no addtional details
 
    Context: What is the eSIM service?
It is a new technology added to modern devices by embedding an eSIM card inside the phone
through scanning a QR code, while keeping the traditional SIM card active. This allows
subscribers to have two different numbers on the same device, and they can easily switch
between them without needing to physically remove the SIM card.
Will the esim function during roaming if the subscriber is not using a Nano SIM card slot
at all?
Yes, the eSIM will work during roaming without using a physical Nano SIM card slot, but the
subscriber must have roaming service activated.
How many mobile phone numbers can a subscriber activate on a single eSIM?
You can activate one mobile phone number on a single eSIM at a time.
How to install an eSIM?
A QR code will be provided to the you, and you should navigate to the iPhone settings. From
settings, scan the QR code, and the eSIM profile will be downloaded after a few steps
(instructions on the device will guide subscribers on completing this process)."
Can you change the mobile number associated with an eSIM at any time? How can this
be done and what are the necessary steps?
This be done and what are the necessary steps? Yes, you can change the mobile number
(MSISDN) on an eSIM, and you should follow the same usual procedures as when changing a
mobile number.
Can I change my current SIM card and switch to an eSIM?
Yes, you can switch from a traditional SIM card to an eSIM. This can be done if your phone
supports eSIM technology and has an updated operating system that also supports this
technology. Additionally, this can be facilitated through a mobile exhibition.
What should I do if I lose my phone? How can I deactivate the SIM card?
Please report the loss of your device to Jawwal. Jawwal can deactivate the eSIM profile,
preventing calls, text messages, and data usage. A new QR code will be generated if needed
(provided the alternate device supports eSIM technology).
Can the same QR code be used on more than one device?
Yes, that's possible but no same time.


 
    Customer's Question: {user_prompt}
 
    Please provide a detailed and helpful response to the customer.
    """
    formatted_prompt = prompt_template.format(context="context", user_prompt=prompt)
    message = HumanMessage(content=formatted_prompt)
    return  cosine_result

