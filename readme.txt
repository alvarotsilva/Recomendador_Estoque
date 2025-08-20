📈 Recomendação Inteligente de Estoque
Este projeto permite calcular, visualizar e exportar recomendações de estoque mínimo e necessidade de reposição de produtos, usando uma planilha única enviada pelo usuário.

Funciona via Streamlit, podendo ser executado localmente ou publicado facilmente na nuvem (Streamlit Community Cloud).

🚀 Funcionalidades
Upload de UM ARQUIVO único de dados (.csv ou .xlsx)
Tratamento automático do campo LeadTime (opcional, assume padrão definido na interface se ausente/nulo)
Validação e feedback inteligente sobre dados incompletos
Filtros dinâmicos por produto, empresa e status de reposição
Visualização gráfico dos itens a repor (curva de reposição)
Exportação do resultado filtrado em Excel
Modelo de arquivo pronto para download e preenchimento
🗂️ Estrutura do Projeto
/

├── estoque_app.py

├── requirements.txt

└── modelouploadestoque.csv

🖥️ Como rodar LOCALMENTE
Instale o Python 3.8+

Instale as dependências:


    pip install -r requirements.txt

Inicie o app:


    streamlit run estoque_app.py
Abra http://localhost:8501 no navegador

Baixe o arquivo modelo (modelo_upload_estoque.csv), preencha seus dados e faça o upload na interface