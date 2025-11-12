# app.py - Versão FINAL, GRATUITA, SEM IA PESADA (Somente Lógica Pura)

from flask import Flask, render_template, request, jsonify
import PyPDF2
from io import BytesIO
from dotenv import load_dotenv
import os

# --- 1. CONFIGURAÇÃO (Variáveis de ambiente) ---

load_dotenv()
# Aqui não precisamos de chaves de API, mas é bom manter a estrutura.

# --- 2. INICIALIZAÇÃO DO FLASK ---

app = Flask(__name__) 

# --- 3. FUNÇÕES DE PROCESSAMENTO E CLASSIFICAÇÃO (Lógica Pura) ---

def preprocess_text(email_content):
    """Função para limpeza e pré-processamento do texto do e-mail."""
    return email_content.strip().lower()

def classify_and_respond_pure_logic(email_content_lower):
    """
    Classifica o e-mail e sugere uma resposta baseada unicamente em regras e palavras-chave.
    Totalmente gratuito e não usa IA pesada ou APIs.
    """

    # Palavras-chave que indicam AÇÃO/PRODUTIVIDADE
    produtivas_keywords = ["preciso", "gostaria de saber", "reclamação", "dúvida", "problema", "erro", "solicito", "quero"]
    
    # Palavras-chave que indicam AGRADECIMENTO/IMPRODUTIVIDADE
    improdutivas_keywords = ["obrigado", "obrigada", "valeu", "entendi", "ok", "confirmado", "agradeço"]

    # Verifica se há palavras produtivas
    if any(k in email_content_lower for k in produtivas_keywords):
        categoria = "Produtivo"
        resposta_sugerida = "Obrigado por nos contatar! Recebemos sua solicitação e já estamos analisando. Em breve entraremos em contato com uma solução ou resposta completa."
        
    # Verifica se há palavras improdutivas
    elif any(k in email_content_lower for k in improdutivas_keywords):
        categoria = "Improdutivo"
        resposta_sugerida = "Olá! Recebemos sua mensagem. Se precisar de algo mais, estamos à disposição. Caso contrário, considere esta conversa encerrada."
        
    # Classificação Padrão (Fallback)
    else:
        categoria = "Produtivo (Padrão)"
        resposta_sugerida = "Obrigado por nos contatar! Recebemos sua mensagem. Por favor, especifique sua dúvida ou solicitação para que possamos ajudá-lo de forma eficiente."

    return categoria, resposta_sugerida

# --- O RESTANTE DO SEU CÓDIGO (ROTAS FLASK) ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_email():
    # 1. TRATAMENTO DE UPLOAD DE ARQUIVOS
    email_content = None
    
    # ... (Seu código de upload de arquivo .txt e .pdf aqui)
    # ATENÇÃO: Use o código do seu último 'app.py' para esta seção 
    # (a parte que lê e extrai texto de .txt e .pdf).

    if 'email_file' in request.files and request.files['email_file'].filename != '':
        email_file = request.files['email_file']
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
    
    else:
        email_content = request.form.get('email_content')
    
    # 2. VERIFICAÇÃO FINAL
    if not email_content:
        return jsonify({"error": "Por favor, insira o conteúdo de um e-mail ou faça upload de um arquivo."}), 400

    # 3. CHAMADA À LÓGICA PURA
    cleaned_text = preprocess_text(email_content)
    # A única chamada de função de classificação mudou aqui:
    categoria, resposta = classify_and_respond_pure_logic(cleaned_text)

    # 4. RETORNO DO RESULTADO
    return jsonify({
        "categoria": categoria,
        "resposta_sugerida": resposta
    })

if __name__ == '__main__':
    app.run(debug=True)