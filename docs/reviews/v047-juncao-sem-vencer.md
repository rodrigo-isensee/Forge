---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-juncao-sem-vencer
commit: 7babe7b84c382dc4ecba5ca59bfac38e3e210995
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047 (E2.247), conserto E2.201 JUNCAO-SEM-VENCER

Escopo revisado: `4138445e...7babe7b8` (2 commits): `bin/forge-check:1323-1329` e `:9564`, `tests/test_forge_check_base_igual.py` (classe `JuncaoSemBase`), `tests/test_forge.py:6972-6975`, `tests/mutantes/v047-juncao-sem-vencer.json` e o fragmento em `changelog.d/`. Parecer completo, porque não havia parecer anterior. Quem escreve é uma instância que não fez a entrega.

## Achados

## Sondas

## Parecer
**Aprovado.**

- Requisito (E2.201, regra E7): sem `--base`, numa branch de trabalho que não está em `BASES_DO_FLUXO`, o `pr_da_cli` passa a usar a `develop` como base. Só faz isso quando `base_do_delta` resolve a develop: com o head já contido nela, ou sem develop, o resultado é `None` e segue o diff literal de antes. Assim o `forge-check pr` fica igual ao `forge-fechar`, que já passa `--base`, e ao `parecer delta`. Trazer a develop por merge limpo não vence o parecer por arquivo que a branch não mudou. O arquivo que a branch mudou depois do parecer continua vencendo. A entrega faz o que o cartão pede, nem mais, nem menos.
- Alcance: os outros chamadores do `pr_da_cli` sem base também ganham a develop implícita: o pré-voo `--previo` do pre-push e `bin/forge-check:8150` quando vem sem base. Isso é coerente com a E7. A catraca do CI chama o `cmd_pr` com a base do evento e não muda. As branches `develop`, `homolog` e `main` seguem com o diff literal (teste `test_branch_de_integracao_segue_o_diff_literal`).
- Mutantes (AR-1, AR-12): as três linhas de guarda mudadas (`:1326`, `:1327` e `:1328`) têm um mutante cada. Rodei `bin/forge-mutante --processos 1` no head: `M1 · morreu · bin/forge-check:1326`, `M2 · morreu · bin/forge-check:1328` e `M3 · morreu · bin/forge-check:1327`. O `--cobertura --base 4138445e` deu as três linhas cobertas. O ramo de falha de cada guarda tem teste de comportamento (AR-2): merge limpo sem vencer, mudança da branch vencendo e branch de integração no diff literal.
- Testes: rodei `python3 -m unittest tests.test_forge_check_base_igual tests.test_forge.TesteEParecerSeparados` na raiz do clone e deu OK em 16 testes. O teste de `test_forge.py` agora procura a linha do parecer e confere as duas partes da mensagem, que passou a trazer `(base origin/develop ...)`. O alvo continua existindo (item 11 do checklist). O `git` dos testes roda com o ambiente sem `GIT_*` (AR-4), pela fixture `BaseIgual` que já existia.
- Suíte: não rerrodei a suíte inteira (R-REVIEW). Valem a entrega 7babe7b8 (Histórico do pedido, 2026-11-16 07:47) e o CI do PR.
- Tamanho (M14): 49 linhas de código e teste (`bin/forge-check` 10, `tests/test_forge.py` 7, `tests/test_forge_check_base_igual.py` 32), um comportamento só.
- Legibilidade: a docstring e o `help` do `--base` descrevem o padrão novo. O `base_do_delta` roda duas vezes no caminho com base implícita. São poucas leituras de ref, sem efeito no veredito.
