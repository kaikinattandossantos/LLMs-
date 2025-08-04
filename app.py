from dotenv import load_dotenv
#lingua humana vai ser HumanMessage e lingua do sistema SystemMessage
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
#a resposta será apenas o texto Str
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
import os

load_dotenv()
chave_api = os.getenv("GEMINI_API_KEY")

parser = StrOutputParser()

#llm = GoogleGenerativeAI(model="gemini-2.5-pro")
#llm.invoke("Once upon a time, a library called LangChain")

modelo = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=chave_api,
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)


mensagens = [
    SystemMessage("traduza o texto a seguir para ingles"),
    HumanMessage("eu gosto de voce malu, meu amor")
]

#sempre usar invoke para mandar o modelo fazer algo
# | serve como "então"
chain = modelo | parser

texto_final = chain.invoke(mensagens)
print(texto_final)


