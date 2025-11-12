# app.py - Versão FINAL com OpenAI API (Atende ao critério "Uso de AI")

from flask import Flask, render_template, request, jsonify
import openai
from dotenv import load_dotenv
import os
import PyPDF2
from io import BytesIO
import json 

# --- 1. CONFIGURAÇÃO DA API (Usa a chave do .env) ---

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY") 

# --- 2. INICIALIZAÇÃO DO FLASK ---

app = Flask(__name__) 

# --- 3. FUNÇÕES DE PROCESSAMENTO E IA ---

def preprocess_text(email_content):
    """Função para limpeza e pré-processamento do texto do e-mail."""
    return email_content.strip()

def classify_and_respond_with_ai(email_content):
    """Usa a API do OpenAI para classificar o e-mail e sugerir uma resposta."""

    # As categorias que a IA deve escolher
    categorias = ["Produtivo", "Improdutivo"]
    
    # Monta o prompt (Este é o seu "ajuste da AI" / Prompt Engineering)
    prompt = f"""
    Você é um assistente de classificação de e-mails de atendimento ao cliente.
    O objetivo é classificar o e-mail abaixo em uma das seguintes categorias:
    - 'Produtivo': O e-mail contém um pedido, uma dúvida ou uma reclamação que exige ação ou resposta detalhada.
    - 'Improdutivo': O e-mail é apenas uma continuação da conversa, um comentário, ou uma mensagem que NÃO exige uma ação posterior do operador (como 'ok' ou 'entendi').

    Além da classificação, forneça uma 'resposta_sugerida' em português, focada, clara e profissional para o e-mail,
    seguindo as diretrizes de atendimento (tempo de resposta e esclarecimento de dúvidas).
    Se a categoria for 'Improdutivo', a resposta sugerida deve ser breve e apenas de cortesia.

    E-MAIL: "{email_content[:2000]}"

    Responda apenas com um JSON formatado, seguindo a estrutura:
    {{
        "categoria": "...",
        "resposta_sugerida": "..."
    }}
    """

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um classificador de e-mails e gerador de respostas."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        resultado_ia = json.loads(response.choices[0].message.content)

        return resultado_ia.get("categoria"), resultado_ia.get("resposta_sugerida")

    except Exception as e:
        print(f"Erro na API do OpenAI: {e}")
        # Fallback para caso de erro na API
        return "Erro - API", "Houve um erro de comunicação com o serviço de IA. Tente novamente."

# --- O RESTANTE DO SEU CÓDIGO (ROTAS FLASK) ---

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_email():
    email_content = None
    email_file = request.files.get('email_file')
    
    # 1. LÓGICA DE TRATAMENTO DE ARQUIVOS (Mantida)
    if email_file and email_file.filename:
        filename = email_file.filename
        
        if filename.endswith('.txt'):
            try:
                email_content = email_file.read().decode('utf-8')
            except Exception as e:
                return jsonify({"error": f"Erro ao ler o arquivo TXT: {e}"}), 400
        
        elif filename.endswith('.pdf'):
            try:
                reader = PyPDF2.PdfReader(BytesIO(email_file.read()))
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                email_content = text
            except Exception as e:
                return jsonify({"error": f"Erro ao ler o arquivo PDF. Garanta que é um PDF baseado em texto: {e}"}), 400
        
        else:
            return jsonify({"error": "Formato de arquivo não suportado. Use .txt ou .pdf."}), 400
    
    # 2. LÓGICA DE TRATAMENTO DE TEXTO (Se nenhum arquivo foi enviado)
    else:
        email_content = request.form.get('email_content')
    
    # 3. VERIFICAÇÃO FINAL
    if not email_content:
        return jsonify({"error": "Por favor, insira o conteúdo de um e-mail ou faça upload de um arquivo."}), 400

    # 4. CHAMADA À IA (MUDANÇA CRUCIAL)
    cleaned_text = preprocess_text(email_content)
    categoria, resposta = classify_and_respond_with_ai(cleaned_text)

    # 5. RETORNO DO RESULTADO
    return jsonify({
        "categoria": categoria,
        "resposta_sugerida": resposta
    })

if __name__ == '__main__':
    app.run(debug=True)