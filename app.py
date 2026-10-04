import streamlit as st
import os
import math
import subprocess  # Adicionado de forma limpa para processos assíncronos futuros
import io          # Centralizado do laboratório
import numpy as np
import random
import matplotlib.pyplot as plt # Centralizado do laboratório
import matplotlib.patches as patches # Centralizado do laboratório
import plotly.graph_objects as go
from extrator import ler_documento
from ia_tutor import responder_com_contexto

# Configuração da página web
st.set_page_config(page_title="Estação Avançada de Engenharia", layout="wide", page_icon="⚡")

# --- SISTEMA DE MEMÓRIA CACHE (Garante velocidade extrema ao ler arquivos) ---
@st.cache_data(show_spinner="Extraindo conteúdo do material...")
def obter_conteudo_cached(caminho_arquivo):
    try:
        if os.path.exists(caminho_arquivo):
            return ler_documento(caminho_arquivo)
        return "Arquivo base não localizado no diretório."
    except Exception as e:
        return f"Não foi possível processar a leitura do documento: {str(e)}"

# --- FUNÇÃO DO MEMORIAL DE CÁLCULO LOCAL ---
def calcular_memorial_vetores_3d(x1, y1, z1, x2, y2, z2):
    soma_x, soma_y, soma_z = x1 + x2, y1 + y2, z1 + z2
    passo_soma = f"$$\\vec{{u}} + \\vec{{v}} = ({x1} + ({x2}),\\ {y1} + {y2},\\ {z1} + {z2}) = ({soma_x},\\ {soma_y},\\ {soma_z})$$"
    sub_x, sub_y, sub_z = x1 - x2, y1 - y2, z1 - z2
    passo_sub = f"$$\\vec{{u}} - \\vec{{v}} = ({x1} - ({x2}),\\ {y1} - {y2},\\ {z1} - {z2}) = ({sub_x},\\ {sub_y},\\ {sub_z})$$"
    t_x, t_y, t_z = x1 * x2, y1 * y2, z1 * z2
    prod_escalar = t_x + t_y + t_z
    passo_escalar = f"$$\\vec{{u}} \\cdot \\vec{{v}} = ({x1} \\cdot {x2}) + ({y1} \\cdot {y2}) + ({z1} \\cdot {z2}) = {t_x} + ({t_y}) + ({t_z}) = {prod_escalar}$$"
    quad_u = x1**2 + y1**2 + z1**2
    norma_u = math.sqrt(quad_u)
    passo_norma_u = f"$$\\|\\vec{{u}}\\| = \\sqrt{{{x1}^2 + {y1}^2 + {z1}^2}} = \\sqrt{{{quad_u}}} \\approx {round(norma_u, 4)}$$"
    quad_v = x2**2 + y2**2 + z2**2
    norma_v = math.sqrt(quad_v)
    passo_norma_v = f"$$\\|\\vec{{v}}\\| = \\sqrt{{{x2}^2 + {y2}^2 + {z2}^2}} = \\sqrt{{{quad_v}}} \\approx {round(norma_v, 4)}$$"
    return {"soma": passo_soma, "sub": passo_sub, "escalar": passo_escalar, "norma_u": passo_norma_u, "norma_v": passo_norma_v}

# --- BANCO DE QUESTÕES DO JOGO (Extraído do seu Material Unificado GAAL.pdf) ---
BANCO_JOGO = [
    {
        "mundo": "MUNDO 1: A Cidade dos Vetores (Baseado no MAPA)",
        "fase": 1,
        "enunciado": "Considerando os dados do seu MAPA, a equipe parte da Base A(1, 1) e vai até a Escola B(5, 4). Determine as coordenadas do vetor deslocamento $\\vec{AB}$.",
        "opcoes": ["(A) $\\vec{AB} = (6, 5)$", "(B) $\\vec{AB} = (4, 3)$", "(C) $\\vec{AB} = (-4, -3)$", "(D) $\\vec{AB} = (5, 4)$"],
        "correta": "(B) $\\vec{AB} = (4, 3)$",
        "explicacao": "Para encontrar o vetor $\\vec{AB}$, subtraímos o ponto inicial do ponto final: $\\vec{AB} = B - A = (5-1, \\ 4-1) = (4, \\ 3)$."
    },
    {
        "mundo": "MUNDO 1: A Cidade dos Vetores (Baseado no MAPA)",
        "fase": 2,
        "enunciado": "Agora que você sabe que o vetor deslocamento é $\\vec{AB} = (4, 3)$, calcule o módulo (norma) deste vetor para descobrir a distância geométrica direta entre a Base e a Escola.",
        "opcoes": ["(A) $\\|\\vec{AB}\\| = 5$", "(B) $\\|\\vec{AB}\\| = 7$", "(C) $\\|\\vec{AB}\\| = \\sqrt{7}$", "(D) $\\|\\vec{AB}\\| = 25$"],
        "correta": "(A) $\\|\\vec{AB}\\| = 5$",
        "explicacao": "O módulo é dado por $\\|\\vec{AB}\\| = \\sqrt{4^2 + 3^2} = \\sqrt{16 + 9} = \\sqrt{25} = 5$."
    },
    {
        "mundo": "MUNDO 2: O Labirinto das Matrizes (Baseado na AE1)",
        "fase": 3,
        "enunciado": "Analisando as definições de matrizes do seu material (Exemplo 8), se tivermos duas matrizes quadradas A e B de ordem 2, qual das seguintes propriedades sobre a multiplicação matricial é verdadeira?",
        "opcoes": ["(A) A multiplicação é sempre comutativa, ou seja, AB = BA.", "(B) O produto AB nunca pode ser calculated se as ordens forem iguais.", "(C) Nem sempre AB é igual a BA, a comutatividade não é uma regra geral.", "(D) Multiplicar por uma matriz identidade altera todos os elementos da matriz original."],
        "correta": "(C) Nem sempre AB é igual a BA, a comutatividade não é uma regra geral.",
        "explicacao": "Como destacado no slide 'Observação (iii)' do seu arquivo, a multiplicação de matrizes não é comutativa em termos gerais: $AB \\neq BA$ na maioria dos casos."
    }
]

# --- CONTROLE DE ESTADOS DO JOGO (Session State) ---
if "fase_atual" not in st.session_state:
    st.session_state.fase_atual = 0
if "xp" not in st.session_state:
    st.session_state.xp = 0
if "vidas" not in st.session_state:
    st.session_state.vidas = 3
if "status_resposta" not in st.session_state:
    st.session_state.status_resposta = None

def resetar_jogo():
    st.session_state.fase_atual = 0
    st.session_state.xp = 0
    st.session_state.vidas = 3
    st.session_state.status_resposta = None

# --- NOVA BARRA LATERAL ORGANIZADA POR MÓDULOS ---
st.sidebar.title("⚡ Engenharia UniCesumar")

# Definição dos módulos e disciplinas disponíveis
ESTRUTURA_CURRICULAR = {
    "Módulo 53": [
        "Geometria Analítica e Álgebra Linear (GAAL)", 
        "Produção do Conhecimento e Disrupção (PCCTD)"
    ],
    "Módulo 54": [
        "Cálculo Diferencial e Integral I", 
        "Engenharia Econômica"
    ]
}

# 1. Seleção do Módulo (Sem a palavra "Atual")
modulo_selecionado = st.sidebar.selectbox(
    "Escolha o Módulo:",
    list(ESTRUTURA_CURRICULAR.keys())
)

# 2. Filtragem dinâmica das disciplinas
materias_disponiveis = ESTRUTURA_CURRICULAR[modulo_selecionado]
materia = st.sidebar.radio(
    "Selecione a Disciplina:",
    materias_disponiveis
)

# --- GERADOR DINÂMICO DE CAMINHOS CORRIGIDO ---
# Sanitização de strings para evitar quebras por acentuação gráfica em diferentes OS
nome_modulo_limpo = modulo_selecionado.replace(" ", "_").replace("ó", "o").lower()

# [CORREÇÃO CRÍTICA] Isolamos o primeiro item da lista [0] para que os .replace() funcionem em texto puro
nome_pasta_limpo = (
    materia.split(" (")[0]
    .replace(" ", "_")
    .replace("á", "a")
    .replace("ú", "u")
    .replace("í", "i")
    .replace("é", "e")
    .replace("ç", "c")
    .replace("ã", "a")
    .lower()
)

# Cria o caminho correto entrando primeiro na pasta do módulo correspondente
pasta_da_materia = os.path.join("dados_unicesumar", nome_modulo_limpo, nome_pasta_limpo)
os.makedirs(pasta_da_materia, exist_ok=True)

# Painel Lateral do Jogo ativo apenas em GAAL
if materia == "Geometria Analítica e Álgebra Linear (GAAL)":
    st.sidebar.markdown("---")
    st.sidebar.subheader("🏆 Status do Gamer")
    st.sidebar.write(f"**XP Atual:** {st.session_state.xp} 🌟")
    st.sidebar.write(f"**Vidas:** {'❤️ ' * st.session_state.vidas if st.session_state.vidas > 0 else '💀 Game Over'}")
    if st.sidebar.button("🔄 Reiniciar Jogo"):
        resetar_jogo()
        st.rerun()  # Corrigido: recarrega a página instantaneamente para aplicar o reset visual

# --- ÁREA CENTRAL ---
st.title("🤖 Estação Avançada de Estudo")
st.write("---")

# ================= SEÇÃO: MÓDULO 53 =================
if materia == "Geometria Analítica e Álgebra Linear (GAAL)":
    st.header("📐 Geometria Analítica e Álgebra Linear")
    
    aba_upload, aba_tutor, aba_calculadora, aba_jogo = st.tabs([
        "📁 Gerenciar Materiais", "👨‍🏫 Tutor Didático", "🧮 Ferramentas de Cálculo", "🎮 Engineering Quest"
    ])
    
    with aba_upload:
        st.subheader("📚 Biblioteca Oficial de Materiais")
        st.write("Consulte os materiais didáticos oficiais disponíveis para esta disciplina.")
        
        # O sistema apenas lista os arquivos que você (administrador) salvou na pasta do servidor
        salvos = os.listdir(pasta_da_materia)
        if salvos:
            sel = st.selectbox("Selecione o material para estudo:", salvos, key="sel_material_gaal")
            # Busca o texto usando o seu sistema de cache ultra rápido
            texto_extraido = obter_conteudo_cached(os.path.join(pasta_da_materia, sel))
            st.text_area("Texto reconhecido pelo sistema:", texto_extraido, height=150)
        else:
            st.info("Aguardando o upload dos materiais oficiais pelo administrador do sistema.")

    with aba_tutor:
        st.subheader("👨‍🏫 Tutor Didático")
        salvos = os.listdir(pasta_da_materia)
        if salvos:
            dbase = st.selectbox("Documento base da IA:", salvos, key="db_tutor_calculo_main")
            pergs = st.text_input("Sua dúvida sobre o arquivo:", key="input_tutor_calculo_main")
            if pergs:
                with st.spinner("Analisando..."): 
                    # Busca a resposta utilizando a leitura otimizada em cache
                    contexto_doc = obter_conteudo_cached(os.path.join(pasta_da_materia, dbase))
                    resposta_bruta = responder_com_contexto(contexto_doc, pergs)
                    
                    # Tratamento de segurança direto na interface do Streamlit
                    resposta_str = str(resposta_bruta).upper()
                    if "503" in resposta_str or "UNAVAILABLE" in resposta_str or "ERRO AO NOS COMUNICARMOS" in resposta_str:
                        st.warning("⚠️ **O servidor do Gemini está muito carregado agora.**")
                        st.info("💡 Como os servidores globais do Google estão enfrentando alta demanda, aguarde cerca de 5 segundos e aperte **Enter** no campo de texto para tentar novamente!")
                    else:
                        st.markdown(resposta_bruta)

    with aba_calculadora:
        st.subheader("🧮 Calculadora Analítica Passo a Passo")
        c1, c2 = st.columns(2)
        with c1:
            ux = st.number_input("UX", value=1.0)
            uy = st.number_input("UY", value=2.0)
            uz = st.number_input("UZ", value=3.0)
        with c2:
            vx = st.number_input("VX", value=-2.0)  # Adicionado: Criação da variável vx que faltava
            vy = st.number_input("VY", value=4.0)
            vz = st.number_input("VZ", value=0.03)
            
        res = calcular_memorial_vetores_3d(ux, uy, uz, vx, vy, vz)
        with st.expander("▶️ Ver Soma"): st.markdown(res["soma"])
        with st.expander("▶️ Ver Subtração"): st.markdown(res["sub"])
        with st.expander("▶️ Ver Produto Escalar"): st.markdown(res["escalar"])
        
    with aba_jogo:
        st.subheader("🕹️ GAAL Engineering Quest - O Jogo do Conhecimento")
        st.write("---")
        
        st.markdown("### 📝 Banco de Desafios Teóricos")
        
        if st.session_state.vidas <= 0:
            st.error("💀 GAME OVER! Você perdeu todas as suas vidas no labirinto da engenharia.")
            st.info("💡 Estude os memoriais na aba de cálculos e clique em 'Reiniciar Jogo' na barra lateral.")
        elif st.session_state.fase_atual >= len(BANCO_JOGO):
            st.balloons()
            st.success(f"🏆 PARABÉNS! Você acumulou {st.session_state.xp} XP!")
        else:
            dados_fase = BANCO_JOGO[st.session_state.fase_atual]
            st.markdown(f"**FASE {dados_fase['fase']} - {dados_fase['mundo']}**")
            
            with st.form(key="form_jogo_atualizado"):
                resposta_usuario = st.radio("Escolha a alternativa correta:", dados_fase["opcoes"])
                botao_enviar = st.form_submit_button(label="🎯 Confirmar Resposta")
                
            if botao_enviar:
                if resposta_usuario == dados_fase["correta"]:
                    st.session_state.status_resposta = "CORRETO"
                    st.session_state.xp += 100
                else:
                    st.session_state.status_resposta = "ERRADO"
                    st.session_state.vidas -= 1
                st.rerun()  # Atualização de estado imediata pós-submissão
                
            if st.session_state.status_resposta == "CORRETO":
                st.success("🎉 EXCELENTE! Você ganhou +100 XP!")
                if st.button("▶️ Avançar para o Próximo Nível"):
                    st.session_state.fase_atual += 1
                    st.session_state.status_resposta = None
                    st.rerun()
            elif st.session_state.status_resposta == "ERRADO":
                st.error("❌ RESPOSTA INCORRETA! Você perdeu 1 vida (❤️).")
                st.info(dados_fase["explicacao"])
                if st.button("🔄 Tentar Novamente"):
                    st.session_state.status_resposta = None
                    st.rerun()

# ================= SEÇÃO: MÓDULO 54 =================
elif materia == "Cálculo Diferencial e Integral I":
    st.header("📉 Cálculo Diferencial e Integral I")
    st.info("Módulo 54 selecionado. Acompanhe as ferramentas práticas de acordo com as aulas ao vivo!")
    
    # Abas principais da disciplina
    aba_upload, aba_tutor, aba_laboratorio = st.tabs(["📁 Gerenciar Materiais", "👨‍🏫 Tutor IA", "🧪 Laboratório Interativo"])
    
    with aba_upload:
        st.subheader("📚 Biblioteca Oficial de Materiais - Cálculo I")
        st.write("Consulte os materiais didáticos oficiais disponíveis para esta disciplina.")
        
        # O sistema apenas lista os arquivos que você colocou previamente na pasta do servidor
        salvos = os.listdir(pasta_da_materia)
        if salvos:
            sel = st.selectbox("Selecione o arquivo de Cálculo:", salvos, key="sel_material_calculo")
            # Busca o texto usando o cache de alta velocidade
            texto_extraido_calculo = obter_conteudo_cached(os.path.join(pasta_da_materia, sel))
            st.text_area("Texto extraído para análise da IA:", texto_extraido_calculo, height=150)
        else:
            st.info("Aguardando o upload dos materiais oficiais pelo administrador do sistema.")
            
    with aba_tutor:
        st.subheader("👨‍🏫 Tutor Inteligente de Cálculo I")
        salvos = os.listdir(pasta_da_materia)
        if salvos:
            dbase = st.selectbox("Documento base de Cálculo:", salvos, key="db_calculo")
            pergs = st.text_input("Qual sua dúvida sobre limites, derivadas ou taxas de variação?", key="input_calculo")
            if pergs:
                with st.spinner("Analisando fórmulas..."):
                    # Otimizado com leitura em cache de alta velocidade
                    contexto_doc_calculo = obter_conteudo_cached(os.path.join(pasta_da_materia, dbase))
                    resposta_bruta = responder_com_contexto(contexto_doc_calculo, pergs)
                    resposta_str = str(resposta_bruta).upper()
                    if "503" in resposta_str or "UNAVAILABLE" in resposta_str or "ERRO" in resposta_str:
                        st.warning("⚠️ O servidor do Gemini está muito carregado agora.")
                        st.info("💡 Como os servidores globais do Google estão enfrentando alta demanda, aguarde cerca de 5 segundos e aperte Enter para tentar novamente!")
                    else:
                        st.markdown(resposta_bruta)
                        
    # MENU INTERNO DO LABORATÓRIO (AULA 1 ATÉ AULA 10)
    with aba_laboratorio:
        # Seleção da aula
        lista_aulas = [f"Aula {i}" for i in range(1, 11)]
        aula_selecionada = st.selectbox("Selecione a Aula do Módulo:", lista_aulas)
        st.write("---")
        # --- CONTEÚDO COMPLETO E DETALHADO DA AULA 1 ---
        if aula_selecionada == "Aula 1":
            st.markdown("## 📐 Prática da Aula 1: Conjuntos, Funções e Retas")
            
            sub_ferramenta1, sub_desafio_pontos, sub_ferramenta2, sub_fabrica_funcoes, sub_intervalos = st.tabs([
                "📊 O Comportamento da Reta", 
                "🎯 Desafio: Descubra a Equação",
                "🎮 Quiz de Conjuntos Dinâmico",
                "🏭 Fábrica de Funções (Conceito)",
                "📏 Intervalos Reais"
            ])
            
            # 1. ABA DO LABORATÓRIO GRÁFICO (Mantida completa e estável)
            with sub_ferramenta1:
                st.subheader("🎛️ Laboratório Interativo da Aula 1: O Comportamento da Reta")
                st.write(
                    "Mova os controles abaixo para entender na prática como os coeficientes "
                    "moldam o gráfico de uma função do primeiro grau ($y = mx + b$)."
                )
                
                col_sliders1, col_sliders2 = st.columns(2)
                with col_sliders1:
                    m = st.slider("Coeficiente Angular (m) - Inclinação da Reta", min_value=-10.0, max_value=10.0, value=2.0, step=0.5, key="m_slider")
                with col_sliders2:
                    b = st.slider("Coeficiente Linear (b) - Intersecção com o Eixo Y", min_value=-10.0, max_value=10.0, value=-2.0, step=0.5, key="b_slider")
                    
                st.info(f"### Equação Atual: $y = {m}x + ({b})$")
                
                x_valores = np.linspace(-10, 10, 100)
                y_valores = m * x_valores + b
                
                fig_reta = go.Figure()
                fig_reta.add_trace(go.Scatter(x=x_valores, y=y_valores, mode='lines', name=f'y = {m}x + {b}', line=dict(color='#ff4b4b', width=4)))
                fig_reta.add_trace(go.Scatter(x=[0], y=[b], mode='markers', name='Coeficiente Linear (b)', marker=dict(color='gold', size=12, line=dict(color='black', width=2))))
                
                fig_reta.update_layout(
                    title="Plano Cartesiano Interativo",
                    xaxis=dict(title="Eixo X", range=[-10, 10], zeroline=True, zerolinewidth=2, zerolinecolor='gray'),
                    yaxis=dict(title="Eixo Y", range=[-10, 10], zeroline=True, zerolinewidth=2, zerolinecolor='gray'),
                    margin=dict(l=20, r=20, t=40, b=20),
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(240,242,246,0.5)'
                )
                st.plotly_chart(fig_reta, use_container_width=True)
                
                st.markdown("### 👨‍🏫 Análise Técnico-Didática da sua Reta:")
                if m > 0:
                    st.success(f"📈 Reta Crescente: Como $m = {m}$ é maior que zero, quanto maior o valor di X, maior será o valor de Y!")
                elif m < 0:
                    st.error(f"📉 Reta Decrescente: Como $m = {m}$ é menor que zero, quanto maior o valor de X, menor será o valor de Y!")
                else:
                    st.warning("➖ Reta Constante: Como $m = 0$, a linha não possui inclinação!")
                st.write(f"📍 A linha cruza o eixo vertical exatamente no ponto (0, {b}).")
                
            # 2. NOVA ABA: DESAFIO DE TRANSFORMAR PONTOS EM EQUAÇÃO (CONCEITO COEFICIENTE ANGULAR)
            with sub_desafio_pontos:
                st.subheader("📍 Desafio Topográfico: Dois Pontos, Uma Reta")
                st.write(
                    r"Como futura(o) engenheira(o), você coletou duas coordenadas em campo. "
                    r"Calcule o Coeficiente Angular (\(m = \frac{y_2 - y_1}{x_2 - x_1}\)) e o Linear (\(b\)) no papel, "
                    "insira suas respostas abaixo e use o gráfico para validar!"
                )
                
                # Ajustado o direcionamento de memória para o session_state correto
                if "verificar_clicado_aula1" not in st.session_state:
                    st.session_state.verificar_clicado_aula1 = False
                    
                # Inicializa os estados das caixas numéricas para permitir o reset manual
                if "val_m_input" not in st.session_state:
                    st.session_state.val_m_input = 0.0
                if "val_b_input" not in st.session_state:
                    st.session_state.val_b_input = 0.0
                    
                # Inicializa os pontos geográficos de forma aleatória e fixa no Session State
                if "pontos_desafio_aula1" not in st.session_state:
                    # Sorteia valores simples para o cálculo não ficar infernal
                    x1 = random.choice([-4, -2, -1, 1, 2])
                    m_alvo = random.choice([-2, -1, 1, 2, 3])
                    b_alvo = random.choice([-3, -1, 0, 2, 4])
                    x2 = x1 + random.choice([2, 3, 4]) # Garante que x2 != x1
                    y1 = m_alvo * x1 + b_alvo
                    y2 = m_alvo * x2 + b_alvo
                    st.session_state.pontos_desafio_aula1 = {"x1": x1, "y1": y1, "x2": x2, "y2": y2, "m": m_alvo, "b": b_alvo}
                    
                p = st.session_state.pontos_desafio_aula1
                
                # Exibe as coordenadas geradas para o aluno
                st.markdown(f"### Encontre a equação da reta que passa por: \(P_1({p['x1']}, {p['y1']})\) e \(P_2({p['x2']}, {p['y2']})\)")
                
                col_inputs1, col_inputs2 = st.columns(2)
                with col_inputs1:
                    m_aluno = st.number_input("Seu Coeficiente Angular (m) calculado:", value=st.session_state.val_m_input, step=0.5, key="m_aluno_input")
                with col_inputs2:
                    b_aluno = st.number_input("Seu Coeficiente Linear (b) calculated:", value=st.session_state.val_b_input, step=0.5, key="b_aluno_input")
                    
                # Caixa de texto para o aluno digitar a equação final
                eq_aluno = st.text_input("Escreva a Equação Geral Resultante (Ex: y = 2x + 4 ou y = -x - 3):", key="eq_aluno_input")
                
                fig_desafio = go.Figure()
                
                # A reta só é adicionada se o aluno clicou em verificar
                if st.session_state.verificar_clicado_aula1:
                    x_sim = np.linspace(-10, 10, 100)
                    y_sim = m_aluno * x_sim + b_aluno
                    # Reta desenhada com a resposta do aluno
                    fig_desafio.add_trace(go.Scatter(x=x_sim, y=y_sim, mode='lines', name='Sua Reta Estimada', line=dict(color='purple', width=3)))
                    
                # Pontos fixos que ele PRECISA atingir
                fig_desafio.add_trace(go.Scatter(x=[p['x1'], p['x2']], y=[p['y1'], p['y2']], mode='markers+text',
                                                 name='Pontos Geográficos Reais',
                                                 text=[f"P1({p['x1']},{p['y1']})", f"P2({p['x2']},{p['y2']})"],
                                                 textposition="top center",
                                                 marker=dict(color='blue', size=14, symbol='diamond-dot')))
                
                # Adicionadas as Spikelines (linhas pontilhadas cruzadas ao passar o mouse)
                fig_desafio.update_layout(
                    xaxis=dict(
                        range=[-10, 10], zeroline=True, zerolinecolor='gray',
                        showspikes=True, spikecolor='gray', spikethickness=1, spikemode='across', spikedash='dash'
                    ),
                    yaxis=dict(
                        range=[-10, 10], zeroline=True, zerolinecolor='gray',
                        showspikes=True, spikecolor='gray', spikethickness=1, spikemode='across', spikedash='dash'
                    ),
                    margin=dict(l=20, r=20, t=20, b=20),
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(240,242,246,0.5)',
                    hovermode="closest"
                )
                
                # scrollZoom: True adicionado nas configurações do plotly_chart
                st.plotly_chart(fig_desafio, use_container_width=True, config={"scrollZoom": True})
                
                # Botão de verificação formal do sistema
                if st.button("🎯 Verificar Memorial de Cálculo", use_container_width=True):
                    st.session_state.verificar_clicado_aula1 = True
                    st.rerun()
                # Processa os feedbacks conceituais após a atualização do botão (VEREDITO FINAL)
                if st.session_state.verificar_clicado_aula1:
                    # Limpeza simples da string digitada para validação robusta
                    eq_limpa = eq_aluno.replace(" ", "").lower()
                    
                    # Monta o gabarito teórico esperado para comparação de strings
                    m_alvo_val = int(p['m']) if float(p['m']).is_integer() else p['m']
                    b_alvo_val = int(p['b']) if float(p['b']).is_integer() else p['b']
                    
                    # Formata variações aceitáveis da equação base (ex: tratando sinais e coeficientes unitários)
                    m_str = "" if m_alvo_val == 1 else ("-" if m_alvo_val == -1 else str(m_alvo_val))
                    b_str = f"+{b_alvo_val}" if b_alvo_val > 0 else (f"{b_alvo_val}" if b_alvo_val < 0 else "")
                    gabarito_eq = f"y={m_str}x{b_str}"
                    if gabarito_eq == "y=x": gabarito_eq = "y=1x"
                    
                    # 1. Validação dos coeficientes numéricos
                    coeficientes_corretos = (m_aluno == float(p['m']) and b_aluno == float(p['b']))
                    
                    # 2. Validação da string de texto escrita
                    string_correta = (gabarito_eq in eq_limpa) or (f"y={m_alvo_val}x{b_str}" in eq_limpa)
                    
                    if coeficientes_corretos and string_correta:
                        st.balloons()
                        st.success(f"🏆 PERFEITO! A reta interceptou os alvos e a equação escrita ({eq_aluno}) está sintaticamente correta!")
                    elif coeficientes_corretos and not string_correta:
                        st.warning(f"📐 Quase lá! O gráfico e os seletores de \(m\) e \(b\) estão corretos, mas a equação de texto escrita não corresponde à sintaxe correta. Esperado algo próximo de: y = {m_alvo_val}x {b_str}")
                    else:
                        st.error("❌ A reta e a equação ainda não condizem com os pontos geográficos.")
                        st.info(f"💡 Dica de Engenharia: Revise o cálculo no papel. Variação vertical sobre horizontal determina \(m\). Ajuste os campos e clique em verificar novamente!")
                        
                if st.button("🔄 Sortear Novos Pontos em Campo"):
                    # Remove os alvos antigos do estado de sessão
                    if "pontos_desafio_aula1" in st.session_state:
                        del st.session_state.pontos_desafio_aula1
                    # Esconde a curva estimada no novo sorteio
                    st.session_state.verificar_clicado_aula1 = False 
                    # Reseta os widgets associados às chaves de input de dados de forma segura
                    if "m_aluno_input" in st.session_state:
                        st.session_state.m_aluno_input = 0.0
                    if "b_aluno_input" in st.session_state:
                        st.session_state.b_aluno_input = 0.0
                    st.rerun()

            # 3. ABA DO QUIZ DE CONJUNTOS (BLINDADA COM COORDENAÇÃO DE CHAVES DINÂMICAS)
            with sub_ferramenta2:
                st.subheader("🎮 Desafio dos Conjuntos dos Números Reais ")
                st.write("Treine a classificação de números reais! Valide sua resposta e clique em avançar quando estiver pronto.")
                
                # [SISTEMA DE CONTROLE DE CHAVE] Inicializa o contador de rodadas para forçar o desfleque
                if "contador_rodadas" not in st.session_state:
                    st.session_state.contador_rodadas = 0
                    
                # Inicializa o número aleatório expandido no Session State
                if "num_quiz_aula1" not in st.session_state:
                    tipo_num = random.choice(["inteiro_neg", "irracional", "fracao", "natural", "dizima", "decimal", "pi"])
                    if tipo_num == "inteiro_neg":
                        st.session_state.num_quiz_aula1 = random.randint(-75, -1)
                        st.session_state.resp_correta_aula1 = "Inteiro (ℤ)"
                    elif tipo_num == "irracional":
                        base_irracional = random.choice([2, 3, 5, 11])
                        st.session_state.num_quiz_aula1 = f"√{base_irracional}"
                        st.session_state.resp_correta_aula1 = "Irracional (I)"
                    elif tipo_num == "fracao":
                        num = random.randint(1, 9)
                        den = random.choice([2, 4, 5, 8])
                        st.session_state.num_quiz_aula1 = f"{num}/{den}"
                        st.session_state.resp_correta_aula1 = "Racional (ℚ)"
                    elif tipo_num == "natural":
                        st.session_state.num_quiz_aula1 = random.randint(0, 100)
                        st.session_state.resp_correta_aula1 = "Natural (ℕ)"
                    elif tipo_num == "dizima":
                        periodo = random.choice([3, 6, 15])
                        st.session_state.num_quiz_aula1 = f"0,{periodo}{periodo}{periodo}..."
                        st.session_state.resp_correta_aula1 = "Racional (ℚ)"
                    elif tipo_num == "decimal":
                        st.session_state.num_quiz_aula1 = round(random.uniform(0.1, 9.9), 2)
                        st.session_state.resp_correta_aula1 = "Racional (ℚ)"
                    elif tipo_num == "pi":
                        st.session_state.num_quiz_aula1 = "π (Número Pi)"
                        st.session_state.resp_correta_aula1 = "Irracional (I)"
                        
                # Criando o Layout de duas colunas lado a lado
                col_quiz_esquerda, col_mapa_direita = st.columns([1.2, 1.0])
                
                with col_quiz_esquerda:
                    st.markdown(f"### Classifique o número:  {st.session_state.num_quiz_aula1}")
                    opcoes_conjuntos = ["Natural (ℕ)", "Inteiro (ℤ)", "Racional (ℚ)", "Irracional (I)"]
                    
                    if "quiz_aula1_respondido" not in st.session_state:
                        st.session_state.quiz_aula1_respondido = False
                        
                    # Formulário de submissão da resposta - O ID do formulário muda a cada rodada
                    with st.form(key=f"form_quiz_dinamico_aula1_rodada_{st.session_state.contador_rodadas}"):
                        # [SOLUÇÃO DEFINITIVA] O key dinâmico obriga o rádio a nascer completamente limpo
                        resposta_aluno = st.radio(
                            "A qual conjunto ele pertence primariamente?",
                            opcoes_conjuntos,
                            index=None,
                            key=f"radio_conjuntos_rodada_{st.session_state.contador_rodadas}"
                        )
                        botao_quiz = st.form_submit_button("🎯 Validar Resposta")
                        
                    if botao_quiz:
                        if resposta_aluno is None:
                            st.warning("⚠️ Selecione uma opção antes de validar!")
                        else:
                            st.session_state.quiz_aula1_respondido = True
                            st.session_state.ultima_resposta_aluno = resposta_aluno
                            st.rerun()
                    if st.session_state.quiz_aula1_respondido:
                        if st.session_state.ultima_resposta_aluno.split(" (")[0] == st.session_state.resp_correta_aula1.split(" (")[0]:
                            st.success("🎉 EXCELENTE! Você dominou o conceito de conjuntos explicado pela Professora Paula!")
                        else:
                            st.error(f"❌ Resposta incorreta. O número {st.session_state.num_quiz_aula1} pertence ao conjunto do tipo {st.session_state.resp_correta_aula1}.")
                            
                        st.markdown("#### 👨‍🏫 Memorial Didático do Conjunto:")
                        if "Natural" in st.session_state.resp_correta_aula1:
                            st.write("👉 Os Naturais (ℕ) são os números inteiros não-negativos usados para contagem simples.")
                        elif "Inteiro" in st.session_state.resp_correta_aula1:
                            st.write("👉 Os Inteiros (ℤ) englobam todos os números naturais e adicionam os seus correspondentes negativos.")
                        elif "Racional" in st.session_state.resp_correta_aula1:
                            st.write("👉 Os Racionais (ℚ) são todos aqueles que podem virar fração! Isso inclui divisões exatas, decimais finitos e dízimas periódicas repetitivas.")
                        elif "Irracional" in st.session_state.resp_correta_aula1:
                            st.write("👉 Os Irracionais (I) possuem infinitas casas decimais e NUNCA se repetem inalteradas, impossibilitando a criação de uma fração geratriz.")
                            
                        st.write("---")
                        if st.button("➡️ Avançar para o Próximo Desafio", use_container_width=True):
                            if "num_quiz_aula1" in st.session_state:
                                del st.session_state.num_quiz_aula1
                            st.session_state.quiz_aula1_respondido = False
                            # Incrementa o contador para alterar as CHAVES e forçar o reset visual total
                            st.session_state.contador_rodadas += 1
                            st.rerun()

                with col_mapa_direita:
                    # Geração otimizada e limpa do diagrama sem redundância de imports
                    fig, ax = plt.subplots(figsize=(5, 5))
                    ax.set_xlim(-6, 6)
                    ax.set_ylim(-6, 6)
                    
                    rect_r = patches.FancyBboxPatch((-5.5, -4.8), 11.0, 9.6, boxstyle="round,pad=0.1",
                                                    linewidth=2.5, edgecolor='#333333', facecolor='#fafafa')
                    
                    circ_q = patches.Circle((-1.8, 0), radius=3.4, linewidth=2, edgecolor='blue', facecolor='#e6f2ff')
                    circ_z = patches.Circle((-1.8, 0), radius=2.3, linewidth=2, edgecolor='green', facecolor='#ebfaeb')
                    circ_n = patches.Circle((-1.8, 0), radius=1.2, linewidth=2, edgecolor='orange', facecolor='#fff5e6')
                    circ_i = patches.Circle((3.5, 0), radius=1.5, linewidth=2, edgecolor='purple', facecolor='#f3e6ff')
                    
                    ax.add_patch(rect_r)
                    ax.add_patch(circ_q)
                    ax.add_patch(circ_z)
                    ax.add_patch(circ_n)
                    ax.add_patch(circ_i)
                    
                    ax.text(-1.8, 0, 'N', fontsize=24, weight='bold', color='orange', ha='center', va='center')
                    ax.text(-1.8, 1.5, 'Z', fontsize=24, weight='bold', color='green', ha='center', va='center')
                    ax.text(-1.8, 2.7, 'Q', fontsize=24, weight='bold', color='blue', ha='center', va='center')
                    ax.text(3.5, 0, 'I', fontsize=24, weight='bold', color='purple', ha='center', va='center')
                    ax.text(-4.8, 4.1, 'R', fontsize=26, weight='bold', color='#333333', ha='center', va='center')
                    
                    ax.set_title("Conjunto dos Números Reais: R = Q U I", fontsize=12, weight='bold')
                    ax.axis('off')
                    
                    buf = io.BytesIO()
                    plt.savefig(buf, format='png', bbox_inches='tight', dpi=120, transparent=True)
                    buf.seek(0)
                    st.image(buf, use_container_width=True)
                    plt.close(fig) # Liberando explicitamente a memória da figura atualizada

            # Sub-abas internas da Aula 1 organizadas com Infinitos e Notações Mistas
            with sub_intervalos:
                st.subheader("📏 Estação de Treinamento Avançada: Intervalos na Reta Real")
                st.write("Explore a reta com infinitos (flechas) e teste seus conhecimentos com notações de parênteses e colchetes!")
                
                # Criando duas abas internas para os comportamentos propostos
                aba_simulador, aba_game = st.tabs(["🎛️ Simulador de Fronteiras", "🎯 Quiz"])
                
                # --- RECURSO 1: SIMULADOR VISUAL DE INTERVALOS COM INFINITO ---
                with aba_simulador:
                    st.markdown("### 1. Laboratório de Configuração de Fronteiras e Infinitos")
                    st.write("Ative os limites infinitos para ver o comportamento das flechas na reta real da professora Paula.")
                    
                    c_sim1, c_sim2 = st.columns(2)
                    with c_sim1:
                        modo_inf = st.radio("Tipo do Limite Inferior:", ["Número Fixo", "Menos Infinito (-∞)"], key="modo_inf")
                        if modo_inf == "Número Fixo":
                            limite_inf = st.slider("Limite Inferior (a)", -10, 10, -3, 1, key="slider_lim_inf")
                            tipo_inf = st.radio("Fronteira Esquerda:", ["Fechada [a", "Aberta ]a ou (a"], key="radio_tipo_inf")
                        else:
                            limite_inf = -11 # Posição lógica para desenhar a flecha fora da tela
                            tipo_inf = "Aberta ]a ou (a"
                            
                    with c_sim2:
                        modo_sup = st.radio("Tipo do Limite Superior:", ["Número Fixo", "Mais Infinito (+∞)"], key="modo_sup")
                        if modo_sup == "Número Fixo":
                            limite_sup = st.slider("Limite Superior (b)", -10, 10, 4, 1, key="slider_lim_sup")
                            tipo_sup = st.radio("Fronteira Direita:", ["Fechada b]", "Aberta b[ / b)"], key="radio_tipo_sup")
                        else:
                            limite_sup = 11 # Posição lógica para desenhar a flecha fora da tela
                            tipo_sup = "Aberta b[ / b)"
                            
                    if modo_inf == "Número Fixo" and modo_sup == "Número Fixo" and limite_inf >= limite_sup:
                        st.error("⚠️ Erro matemático: O limite inferior (a) deve ser menor que o limite superior (b)!")
                    else:
                        # Monta as strings textuais das representações com as duas opções de escrita
                        if modo_inf == "Menos Infinito (-∞)":
                            txt_inf_colchete = "]-∞"
                            txt_inf_parentese = "(-∞"
                            sinal_inf_cond = ""
                        else:
                            txt_inf_colchete = "[" if "Fechada" in tipo_inf else "]"
                            txt_inf_parentese = "[" if "Fechada" in tipo_inf else "("
                            txt_inf_colchete += str(limite_inf)
                            txt_inf_parentese += str(limite_inf)
                            sinal_inf_cond = f"{limite_inf} ≤ " if "Fechada" in tipo_inf else f"{limite_inf} < "
                            
                        if modo_sup == "Mais Infinito (+∞)":
                            txt_sup_colchete = "+∞["
                            txt_sup_parentese = "+∞)"
                            sinal_sup_cond = ""
                        else:
                            txt_sup_colchete = "]" if "Fechada" in tipo_sup else "["
                            txt_sup_parentese = "]" if "Fechada" in tipo_sup else ")"
                            txt_sup_colchete = str(limite_sup) + txt_sup_colchete
                            txt_sup_parentese = str(limite_sup) + txt_sup_parentese
                            sinal_sup_cond = f" ≤ {limite_sup}" if "Fechada" in tipo_sup else f" < {limite_sup}"
                            
                        # Determina o miolo da condição matemática x
                        if modo_inf == "Menos Infinito (-∞)" and modo_sup == "Mais Infinito (+∞)":
                            condicao_x = r"x \in \mathbb{R}"
                        elif modo_inf == "Menos Infinito (-∞)":
                            condicao_x = f"x {'<' if 'Aberta' in tipo_sup else '≤'} {limite_sup}"
                        elif modo_sup == "Mais Infinito (+∞)":
                            condicao_x = f"x {'>' if 'Aberta' in tipo_inf else '≥'} {limite_inf}"
                        else:
                            condicao_x = f"{limite_inf} {'≤' if 'Fechada' in tipo_inf else '<'} x {'≤' if 'Fechada' in tipo_sup else '<'} {limite_sup}"
                            
                        st.info(f"""
                        ### Representações equivalentes no material:
                        * **Notação em Colchetes:**  ` {txt_inf_colchete}, {txt_sup_colchete} `
                        * **Notação em Parênteses:** ` {txt_inf_parentese}, {txt_sup_parentese} `
                        * **Notação de Conjunto:** A = {{ x ∈ ℝ | {condicao_x} }}
                        """)
                        
                        # Geração gráfica otimizada sem redundância de imports em tempo de execução
                        fig, ax = plt.subplots(figsize=(8, 1.8))
                        ax.set_xlim(-12, 12)
                        ax.set_ylim(-1, 1)
                        
                        # Desenha a linha cinza de fundo
                        ax.axhline(0, color='lightgray', linewidth=2, zorder=1)
                        for tick in range(-10, 11, 2):
                            ax.plot([tick, tick], [-0.1, 0.1], color='lightgray', linewidth=1)
                            ax.text(tick, -0.5, str(tick), fontsize=9, ha='center', color='gray')
                        
                        # LÓGICA DE DESENHO DA LINHA VERMELHA E DAS FLECHAS DE INFINITO
                        barra_inf = -12 if modo_inf == "Menos Infinito (-∞)" else limite_inf
                        barra_sup = 12 if modo_sup == "Mais Infinito (+∞)" else limite_sup
                        
                        # Desenha o segmento de linha principal do intervalo
                        ax.plot([barra_inf, barra_sup], [0, 0], color='#ff4b4b', linewidth=6, zorder=2)
                        
                        # Se for menos infinito, adiciona uma flecha na ponta esquerda
                        if modo_inf == "Menos Infinito (-∞)":
                            ax.annotate('', xy=(-11, 0), xytext=(-5, 0),
                                        arrowprops=dict(arrowstyle="->", color='#ff4b4b', lw=6, mutation_scale=20), zorder=2)
                        else:
                            cor_inf = '#ff4b4b' if "Fechada" in tipo_inf else 'white'
                            ax.scatter(limite_inf, 0, color=cor_inf, edgecolors='#ff4b4b', s=150, linewidths=3, zorder=3)
                            
                        # Se for mais infinito, adiciona uma flecha na ponta direita
                        if modo_sup == "Mais Infinito (+∞)":
                            ax.annotate('', xy=(11, 0), xytext=(5, 0),
                                        arrowprops=dict(arrowstyle="->", color='#ff4b4b', lw=6, mutation_scale=20), zorder=2)
                        else:
                            cor_sup = '#ff4b4b' if "Fechada" in tipo_sup else 'white'
                            ax.scatter(limite_sup, 0, color=cor_sup, edgecolors='#ff4b4b', s=150, linewidths=3, zorder=3)
                        
                        ax.axis('off')
                        buf = io.BytesIO()
                        plt.savefig(buf, format='png', bbox_inches='tight', dpi=110, transparent=True)
                        buf.seek(0)
                        st.image(buf, use_container_width=True)
                        plt.close(fig) # Liberando explicitamente a memória RAM associada à figura
                        
                # --- RECURSO 2: QUIZ VARIADO COM INFINITOS, COLCHETES E PARÊNTESES ---
                with aba_game:
                    st.markdown("### 2. Desafio das Extremidades e Multi-Notações")
                    st.write("Responda se o ponto faz parte do intervalo. Fique atento pois o sistema alternará dinamicamente entre parênteses e colchetes!")
                    
                    if "cont_rodadas_intervalos" not in st.session_state:
                        st.session_state.cont_rodadas_intervalos = 0
                        
                    if "game_intervalo_atual" not in st.session_state:
                        tipo_exercicio = random.choice(["finito", "inf_esq", "inf_dir"])
                        f_esq = random.choice(["aberto", "fechado"])
                        f_dir = random.choice(["aberto", "fechado"])
                        estilo_notacao = random.choice(["colchete", "parentese"])
                        
                        if tipo_exercicio == "finito":
                            a_game = random.randint(-5, 2)
                            b_game = a_game + random.randint(3, 6)
                            ponto_teste = random.choice([a_game, b_game])
                            pertence = "Sim" if (ponto_teste == a_game and f_esq == "fechado") or (ponto_teste == b_game and f_dir == "fechado") else "Não"
                            
                            if estilo_notacao == "colchete":
                                texto_intervalo = f"{']' if f_esq == 'aberto' else '['}{a_game}, {b_game}{'[' if f_dir == 'aberto' else ']'}"
                            else:
                                texto_intervalo = f"{'(' if f_esq == 'aberto' else '['}{a_game}, {b_game}{')' if f_dir == 'aberto' else ']'}"
                                
                        elif tipo_exercicio == "inf_esq":
                            b_game = random.randint(-2, 5)
                            ponto_teste = b_game
                            pertence = "Sim" if f_dir == "fechado" else "Não"
                            
                            if estilo_notacao == "colchete":
                                texto_intervalo = f"]-∞, {b_game}{'[' if f_dir == 'aberto' else ']'}"
                            else:
                                texto_intervalo = f"(-∞, {b_game}{')' if f_dir == 'aberto' else ']'}"
                        
                        else: # inf_dir
                            a_game = random.randint(-5, 3)
                            ponto_teste = a_game
                            pertence = "Sim" if f_esq == "fechado" else "Não"
                            
                            if estilo_notacao == "colchete":
                                texto_intervalo = f"{']' if f_esq == 'aberto' else '['}{a_game}, +∞["
                            else:
                                texto_intervalo = f"{'(' if f_esq == 'aberto' else '['}{a_game}, +∞)"
                                
                        st.session_state.game_intervalo_atual = {
                            "texto": texto_intervalo, "ponto": ponto_teste, "resposta": pertence
                        }
                        
                    g = st.session_state.game_intervalo_atual
                    st.markdown(f"### Considere o intervalo real: ` A = {g['texto']} `")
                    st.markdown(f"### O número **` {g['ponto']} `** pertence ao intervalo A?")
                    
                    if "intervalo_respondido" not in st.session_state:
                        st.session_state.intervalo_respondido = False
                        
                    if not st.session_state.intervalo_respondido:
                        with st.form(key=f"form_intervalos_r{st.session_state.cont_rodadas_intervalos}"):
                            res_aluno = st.radio("Escolha uma resposta:", ["Sim", "Não"], index=None, key=f"radio_int_r{st.session_state.cont_rodadas_intervalos}")
                            btn_valida = st.form_submit_button("🎯 Validar Resposta")
                            
                        if btn_valida:
                            if res_aluno is None:
                                st.warning("⚠️ Selecione uma alternativa primeiro!")
                            else:
                                st.session_state.intervalo_respondido = True
                                st.session_state.ultima_resposta_int = res_aluno
                                st.rerun()
                                
                    if st.session_state.intervalo_respondido:
                        if st.session_state.ultima_resposta_int == g['resposta']:
                            st.success("🎉 PARABÉNS! ")
                        else:
                            st.error(f"❌ Resposta incorreta. O número `{g['ponto']}` {g['resposta'].lower()} pertence ao conjunto.")
                            
                        st.markdown("#### 👨‍🏫 Explicação de Engenharia da UniCesumar:")
                        st.write("Fique muito atento à tabela de equivalências: parênteses `()` e colchetes voltados para fora `][` significam exatamente a mesma coisa: **Intervalo Aberto (Bolinha Extremidade Não Incluída)**.")
                        # Corrigido: Usando a notação matemática limpa com \$ para evitar conflitos de escape no interpretador do Python
                        st.write("Por definição conceitual, as extremidades infinitas (\(\infty\)) são sempre abertas e representadas por parênteses ou colchetes para fora!")
                        
                        st.write("---")
                        if st.button("➡️ Próximo Intervalo", use_container_width=True):
                            if "game_intervalo_atual" in st.session_state:
                                del st.session_state.game_intervalo_atual
                            st.session_state.intervalo_respondido = False
                            st.session_state.cont_rodadas_intervalos += 1
                            st.rerun()


            # 4. NOVA SUB-ABA: ESQUELETO DA FÁBRICA DE FUNÇÕES E CONCEITOS RIGOROSOS
            with sub_fabrica_funcoes:
                st.subheader("🏭 Central de Processamento de Funções")
                # Corrigido: Removidas quaisquer barras de escape para textos puramente explicativos, eliminando os avisos de sintaxe
                st.write("Entenda o Conceito Rigoroso de Função como uma máquina industrial:")
                st.write("você insere uma entrada (x), a máquina aplica uma regra matemática,")
                st.write("e devolve uma saída exclusiva (y) ou f(x).")
                
                # Menu Seletor para navegar entre os esqueletos estruturais das 3 ideias pedagógicas
                opcao_estacao = st.radio(
                    "Selecione a Estação de Aprendizado Prático:",
                    [
                        "1. A Máquina de Funções Interativa",
                        "2. Simulador de Flechas (Domínio, Contradomínio e Imagem)",
                        "3. Detetive de Restrições (Evitando Erros de Engenharia)"
                    ],
                    horizontal=True
                )
                
                st.write("---")
                
                # --- ESTAÇÃO 1: PAINEL INTEGRADO EM TEMPO REAL (SEM BOTÃO E COM MÁXIMO ESPAÇO) ---
                if "1." in opcao_estacao:
                    # Criação das duas grandes colunas macro para dividir a tela ao meio
                    col_painel_esq, col_grafico_dir = st.columns([0.8, 1.2])
                    
                    with col_painel_esq:
                        # Seletor do grau da função
                        grau_funcao = st.selectbox(
                            "Escolha o Grau da Máquina Matemática:", 
                            [
                                "1º Grau (Função Afim: f(x) = ax + b)", 
                                "2º Grau (Função Quadrática: f(x) = ax² + bx + c)", 
                                "3º Grau (Função Cúbica: f(x) = ax³ + bx² + cx + d)"
                            ],
                            key="select_grau_funcao"
                        )
                        
                        # Entrada x principal
                        x_entrada = st.number_input("Insira o valor da entrada (x):", value=2.0, step=0.5, key="num_x_fabrica")
                        
                        st.markdown("##### Defina os Parâmetros da Função:")
                        c_coef1, c_coef2 = st.columns(2)
                        
                        # Processamento condicional instantâneo dos coeficientes e cálculo de y
                        if "1º Grau" in grau_funcao:
                            with c_coef1:
                                coef_a = st.number_input("Coeficiente (a):", value=2.0, step=0.5, key="coef_a_1")
                            with c_coef2:
                                coef_b = st.number_input("Coeficiente (b):", value=3.0, step=0.5, key="coef_b_1")
                                
                            coef_c, coef_d = 0.0, 0.0
                            y_saida = coef_a * x_entrada + coef_b
                            b_sinal = f"+ {coef_b}" if coef_b >= 0 else f"- {abs(coef_b)}"
                            lei_geral_texto = f"f(x) = {coef_a}x {b_sinal}"
                            memorial_texto = rf"f({x_entrada}) = {coef_a} \cdot ({x_entrada}) {b_sinal} = {coef_a * x_entrada} {b_sinal} = {y_saida}"
                            
                        elif "2º Grau" in grau_funcao:
                            with c_coef1:
                                coef_a = st.number_input("Coeficiente (a):", value=1.0, step=0.5, key="coef_a_2")
                                coef_b = st.number_input("Coeficiente (b):", value=0.0, step=0.5, key="coef_b_2")
                            with c_coef2:
                                coef_c = st.number_input("Coeficiente (c):", value=0.0, step=0.5, key="coef_c_2")
                                
                            coef_d = 0.0
                            y_saida = coef_a * (x_entrada ** 2) + coef_b * x_entrada + coef_c
                            b_sinal = f"+ {coef_b}" if coef_b >= 0 else f"- {abs(coef_b)}"
                            c_sinal = f"+ {coef_c}" if coef_c >= 0 else f"- {abs(coef_c)}"
                            lei_geral_texto = f"f(x) = {coef_a}x^2 {b_sinal}x {c_sinal}"
                            memorial_texto = rf"f({x_entrada}) = {coef_a} \cdot ({x_entrada})^2 {b_sinal} \cdot ({x_entrada}) {c_sinal} = {y_saida}"
                            
                        else:
                            with c_coef1:
                                coef_a = st.number_input("Coeficiente (a):", value=1.0, step=0.5, key="coef_a_3")
                                coef_b = st.number_input("Coeficiente (b):", value=0.0, step=0.5, key="coef_b_3")
                            with c_coef2:
                                coef_c = st.number_input("Coeficiente (c):", value=0.0, step=0.5, key="coef_c_3")
                                d_num = st.number_input("Coeficiente (d):", value=0.0, step=0.5, key="coef_d_3")
                                coef_d = d_num
                                
                            y_saida = coef_a * (x_entrada ** 3) + coef_b * (x_entrada ** 2) + coef_c * x_entrada + coef_d
                            b_sinal = f"+ {coef_b}" if coef_b >= 0 else f"- {abs(coef_b)}"
                            c_sinal = f"+ {coef_c}" if coef_c >= 0 else f"- {abs(coef_c)}"
                            d_sinal = f"+ {coef_d}" if coef_d >= 0 else f"- {abs(coef_d)}"
                            lei_geral_texto = f"f(x) = {coef_a}x^3 {b_sinal}x^2 {c_sinal}x {d_sinal}"
                            memorial_texto = rf"f({x_entrada}) = {coef_a} \cdot ({x_entrada})^3 {b_sinal} \cdot ({x_entrada})^2 {c_sinal} \cdot ({x_entrada}) {d_sinal} = {y_saida}"
                            
                        # [SISTEMA EM TEMPO REAL] Exibe os blocos diretamente sem necessidade de clique em botão
                        st.write("---")
                        st.success(f"### Saída Obtida: $y = {y_saida}$")
                        st.markdown("##### 🔬 Memorial de Cálculo Ativo:")
                        st.latex(memorial_texto)
                        
                    with col_grafico_dir:
                        # Geração contínua e instantânea do rastro da curva
                        x_curva = np.linspace(-10, 10, 300)
                        if "1º Grau" in grau_funcao:
                            y_curva = coef_a * x_curva + coef_b
                        elif "2º Grau" in grau_funcao:
                            y_curva = coef_a * (x_curva ** 2) + coef_b * x_curva + coef_c
                        else:
                            y_curva = coef_a * (x_curva ** 3) + coef_b * (x_curva ** 2) + coef_c * x_curva + coef_d
                            
                        fig_fabrica = go.Figure()
                        
                        # Desenha o rastro da linha
                        fig_fabrica.add_trace(go.Scatter(
                            x=x_curva, y=y_curva, mode='lines', 
                            name=lei_geral_texto, line=dict(color='#ff4b4b', width=3)
                        ))
                        
                        # Desenha as linhas tracejadas de projeção
                        fig_fabrica.add_trace(go.Scatter(
                            x=[x_entrada, x_entrada], y=[0, y_saida],
                            mode='lines', name='Projeção X (Domínio)',
                            line=dict(color='gray', width=2, dash='dash'),
                            showlegend=False
                        ))
                        fig_fabrica.add_trace(go.Scatter(
                            x=[0, x_entrada], y=[y_saida, y_saida],
                            mode='lines', name='Projeção Y (Imagem)',
                            line=dict(color='gray', width=2, dash='dash'),
                            showlegend=False
                        ))
                        
                        # Desenha a bolinha amarela do ponto gerado
                        fig_fabrica.add_trace(go.Scatter(
                            x=[x_entrada], y=[y_saida], mode='markers', 
                            name=f'Ponto Processado ({x_entrada}, {y_saida})',
                            marker=dict(color='gold', size=14, symbol='circle', line=dict(color='black', width=2))
                        ))
                        
                        # Layout maximizado: título removido e legenda horizontal na parte inferior
                        fig_fabrica.update_layout(
                            xaxis=dict(title="Eixo X (Domínio)", range=[-10, 10], zeroline=True, zerolinecolor='black', zerolinewidth=1.5),
                            yaxis=dict(title="Eixo Y (Imagem)", range=[-10, 20] if "2º Grau" in grau_funcao else [-10, 15], zeroline=True, zerolinecolor='black', zerolinewidth=1.5),
                            margin=dict(l=10, r=10, t=10, b=10),
                            height=520,
                            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(240,242,246,0.5)',
                            hovermode="closest",
                            legend=dict(
                                orientation="h",
                                yanchor="top",
                                y=-0.15,
                                xanchor="center",
                                x=0.5
                            )
                        )
                        st.plotly_chart(fig_fabrica, use_container_width=True, config={"scrollZoom": True})
                        
                # --- ESTAÇÃO 2: SIMULADOR DE FLECHAS ---
                elif "2." in opcao_estacao:
                    st.markdown("### 🏹 Estação 2: Diagrama de Flechas (Domínio vs Imagem)")
                    st.write(
                        "Aqui renderizaremos dois conjuntos circulares (Venn) lado a lado. "
                        "Ao rodar o simulador, flechas animadas sairão do Domínio (Conjunto A) "
                        "e atingirão o Contradomínio (Conjunto B), destacando quais números farão parte da Imagem."
                    )
                    st.warning("🟡 Módulo estrutural criado. O mapa visual de flechas geométricas está sendo preparado para codificação.")

                # --- ESTAÇÃO 3: DETETIVE DE RESTRIÇÕES ---
                else:
                    st.markdown("### 🕵️ Estação 3: O Detetive de Restrições")
                    st.write(
                        r"Aqui montaremos o minigame focado nas funções que 'quebram' (como divisões por zero). "
                        r"O estudante precisará analisar equações e identificar quais valores de \(x\) explodiriam a máquina, "
                        "acumulando pontos por prever falhas em projetos técnicos."
                    )
                    st.warning("🟡 Módulo estrutural criado. O banco de desafios de restrições lógicas está aguardando os códigos matemáticos.")

        # --- OUTRAS AULAS AGUARDANDO LIBERAÇÃO ---
        else:
            st.markdown(f"## 🧪 {aula_selecionada}")
            st.info("🟡 Esta aula ainda não aconteceu ao vivo. O conteúdo prático será liberado em breve!")

elif materia == "Engenharia Econômica":
    st.header("💰 Engenharia Econômica")
    st.info("Módulo 54 selecionado. Estrutura pronta para receber o desenvolvimento de ferramentas de engenharia financeira.")
    
    aba_upload, aba_tutor, aba_calculadora_financas = st.tabs(["📁 Gerenciar Materiais", "👨‍🏫 Tutor IA", "📊 Analisador de Viabilidade"])
    
    with aba_upload:
        st.subheader("📚 Biblioteca Oficial de Materiais - Eng. Econômica")
        st.write("Consulte os materiais didáticos oficiais disponíveis para esta disciplina.")
        
        # O sistema apenas lista os arquivos que você colocou previamente na pasta do servidor
        salvos = os.listdir(pasta_da_materia)
        if salvos:
            sel = st.selectbox("Selecione o arquivo de Economia:", salvos, key="sel_material_economia")
            # Busca o texto usando o cache de alta velocidade
            texto_extraido_economia = obter_conteudo_cached(os.path.join(pasta_da_materia, sel))
            st.text_area("Texto extraído para análise da IA:", texto_extraido_economia, height=150)
        else:
            st.info("Aguardando o upload dos materiais oficiais pelo administrador do sistema.")
            
    with aba_tutor:
        st.subheader("👨‍🏫 Tutor Inteligente de Engenharia Econômica")
        salvos = os.listdir(pasta_da_materia)
        if salvos:
            dbase = st.selectbox("Documento base de Economia:", salvos, key="db_economia")
            pergs = st.text_input("Qual sua dúvida sobre VPL, TIR, juros ou amortizações?")
            if pergs:
                with st.spinner("Analisando fluxos de caixa..."): 
                    # Otimizado com leitura em cache de alta velocidade
                    contexto_doc_economia = obter_conteudo_cached(os.path.join(pasta_da_materia, dbase))
                    st.markdown(responder_com_contexto(contexto_doc_economia, pergs))

    with aba_calculadora_financas:
        st.subheader("📊 Motor de Análise Financeira")
        st.write("Em breve: Resolução interativa e gráfica de VPL, TIR e amortizações.")
