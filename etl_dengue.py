import os
import io
import polars as pl
from google.cloud import storage
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env (incluindo as credenciais do GCP)
load_dotenv()

# --- CONFIGURAÇÕES ---
# Google Cloud Storage
BUCKET_NAME = 'dados-brutos-dengue-avv'

# Banco de Dados PostgreSQL
DB_USER = 'postgres'
DB_PASSWORD = '1234'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'dengue_db'

def download_blob_to_memory(bucket_name, source_blob_name):
    """Faz o download de um arquivo do GCS para um buffer em memória."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)
        
        print(f"Baixando arquivo '{source_blob_name}' do bucket '{bucket_name}'...")
        file_as_bytes = blob.download_as_bytes()
        return io.BytesIO(file_as_bytes)
    except Exception as e:
        print(f"Erro ao baixar o arquivo {source_blob_name}: {e}")
        return None

def process_dengue_data(file_buffer):

    print("Processando dados com Polars...")
    
    colunas_selecionadas = ["ID_AGRAVO", "DT_NOTIFIC", "CLASSI_FIN", "ID_MN_RESI"]

    try:
        # 1. Lê o CSV selecionando APENAS as colunas de interesse para evitar erros de parse
        df = pl.read_csv(file_buffer, separator=',', columns=colunas_selecionadas, encoding='latin-1', try_parse_dates=True)

        # 2. Filtra para garantir que o agravo é Dengue (CID-10 A90).
        df_dengue = df.filter(pl.col("ID_AGRAVO") == 'A90')
        
        codigos_confirmados = [1, 10, 11, 12]
        df_confirmados = df_dengue.filter(pl.col("CLASSI_FIN").is_in(codigos_confirmados))

        # 4. Agrega os dados por mês e município de RESIDÊNCIA
        df_agregado = df_confirmados.group_by(
            pl.col("DT_NOTIFIC").dt.truncate("1mo").alias("ano_mes"),
            pl.col("ID_MN_RESI").alias("municipio_id")
        ).agg(
            pl.len().alias("casos_confirmados")
        ).filter(
            pl.col("municipio_id").is_not_null()
        )
        
        print(f"Processamento concluído. {len(df_agregado)} registros agregados encontrados.")
        return df_agregado
    except Exception as e:
        print(f"Erro ao processar os dados com Polars: {e}")
        return None

def main():
    """Função principal do pipeline de ETL."""
    print("Iniciando pipeline de ETL de dados da Dengue...")
    
    storage_client = storage.Client()
    blobs = storage_client.list_blobs(BUCKET_NAME)
    
    lista_dfs_agregados = []
    
    for blob in blobs:
        if blob.name.endswith('.csv'):
            file_buffer = download_blob_to_memory(BUCKET_NAME, blob.name)
            if file_buffer:
                df_agregado = process_dengue_data(file_buffer)
                if df_agregado is not None and len(df_agregado) > 0:
                    lista_dfs_agregados.append(df_agregado)

    if not lista_dfs_agregados:
        print("Nenhum dado foi processado. Encerrando o pipeline.")
        return

    # Concatena todos os dataframes anuais em um só
    df_final = pl.concat(lista_dfs_agregados)
    
    # É possível que o mesmo município no mesmo mês apareça em arquivos de anos diferentes
    df_final = df_final.group_by("ano_mes", "municipio_id").agg(
        pl.sum("casos_confirmados").alias("casos_confirmados")
    )

    # Converte para Pandas para carregar no banco
    df_final_pandas = df_final.to_pandas()
    
    print(f"Total de {len(df_final_pandas)} registros agregados para carregar no banco.")
    print("Carregando dados agregados para o PostgreSQL...")
    try:
        engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
        
        # Limpa a tabela antes de inserir para evitar duplicatas em re-execuções
        with engine.connect() as connection:
            connection.execute(text('TRUNCATE TABLE fato_casos_dengue;'))
            connection.commit()
            
        df_final_pandas.to_sql('fato_casos_dengue', engine, if_exists='append', index=False)
        print("Carga de dados no PostgreSQL concluída com sucesso!")
    except Exception as e:
        print(f"Erro ao carregar dados para o PostgreSQL: {e}")

if __name__ == '__main__':
    main()