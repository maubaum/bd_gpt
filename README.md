# AI SQL Assistant com OpenAI e Supabase

Este projeto permite que usuários façam perguntas em linguagem natural sobre dados em um banco PostgreSQL (via Supabase) e recebam respostas em linguagem simples. Ele usa a OpenAI para gerar SQL automaticamente, executa a consulta e traduz o resultado para o usuário.

## Requisitos
- Python
- API Key da OpenAI
- Conta no Supabase
- `.env` com: `OPENAI_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_DB_PASSWORD`

## Instalação
```bash
pip install openai python-dotenv psycopg2-binary supabase
```

## Uso
```bash
python seu_arquivo.py
```

## Principais funções
- `obter_esquema()`: Coleta estrutura do banco.
- `gerar_query_sql()`: Com base na pergunta do usuário, e o esquema da base SQL , um agente cria uma query SQL para responder a pergunta.
- `executar_query_supabase()`: Executa a query SQL gerada pelo primeiro agente
- `gerar_resposta_natural()`: Com base na pergunta do usuário, na query criada e na resposta, usa um agente ára responder ao usuário em uma linguagem comum.
- `main()`: Função principal que chama as funções acima

## Observações do banco de dados
- Campo `amount` está em centavos (30026 = R$300,26)
