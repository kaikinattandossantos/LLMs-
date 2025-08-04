from flask import Flask, render_template, request
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
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
    HumanMessage("{texto}")
]



template_mensagem = ChatPromptTemplate.from_messages([
    ("system", "Traduza o texto a seguir para {idioma}, sem qualquer explicação ou texto introdutório"),
    ("user", "{texto}" ),
])

template_mensagem.invoke({"idioma": "inglês", "texto": "texto do usuário"})


chain = template_mensagem | modelo | parser



app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    traducao = None
    texto_original = ""
    idioma_original = ""

    if request.method == 'POST':
        idioma = request.form.get('idioma')
        texto = request.form.get('texto')

        texto_original = texto
        idioma_original = idioma

        if idioma and texto:
            traducao = chain.invoke({"idioma": idioma, "texto": texto})

    return render_template(
        'index.html',
        traducao=traducao,
        texto_original=texto_original,
        idioma_original=idioma_original
        )


if __name__ == '__main__':
    app.run(debug=True)