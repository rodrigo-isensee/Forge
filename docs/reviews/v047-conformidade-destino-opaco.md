---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-conformidade-destino-opaco
commit: e25f079b9834ba470ac8ccda65e5ad678a426aaa
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-14
---
# Review: v047 · CONFORMIDADE-A9-DESTINO-OPACO e CONFORMIDADE-A10-OPERADOR-COLADO (E1.279)

Revalidação por delta do head e25f079b (volta da E1.232: U4, lista positiva do valor calculado; palavras do corpo por regex, crase depois do `of=` do dd, mutantes O83 a O98, A3 recomendados). Instância que não fez a entrega.

Delta lido: `forge-check parecer delta docs/reviews/v047-conformidade-destino-opaco.md`, intervalo `e8c459de..e25f079b`, domínio código e testes: `hooks/conformidade.py` (+164/-3), `tests/test_conformidade_opaco.py`, `tests/test_hook_destino_opaco.py`, `docs/hooks.md`, `docs/hooks-fixtures.md`, 54 fixtures `opaco-u4-*` e `opaco-semresto-*`, mutantes `tests/mutantes/v047-destino-opaco-2,7,9..15.json`.

## Achados
- A1 (bloqueante) hooks/conformidade.py:530 · `valores_do_corpo` aceita a lista positiva antes de ver a função da linha: `date(){ printf .gi%s t/config; }; echo a > "$(date)"` dá rc 0 e o bash grava `.git/config` (S1, S2); o U3 (:1334) libera igual com `cp config` (S3). Conferir a redefinição antes da lista (R-CONFORMIDADE).

## Sondas
- S1 · Bash `date(){ printf .gi%s t/config; }; echo a > "$(date)"` no hook do head e25f079b · espera: rc 2 · obtido: rc 0; no bash, a linha `[core] x = 1` gravada em `.git/config`
- S2 · Bash `mktemp(){ printf .gi%s t/hooks/pre-push; }; cp x "$(mktemp)"` (também `pwd(){…}` e `true(){…}`) · espera: rc 2 · obtido: rc 0
- S3 · Bash `date(){ printf .gi%s t; }; cp config "$(date)"` (U3, origem de nome do git) · espera: rc 2 · obtido: rc 0

## Parecer
Reprovado no e25f079b por A1. O resto da volta fecha o que foi pedido: o A1 do review E1.205 (duas substituições coladas) recusa e entrou no gerador (`duas-coladas`); o A1 e o A2 da segurança E1.206 (corpo que calcula, resto colado) recusam pelo U4, e as sondas S1 e S12 da segurança dão rc 2 no head; o A3 da segurança entrou em `na_lista_positiva`, e o A3 deste review ficou como falso positivo aceito no `docs/hooks.md`. O desenho do U4 é bom: lista positiva (AR-3), teto de 64 combinações, variável com nome citado de outro jeito na linha recusa, `SEM_VALOR` sozinho no componente.

- hooks/conformidade.py:530 e :1334 · problema: `na_lista_positiva` confia no nome do comando (`date`, `mktemp`, `pwd`, `true`, `false`, `:`, `git`), mas a linha pode redefini-lo como função; o `corpo_da_funcao` só é consultado depois, e o U3 nem o consulta. `git(){…}` já recusa por outra trava (chaves com ação crítica), os demais não · sugestão: só valer a lista positiva quando `corpo_da_funcao(primeira palavra, linha)` diz não definida (no U4 e no U3), com fixtures `opaco-u4-*` de bloqueio para S1 a S3 e um mutante na guarda nova · severidade: bloqueia.

Fora do achado, para o mesmo ajuste ou cartão: `PATH=.:$PATH` com um `date` executável no projeto tem o mesmo efeito, mas exige gravar o executável antes e é da codificação arbitrária (residual R1).

Provas rodadas por mim: `python3 -m unittest tests.test_hook_destino_opaco`, 4 testes, OK (20 s), com as 54 fixtures `opaco-u4`. Sondas pelo `tests/test_oraculo_v047.py` como biblioteca (`rodar_hook`, papel `forge:tech-lead`, projeto em `melhoria/x`), sem editá-lo; o efeito no bash conferido num repositório temporário. Mutantes: 15 specs; não rerrodei, cito o PQ do autor. Sem PR aberto, não há CI a citar.

Teto M14: 962 linhas de código e teste (`git diff --numstat --no-renames origin/develop...HEAD` nos caminhos que contam), acima das 150; uma classe só (destino opaco do Bash), com corpus próprio (`opaco-*`, 139 fixtures). O corpo do PR precisa de `teto: excedido, <n> linhas, <motivo>`.
