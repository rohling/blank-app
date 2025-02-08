import streamlit as st
import os
import random
import string
import pdfplumber
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores  import FAISS
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA


# Define o diretório onde o PDF será salvo
diretorio_pdf = 'uploads'

# Passo 3: Gerar embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Configurar o caminho do diretório para o índice
INDEX_FOLDER = "faiss_index"



# Configurar embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


# Define a função de extração de texto primeiro
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""  # Adiciona "" se extract_text() retornar None
            text = text.replace("Selecionar", "")
            text = text.replace("Seu voo para", "Este voo tem como destination para a cidade")
            if "Total da Passagem" in text:
                break
    return text



# Verifica se o diretório existe, se não, cria um
if not os.path.exists(diretorio_pdf):
    os.makedirs(diretorio_pdf)

# Cria o widget de upload de arquivo
arquivo_pdf = st.file_uploader("Upload de arquivo PDF", type=["pdf"])

# Inicializa a variável text
text = ""

# Se um arquivo foi carregado
if arquivo_pdf is not None:
    # Gera um sufixo randômico
    sufixo_randomico = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
    
    # Cria o novo nome do arquivo com o sufixo randômico
    novo_nome_arquivo = f"{os.path.splitext(arquivo_pdf.name)[0]}_{sufixo_randomico}.pdf"
    caminho_arquivo = os.path.join(diretorio_pdf, novo_nome_arquivo)
    
    # Salva o arquivo no diretório especificado
    with open(caminho_arquivo, "wb") as pdf_file:
        pdf_file.write(arquivo_pdf.getbuffer())
    
    st.success(f"Arquivo '{arquivo_pdf.name}' salvo com sucesso com o nome '{novo_nome_arquivo}' em '{caminho_arquivo}'.")
    
    # Extrai o texto do PDF
    text = extract_text_from_pdf(caminho_arquivo)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
  
    # Passo 4: Armazenar vetores
    if os.path.exists(INDEX_FOLDER):
       
        vector_store = FAISS.load_local(
            folder_path=INDEX_FOLDER,  # Use o caminho do diretório
            embeddings=embeddings,
            allow_dangerous_deserialization=True
        )
        # Carregar o índice existente sem segurança
        # vector_store = FAISS.load_local(INDEX_FILE, embeddings)
        # Adicionar novos vetores ao índice existente
        vector_store.add_texts(chunks)
        st.success("Novos vetores adicionados ao índice FAISS existente.")
    else:
        # Criar o diretório se não existir
        if not os.path.exists(INDEX_FOLDER):
            os.makedirs(INDEX_FOLDER)
        # Criar um novo índice se não existir
        vector_store = FAISS.from_texts(chunks, embeddings)
        st.success("Novo índice FAISS criado.")
        st.write(f"Total de vetores no índice: {vector_store.index.ntotal}")
        #vector_store = FAISS.from_texts(chunks, embeddings)

    arquivo_pdf = None
    # Salvar o índice atualizado
    vector_store.save_local(INDEX_FOLDER)
    st.success(f"Índice FAISS salvo em {INDEX_FOLDER}")

    # Opcional: Mostrar a quantidade de vetores no índice
    st.write(f"Total de vetores no índice: {vector_store.index.ntotal}")

# Mostra o texto extraído
#st.text_area("Texto extraído do PDF:", value=text, height=200)

# Passo 2: Dividir em chunks

# Passo 5: Configurar Groq + RAG

# Cria um input para o usuário digitar o texto
texto_inserido = st.text_input('Digite seu texto aqui:')

# Cria um botão para processar o texto
if st.button('Processar Texto'):

    if not os.path.exists(INDEX_FOLDER):
        st.error("Por favor, faça upload de um PDF primeiro para criar o índice.")
        st.stop()

# # Carrega o índice FAISS diretamente da pasta
    loaded_vector_store = FAISS.load_local(
        folder_path=INDEX_FOLDER,
        embeddings=embeddings,
        allow_dangerous_deserialization=True
    )
    # Configura o modelo e o QA
    llm = ChatGroq(
        temperature=0.6,
        model_name="deepseek-r1-distill-llama-70b",
        groq_api_key='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'
    )

    
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=loaded_vector_store.as_retriever(search_kwargs={"k": 3}),
        return_source_documents=True
    )

    # Executa a função com o valor do input
    texto_processado = qa.invoke(texto_inserido)    
    # Exibe o resultado
    st.subheader('Texto Processado:')
    st.write(texto_processado["result"])

# pergunta = "Quem são os passageiros?"
# resposta = qa.invoke(pergunta)
# # print(resultado)
# print(resposta["result"])