import streamlit as st
import os

# Define o diretório onde o PDF será salvo
diretorio_pdf = 'uploads'

# Verifica se o diretório existe, se não, cria um
if not os.path.exists(diretorio_pdf):
    os.makedirs(diretorio_pdf)

# Cria o widget de upload de arquivo
arquivo_pdf = st.file_uploader("Upload de arquivo PDF", type=["pdf"])

# Se um arquivo foi carregado
if arquivo_pdf is not None:
    # Salva o arquivo no diretório especificado
    caminho_arquivo = os.path.join(diretorio_pdf, arquivo_pdf.name)
    
    with open(caminho_arquivo, "wb") as pdf_file:
        pdf_file.write(arquivo_pdf.getbuffer())
    
    st.success(f"Arquivo '{arquivo_pdf.name}' salvo com sucesso em '{caminho_arquivo}'.")
