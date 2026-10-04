import os
import pypdf  # CORRIGIDO: Tudo em letras minúsculas para o Linux reconhecer

def extrair_texto_pdf(caminho_arquivo):
    """Lê todas as páginas de um arquivo PDF e retorna o texto consolidado."""
    texto_completo = ""
    try:
        with open(caminho_arquivo, "rb") as f:
            leitor = pypdf.PdfReader(f)  # CORRIGIDO: pypdf com inicial minúscula
            for num_pagina in range(len(leitor.pages)):
                pagina = leitor.pages[num_pagina]
                texto_completo += pagina.extract_text() + "\n"
    except Exception as e:
        return f"Erro ao ler PDF: {str(e)}"
    return texto_completo

def extrair_texto_docx(caminho_arquivo):
    """Lê um arquivo do Word (.docx) e retorna o texto extraído de forma nativa e rápida."""
    try:
        import docx
        doc = docx.Document(caminho_arquivo)
        return "\n".join([paragrafo.text for paragrafo in doc.paragraphs])
    except Exception as e:
        return f"Erro ao ler DOCX: {str(e)}"

def ler_documento(caminho_arquivo):
    """Função central que identifica a extensão do arquivo e extrai seu texto."""
    extensao = os.path.splitext(caminho_arquivo)[1].lower()
    
    if extensao == ".pdf":
        return extrair_texto_pdf(caminho_arquivo)
    elif extensao == ".docx":
        return extrair_texto_docx(caminho_arquivo)
    elif extensao == ".txt":
        try:
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            with open(caminho_arquivo, "r", encoding="iso-8859-1") as f:
                return f.read()
    else:
        return "Formato de arquivo não suportado."

