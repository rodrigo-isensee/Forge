---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-custo-por-agente
commit: b2a1470ae35196c6df3be1fb8c8c00046c42a6c7
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047 (E2.352, melhoria/v047-custo-por-agente)

Code review completo (`R-REVIEW`) do CUSTO-MEDIA-POR-AGENTE (E2.312, escopo E2.350) no head `b2a1470a`, feito por uma instância que não fez a entrega. Não havia parecer anterior, então não houve delta.

## Achados
- A1 (recomendado) docs/transcricoes.md:28 · A seção "Medir o custo em tokens" lista as opções do `custo`, mas não traz `--media-por-agente`. A linha de uso em bin/forge-check:10 também não. Hoje só a ajuda do argparse e o changelog falam da opção. Vale uma frase em cada lugar.
- A2 (recomendado) bin/forge_transcricao.py:421 · O aviso "vai ler docs/kanban/entregas.md" no stderr sai depois da leitura (linha 419). Nos avisos de `avisos` e das medidas (linhas 233 e 356) ele sai antes. Sugestão: imprimir antes de `ler_entregas`.

## Sondas

## Parecer
**Aprovado** no head `b2a1470a`.

O item faz o que o E2.312 pede. `forge-check transcricao custo --media-por-agente` lê só `docs/kanban/entregas.md` (da `--raiz-pedidos`, se dada) e imprime uma linha por agente (entregas, mínimo, média inteira, máximo) e o total. Não há rede nem transcrição. Rodei no registro real (`--raiz-pedidos ~/.forge-contrib`): rc=0, 9 agentes, 17 linhas, 0 ignoradas. O despacho segue o escopo do E2.350: três linhas em `bin/forge-check` (o argumento e o desvio em `executar`, antes do `custo` antigo) e a lógica em `bin/forge_transcricao.py`. Sem a opção, o `custo` das transcrições não muda; o M1 prova isso.

Checklist de leitura:
- As funções são curtas e têm um propósito cada: `ler_entregas`, `tokens_por_agente` e `cmd_media_por_agente`.
- O cabeçalho é achado pelos nomes das colunas, em qualquer caixa e ordem. Assim cobre a tabela do registro da fábrica e a do modelo de projeto (`templates/projeto/docs/kanban/entregas.md`).
- Linha fora de tabela fecha a tabela. Linha curta e token não inteiro contam como ignorados.
- Caractere de controle no nome do agente é trocado por espaço. O teto de 2 MB e a recusa de link simbólico batem com o texto da mensagem.
- A combinação com alvo, `--entregas`, `--pedido`, `--desde` ou `--ate` dá rc 2.
- Não há dependência nova.
- Os testes rodam em subprocesso com `-I` e ambiente limpo (AR-4 e AR-5 conferidos).
- O fragmento do changelog está presente. Os commits seguem Conventional Commits em português.

Conferi os itens do PA-7 (`docs/engineering/achados-recorrentes.md`) que alcançam o diff. Nenhum se repete: as specs estão no lugar (AR-12) e o limite citado no texto bate com `TETO_ENTREGAS` (AR-9).

Duas bordas, registradas sem achado:
- Uma linha de tabela toda vazia é pulada como separador e não conta em `ignoradas`.
- Token com separador de milhar (`1.234`) conta como ignorado, o que bate com o docstring.

Guardas e mutantes (rodados por mim, 1 processo):
- `bin/forge-mutante --cobertura --base 1b88640e`: as 12 linhas de guarda do diff aparecem como `coberta`, nenhuma `sem mutante`.
- `bin/forge-mutante --processos 1 --base 1b88640e` nas três specs: M1 a M19 morreram.

Testes do item: `python3 -m unittest tests.test_medidas_m14b` deu 73 testes OK. Suíte: o brief diz "sem PR", então não há CI para citar; a suíte inteira fica no CI do PR.

Tamanho (M14): contra a base, `bin/forge-check` tem 3 linhas, `bin/forge_transcricao.py` 66 e `tests/test_medidas_m14b.py` 86, num total de 155. Passa da orientação de 150. Quando o PR abrir, o corpo dele traz `teto: excedido, 155 linhas, <motivo>`. Não é trava: o diff tem um só comportamento e é de leitura local.

Segurança (`R-SEGURANCA`) e QA têm pareceres próprios (E2.353 e E2.354). Não os refiz.
