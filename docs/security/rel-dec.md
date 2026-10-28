---
tipo: revisao-seguranca
contrato: 1
pedido: rel-dec
branch: melhoria/rel-dec
commit: 767f38738032796b9de22b05a81d91b1258e4bec
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-28
---
# Review de segurança: rel-dec

Base `ed7fbd80ba9b57562442a20c9cfa479a1a5c94c7`, head `767f387`; primeira rodada pelo diff (7 arquivos) em `fcc5980`; volta 2 por delta (`forge-check delta`: `agents/tech-lead.md:32`, `docs/promocao-integrador.md`, `docs/regras/R-FLUXO.md:13`, `scripts/promover-homolog.py`, `tests/config.json:415`, teste do script), com leitura integral dos trechos que tocam controle.

## Gatilhos
`controles do Forge`: regra `R-FLUXO` (integração e promoção), `agents/tech-lead.md`, `scripts/promover-homolog.py`, invariantes em `tests/config.json`. Não toca segredo, dependência nem workflow.

## Achados
- A1 (recomendado) docs/regras/R-FLUXO.md:13 · o ruleset `merge-commit-homolog-main` ainda exige só `bateria` e `catraca` (lido hoje, `gh api .../rules/branches/homolog`, só leitura); o texto diz "todos os checks" e o merge armado antes dos checks só espera os obrigatórios; falta a ação do dono (decisão de 10:15, A2 do review) de pôr `bateria (python 3.14)` nos obrigatórios, senão o merge automático mescla com o 3.14 vermelho; dono: dono do repositório (configuração), não é defeito do código; confirmar a ação antes de armar o primeiro merge automático

## Detalhe dos achados
Sem bloqueante. Volta 2, sobre o delta:
- Merge armado antes dos checks: o script só imprime o comando (`scripts/promover-homolog.py:242-245` e `261-264`), não mescla. A ordem mantém a catraca vermelha sem rótulo em saída 3 antes de qualquer impressão, e check vermelho (fora a catraca) em `parar` (linhas 246-248); o comando só sai com verde, pendente ou sem check ainda. O que impede mesclar sem verde é o `--match-head-commit <sha>` (prende o head conferido; push novo na `develop` faz o merge falhar) e os checks obrigatórios do ruleset (`bateria`, `catraca`; mais o 3.14 quando o dono agir, A1).
- Recomendações da volta 1: o comando único com `--match-head-commit` está em `R-FLUXO.md:13`, `agents/tech-lead.md:32` e `docs/promocao-integrador.md:18`; a invariante nova (`tests/config.json:415`, a frase da `R-FLUXO.md:13` sobre a `main`) casa com `R-FLUXO.md:13` e guarda o limite do merge automático à `homolog`; a divergência texto x script sobre checks pendentes foi resolvida (sai 0 e imprime o comando).
- A `main` continua barrada pelo hook (`hooks/conformidade.py:1565`, `R-MAIN`) e o rótulo `afrouxa-regra` continua do dono (`hooks/conformidade.py:1422`). `allow_auto_merge` = true (E3.1). `python3 -m unittest tests.test_promover_homolog`: 25 OK.

Verificações da primeira rodada, mantidas:
- Merge automático só na homolog, nunca na main: `docs/regras/R-FLUXO.md:13` limita o merge automático à `homolog` e deixa a `main` com o usuário; o script não mescla e não aplica rótulo.
- O merge automático não afrouxa o portão: catraca vermelha sem o rótulo continua barrando; o merge sai sozinho quando o dono aplica o rótulo e o check fica verde.
- REL-R4: o `forge-check pr` confere de fato o merge simulado (`bin/forge-check:395-406`, `git merge-tree --write-tree`; `commit_vale`), então a frase da regra descreve um controle que existe.
- As invariantes de `tests/config.json` foram trocadas, não removidas.
- Sem segredo, sem credencial nova, sem execução de entrada externa no diff.

Registrado (informativo): REL-R4 troca a leitura do review sobre o código integrado pelo diff da entrega; interação semântica sem conflito textual só é pega pela bateria do PR (merge ref). É o custo aceito na decisão do dono de 2026-10-28. O ruleset não restringe quem arma o merge automático na `main`; `R-MAIN` segue por regra e hook, como antes.

PA-7 (`docs/engineering/achados-recorrentes.md`): conferida; nenhuma classe recorrente nova a registrar.

## Riscos aceitos e ferramentas
Nenhum risco aceito pelo usuário. Ferramentas: leitura do diff, `gh api` somente leitura (rulesets), leitura do código do `forge-check` e do hook; `gitleaks`, `zizmor`, `actionlint` e `semgrep` não estão no PATH (lacuna registrada; o diff não toca workflow, segredo nem dependência).
