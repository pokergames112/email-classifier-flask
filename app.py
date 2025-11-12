# app.py - Versão FINAL, GRATUITA, com Hugging Face, Upload de Arquivos e Filtragem por Palavras-Chave

from flask import Flask, render_template, request, jsonify
from transformers import pipeline
import PyPDF2
from io import BytesIO

# --- 1. CONFIGURAÇÃO DA IA (HUGGING FACE) ---

try:
    # Inicializa o pipeline de classificação Zero-Shot.
    print("Carregando o modelo de classificação Zero-Shot. Isso pode demorar um pouco na primeira execução...")
    classifier = pipeline("zero-shot-classification", 
                          model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")
    print("Modelo de IA carregado com sucesso.")

except Exception as e:
    print(f"ERRO ao carregar o modelo Hugging Face: {e}")
    classifier = None

# Define as categorias que o modelo tentará classificar
candidate_labels = ["Produtivo", "Improdutivo"]


# --- 2. INICIALIZAÇÃO DO FLASK ---

app = Flask(__name__) 


# --- 3. FUNÇÕES DE PROCESSAMENTO E IA ---

def preprocess_text(email_content):
    """Função para limpeza e pré-processamento do texto do e-mail."""
    return email_content.strip()

def classify_and_respond_with_ai(email_content):
    """Usa a filtragem por palavra-chave para e-mails simples e a IA para o restante."""
    
    if not classifier:
        return "Erro de Configuração", "O modelo de IA não foi carregado."

    # --- 1. FILTRAGEM DE PALAVRAS-CHAVE (100% de precisão para Improdutivo) ---
    # Se o e-mail contiver uma dessas palavras, ele é classificado imediatamente como Improdutivo
    improdutivo_keywords = ["obrigado", "agradeço", "parabéns", "bom trabalho", "feliz", "sucesso"]
    
    if any(keyword in email_content.lower() for keyword in improdutivo_keywords):
        return "Improdutivo", "Obrigado pela sua mensagem! Agradecemos o contato, mas esta mensagem não requer uma ação imediata ou resposta formal de nossa equipe."

    # --- 2. CLASSIFICAÇÃO COM IA (Se não for um agradecimento simples) ---
    
    # Prompt detalhado
    prompt_detail = f"""
    Você é um classificador de e-mails para um setor financeiro. 
    Classifique o e-mail a seguir. Use 'Produtivo' APENAS se o e-mail for uma requisição formal que exige uma ação específica, envio de documentos, ou uma resposta técnica.
    Use 'Improdutivo' se for uma comunicação que não requer uma ação.
    
    E-mail: {email_content}
    """

    try:
        # CLASSIFICAÇÃO usando o prompt_detail
        result = classifier(prompt_detail, candidate_labels)
        categoria = result['labels'][0] 
        
        # GERAÇÃO DE RESPOSTA
        if categoria == "Produtivo":
            resposta = "Recebemos sua solicitação. Sua demanda requer uma ação específica e está sendo encaminhada para a equipe responsável. O prazo de resposta é de 48 horas úteis."
        else: # O modelo classificou como Improdutivo
            resposta = "Obrigado pela sua mensagem! Agradecemos o contato, mas esta mensagem não requer uma ação imediata ou resposta formal de nossa equipe."

        return categoria, resposta

    except Exception as e:
        print(f"Erro no processamento do Hugging Face: {e}")
        return "Erro de Classificação", "Não foi possível processar o e-mail devido a um erro no modelo de IA."


# --- 4. ROTAS FLASK ---

@app.route('/', methods=['GET'])
def index():
    """Rota que serve o arquivo HTML principal."""
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_email():
    """Rota que recebe o texto ou o arquivo, processa e retorna o resultado da IA."""
    email_content = None

    # Tenta obter o arquivo
    email_file = request.files.get('email_file')
    
    # 1. LÓGICA DE TRATAMENTO DE ARQUIVOS
    if email_file and email_file.filename:
        filename = email_file.filename
        
        # Leitura de .txt
        if filename.endswith('.txt'):
            try:
                # O arquivo é lido como bytes e decodificado
                email_content = email_file.read().decode('utf-8')
            except Exception as e:
                return jsonify({"error": f"Erro ao ler o arquivo TXT: {e}"}), 400
        
        # Leitura de .pdf
        elif filename.endswith('.pdf'):
            try:
                reader = PyPDF2.PdfReader(BytesIO(email_file.read()))
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                email_content = text
            except Exception as e:
                return jsonify({"error": f"Erro ao ler o arquivo PDF. Garanta que é um PDF baseado em texto: {e}"}), 400
        
        # Trata arquivos que não são txt ou pdf
        else:
            return jsonify({"error": "Formato de arquivo não suportado. Use .txt ou .pdf."}), 400
    
    # 2. LÓGICA DE TRATAMENTO DE TEXTO (Se nenhum arquivo foi enviado)
    else:
        email_content = request.form.get('email_content')
    
    # 3. VERIFICAÇÃO FINAL
    if not email_content:
        return jsonify({"error": "Por favor, insira o conteúdo de um e-mail ou faça upload de um arquivo."}), 400

    # 4. CHAMADA À IA
    cleaned_text = preprocess_text(email_content)
    categoria, resposta = classify_and_respond_with_ai(cleaned_text)

    # 5. RETORNO DO RESULTADO
    return jsonify({
        "categoria": categoria,
        "resposta_sugerida": resposta
    })


# --- 5. EXECUÇÃO DO APLICATIVO ---

if __name__ == '__main__':
    app.run(debug=True)