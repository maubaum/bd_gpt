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

## Funcionalidades
- `obter_esquema()`: Coleta estrutura do banco.
- `gerar_query_sql()`: Gera SQL via IA.
- `executar_query_supabase()`: Executa SQL.
- `gerar_resposta_natural()`: Traduz resultado para linguagem comum.
- `main()`: Interface de perguntas/respostas com o usuário.

## Observações
- Campo `amount` está em centavos (30026 = R$300,26)
- Ignorar `type` e `account_group` nas queries.