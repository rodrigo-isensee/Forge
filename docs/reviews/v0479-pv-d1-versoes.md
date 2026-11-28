---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-d1-versoes
commit: 0204884e682798a4a0b83e3538c75bff62248620
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 E57.58 (PR-VERDE D1, `forge-testes --versoes`)

Diff revisado: `d4f0b10a..0204884e` (2 commits; `bin/forge-testes`, `tests/test_testes_tocados.py`, `tests/mutantes/v0479-pv-d1-versoes.json`, `tests/mutantes/v0479-pv-d1-versoes-2.json`, `changelog.d/v0479-pv-d1-versoes.md`). Código de produção: 79 linhas em `bin/forge-testes`, um comportamento (H1 dentro do teto).

## Ferramenta (citada, sem refazer)
- `bin/forge-mutante --processos 1 tests/mutantes/v0479-pv-d1-versoes.json tests/mutantes/v0479-pv-d1-versoes-2.json` (rev 0204884e6827): G1 a G10 morreram (`bin/forge-testes:1077,1080,1086,1090,1095,1103,1106,1116,1172,1211`).
- `bin/forge-mutante --processos 1 --cobertura --base d4f0b10a`: rc=0, toda guarda do diff coberta, nenhuma descoberta.
- Teste novo: `python3 -m unittest tests.test_testes_tocados.Versoes`: 9 testes, OK. Suíte inteira: fica com o CI do PR (`R-REVIEW`); sem suíte local, como o brief pede.

## Leitura
- Faz o que o D1 do desenho PR-VERDE pede: versões tiradas do `ci.yml` (nunca do ambiente), em série e ordem numérica, intérprete do PATH só vale se se diz da versão, log por versão com `head=` na 1.ª linha e `rc=` na última; ausente é aviso e não é verde (saída 1); sem versão, árvore suja ou git ilegível saem 2 sem log.
- Os filhos do `suite-partes`/`suite-paralela` usam `sys.executable`, então rodam todos na versão pedida, não só o processo de cima.
- `ValueError` do `oraculos()` (chamado dentro do `planejar_afetados`) é capturado e vira 2, como no `--afetados`.
- Testes: intérpretes falsos com versões inexistentes (9.1, 9.2), ambiente limpo, git com config global nula; cada guarda tem teste do ramo de falha por comportamento, nenhum lê a fonte. A lista de exclusão do `--versoes` cobre as outras opções (G8).
- Commits em Conventional Commits em português; fragmento de changelog presente.

## Achados
- A1 (recomendado) bin/forge-testes:1061 · o padrão só lê `python-version: "X.Y"` entre aspas duplas; `3.13` sem aspas, entre aspas simples ou em lista de matriz some calado, e as outras versões dão verde. Sugestão: sem veredito (2) quando há `python-version` que o padrão não lê.
- A2 (recomendado) bin/forge-testes:1079 · a pergunta da versão roda sem `timeout` e sem tratar `OSError`; um `python<X.Y>` do PATH que trava prende o `--versoes`, e um que não executa (shebang quebrado) sai em traceback. Sugestão: teto curto e tratar como ausente.

## Sondas

## Parecer
Aprovado. O `--versoes` cumpre o D1, os dez mutantes declarados morrem, a cobertura de guardas fecha e o teste novo passa. Os dois achados são recomendados (formatos de configuração que o `ci.yml` atual não usa; intérprete defeituoso no PATH) e viram cartão depois do merge (`R-REVIEW`).
