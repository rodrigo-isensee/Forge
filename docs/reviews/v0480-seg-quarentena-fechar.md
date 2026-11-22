---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-seg-quarentena-fechar
commit: e77f3543f1844065aa66c90e6c1ba3123e66e55c
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-22
---
# Review: v0478 (E114.2, branch melhoria/v0480-seg-quarentena-fechar)

Diff `b0895f6c..e77f3543` (29 arquivos; código: `bin/forge-fechar` +61/-68, das quais 38 linhas acrescidas fora de comentário, e `bin/forge_quarentena.py` 1 linha). Dois commits, um comportamento cada: QUARENTENA-DIGITO-ASCII (541b96b4) e FECHAR-SEM-AUTO-MERGE (e77f3543). Dentro do teto H1.

## Achados
- A1 (recomendado) docs/fechamento-integrador.md:28 · ainda diz "Com `--armar`, a linha do `--limpar` impressa leva `--cartao` e `--quadro`"; o `--armar` agora só recusa e não imprime linha nenhuma. Tirar a frase.
- A2 (recomendado) bin/forge-check:1469 · comentário ainda fala em "armar o auto-merge" do forge-fechar; com FECHAR-SEM-AUTO-MERGE o passo 6 é merge direto. Ajustar o texto.
- A3 (recomendado) bin/forge-fechar:118 · `checks_do_head_verdes` mede o prazo com `ini=$SECONDS` próprio, então a espera do passo 6 recomeça o `--espera` depois do passo 4 (até 2x no pior caso); o doc diz "até --espera". Usar o `inicio` do passo 4 ou registrar o teto real no doc.

## Parecer
**Aprovado.** Faz o que a decisão do dono de 21/11 pede: nenhum `--auto` resta em `bin/forge-fechar` (`grep -c -- --auto` = 0); o `--armar` morre no parser antes de qualquer ação (`:117`), com o porquê e o comando certo; o passo 6 e o P6 da promoção passam por `checks_do_head_verdes` logo antes de `mesclar_direto`, preso ao head por `--match-head-commit`, sem `--admin`. Falha terminada para; pendente ou ausente espera e relê; leitura que falha para (falha fechada). As guardas que dependiam de `$armar` (lote, promover, `--limpar`, `--esperar-rotulo`, `ler_exigidos_do_destino`, a pulada do passo 4) saíram de forma coerente, sem deixar caminho que pule a leitura dos checks. P6: a catraca e a bateria rodam em `pull_request` para qualquer base (`.github/workflows/catraca.yml:6-8`, `ci.yml:20-22`), então os três exigidos existem no PR `promocao/* -> homolog`.

Quarentena: `A-[0-9]+` no lugar de `A-\d+` fecha o dígito Unicode; teste `test_autorizacao_so_com_digito_ascii`.

Guardas e mutantes (V2): cada linha de guarda mudada tem mutante declarado (specs `v0478-fechar-checks*.json`, `v047-integracao-em-lote*.json`, `v0474-merge-checks-*.json` atualizadas, nova `v0480-seg-quarentena-fechar.json`), com teste de comportamento do ramo de falha (pendente no fim do prazo, `--armar` com `--dry-run`/`--limpar`/`--esperar-rotulo`, MERGED fora do prazo). O falso do `gh` em `test_fechar` recusa `--auto` (código 65) e registra a chamada, e `test_fechar_auto_merge` afirma que nenhuma ocorreu: o falso é tão estrito quanto a regra (item 12 do checklist).

Delta lido: código e testes de `b0895f6c..e77f3543`; o commit 5a6f5cb4 (parecer de segurança) é só documento e não muda o revisado.

Rodado aqui, sem a suíte inteira (fica no CI do PR): `python3 -m unittest tests.test_fechar_auto_merge tests.test_fechar_checks_do_head tests.test_forge_quarentena tests.test_fechar_move_cartao tests.test_fechar_lote` deu `Ran 118 tests ... OK`; `bin/forge-mutante tests/mutantes/v0480-seg-quarentena-fechar.json` deu `QD1 · morreu` e `FS1 · morreu`. `shellcheck` não está instalado neste ambiente: fica para o CI (regra "ferramenta").
