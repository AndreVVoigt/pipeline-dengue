import pandas as pd
from sqlalchemy import create_engine

# --- CONFIGURAÇÕES ---
# Banco de Dados PostgreSQL
DB_USER = 'postgres'
DB_PASSWORD = '1234'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'dengue_db'

# --- DICIONÁRIO DE TRADUÇÃO (MAPEAMENTO CÓDIGO UF -> SIGLA) ---
# Fonte: IBGE
mapa_uf_codigo_para_sigla = {
    11: 'RO', 12: 'AC', 13: 'AM', 14: 'RR', 15: 'PA', 16: 'AP', 17: 'TO',
    21: 'MA', 22: 'PI', 23: 'CE', 24: 'RN', 25: 'PB', 26: 'PE', 27: 'AL', 28: 'SE', 29: 'BA',
    31: 'MG', 32: 'ES', 33: 'RJ', 35: 'SP',
    41: 'PR', 42: 'SC', 43: 'RS',
    50: 'MS', 51: 'MT', 52: 'GO', 53: 'DF'
}

def preparar_dados_para_dashboard():
    """
    Busca os dados agregados de dengue do PostgreSQL, enriquece com nomes de
    municípios e SIGLAS de estados, e salva em um arquivo CSV.
    """
    print("Iniciando a preparação dos dados para o dashboard...")
    
    try:
        # --- CORREÇÃO AQUI ---
        # Adicionamos o parâmetro `client_encoding='latin1'` para garantir que o Python
        # leia os dados do PostgreSQL com a codificação correta.
        engine = create_engine(
            f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}',
            connect_args={'client_encoding': 'latin1'}
        )
        
        print("Carregando dados da tabela fato_casos_dengue...")
        df_dengue = pd.read_sql("SELECT * FROM fato_casos_dengue;", engine)
        print(f"{len(df_dengue)} registros de casos carregados.")

        print("Carregando dados de municípios brasileiros...")
        df_municipios = pd.read_csv('lookup_data/municipios.csv')
        
        # Cria a coluna 'uf' com a SIGLA, usando o dicionário de tradução (mapa)
        df_municipios['uf'] = df_municipios['codigo_uf'].map(mapa_uf_codigo_para_sigla)
        
        # Ajusta o código do IBGE para 6 dígitos para compatibilidade
        df_municipios['codigo_ibge_6d'] = (df_municipios['codigo_ibge'] // 10).astype(int)
        
        # Seleciona as colunas que vamos usar para o join
        df_lookup = df_municipios[['codigo_ibge_6d', 'nome', 'uf']]

        print("Enriquecendo os dados de dengue com nomes de municípios e UFs...")
        df_final = pd.merge(
            df_dengue,
            df_lookup,
            left_on='municipio_id',
            right_on='codigo_ibge_6d',
            how='inner'
        )

        output_path = 'dados_dashboard_dengue.csv'
        df_final.to_csv(output_path, index=False)
        
        print("\nSucesso! Os dados para o dashboard foram salvos em:")
        print(output_path)
        print(f"Total de {len(df_final)} registros prontos para visualização.")

    except Exception as e:
        print(f"\nOcorreu um erro: {e}")

if __name__ == '__main__':
    preparar_dados_para_dashboard()