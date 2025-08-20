import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

# Funções Auxiliares
def validar_colunas(df, colunas_minimas):
    missing = set(colunas_minimas) - set(df.columns)
    if missing:
        st.error(f"O arquivo enviado está faltando as colunas: {', '.join(missing)}")
        return False
    return True

def calcula_recomendacao(df, dias_periodo, leadtime_padrao, perc_seguranca):
    if "LeadTime" not in df.columns:
        df["LeadTime"] = np.nan
    # Preenche valores faltantes com padrão, e converte para inteiro
    df["LeadTime"] = df["LeadTime"].fillna(leadtime_padrao).astype(int)
    df["TotalVendido"] = df["TotalVendido"].astype(float)
    df["EstoqueAtual"] = df["EstoqueAtual"].fillna(0).astype(float)
    df["MediaDiaria"] = df["TotalVendido"] / dias_periodo
    df["EstoqueSeguranca"] = np.ceil(df["MediaDiaria"] * df["LeadTime"] * perc_seguranca)
    df["EstoqueMinimo"] = np.ceil(df["MediaDiaria"] * df["LeadTime"] + df["EstoqueSeguranca"])
    df["QtdRepor"] = df["EstoqueMinimo"] - df["EstoqueAtual"]
    df["QtdRepor"] = df["QtdRepor"].apply(lambda x: max(x, 0))
    df["Repor"] = df["QtdRepor"].apply(lambda x: "SIM" if x > 0 else "NÃO")
    colunas = ["Empresa", "Produto", "TotalVendido", "EstoqueAtual", "LeadTime", "MediaDiaria", "EstoqueSeguranca", "EstoqueMinimo", "QtdRepor", "Repor"]
    return df[colunas]

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# Modelo de planilha disponível para download
modelo = pd.DataFrame({
    "Empresa": ["01", "01"],
    "Produto": ["PROD001", "PROD002"],
    "TotalVendido": [100, 50],
    "EstoqueAtual": [20, 10],
    "LeadTime": [7, None],  # Pode ser preenchido ou não
})
csv = modelo.to_csv(index=False, sep=";").encode()

# --- Interface Streamlit ---
st.title("Recomendação de Estoque (Upload Único)")

st.markdown("""
Faça upload de um arquivo (.csv ou .xlsx) com as colunas:
- **Empresa**
- **Produto**
- **TotalVendido**
- **EstoqueAtual**
- **LeadTime** (opcional)<br>
Se não for informado, será utilizado o padrão ao lado.
""", unsafe_allow_html=True)

st.download_button(
    "Baixar modelo (.csv)", 
    data=csv,
    file_name="modelo_upload_estoque.csv",
    mime="text/csv"
)

# Parâmetros
leadtime_padrao = st.sidebar.number_input("Lead Time padrão (dias)", min_value=1, value=7)
perc_seguranca = st.sidebar.slider("% Estoque Segurança", min_value=0.0, max_value=1.0, value=0.1)
dias_periodo = st.sidebar.number_input("Período analisado (dias)", min_value=1, value=30)

# Upload
upload = st.file_uploader("Arquivo de Vendas/Estoque (.xlsx ou .csv)", type=["xlsx", "csv"])

def ler_arquivo(arquivo):
    if arquivo is None:
        return None
    if arquivo.name.endswith(".xlsx"):
        return pd.read_excel(arquivo)
    if arquivo.name.endswith(".csv"):
        return pd.read_csv(arquivo, sep=None, engine='python')
    return None

if upload:
    df = ler_arquivo(upload)
    # Colunas obrigatórias
    obrigatorias = ["Empresa", "Produto", "TotalVendido", "EstoqueAtual"]
    if not validar_colunas(df, obrigatorias):
        st.stop()

    resultado = calcula_recomendacao(df, dias_periodo, leadtime_padrao, perc_seguranca)

    # Filtros
    with st.expander("Filtros"):
        opcao_repor = st.checkbox("Mostrar apenas produtos para repor", value=True)
        pesquisa_produto = st.text_input("Buscar produto")
        empresas = resultado["Empresa"].unique()
        emp_escolhidas = st.multiselect("Filtrar Empresas", empresas, default=list(empresas))

    df_view = resultado.copy()
    if opcao_repor:
        df_view = df_view[df_view["Repor"] == "SIM"]
    if pesquisa_produto:
        df_view = df_view[df_view["Produto"].str.contains(pesquisa_produto, case=False, na=False)]
    if emp_escolhidas:
        df_view = df_view[df_view["Empresa"].isin(emp_escolhidas)]

    st.subheader("Tabela de Recomendação")
    st.dataframe(df_view, use_container_width=True)

    # Gráfico
    import plotly.express as px
    if not df_view.empty:
        fig = px.bar(
            df_view.sort_values("QtdRepor", ascending=False),
            x="Produto", y="QtdRepor", color="Empresa",
            title="Produtos que precisam de reposição",
            text="QtdRepor"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhum produto precisa de reposição neste cenário/filtros.")

    # Download
    excel = to_excel(df_view)
    st.download_button("Baixar tabela filtrada (Excel)", data=excel, file_name="recomendacao_estoque.xlsx")
else:
    st.info("Envie o arquivo para visualizar a recomendação.")

