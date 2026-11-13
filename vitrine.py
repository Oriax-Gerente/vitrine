import streamlit as st
import urllib.parse
import base64
import unicodedata
import os
import sys
import sqlite3
from datetime import datetime
import pandas as pd

# ==============================================================================
# 1. CONFIGURAÇÃO DA PÁGINA E METADADOS
# ==============================================================================
st.set_page_config(
    page_title="EMCCAMP|INX Residencial | Equipe Gerente Oriax",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 2. SISTEMA DE BANCO DE DADOS E ESTATÍSTICAS (CONTADOR DE VISITAS E CLIQUES)
# ==============================================================================
DB_PATH = "estatisticas_vitrine.db"

def inicializar_banco():
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS acessos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_hora TEXT,
                tipo_evento TEXT,
                detalhe TEXT
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao inicializar banco de dados: {e}")

def registrar_evento(tipo_evento: str, detalhe: str = "Geral"):
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        cursor = conn.cursor()
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO acessos (data_hora, tipo_evento, detalhe) VALUES (?, ?, ?)", 
                       (data_hora, tipo_evento, detalhe))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao registrar evento: {e}")

inicializar_banco()

# ==============================================================================
# 3. CONSTANTES E UTILITÁRIOS DE IMAGEM
# ==============================================================================
WHATSAPP_NUMERO = "5511982003873"
WHATSAPP_DISPLAY = "(11) 98200-3873"
GERENTE_NOME = "Gerente Oriax"

def obter_caminho_recurso(caminho_relativo: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, caminho_relativo)

def normalizar_texto(texto: str) -> str:
    nfkd = unicodedata.normalize("NFKD", str(texto).lower())
    sem_acento = "".join([c for c in nfkd if not unicodedata.combining(c)])
    return sem_acento.replace("-", "_").replace(" ", "_")

def carregar_imagem_base64(caminho_arquivo: str) -> str:
    if not caminho_arquivo or not os.path.exists(caminho_arquivo):
        return ""
    ext = os.path.splitext(caminho_arquivo)[1].lower().replace(".", "")
    mime = "jpeg" if ext in ["jpg", "jpeg"] else ("webp" if ext == "webp" else "png")
    with open(caminho_arquivo, "rb") as f:
        dados_b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/{mime};base64,{dados_b64}"

def obter_empreendimento_imagem(nome_arquivo_imagem: str) -> str:
    if not nome_arquivo_imagem:
        return ""
    pasta_imagens = obter_caminho_recurso("imagens")
    if not os.path.exists(pasta_imagens):
        return ""

    caminho_exato = os.path.join(pasta_imagens, nome_arquivo_imagem)
    if os.path.exists(caminho_exato):
        return carregar_imagem_base64(caminho_exato)

    alvo_norm = normalizar_texto(os.path.splitext(nome_arquivo_imagem)[0])
    extensoes_validas = {".jpg", ".jpeg", ".png", ".webp"}

    for arquivo in os.listdir(pasta_imagens):
        nome_arq, ext_arq = os.path.splitext(arquivo)
        if ext_arq.lower() in extensoes_validas:
            if normalizar_texto(nome_arq) == alvo_norm:
                return carregar_imagem_base64(os.path.join(pasta_imagens, arquivo))

    return ""

def carregar_logo_base64() -> str:
    possiveis_nomes = ["logo_oriax.jpg", "logo_oriax.png", "channels4_profile.jpg", "logo.jpg", "logo.png"]
    for nome in possiveis_nomes:
        caminho = obter_caminho_recurso(nome)
        if os.path.exists(caminho):
            return carregar_imagem_base64(caminho)
    return ""

def gerar_link_whatsapp(mensagem: str) -> str:
    return f"https://wa.me/{WHATSAPP_NUMERO}?text={urllib.parse.quote(mensagem)}"

def formatar_moeda_br(valor: float) -> str:
    try:
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"

# ==============================================================================
# 4. ESTILIZAÇÃO VISUAL (TEMA ESCURO + VERDE, BRANCO, LARANJA)
# ==============================================================================
st.markdown("""
<style>
    .stApp { background-color: #0B0F17; color: #FFFFFF; }
    section[data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #1F2937; }
    section[data-testid="stSidebar"] * { color: #F9FAFB; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {background-color: transparent !important;}

    .hero-banner {
        background: linear-gradient(135deg, #111827 0%, #064E3B 100%);
        border: 1px solid #10B981;
        border-radius: 16px;
        padding: 32px;
        margin-bottom: 28px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    .hero-badge {
        background-color: #F97316; color: #FFFFFF;
        padding: 5px 14px; border-radius: 20px;
        font-size: 0.80rem; font-weight: 800; text-transform: uppercase;
        display: inline-block; margin-bottom: 12px;
    }

    .product-card {
        background-color: #151C28;
        border: 1px solid #263143;
        border-radius: 14px;
        overflow: hidden;
        margin-bottom: 14px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .product-card:hover {
        transform: translateY(-4px);
        border-color: #10B981;
        box-shadow: 0 8px 24px rgba(16, 185, 129, 0.15);
    }

    .card-img-container {
        width: 100%;
        height: 185px;
        overflow: hidden;
        background-color: #0F172A;
        border-bottom: 2px solid #F97316;
        position: relative;
    }
    .card-img {
        width: 100%;
        height: 185px;
        object-fit: cover;
        display: block;
    }
    .card-img-placeholder {
        width: 100%;
        height: 185px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #111827 0%, #064E3B 100%);
        color: #9CA3AF;
        font-size: 0.82rem;
        font-weight: 700;
        text-align: center;
        padding: 12px;
    }

    .custom-footer {
        background-color: #151C28;
        border: 1px solid #263143;
        border-top: 3px solid #F97316;
        border-radius: 14px;
        padding: 32px;
        margin-top: 40px;
        text-align: center;
        color: #D1D5DB;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }

    .footer-whatsapp-btn {
        display: inline-block;
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: #FFFFFF !important;
        padding: 14px 28px;
        border-radius: 8px;
        font-weight: 800;
        font-size: 1.05rem;
        text-decoration: none !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        margin: 16px 0;
    }
    .footer-whatsapp-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 5. CARREGAMENTO DINÂMICO VIA PLANILHA (tabelavitrine.xlsx)
# ==============================================================================
EXCEL_PATH = obter_caminho_recurso("tabelavitrine.xlsx")

def carregar_empreendimentos():
    if not os.path.exists(EXCEL_PATH):
        st.error(f"⚠️ O arquivo '{EXCEL_PATH}' não foi encontrado na pasta do projeto!")
        return []
    
    try:
        df = pd.read_excel(EXCEL_PATH)
        
        colunas_texto = ["nome", "imagem", "estado", "cidade", "endereco", "status", "tipologia", "diferenciais", "programa"]
        for col in colunas_texto:
            if col in df.columns:
                df[col] = df[col].fillna("").astype(str)
                
        if "preco_a_partir" in df.columns:
            df["preco_a_partir"] = pd.to_numeric(df["preco_a_partir"], errors="coerce").fillna(0.0)

        return df.to_dict(orient="records")
    
    except Exception as e:
        st.error(f"Erro ao ler a planilha 'tabelavitrine.xlsx': {e}")
        return []

EMPREENDIMENTOS = carregar_empreendimentos()

if "visitou_vitrine" not in st.session_state:
    registrar_evento("visualizacao_pagina", "Home Principal")
    st.session_state["visitou_vitrine"] = True

# ==============================================================================
# 6. BARRA LATERAL (LOGO + FILTROS + SIMULADOR + PAINEL DE ESTATÍSTICAS)
# ==============================================================================
logo_uri = carregar_logo_base64()

with st.sidebar:
    if logo_uri:
        st.markdown(f'<div style="text-align:center;"><img src="{logo_uri}" style="width:140px; height:140px; object-fit:cover; border-radius:14px; border:2px solid #F97316; margin-bottom:10px;"></div>', unsafe_allow_html=True)

    st.markdown(
        f'<div style="text-align:center; padding: 4px 0 10px 0; border-bottom: 1px solid #1F2937;">'
        f'<span style="background:#F97316; color:#FFF; padding:4px 12px; border-radius:6px; font-weight:800; font-size:0.75rem;">ATENDIMENTO VIP</span>'
        f'<h2 style="margin:6px 0 4px 0; color:#FFFFFF; font-size:1.4rem;">EMCCAMP|INX</h2>'
        f'<p style="margin:0; color:#10B981; font-weight:700; font-size:0.95rem;">Equipe {GERENTE_NOME}</p>'
        f'<p style="margin:4px 0 0 0; color:#9CA3AF; font-size:0.85rem;">WhatsApp: {WHATSAPP_DISPLAY}</p>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown("### 🔍 Filtrar Imóveis")
    
    opcoes_status = sorted(list(set(str(emp.get("status", "")).strip() for emp in EMPREENDIMENTOS if str(emp.get("status", "")).strip())))
    
    status_selecionado = st.multiselect(
        "Estágio da Obra / Status:",
        options=opcoes_status,
        default=opcoes_status
    )

    preco_max = st.slider(
        "Valor Máximo do Imóvel (R$):",
        min_value=100000, max_value=800000, value=600000, step=10000, format="R$ %d"
    )

    busca_texto = st.text_input("Buscar por bairro ou nome:", placeholder="Ex: Santo Amaro, Jundiaí...")

    st.markdown("---")
    st.markdown("### 🧮 Simulação Rápida MCMV")
    renda_cliente = st.number_input("Sua Renda Familiar Bruta (R$):", min_value=1500.0, max_value=25000.0, value=4500.0, step=250.0)
    fgts_cliente = st.number_input("Saldo de FGTS disponível (R$):", min_value=0.0, max_value=150000.0, value=15000.0, step=1000.0)

    parcela_estimada = renda_cliente * 0.30
    st.info(f"💡 **Parcela estimada:** {formatar_moeda_br(parcela_estimada)}/mês")

    msg_simulacao = f"Olá! Gostaria de fazer uma simulação de financiamento EMCCAMP|INX com a equipe do {GERENTE_NOME}. Renda: {formatar_moeda_br(renda_cliente)}, FGTS: {formatar_moeda_br(fgts_cliente)}."
    
    if st.link_button(f"📲 Enviar Simulação ao {GERENTE_NOME}", gerar_link_whatsapp(msg_simulacao), use_container_width=True):
        registrar_evento("clique_botao", "Simulador Rápido MCMV")

    st.markdown("---")
    with st.expander("📊 Painel Gerencial (Acessos)"):
        senha_gerente = st.text_input("Senha do Gerente:", type="password")
        if senha_gerente == "Creci282678FSP":
            try:
                conn = sqlite3.connect(DB_PATH, check_same_thread=False)
                df_logs = pd.read_sql_query("SELECT * FROM acessos ORDER BY id DESC", conn)
                conn.close()

                total_visitas = len(df_logs[df_logs["tipo_evento"] == "visualizacao_pagina"])
                total_cliques = len(df_logs[df_logs["tipo_evento"] == "clique_imovel"])

                st.metric("Total de Visitas Únicas", total_visitas)
                st.metric("Cliques em Imóveis", total_cliques)

                if not df_logs.empty:
                    st.markdown("#### Últimos Registros:")
                    st.dataframe(df_logs.head(10), use_container_width=True)
            except Exception as e:
                st.error(f"Erro ao carregar dados: {e}")
        elif senha_gerente:
            st.error("Senha incorreta!")

# ==============================================================================
# 7. BANNER HERO
# ==============================================================================
msg_geral = f"Olá! Acessei o catálogo digital da EMCCAMP|INX e gostaria de ser atendido pela equipe de corretores do {GERENTE_NOME}."

st.markdown(
    f'<div class="hero-banner">'
    f'<div class="hero-badge">PORTFÓLIO OFICIAL • SÃO PAULO E REGIÃO</div>'
    f'<h1 style="color: #FFFFFF; font-size: 2.3rem; margin-bottom: 10px;">Conquiste seu EMCCAMP|INX com Condições Diretas de Construtora</h1>'
    f'<p style="color: #D1D5DB; font-size: 1.05rem; margin-bottom: 20px;">'
    f'Explore todos os lançamentos, obras em andamento, imóveis prontos e empreendimentos no interior paulista. '
    f'Atendimento exclusivo realizado pela <strong>equipe de corretores do {GERENTE_NOME}</strong>.'
    f'</p>'
    f'</div>',
    unsafe_allow_html=True
)
if st.link_button(f"💬 Falar no WhatsApp: {WHATSAPP_DISPLAY} ({GERENTE_NOME})", gerar_link_whatsapp(msg_geral), use_container_width=True):
    registrar_evento("clique_botao", "Banner Principal WhatsApp")
st.write("")

# ==============================================================================
# 8. FILTRAGEM E EXIBIÇÃO EM GRID PROFISSIONAL
# ==============================================================================
def filtrar_lista():
    filtrados = []
    for item in EMPREENDIMENTOS:
        status_item = str(item.get("status", "")).strip()
        if status_item not in status_selecionado:
            continue
        
        preco_val = float(item.get("preco_a_partir", 0))
        if preco_val > 0 and preco_val > preco_max:
            continue
            
        if busca_texto.strip():
            termo = busca_texto.lower().strip()
            if termo not in str(item.get("nome", "")).lower() and termo not in str(item.get("cidade", "")).lower() and termo not in str(item.get("diferenciais", "")).lower():
                continue
        filtrados.append(item)
    return filtrados

def renderizar_grade(imoveis):
    if not imoveis:
        st.warning("Nenhum empreendimento encontrado com os filtros atuais.")
        return

    for i in range(0, len(imoveis), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(imoveis):
                emp = imoveis[i + j]
                with cols[j]:
                    img_uri = obter_empreendimento_imagem(emp.get("imagem", ""))
                    if img_uri:
                        bloco_img = f'<div class="card-img-container"><img src="{img_uri}" class="card-img"></div>'
                    else:
                        bloco_img = f'<div class="card-img-container"><div class="card-img-placeholder"><span>🏢 EMCCAMP|INX • {emp.get("nome", "")}</span></div></div>'

                    status_emp = str(emp.get("status", "Disponível"))
                    if "Lançamento" in status_emp:
                        badge_status = f'<span style="background:rgba(249,115,22,0.18); color:#FB923C; border:1px solid #F97316; padding:2px 8px; border-radius:4px; font-size:0.7rem; font-weight:700;">{status_emp}</span>'
                    elif "Pronto" in status_emp or "Entregue" in status_emp:
                        badge_status = f'<span style="background:rgba(255,255,255,0.15); color:#FFFFFF; border:1px solid #FFFFFF; padding:2px 8px; border-radius:4px; font-size:0.7rem; font-weight:700;">{status_emp}</span>'
                    else:
                        badge_status = f'<span style="background:rgba(16,185,129,0.18); color:#34D399; border:1px solid #10B981; padding:2px 8px; border-radius:4px; font-size:0.7rem; font-weight:700;">{status_emp}</span>'

                    preco_valor = float(emp.get("preco_a_partir", 0))
                    texto_preco = formatar_moeda_br(preco_valor) if preco_valor > 0 else "Consulte Disponibilidade"

                    html_card = (
                        f'<div class="product-card">'
                        f'<div>'
                        f'{bloco_img}'
                        f'<div style="padding: 16px 18px 0 18px;">'
                        f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">'
                        f'<span style="background:#1F2937; color:#10B981; border:1px solid #10B981; padding:2px 8px; border-radius:4px; font-size:0.7rem; font-weight:700;">📍 {emp.get("estado", "SP")} • {emp.get("programa", "MCMV")}</span>'
                        f'{badge_status}'
                        f'</div>'
                        f'<div style="font-size: 1.25rem; font-weight: 800; color: #FFFFFF; margin-bottom: 4px;">{emp.get("nome", "")}</div>'
                        f'<div style="font-size: 0.85rem; color: #9CA3AF; margin-bottom: 12px;">{emp.get("cidade", "")}<br><small>{emp.get("endereco", "")}</small></div>'
                        f'<div style="background-color:#0F1520; border-left:3px solid #F97316; padding:8px; border-radius:6px; font-size:0.82rem; color:#E5E7EB; margin-bottom:14px;">'
                        f'<strong>Tipologia:</strong> {emp.get("tipologia", "")}<br>'
                        f'<span style="color:#D1D5DB;">{emp.get("diferenciais", "")}</span>'
                        f'</div>'
                        f'</div>'
                        f'</div>'
                        f'<div style="padding: 0 18px 18px 18px;">'
                        f'<div style="font-size: 0.75rem; color: #9CA3AF; text-transform: uppercase;">Unidades a partir de</div>'
                        f'<div style="font-size: 1.4rem; font-weight: 800; color: #10B981;">{texto_preco}</div>'
                        f'</div>'
                        f'</div>'
                    )

                    st.markdown(html_card, unsafe_allow_html=True)

                    msg_wpp = f"Olá! Tenho interesse no empreendimento *{emp.get('nome', '')}* ({emp.get('cidade', '')} - {emp.get('estado', 'SP')}). Gostaria de receber a tabela de valores com a equipe do {GERENTE_NOME}."
                    
                    if st.link_button(f"📲 Consultar Equipe Gerente", gerar_link_whatsapp(msg_wpp), use_container_width=True):
                        registrar_evento("clique_imovel", emp.get("nome", "Imóvel"))

lista_imoveis = filtrar_lista()
st.markdown(f"### 🏙️ Catálogo de Empreendimentos (São Paulo e Região)")
st.markdown(f"**Exibindo {len(lista_imoveis)} empreendimento(s) disponível(is)**")
renderizar_grade(lista_imoveis)

# ==============================================================================
# 9. RODAPÉ INSTITUCIONAL COM ESTILO PREMIUM
# ==============================================================================
st.markdown(f"""
<div class="custom-footer">
    <h3 style="color:#FFFFFF; margin-bottom:8px; font-size:1.4rem; font-weight:800;">Atendimento Exclusivo — Equipe de Corretores do {GERENTE_NOME}</h3>
    <p style="color:#9CA3AF; font-size:0.95rem; max-width:750px; margin:0 auto 16px auto; line-height: 1.5;">
        Consultoria especializada em Minha Casa Minha Vida, Casa Paulista, uso de FGTS e aprovação de crédito junto à Caixa Econômica Federal.
        Todos os atendimentos deste portal são direcionados diretamente para a equipe do <strong>{GERENTE_NOME}</strong>.
    </p>
    <a href="{gerar_link_whatsapp(msg_geral)}" target="_blank" class="footer-whatsapp-btn">
        📞 Chamar no WhatsApp: {WHATSAPP_DISPLAY}
    </a>
    <p style="color:#6B7280; font-size:0.8rem; margin-top:18px;">
        *Valores iniciais sujeitos à disponibilidade de unidades e alteração de tabela pela incorporadora sem aviso prévio.
    </p>
</div>
""", unsafe_allow_html=True)