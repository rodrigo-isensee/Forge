---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-prepush-patch
commit: 805a0a1048222c22dc60f847eb879b16069fbbd6
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047 (melhoria/v047-prepush-patch, E2.325)

Parecer completo (não havia parecer anterior) do head 805a0a10 contra a base 1b88640e: `docs/devops/pp1-pre-push.patch` (63 linhas), `tests/test_pre_push_patch.py` (219) e o fragmento `changelog.d/v047-prepush-patch.md`. O `.githooks/pre-push` em vigor não muda; o patch é para o dono aplicar.

## Achados
- A1 (bloqueante) docs/devops/pp1-pre-push.patch:36 · Escopo diferente da catraca (R-REVIEW): com um hooks/*.py no diff, o --cobertura julga todo Python do diff; tests/catraca.py e helper tests/apoio_*.py com condição mudada barram o envio que a catraca do CI aceita, e a mensagem diz "o CI reprova igual" (S1, S2). Filtre a saída pela lista da catraca.
- A2 (recomendado) docs/devops/pp1-pre-push.patch:45 · O ramo de aviso (saída 2 do --cobertura, ex.: spec inválida) não tem teste de comportamento (R-QA); um caso com spec malformada no repo de teste prova que o envio segue com o aviso.
- A3 (recomendado) docs/devops/pp1-pre-push.patch:13 · A guarda `[ -e /proc/self/fd/9 ] || return 0` é equivalente: sem ela o head falha no fd ausente, o 2>/dev/null cala e a saída é vazia igual; tests/test_pre_push_patch.py:102 não a distingue. Declare-a equivalente ou tire.
- A4 (recomendado) tests/test_pre_push_patch.py:1 · 219 linhas de teste passam a orientação de 150 (M14); o PR, quando abrir, traz `teto: excedido, <n> linhas, <motivo>`.

## Sondas
- S1 · repo temporário com o hook remendado: diff muda hooks/h.py sem condição e tests/apoio_x.py `if a` -> `if a and b`, sem spec · espera: pre-push rc=0, como catraca.regra_guardas_dos_hooks == [] · obtido: pre-push rc=1 "sem mutante · tests/apoio_x.py:2"; catraca []
- S2 · mesmo repo, tests/catraca.py `if a` -> `if a and b` com hooks/h.py sem condição, sem spec · espera: pre-push rc=0, como a catraca ([]) · obtido: pre-push rc=1 "sem mutante · tests/catraca.py:2"; catraca []

## Parecer
Reprovado por A1. Os três consertos fazem o que o item pede e o teste prova cada um contra o original (o original é o mutante): leitura da trava pelo fd 9 (conferi à parte que `/proc/self/fd/9` lê também o fd aberto com `9>>`, como no hook real, linha 466), `FORGE_FILA_INTERVALO` 0/00/000 recusado antes da fila, e o envio leve reprovando condição mudada em `hooks/*.py` sem mutante. O patch aplica limpo no `.githooks/pre-push` da base (`git apply --check`, blob f9443600), `bash -n` ok, modo executável mantido; o teste limpa `GIT_*`/`FORGE_*` do ambiente (AR-4) e chama o `forge-mutante` com `-I` (AR-5).

O defeito do A1: o gatilho do patch (linhas 34 a 38) olha uma lista própria de caminhos, mas a análise roda sobre o diff inteiro, e o `--cobertura` só exclui `tests/test_*.py` e `.md`. A catraca (`tests/catraca.py`, `guardas_do_diff`) usa `motivo_de_controle` do `forge-check` e tira tudo o que casa `TESTE` (qualquer coisa em `tests/`). Com isso o envio local reprova o que o CI aprova, o contrário do "nunca afrouxa, o CI roda as mesmas checagens" do bloco PREPUSH-BARATAS, e a lista fixa (`templates/projeto/*`, `tests/catraca.py`, `tests/neutralidade.py`) diverge da fonte única. Sugestão: no lugar da lista e do `--cobertura` cru, chamar `catraca.regra_guardas_dos_hooks` (uma fonte só, já carrega o `forge-mutante` da base) ou filtrar as linhas `sem mutante|só equivalente|apagada` pelo mesmo `motivo_de_controle` sem `TESTE`; e um caso de teste com helper em `tests/` que tem de passar.

Ferramentas: `python3 -m unittest tests.test_pre_push_patch` na raiz do clone, 8 testes, OK (11,3 s). Suíte completa: sem PR ainda, o CI não rodou neste head; fica para o CI do PR. Shellcheck do hook remendado e mutação do diff: não citados pelo autor; o diff não muda shell nem Python de controle do repositório (o hook é texto num `.patch`), e o próprio teste faz o papel do mutante (original contra remendado).
