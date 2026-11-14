---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-conformidade-destino-opaco
commit: e8c459de79e98bd22a65892b4605c97a7583de58
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-14
---
# Review: v047 · CONFORMIDADE-A9-DESTINO-OPACO e CONFORMIDADE-A10-OPERADOR-COLADO (E1.205)

Head revisado e8c459de (lote B, classe C, `hooks/conformidade.py`; volta E1.175 com os 9 casos D2b e a develop trazida). Intervalo `origin/develop..e8c459de`. Instância que não fez a entrega.

## Achados
- A1 (bloqueante) hooks/conformidade.py:464 · `palavra_juntada` só lê a variável colada como `*`; substituição colada a outra (`$(echo .gi)$(echo t/hooks/pre-push)`, também com crase) monta `.git` sem resto e libera (S1, S2), e o bash grava o hook. Mesma classe D2b do oráculo (R-CONFORMIDADE); ler `$(…)`/crase colado como `*`.
- A2 (recomendado) hooks/conformidade.py:1136 · com resto, `"$(echo .gi)t/config"` também grava o `.git/config` com rc 0 (já na base f4b0c2ae, domínio do `resto_no_git`, fora do A9). Cartão próprio para a junção opaco+literal no resto.
- A3 (recomendado) hooks/conformidade.py:1146 · U3 recusa `cp config "$TMPDIR"` e `cp config "$DEST"` (variável do ambiente, sem `nome=` na linha). Lado seguro, mas é forma comum dos agentes; listar no falso positivo aceito do `docs/hooks.md:112` ou tratar `$TMPDIR` como positivo.

## Sondas
- S1 · Bash `cp x "$(echo .gi)$(echo t/hooks/pre-push)"` no hook do head e8c459de · espera: rc 2 (destino opaco sem resto no .git) · obtido: rc 0; no bash, `.git/hooks/pre-push` criado
- S2 · Bash `echo a > "$(echo .gi)$(echo t/config)"` no hook do head e8c459de · espera: rc 2 · obtido: rc 0

## Parecer
Reprovado no e8c459de por A1. A regra única do A9 (destino opaco sem resto) e a volta D2b pela palavra juntada estão bem desenhadas: listas fechadas e positivas (AR-3), teto de 64 por linha (C21), o A10 tira a liberação do #512 com rev-parse de mais de um comando, e o `texto_da_linha` é restaurado por nível no `finally`. O furo de A1 é o mesmo do D2b (concatenação que monta `.git`), só que entre duas substituições em vez de variável e texto: o gerador do `tests/test_conformidade_opaco.py` não tem forma com duas partes opacas coladas, por isso não o pegou.

- hooks/conformidade.py:464 · problema: em `palavra_juntada`, `REF_DE_VARIAVEL` casa só `$x`/`${x}`; a palavra `.gi)$(echo t/...` fica sem `.git` e sem curinga · sugestão: ler cada `$(…)` e crase colado a outro texto ou a outra parte opaca como `*` (o corpo `echo .gi` segue nos precisos), com fixture `opaco-d2b-*` de bloqueio (duas substituições, crase mais substituição) e o caso no gerador · severidade: bloqueia.
- A2 e A3 não devolvem.

Sondas rodadas por mim com o `hooks/conformidade.py` do head e da base (projeto temporário com `.forge/versao`, Bash do `forge:tech-lead`): S1 e S2 dão rc 0 no head e na base; no bash, S1 cria `.git/hooks/pre-push` e `echo a > "$(echo .gi)t/config"` sobrescreve `.git/config`. Formas que recusam como o esperado: `cp config "$(echo .git)"`, `a=.g; …"$(echo ${a}it/config)"`, `p=.gi; q=t; …"$p$q"`, `"$(echo .gi)$(echo t)/config"` (pelo `resto_no_git`). `"$(printf .gi%s t)"` e `"$(echo tig. | rev)"` liberam: codificação arbitrária, residual R1 do plano da E1.133, fora do achado.

Teto M14: 797 linhas de código e teste (`git diff --numstat --no-renames origin/develop...HEAD` nos caminhos que contam; 384 delas são o oráculo do portão), acima das 150; uma classe só (destino opaco do Bash), com corpus próprio (`opaco-*`, 85 fixtures). O corpo do PR precisa de `teto: excedido, <n> linhas, <motivo>`.

Mutantes declarados: 49 em 8 specs (`tests/mutantes/v047-destino-opaco*.json`, até 8 por arquivo); não rerrodei, cito o PQ do autor. Provas rodadas por mim: `python3 -m unittest tests.test_oraculo_v047 tests.test_hook_destino_opaco tests.test_conformidade_opaco`, 8 testes, OK (452 s). Sem PR aberto, não há CI a citar; a suíte inteira fica para o CI do PR.
