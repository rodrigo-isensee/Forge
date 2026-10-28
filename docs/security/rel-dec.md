---
tipo: revisao-seguranca
contrato: 1
pedido: rel-dec
branch: melhoria/rel-dec
commit: fcc5980ee53f58cb021b7c96e19ca81d712d07e8
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-28
---
# Review de segurança: rel-dec

Base `ed7fbd80ba9b57562442a20c9cfa479a1a5c94c7`, head `fcc5980`; revisado pelo diff (7 arquivos).

## Gatilhos
`controles do Forge`: regra `R-FLUXO` (integração e promoção), `agents/tech-lead.md`, `scripts/promover-homolog.py`, invariantes em `tests/config.json`. Não toca segredo, dependência nem workflow.

## Achados

## Detalhe dos achados
Sem bloqueante. Verificações que sustentam o parecer:
- Merge automático só na homolog, nunca na main: `docs/regras/R-FLUXO.md:13` limita o merge automático à `homolog` e deixa a `main` com o usuário; o rótulo `afrouxa-regra` continua do dono (`docs/promocao-integrador.md`, passo 7). O script não mescla e não aplica rótulo (`scripts/promover-homolog.py:263`, só imprime).
- O merge automático não afrouxa o portão: o ruleset ativo `merge-commit-homolog-main` (lido por `gh api repos/.../rules/branches/homolog`, só leitura) exige os checks `bateria` e `catraca` e só o método merge. Catraca vermelha sem o rótulo continua barrando; o merge sai sozinho quando o dono aplica o rótulo e o check fica verde. `allow_auto_merge` está `true`, como a decisão do dono pede (E3.1).
- REL-R4: o `forge-check pr` confere de fato o merge simulado (`bin/forge-check:395-406`, `git merge-tree --write-tree`; `commit_vale`), então a frase da regra descreve um controle que existe. Conflito que muda o patch segue invalidando os pareceres dos arquivos tocados.
- As invariantes de `tests/config.json` foram trocadas, não removidas: o texto novo continua protegido (`só na hora do merge`, `confere o merge simulado`).
- Sem segredo, sem credencial nova, sem execução de entrada externa no diff.

Recomendações (não devolvem):
- Prender o head no merge automático de `docs/regras/R-FLUXO.md:13` e `agents/tech-lead.md:32`: o comando que os dois ensinam (liga o merge automático por nome de branch, `--auto --merge`) não traz `--match-head-commit`, que só o script imprime (`scripts/promover-homolog.py:213`). Com o merge armado, um merge novo na `develop` muda o conteúdo que vai à homolog; a bateria e a catraca obrigatórias ainda rodam sobre o novo head, por isso é recomendação. Severidade baixa, esforço P, dono `tech-lead`.
- `agents/tech-lead.md:32` diz "você não espera os checks", e o script sai com 3 enquanto os checks estão pendentes (`docs/promocao-integrador.md`, passo 5). Dizer qual caminho vale (com o script, o tech-lead liga o merge depois dos checks verdes; sem ele, liga logo e confia no ruleset). Severidade informativa, esforço P, dono `tech-lead`.
- REL-R4 troca a leitura do review sobre o código integrado pelo diff da entrega: interação semântica entre a entrega e a `develop` sem conflito textual só é pega pela bateria do PR (merge ref), não pelo parecer. É o custo aceito na decisão do dono de 2026-10-28; fica registrado. Severidade informativa.
- O ruleset não restringe quem arma o merge automático na `main`; `R-MAIN` segue por regra e hook, como antes (mesmo poder que o merge manual já dava). Sem mudança proposta.

PA-7 (`docs/engineering/achados-recorrentes.md`): conferida; nenhuma classe recorrente nova a registrar.

## Riscos aceitos e ferramentas
Nenhum risco aceito pelo usuário. Ferramentas: leitura do diff, `gh api` somente leitura (rulesets), leitura do código do `forge-check`; `gitleaks`, `zizmor`, `actionlint` e `semgrep` não estão no PATH (lacuna registrada; o diff não toca workflow, segredo nem dependência).
