# 09 - Execucao Final e Limitacoes

## 1. Como executar
1. Instalar dependencias:
   - /agent/.venv/bin/python -m pip install -r requirements.txt
2. Rodar aplicacao:
   - /agent/.venv/bin/streamlit run app/main.py
3. Rodar testes:
   - /agent/.venv/bin/pytest -q

## 2. Evidencias de validacao
- Suite automatizada com testes unitarios e de integracao.
- Persistencia de resultados em JSON para auditoria.
- Backtest com comparacao Buy-and-Hold e alpha.

## 3. Limitacoes conhecidas
- Monitoramento continuo depende da sessao Streamlit aberta.
- Qualidade de noticias depende da disponibilidade dos feeds externos.
- Integracao Azure OpenAI e obrigatoria no fluxo principal de decisao/reflexao/chat; sem configuracao valida, o pipeline falha com erro explicito.
- Backtest atual e simplificado (horizonte curto D+1 por sinal).

## 4. Nota importante sobre o backtest (D+1)
- O backtest so gera linha quando existe preco de mercado em data posterior ao sinal (D+1 ou maior) para o mesmo ticker e modo de dados.
- Se os sinais forem mais recentes do que o historico tecnico salvo, o resultado pode vir com 0 linhas avaliadas.
- Esse comportamento nao indica erro automatico do sistema; indica falta de dado de fechamento posterior ao sinal.

Como validar se o backtest esta OK (modo real):
1. Rodar o pipeline em um dia de pregao (gerar sinais).
2. Rodar novamente em pregao posterior (garantir historico apos o sinal).
3. Abrir Backtest minimo com janela cobrindo os dois dias.
4. Confirmar que ha linhas geradas e sinais avaliados maiores que zero.

Leitura do diagnostico na tela:
- "linhas geradas: 0" + "sem preco de entrada ou D+1" alto = faltou historico posterior ao sinal.
- "sem historico por ticker/modo" alto = faltam pontos no technical_history para aquele ticker/modo.
- "duplicados descartados (mesmo ticker+data)" alto = houve varias execucoes no mesmo dia para o mesmo ticker; o backtest manteve apenas o registro mais recente.

## 5. Delimitacao de escopo
- Projeto implementado estritamente no escopo do enunciado do professor.
- Itens extras sugeridos no enunciado (ex.: alertas externos, memoria longa) nao foram incluidos no MVP atual.
