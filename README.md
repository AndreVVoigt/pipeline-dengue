# Projeto de Portfólio: Pipeline de Dados e Sala de Situação da Dengue no Brasil

## 🎯 Objetivo

Este projeto implementa um pipeline de dados ponta a ponta para processar microdados de notificações de casos de Dengue no Brasil, disponibilizados publicamente pelo DATASUS (SINAN). O objetivo é transformar dados brutos e massivos em um dashboard analítico e interativo ("Sala de Situação") que permita o monitoramento epidemiológico da doença em nível nacional.

O projeto aborda desafios do mundo real, como o manuseio de grandes volumes de dados (milhões de registros), a limpeza de dados governamentais e a implementação de uma arquitetura de dados baseada em nuvem.

## 🏛️ Arquitetura do Pipeline

Para simular um ambiente de dados profissional, foi utilizada a seguinte arquitetura:


1.  **Data Lake (Armazenamento Bruto):** Os arquivos CSV originais do DATASUS são armazenados em um bucket no **Google Cloud Storage**, servindo como nosso repositório central de dados brutos.
2.  **Processamento (ETL):** Um script Python local orquestra todo o processo. Ele se conecta de forma segura ao Google Cloud, baixa os dados em memória e utiliza a biblioteca **Polars** para processamento de alta performance.
3.  **Data Warehouse (Armazenamento Analítico):** Após a limpeza, filtragem e agregação dos dados (casos confirmados por município e mês), o resultado consolidado é carregado em um banco de dados **PostgreSQL**, servindo como nossa fonte de verdade para análises.
4.  **Visualização (BI):** O dashboard final é construído no **Google Looker Studio**, que se conecta aos dados preparados para gerar mapas, gráficos e filtros interativos.

## 🚀 Tecnologias Utilizadas

- **Nuvem:** Google Cloud Platform (GCP)
  - **Data Lake:** Google Cloud Storage
- **Linguagem:** Python
- **Bibliotecas de Processamento:**
  - **Polars:** Para manipulação de grandes volumes de dados com alta performance e baixo consumo de memória.
  - **Pandas:** Para enriquecimento dos dados e integração com outras ferramentas.
- **Banco de Dados:** PostgreSQL
- **Ferramenta de BI:** Google Looker Studio
- **Autenticação:** Google Cloud Service Accounts

## 📊 Dashboard - Sala de Situação

O dashboard interativo permite a análise dos dados sob diversas perspectivas, incluindo:
-   Um mapa geoespacial do Brasil que mostra a concentração de casos por estado.
-   Uma série temporal para identificar picos sazonais da doença.
-   Filtros interativos para explorar os dados por período e região.

**[>> Clique aqui para ver o dashboard interativo <<](https://lookerstudio.google.com/reporting/50adc11a-611b-452e-9957-15443d9927d1)**

## ⚙️ Como Executar o Projeto

Para replicar este ambiente e executar o pipeline, siga os passos abaixo:

### 1. Pré-requisitos
- Ter o [Python 3](https://www.python.org/downloads/) instalado.
- Ter o [PostgreSQL](https://www.postgresql.org/download/) instalado. O **pgAdmin**, que é a interface gráfica, geralmente é incluído na instalação.
- Uma conta no [Google Cloud Platform](https://console.cloud.google.com/).

### 2. Configuração do Ambiente

1.  **Adicione os Dados Brutos:** [https://opendatasus.saude.gov.br/gl/dataset/arboviroses-dengue](https://opendatasus.saude.gov.br/gl/dataset/arboviroses-dengue)

2.  **Clone o Repositório:**
    ```bash
    git clone https://github.com/AndreVVoigt/pipeline-dengue
    ```
3.  **Instale as Dependências:**
    ```bash
    pip install polars google-cloud-storage pandas sqlalchemy psycopg2-binary python-dotenv pyarrow
    ```
4.  **Configure o Google Cloud:**
    -   Crie um projeto no GCP.
    -   Crie um bucket no Cloud Storage e faça o upload dos arquivos CSV brutos da Dengue.
    -   Crie uma Conta de Serviço (`Service Account`) com o papel de "Visualizador de Objetos do Storage".
    -   Gere uma chave JSON para esta conta, renomeie-a para `gcp_credentials.json` e coloque-a na raiz do projeto.
5.  **Variáveis de Ambiente:**
    -   Crie um arquivo `.env` na raiz do projeto.
    -   Adicione a seguinte linha, apontando para sua chave JSON:
        ```
        GOOGLE_APPLICATION_CREDENTIALS="gcp_credentials.json"
        ```
6.  **Configure o Banco de Dados:**
    -   Usando o pgAdmin, crie um banco de dados (ex: `dengue_db`).
    -   Execute o script do arquivo `schema.sql` (se você tiver um) para criar a tabela `fato_casos_dengue`.

### 3. Execução do Pipeline
1.  **Atualize as Configurações:** No script `etl_dengue.py`, atualize as variáveis `BUCKET_NAME` e as credenciais do seu banco de dados.
2.  **Execute o ETL:**
    ```bash
    python etl_dengue.py
    ```
3.  **Prepare os Dados para o Dashboard:**
    -   Atualize as credenciais do banco no script `preparar_dashboard.py`.
    -   Execute o script para gerar o CSV final enriquecido:
        ```bash
        python preparar_dashboard.py
        ```
4.  **Visualize:** Use o arquivo `dados_dashboard_dengue.csv` gerado como fonte de dados para criar seu dashboard no Looker Studio.