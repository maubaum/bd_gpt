from openai import OpenAI
from dotenv import load_dotenv
import os
import psycopg2
from supabase import create_client, Client

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv("password.env")

# Acessando as variáveis de ambiente
openai_api_key = os.getenv("OPENAI_API_KEY")
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

# Configurações da OpenAI
OpenAI.api_key = openai_api_key  # Substitua com sua chave da OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Configuração do Supabase
url = supabase_url #'https://<YOUR-SUPABASE-URL>'  # Substitua com o seu URL do Supabase
chave = supabase_key  # Substitua com a chave pública do Supabase
supabase = create_client(url, chave)


# Função para obter o esquema do banco de dados (tabelas e colunas)
def obter_esquema():
    # Abrir conexão única com o banco
    conn = psycopg2.connect(
        host="aws-0-eu-west-2.pooler.supabase.com",
        port=6543,
        dbname="postgres",
        user="postgres.uhipbmjphboyisuxwmyr",
        password=os.getenv("SUPABASE_DB_PASSWORD")
    )

    cur = conn.cursor()

    # Obter tabelas do schema público
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public';
    """)
    tabelas = cur.fetchall()

    esquema = {}

    for tabela in tabelas:
        tabela_nome = tabela[0]
        
        # Obter colunas da tabela
        cur.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = %s;
        """, (tabela_nome,))
        
        colunas = cur.fetchall()

        esquema[tabela_nome] = [
            {"column_name": col[0], "data_type": col[1]} for col in colunas
        ]

    cur.close()
    conn.close()

    return esquema


# Função para enviar a consulta para o OpenAI
def gerar_query_sql(esquema_texto,prompt_usuario):
    system_prompt = f"""
    Você é um assistente que escreve queries SQL com base em perguntas em linguagem natural.
    Considere o seguinte esquema do banco de dados PostgreSQL:
    {esquema_texto}
    Importante que sua resposta retorne APENAS a consulta SQL, respeitando rigorosamente o esquema do banco de dados.
    """
    #print(system_prompt)
    #print(prompt_usuario)

    resposta = client.chat.completions.create(
        model="gpt-4",  # ou "gpt-3.5-turbo"
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt_usuario}
        ],
        temperature=0.0
    )

    return resposta.choices[0].message.content

def gerar_resposta_natural(esquema_texto, prompt_usuario, query_sql, resultado_sql):
    system_prompt = f"""
    Você é um assistente que transforma resultados de SQL em respostas claras para usuários leigos.
    Responda sempre de forma objetiva e natural, como se estivesse explicando para alguém sem conhecimento técnico.
    """
    user_prompt = f"""
    O usuário perguntou: "{prompt_usuario}"

    O esquema da base de dados é:
    {esquema_texto}                

    A query SQL gerada foi:
    {query_sql}

    O resultado da query foi:
    {resultado_sql}

    O campo 'amount' está em reais e é representado por R$. 
    O valor acumulado de 'amount' representa o Saldo em Conta atual que significa o dinheiro que um usuário possui neste momento.
    O valor acumulado de 'amount' até uma determinada data representa o Saldo em Conta naquela data. 
    O valor acumulado de 'amount' entre duas datas representa o valor recebido ou pago no período. 
    Os valores negativos para 'amount' representam saídas de dinheiro, enquanto os valores positivos para 'amount' representam entradas de dinheiro.
    O número no campo amount está multiplicado por 100. Por exempo, se o valor de uma agregação de 'amount' for 30026 isso significa R$300,26.
    Nunca usar o campo 'type' na query. O o campo 'type' só contem o valor fixo 'p2p'.
    Nunca usar o campo 'account_group' na query.
    Atenção com queries que tenham nome: first_name só contém o primeiro nome. full_name contem o nome completo. 
    
    Como você responderia essa pergunta ao usuário de forma clara e natural?

    """

    resposta = client.chat.completions.create(
        model="gpt-4",  # ou gpt-3.5-turbo
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        temperature=0.5
    )

    return resposta.choices[0].message.content

# Função para executar a query no Supabase
def executar_query_supabase(query_sql):
    try:
        conn = psycopg2.connect(
            host="aws-0-eu-west-2.pooler.supabase.com",
            port=6543,
            dbname="postgres",
            user="postgres.uhipbmjphboyisuxwmyr",
            password=os.getenv("SUPABASE_DB_PASSWORD")
        )
        cur = conn.cursor()
        cur.execute(query_sql)
        resultado = cur.fetchall()
        colunas = [desc[0] for desc in cur.description]
        cur.close()
        conn.close()

        # Retorna como lista de dicionários
        return [dict(zip(colunas, linha)) for linha in resultado]

    except Exception as e:
        return f"Erro ao executar a consulta: {e}"

# Função principal para interagir com o usuário
def main():
    
    # Exibir esquema
    schema_db = obter_esquema()
    
    while True:
        # Receber o pedido do usuário
        pergunta_usuario = input("Qual é a sua pergunta? ")

        # Gerar a query SQL usando o OpenAI
        query_sql = gerar_query_sql(str(schema_db), pergunta_usuario)
        print(f"Query gerada: {query_sql}")

        # Executar a consulta no Supabase
        resultado = executar_query_supabase(query_sql)
        print("Resultado:", resultado)

        # Exibir a resposta para o usuário
        resposta = gerar_resposta_natural(str(schema_db), pergunta_usuario, query_sql, resultado)
        print("Resposta:", resposta)
        print()


# Executar o programa
if __name__ == "__main__":
    main()
    
