---
tipo: review
contrato: 1
pedido: hook-ansi-c
branch: melhoria/hook-ansi-c
commit: aadbcc165229e21e9af00d2c09d802dac7936ea7
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-27
---
# Review: hook-ansi-c

Escopo revisado: a revalidação por delta `f3d1fd092979c2bb8eb0af09db16e33909f94154..aadbcc165229e21e9af00d2c09d802dac7936ea7` (pareceres da volta 1 e merge da develop 03de011). A volta 1 (parecer e4f4999, aprovado no head f3d1fd0) segue como já lida; seu texto completo está no histórico do git.

## Achados

## Parecer
**Aprovado.** O merge da `develop` não mexeu em `hooks/` nem no leitor de `$'…'`, e a resolução manual está correta.

### Revalidação por delta
`bin/forge-check delta --parecer docs/reviews/hook-ansi-c.md` (parecer anterior, e4f4999) listou, além de pareceres e fragmentos, só conteúdo que veio da `develop` (README, `agents/jarvis.md`, `scripts/suite-paralela.py`, skills, `tests/apoio_volta_unica.py`, testes da volta única, mutantes de outros pedidos, `docs/regras/R-QA.md`), já revisado nos PRs deles. Li só o que toca esta entrega: `bin/forge-testes`:73, `tests/test_testes_tocados.py` e o que o merge poderia ter quebrado em `hooks/`. O resto ficou como "já lido".

- **`hooks/` intacto.** `git diff f3d1fd0 aadbcc1 -- hooks` vazio; o diff da branch contra a `develop` (03de011, que é o merge-base) mantém em `hooks/_comum.py` as mesmas 27 linhas já revisadas. `tests/test_hook_ansi_c.py` e `tests/mutantes/hook-ansi-c.json` também não mudaram desde f3d1fd0.
- **Resolução manual.** `bin/forge-testes`:73 tem `test_hook_ansi_c` e `test_medida_cpu` no `FORGE_CHECK`, e a contagem calculada da tupla (com `VOLTA_UNICA`) dá 27, igual a `tests/test_testes_tocados.py:61`, com `test_hook_ansi_c` no `assertIn`. A regra `hooks/.*` (linha 101) segue com `test_hook_ansi_c`; `forge-testes --listar hooks/_comum.py` o inclui.
- **Nada da develop quebra o leitor.** Os testes da volta única mudaram na develop só na medição (CPU em vez de relógio). Sonda em `palavras_do_texto`: `\$'it\'s'; cat .env \'` marca `aspa_escapada`; `echo $'a\nb'; ls` e `ls` não. `python3 -m unittest tests.test_hook_ansi_c tests.test_testes_tocados` passou, 90 testes OK.
- **Teto M14.** Contra a `develop`: 180 linhas contáveis, abaixo de 400. Uma classe de comportamento em `hooks/`; `hooks/conformidade.py` e `tests/config.json` intocados.
- **PA-7.** `docs/engineering/achados-recorrentes.md` segue sem itens; nada a conferir.

## Revisões
- Portões de outros: segurança (`docs/security/hook-ansi-c.md`, E2.1) e QA (`docs/qa/hook-ansi-c.md`, E3.1) revalidam este head em outra delegação.
- O A2 da segurança (`hooks/pesado.py:90`) segue como o cartão PESADO-ANSI-C, fora desta revisão.
