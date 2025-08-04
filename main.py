# main.py

import os
from dotenv import load_dotenv
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

# 1. Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# --- Bloco de Configuração ---

# 2. Configuração do Flask e SQLAlchemy
app = Flask(__name__)

# Leitura correta das variáveis de ambiente para o banco
user = os.getenv("DB_USER")
password = os.getenv("SENHA_BD")
host = os.getenv("DB_HOST")
dbname = os.getenv("DB_NAME")
chave_api = os.getenv("GEMINI_API_KEY")

if not all([user, password, host, dbname, chave_api]):
    raise ValueError("Uma ou mais variáveis de ambiente (DB_USER, DB_PASSWORD, DB_HOST, DB_NAME, GEMINI_API_KEY) não foram definidas.")

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{user}:{password}@{host}/{dbname}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 3. Configuração da IA (LangChain com Gemini)
parser = StrOutputParser()
modelo = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=chave_api,
    temperature=0
)
template_mensagem = ChatPromptTemplate.from_messages([
    ("system", "Traduza o texto a seguir para {idioma}, sem qualquer explicação ou texto introdutório."),
    ("user", "{texto}"),
])
chain = template_mensagem | modelo | parser


# 4. Definição do Modelo do Banco de Dados (corrigido de models.py)
class Historico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    texto_original = db.Column(db.Text, nullable=False)
    idioma = db.Column(db.String(50), nullable=False) # Usar String é mais eficiente para idiomas
    traducao = db.Column(db.Text, nullable=False)


# --- Bloco da Aplicação ---

@app.route('/', methods=['GET', 'POST'])
def home():
    traducao_resultado = None
    texto_original_form = ""
    idioma_original_form = ""

    if request.method == 'POST':
        idioma = request.form.get('idioma')
        texto = request.form.get('texto')

        # Mantém os valores no formulário para o usuário não ter que digitar novamente
        texto_original_form = texto
        idioma_original_form = idioma

        if idioma and texto:
            # Invoca a IA para obter a tradução
            traducao_resultado = chain.invoke({"idioma": idioma, "texto": texto})
            
            # Cria o objeto com os dados corretos
            novo_registro = Historico(
                texto_original=texto,
                idioma=idioma,
                traducao=traducao_resultado
            )

            # Salva o registro no banco de dados
            db.session.add(novo_registro)
            db.session.commit()

    return render_template(
        'index.html',
        traducao=traducao_resultado,
        texto_original=texto_original_form,
        idioma_original=idioma_original_form
    )


# 5. Ponto de entrada para executar a aplicação
if __name__ == '__main__':
    # Garante que a tabela do banco de dados seja criada antes de rodar a app
    with app.app_context():
        db.create_all()
    app.run(debug=True)