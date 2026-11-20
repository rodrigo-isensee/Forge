---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae1-onde
commit: bef021c1cf681e4ca46590b0bc01eafcc3194025
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-ae1-onde

Etapa E58.7 do pedido v0478 (AE1.1, `forge-check onde`). Escopo lido: `5ccac0bf..bef021c1` (`bin/forge_onde.py`, `bin/forge-check` nos pontos de registro e despacho, `bin/forge-testes`, `tests/test_forge_onde.py`, mutantes, `changelog.d/`, `docs/indice-forge.md`, `tests/pesos-d4.json`).

## Gatilhos
Gatilhos: controle do Forge (ferramenta que produz prova de estado), entrada livre repassada a processo externo (git e gh).

## Resumo
Subcomando só de leitura, sem `fetch`, sem escrita e sem segredo. As fronteiras estão cobertas:
- Injeção de argumento: `tipo_do_alvo` (`bin/forge_onde.py:24`) só deixa passar formatos fechados; nada que comece com `-`, tenha `..`, `@{`, `~`, `^`, `:`, espaço ou quebra de linha chega ao git (`fullmatch` não aceita `\n` final; conferido por sonda local). `sha_de` usa `--verify --quiet --end-of-options`; o cartão vai ao `git log` com `--fixed-strings`; o número do PR é só dígitos. Teste: `tests/test_forge_onde.py:95` e o ponta a ponta em `:320`.
- Forja de linha na saída: toda linha passa por `sem_controle` (`bin/forge_onde.py:137`); o texto do gh é cortado em 200 caracteres antes. Teste: `tests/test_forge_onde.py:217`.
- Falha fechada: gh ausente, lento (teto do `gh_json`) ou com resposta ilegível sai `nao-verificavel` e rc 2, nunca `sim`. Testes: `tests/test_forge_onde.py:182`, `:190`, `:250`.
- Custo (`R-CUSTO`): só git local e `gh` de leitura.

Suíte: a inteira não foi rodada aqui (brief: sem suíte local; não há PR nem CI na branch, o CI do PR é o portão). Rodei o teste novo: `python3 -m unittest tests.test_forge_onde`, 30 testes, OK.

## Achados
- A1 (recomendado) bin/forge_onde.py:132 · sha curto resolve para tag ou branch local de mesmo nome antes do objeto (git prefere a ref; `--quiet` cala o aviso): `onde abc1234` responde sobre outro commit. Conferir que o sha lido começa pelo alvo; se não, nao-verificavel e rc 2.
- A2 (recomendado) bin/forge-check:10391 · git que estoura o GIT_TIMEOUT_S no `onde` sai rc 1, que o contrato do `onde` reserva a "alvo não existe" (docstring de bin/forge_onde.py:8); a leitura que falhou deve sair rc 2. Capturar TimeoutExpired no `executar` do onde e devolver 2.

## Sondas

## Detalhe dos achados
**A1.** Evidência: `bin/forge_onde.py:132` passa o alvo hexadecimal cru a `sha_de` (`:35`). Sonda local em repositório descartável em `$TMPDIR`: commit A, commit B, tag com os 7 primeiros hex de A apontando para B; `git rev-parse --verify --quiet --end-of-options <7hex>^{commit}` devolveu o sha de B, rc 0. Com o sha de 40 hex o git usa o objeto (conferido). Caminho de ataque: quem pode criar tag no remoto (ou ref local) com nome hexadecimal faz o `onde <sha curto>` responder `sim`/`nao` sobre outro commit, e a prova colada afirma estado falso. Exige escrita no repositório; severidade baixa. Correção mínima: no tipo `commit`, se `sha` não começa por `valor`, devolver `nao-verificavel (sha ambíguo com ref)` e rc 2; o mesmo vale no `mergeCommit` do PR (`:68`), onde o oid já é de 40 hex e a conferência é barata. Esforço P. Dono: tech-lead.

**A2.** Evidência: `bin/forge-check:10389-10391` trata `subprocess.TimeoutExpired` de qualquer subcomando com `return 1`; o `onde` chama o `git` com `GIT_TIMEOUT_S` de 5 s (`bin/forge-check:184`) em `rev-parse`, `merge-base`, `rev-list` e `log`. Caminho: clone grande ou disco lento, o `log --grep` estoura e quem lê o rc conclui "não existe" (falso negativo, não falso `sim`). Severidade baixa; o texto impresso diz "tempo esgotado", mas o rc contradiz o contrato. Correção mínima: em `bin/forge_onde.py`, `executar` captura `subprocess.TimeoutExpired`, imprime `onde: nao-verificavel (git sem resposta)` e devolve 2; um teste com `git` falso que levanta o timeout. Esforço P. Dono: tech-lead.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: leitura estática e sondas locais com git e o interpretador da stack em `$TMPDIR`. Ausentes no PATH (lacuna, não instaladas): gitleaks, semgrep, zizmor, actionlint, osv-scanner; nenhum segredo, workflow ou dependência nova no diff.
