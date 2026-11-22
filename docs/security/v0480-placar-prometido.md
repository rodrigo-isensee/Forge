---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-placar-prometido
commit: afc7083d568d98634c39a498fef1954cc4f3dc1f
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-22
---
# Review de segurança: v0478 (E110.3, placar prometido)

Escopo: diff `900bfdfe..afc7083d` (6 arquivos): `bin/forge-placar` (regex `PROMETIDO`, `ganho_real`, `prometidos`, saída de `cmd_propostas`), `tests/test_placar_prometido.py`, dois specs de mutantes, `tests/pesos-d4.json`, fragmento de changelog.

## Gatilhos
Gatilhos: nenhum (sem hook, `docs/regras/`, `tests/catraca.py`, `tests/config.json`, `.github/`, dependência, segredo ou dado pessoal; leitura local de `docs/kanban/` e `docs/pedidos/`, sem rede).

## Achados
- A1 (recomendado) bin/forge-placar:596 · `prometido:` com centenas de dígitos vira float inf e o `--json` emite `Infinity`, fora do JSON estrito (RFC 8259); limitar os dígitos na regex ou rejeitar valor não finito como `falta:`.

## Sondas

## Detalhe dos achados
**A1.** Evidência: `bin/forge-placar:111` aceita `\d+` sem teto; `:596` faz `float(...)`; `:622` serializa com `json.dumps` sem `allow_nan=False`. Reproduzido numa raiz temporária com `taxa_forma prometido: <400 noves>%`: rc 0, `"prometido": Infinity` no `--json` e `prometido +inf%` no texto. Caminho de ataque: nenhum realista; quem escreve `docs/kanban/melhorias.md` é o próprio Jarvis e hoje nenhum consumidor lê a chave `prometidos` (busca em `.githooks/`, `.github/`, `bin/`, `scripts/`, `hooks/` sem chamada a `forge-placar propostas`). Severidade: informativa (robustez do contrato `--json`). Correção mínima: `\d{1,6}` na regex ou `math.isfinite` com `falta:`. Esforço P. Dono: autor da E110.1.

Pontos conferidos sem achado:
- Regex `PROMETIDO` (`:111`): sem retrocesso catastrófico; 1 MB de entrada hostil (espaços repetidos, 50 mil dígitos) em cerca de 0,1 s.
- `prometidos` (`:592`) só chama `carregar` quando alguma proposta anuncia ganho; `carregar` não acessa a rede; o único subprocesso é `git log` em lista de argumentos e só com `--git` (`:205`), opção de quem opera.
- Fonte ilegível (bytes inválidos em `conferencias.md`) sai `SystemExit` com rc 2 e mensagem, sem traceback; `propostas` não é portão de envio nem de CI, então não há bloqueio contornável nem negação de serviço em controle.
- `ganho_real` (`:577`): base zero, janela aberta, métrica fora do placar e data inválida viram `None` (`real sem medida`), sem divisão por zero; teste do pedido cobre cada caso.
- Teste novo roda com `-I`, `HOME` e raiz temporários e `PATH` herdado, sem rede: `python3 -m unittest tests.test_placar_prometido` com 12 testes OK neste head.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Suíte inteira: fica para o CI do PR (não rodada aqui, conforme o brief); rodado só o teste novo. Ferramentas: leitura estática do diff e sondas locais; sem varredura de segredos ou de dependências por não haver gatilho nem dependência nova.
