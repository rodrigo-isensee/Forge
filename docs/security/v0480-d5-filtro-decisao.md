---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-d5-filtro-decisao
commit: 8916a422b5b7b811f858847881a686e7f3108f19
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0478 (D5, filtro de decisão, PR #863, E173.21, revalidação por delta)

Gatilhos: controle de conformidade que analisa entrada (o decisor decide no lugar do dono, R-DECISAO), registro em `docs/kanban/decisoes-obvias.jsonl`.

Rodada anterior: reprovado no `6c4a7dcc` (A1 a A3, sondas S1 a S9; texto no git, commit `d62c1db7`).

## Delta lido
`forge-check parecer delta` de `6c4a7dcc..8916a422`: no domínio, só `bin/forge_decisor.py` (`_git`, `parecer_no_git`, `frontmatter`, `confirmacao_escrita` com `pedido` e `porta`, chamada em `executar`), lido inteiro. Fora do domínio, lidos para conferir as sondas: `tests/test_decisor.py`, `tests/test_forge_dono.py`, os dois JSON de mutantes, o fragmento do changelog. Nada no delta toca hook, workflow, `.githooks/` nem segredo.

## Achados anteriores
- A1 (bloqueante) corrigido: `bin/forge_decisor.py:65-80` lê o parecer pelo git no HEAD, exige a raiz igual ao `--show-toplevel`, modo `100644`, teto de 1 MiB e nenhuma diferença no índice nem na árvore; `:107` exige `tipo`, `parecer: aprovado`, `revisor` e `pedido` iguais ao `--pedido`, com frontmatter que falha fechado em linha torta ou chave repetida (`:82-97`).
- A2 (bloqueante) corrigido: `bin/forge_decisor.py:34` e `:109`, linha de forma fixa (fullmatch, sem recuo) com a porta normalizada igual à do `--porta`; os pareceres já na develop não confirmam (S9, S10).
- A3 (bloqueante) corrigido: a busca solta saiu; pergunta, título e negação não confirmam (S3 a S7).

Sondas: rodadas de novo no head, `bin/forge-check --raiz <tmp> decisoes registrar` numa raiz temporária em git com um parecer só, os fatos de porta aberta e `--so-aperta sim`; salvo S1, o arquivo está commitado no HEAD.

## Sondas
- S1 · f.md fora do git, sem frontmatter, "qualquer coisa" e "só aperta" · espera: rc 1, pergunta · obtido: rc 1, condição não atendida: seguranca
- S2 · frontmatter com parecer: reprovado e a linha da porta · espera: rc 1, pergunta · obtido: rc 1, condição não atendida: seguranca
- S3 · "## Só aperta?" e na linha seguinte "Não. Aceita mais." · espera: rc 1, pergunta · obtido: rc 1, condição não atendida: seguranca
- S4 · "A mudança não é só aperta: afrouxa." · espera: rc 1, pergunta · obtido: rc 1, condição não atendida: seguranca
- S5 · "não" e "só aperta" em linhas seguidas · espera: rc 1, pergunta · obtido: rc 1, condição não atendida: seguranca
- S6 · "não  só aperta" (dois espaços) · espera: rc 1, pergunta · obtido: rc 1, condição não atendida: seguranca
- S7 · "não só aperta" (controle) · espera: rc 1, pergunta · obtido: rc 1, condição não atendida: seguranca
- S8 · frontmatter tipo: review, pedido: outro e a linha da porta · espera: rc 1, pergunta · obtido: rc 1, condição não atendida: seguranca
- S9 · cópia literal de docs/security/release-0.47.15.md como --seguranca do pedido p1 · espera: rc 1, pergunta · obtido: rc 1, condição não atendida: seguranca
- S10 · a mesma cópia com --pedido igual ao pedido dela · espera: rc 1, pergunta · obtido: rc 1, condição não atendida: seguranca

## Detalhe
Dimensões novas, todas rc 1 (pergunta): porta diferente, linha com recuo, linha boa só na árvore depois do commit, linha boa só no índice, `parecer:` duplicado no frontmatter, `revisor: forge:tech-lead`, frontmatter e linha válidos mas fora do git, porta com dois espaços depois dos dois-pontos (falha fechada). Controle legítimo (parecer válido commitado) e o mesmo em CRLF: rc 0, decidida. Script na pasta temporária da sessão, biblioteca padrão, `python3 -I`.

**Só aperta ou neutro, por escrito:** o delta só aperta. Em relação ao `6c4a7dcc`, a confirmação passa de "frase em arquivo da árvore" para "parecer aprovado da segurança, do mesmo pedido, commitado e limpo, com a linha da porta"; tudo o que o `6c4a7dcc` recusava continua recusado (a forma do caminho em `CONFIRMACAO` não mudou), e o que ele aceitava por frase solta agora vira pergunta. O `_git` tira as `GIT_*` herdadas e falha fechado se o git não roda.

Resíduo, fora do delta e já registrado na rodada anterior como cartão ao tech-lead (não bloqueia): `--raiz` aceita qualquer repositório, então quem consegue commitar um parecer forjado num repositório temporário decide ali (o controle legítimo acima é exatamente isso), e o `decidido:` do commit não é conferido contra o registro da raiz real (`.githooks/commit-msg:9`). Casar a linha `decidido:` com uma entrada `decidida` do registro do repositório fecha os dois.

Suíte: CI do head `8916a422` (run 45453442466) com as dez partes da suíte verdes em python 3.12 e 3.14, instalação e bateria (passos e verificações longas) verdes; `bateria (pareceres)` e `catraca` em falha; a da bateria é o R-REVIEW sobre o parecer de review ainda reprovado, que a revalidação do review troca. Local: `tests.test_decisor`, `tests.test_forge_dono`, `tests.test_anotar`, 132 testes, OK.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do delta, sondas locais em raiz temporária, unittest dos arquivos tocados; nenhuma ferramenta externa necessária.
