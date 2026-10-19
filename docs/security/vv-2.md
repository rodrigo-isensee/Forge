---
tipo: revisao-seguranca
contrato: 1
pedido: vv-2
branch: melhoria/vv-2
commit: 6396f2da9d1344b665ed829634fc84d3670e0499
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-19
---
# Review de segurança: VV-2 (volta por delta)

Rodada 2 (E2.2): revalidação só do delta da volta 1, `29fea960d2a6b4fbaf324072ee11d85fb0d04af6..6396f2da9d1344b665ed829634fc84d3670e0499` (13 arquivos, 121+/11-: `hooks/conformidade.py`, `bin/forge-check`, `bin/forge-testes`, `agents/conferente.md`, `agents/jarvis.md`, os modelos de parecer, dois fixtures em `tests/hooks/conformidade/`, `tests/test_volta_por_delta.py`, o fragmento `changelog.d/vv-2.md`). O resto da branch foi revisto na rodada 1 (`commit: e925152b3886dc7de006676f213328fec0c58d34`, parecer `reprovado` por A1; o texto completo dele, com o roteiro da E2.2 itens 1 a 10, está no histórico deste arquivo). Revisão estática e reprodução local num repositório temporário (`git init` com `.forge/versao`), com o `hooks/conformidade.py` e o `bin/forge-check` da branch rodados diretamente; nada de rede.

## Gatilhos
Controles do Forge (`R-SEGURANCA`): o delta muda a lista de opções que gravam no hook `conformidade.py` (portão do papel só de leitura), a raiz aceita pelo `forge-check brief --anterior` e o texto do conferente e do Jarvis sobre a origem do `--desde`.

## Achados

## Detalhe dos achados
Estado dos achados da rodada 1 (numeração do parecer em `e925152`; o pedido os cita como S-A1 a S-A5). Ambiente: hook com `CLAUDE_PROJECT_DIR=<repo temporário com .forge/versao>` e entrada JSON do PreToolUse com `agent_type: forge:conferente`, salvo onde dito.

- **A1 (bloqueante) → fechado.** `hooks/conformidade.py:180-182`: `--destino-arquivo` saiu de `FORGE_CHECK_GRAVA` (casamento por prefixo) e foi para `FORGE_CHECK_GRAVA_EXATA`, comparado por nome inteiro (`a.split("=", 1)[0] in ...`, linha 843). Reprodução (S1 da rodada 1): `forge-check brief docs/briefs/p1-tech-lead-1.md --pedido p1 --destino forge:tech-lead` → rc 0 (na rodada 1, rc 2); a forma da rodada de confirmação, `... --destino forge:tech-lead --anterior docs/briefs/p1-tech-lead-0.md --ref melhoria/x` → rc 0; `--destino=forge:tech-lead` → rc 0. Fixtures: `tests/hooks/conformidade/conferente-brief-destino-libera.json` (espera rc 0) e `conferente-brief-destino-arquivo-bloqueia.json` (espera rc 2, `opção que grava`); as duas entradas rodadas direto no hook: rc 0 e rc 2 (`R-CONFORMIDADE: \`forge-check brief\` com opção que grava arquivo`); `--destino-arquivo=x.md` → rc 2. `python3 -m unittest tests.test_hooks` → `Ran 20 tests ... OK`.
- **A recusa por nome inteiro não abre outra opção de gravação.** As quatro opções da lista de prefixo seguem recusadas, inclusive abreviadas: `forge-check entrega p1 --gerar-entrada`, `--gerar`, `--grav x`, `--salvar x`, `--escrever x` → rc 2 nos cinco; `forge-check conferencia registrar` → rc 2 (fora de `so_leitura`). Pelo `--help` da branch, nenhuma opção dos subcomandos liberados grava hoje (`brief`: `--anterior --base --branch --destino --etapa --is-ancestor --parecer --pedido --ref --volta`; `entrega`: `--base --base-sha --branch --desde --etapa`; `delta`: `--parecer`; `docs` e `pr`: nada que grave): a troca não abre caminho atual. Efeito colateral, sem caminho hoje: a abreviação `--destino-arq x.md` passa no hook (rc 0) e o argparse a recusa (`unrecognized arguments`, rc 2), porque `--destino-arquivo` não existe; no dia em que a opção nascer, o argparse (sem `allow_abbrev=False`) aceitará `--destino-a...` e o hook não a verá. É a classe do A3 (lista negra), já no cartão VV2-LISTA-BRANCA: a opção, ao nascer, entra na lista de prefixo (ou o `forge-check` passa a usar `allow_abbrev=False`), ou a lista branca resolve. Informativo, sem linha no bloco.
- **A2 (recomendado) → fechado na forma proposta (texto).** `agents/conferente.md:66` e `:75`, `agents/jarvis.md:64`: o `--desde` vem do campo `Desde:` da mensagem do Jarvis (canal que o autor não escreve); o conferente confere com `grep -n conferida <pedido>` e reprova com `escopo: --desde da mensagem diverge do Histórico` se divergir ou faltar. Reprodução (S2): Write do `forge:tech-lead` em `~/.forge-contrib/docs/pedidos/vv-2.md` com `CLAUDE_PROJECT_DIR` num projeto → rc 2; com `CLAUDE_PROJECT_DIR=~/Forge` (clone do Forge) → rc 0, como antes. A classe de sessão fora de projeto continua (anterior à VV-2, ADR 0009 seção 6), mas a linha `conferida` gravada pelo autor deixa de valer sozinha: o valor usado é o da mensagem e a divergência reprova; a etapa `pr` segue pela branch inteira. Texto travado por `test_desde_vem_da_mensagem_do_jarvis_e_o_texto_do_hook_e_exato` (OK). Selagem por máquina fica para o K1.
- **A3 (recomendado) → fora desta rodada** (cartão VV2-LISTA-BRANCA, decisão técnica no pedido). Reprodução (S3): `forge-check entrega p1 --saida x.md` → rc 0, sem mudança (o argparse a recusa; sem caminho hoje).
- **A4 (recomendado) → fora desta rodada** (mesmo cartão e K1). O delta migra os quatro modelos de parecer para o formato do bloco (`templates/projeto/docs/{reviews,qa,security}/_modelo.md`, `docs/security/_modelo.md`), o que reduz a origem do caso; o `forge-check docs` segue na transição. `test_parecer_escrito_pelo_modelo_passa_no_gerar_volta` → OK nos quatro modelos.
- **A5 (recomendado) → fechado.** `agents/conferente.md:25` agora diz que o hook recusa a forma `--opção=-valor` e que a forma `--opção -valor` passa ao `forge-check`, que a trata como valor. Reprodução (S5): `forge-check entrega p1 --branch -x` → rc 0; `--branch=-x` → rc 2 (`valor de opção que começa com \`-\``): o texto bate com o código.

Itens novos do delta, sem achado:
- `bin/forge-check:2680` (`cmd_brief_conferir`, `--anterior`): troca `dentro_da_raiz(raiz, ...)` por `caminho_de_brief`, que aceita também `~/.forge-contrib/docs/briefs/` (`RAIZES_DE_BRIEF`, linha 792), a mesma raiz que o `--volta` já aceitava. Só leitura, com `realpath`. Reprodução com `HOME` temporário: symlink em `~/.forge-contrib/docs/briefs/l.md` para fora → rc 2; `.../docs/briefs/../../../segredo` → rc 2; `/etc/passwd` → rc 2; `test_anterior_na_raiz_de_brief_do_forge` → OK (inclui `~/.forge-contrib/docs/outro.md`, rc 2).
- `bin/forge-testes`: duas entradas do mapa ligam os modelos de parecer ao `test_volta_por_delta`; sem efeito de segurança.
- `tests/test_volta_por_delta.py`: nome de arquivo acentuado (`-z`, `core.quotePath`) chega sem aspas; OK.
- E5 (`79d42f9`): ancestral de `29fea960`; o único hunk do delta em `bin/forge-check` (linha 2680, `--anterior`) não toca os da E5 (`brief gerar --etapa merge-integracao`, ancestralidade); `hooks/conformidade.json` e `docs/security/ameacas/vv-2.md` estão fora do delta.

Suítes: `python3 -m unittest tests.test_hooks` → `Ran 20 tests ... OK`; `python3 -m unittest tests.test_volta_por_delta` → `Ran 51 tests ... OK`. Suíte inteira e `validar-plugin` não refeitas (R-TETO; o QA as roda no head).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: git, python3 e as suítes do repositório. `gitleaks`, `semgrep`, `osv-scanner` e `shellcheck` não estão no PATH (lacuna registrada; o delta não traz dependência nova nem segredo à vista na leitura).

## Parecer
**Aprovado.** O A1 (único bloqueante) está fechado e coberto pelos dois fixtures; A2 e A5 fechados no texto; A3 e A4 seguem no cartão VV2-LISTA-BRANCA. A troca para casamento por nome inteiro não abre opção de gravação hoje; a abreviação futura de `--destino-arquivo` fica registrada para o mesmo cartão.
