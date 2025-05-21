import streamlit as st
from azure.storage.blob import BlobServiceClient
import os
import pymssql
import uuid
import json
from dotenv import load_dotenv
load_dotenv()

BlobConnectionString = os.getenv('BLOB_CONECTION_STRING')
BlobContainerName = os.getenv('BLOB_CONTAINER_NAME')
BlobAccountName = os.getenv('BLOB_ACCOUNT_NAME')

SQL_SERVER = os.getenv('SQL_SERVER')
SQL_DATABASE = os.getenv('SQL_DATABASE')
SQL_USER = os.getenv('SQL_USER')
SQL_PASSWORD = os.getenv('SQL_PASSWORD')

st.title('Cadastro de Produtos')

#formulário cadastro de produtos
product_name = st.text_input('Nome do Produto')
product_descricao = st.text_area('Descrição do Produto')
product_price = st.number_input("Preço do Produto", min_value=0.0, format='%.2f')
product_img = st.file_uploader('Imagem do Produto', type=['jpg', 'png', 'jpeg'])

#save image to blob storage
def upload_blob(file):
    blob_service_client = BlobServiceClient.from_connection_string(BlobConnectionString)
    container_client = blob_service_client.get_container_client(BlobContainerName)
    blob_name = str(uuid.uuid4()) + file.name
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(file.read(), overwrite=True)
    image_url = f"https://{BlobAccountName}.blob.core.windows.net/{BlobContainerName}/{blob_name}"
    return image_url

def insert_product_to_db(product_name, product_description, product_price, product_image_url):
    try:
        imagem_url = upload_blob(product_img)

        connection = pymssql.connect(server=SQL_SERVER,user=SQL_USER,password=SQL_PASSWORD,database=SQL_DATABASE)
        print(connection)
        cursor = connection.cursor()
        sql = "INSERT INTO Produtos (nome, descricao, preco, imagem_url) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (product_name, product_description, product_price, imagem_url))
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return False

def list_products_from_db():
    try:
        connection = pymssql.connect(server=SQL_SERVER,user=SQL_USER,password=SQL_PASSWORD,database=SQL_DATABASE)
        cursor = connection.cursor()
        sql = "SELECT * FROM Produtos"
        cursor.execute(sql)
        products = cursor.fetchall()
        connection.commit()
        cursor.close()
        connection.close()
        return products
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return []

def list_products_screen():
    products = list_products_from_db()
    if products:
        cards_por_linha = 3
        cols = st.columns(cards_por_linha)
        for i, product in enumerate(products):
            col = cols[i % cards_por_linha]
            with col:
                # Acessando os valores da tupla pelo índice
                st.markdown(f"### {product[1]}")  # Índice 1 para 'nome'
                st.write(f"**Descrição:** {product[2]}")  # Índice 2 para 'descricao'
                st.write(f"**Preço:** {product[3]:.2f}")  # Índice 3 para 'preco'
                if product[4]:  # Índice 4 para 'imagem_url'
                    html_img = f'<img src="{product[4]}" width="200" height="200" alt="Imagem do produto">'
                    st.markdown(html_img, unsafe_allow_html=True)
                st.markdown("---")
            if (i + 1) % cards_por_linha == 0 and (i + 1) < len(products):
                cols = st.columns(cards_por_linha)
    else:
        st.info("Nenhum produto encontrado.")

if st.button('Salvar Produto'):
    insert_product_to_db(product_name, product_descricao, product_price, product_img)
    list_products_screen()
    return_menssage = 'Produto salvo com sucesso'

st.header('Produtos Cadastrados')
if st.button('Listar Produtos'):
    list_products_screen()
    return_menssage = 'Produtos listados com sucesso'