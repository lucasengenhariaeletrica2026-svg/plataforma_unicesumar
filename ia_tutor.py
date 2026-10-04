import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Descobre o caminho absoluto da pasta onde este arquivo está salvo
caminho_da_pasta_atual = os.path.dirname(os.path.abspath(__file__))
caminho_do_env = os.path.join(caminho_da_pasta_atual, ".env")

# Força o carregamento do arquivo .env apontando diretamente para o local correto
load_dotenv(dotenv_path=caminho_do_env)

# Puxa a chave de API localizada com precisão
api_key = os.getenv("GEMINI_API_KEY")

# Inicializa o cliente oficial do Google AI
if api_key:
    client = genai.Client(api_key=api_key)
else:
    client = None

def responder_com_contexto(texto_pdf, pergunta_usuario):
    """
    Envia o conteúdo do PDF extraído junto com a dúvida do usuário 
    para o Gemini responder de forma altamente didática e focada em engenharia.
    Inclui proteção contra sobrecarga dos servidores (Erros 503/High Demand).
    """
    if not client:
        return "⚠️ Erro: Chave de API (GEMINI_API_KEY) não encontrada no arquivo .env."
    
    config = types.GenerateContentConfig(
        system_instruction=(
            "Você é um tutor acadêmico especialista em Engenharia Elétrica. "
            "Seu objetivo é explicar os conceitos contidos nos materiais de forma extremamente didática, "
            "passo a passo, focando no aprendizado prático do aluno. "
            "Use formatação clara, tópicos e fórmulas matemáticas legíveis sempre que necessário."
        ),
        temperature=0.3,
    )
    
    prompt_completo = f"""
    Baseando-se no seguinte material de estudo fornecido pelo aluno:
    ---
    {texto_pdf}
    ---
    
    Responda de forma didática à seguinte dúvida/solicitação:
    {pergunta_usuario}
    """
    
    # Configuração de tentativas automáticas para contornar instabilidades temporárias
    tentativas_maximas = 3
    for tentativa in range(tentativas_maximas):
        try:
            resposta = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=prompt_completo,
                config=config
            )
            return resposta.text
            
        except Exception as e:
            erro_str = str(e).upper()
            # Identifica se o erro é de indisponibilidade/alta demanda (como o 503)
            if "503" in erro_str or "UNAVAILABLE" in erro_str or "RESOURCE_EXHAUSTED" in erro_str:
                if tentativa < tentativas_maximas - 1:
                    # Aguarda 1.5 segundos antes de tentar novamente
                    time.sleep(1.5)
                    continue
            
            # Se esgotarem as tentativas ou for outro tipo de erro, retorna um aviso limpo
            return (
                "⚠️ **O servidor do Tutor IA está altamente congestionado neste instante.**\n\n"
                "Os servidores globais do Gemini estão recebendo uma alta demanda de requisições. "
                "Por favor, aguarde alguns segundos e clique em enviar sua pergunta novamente!"
            )
