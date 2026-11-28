---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-sessao-forge
commit: 6aa5b7bec87035d37234363585f610a674fa0655
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: travas do conformidade na sessão do Forge, revalidação (v0478 E51.34, parecer E51.36)

Volta por delta (`R-REVIEW`): a rodada anterior (E51.24, `commit: b22efaa`, aprovado) está no git. Delta lido: `forge-check parecer delta` de `b22efaa..6aa5b7b`, sem o que veio da `develop`. No domínio: `hooks/conformidade.py`, `docs/hooks.md`, `tests/test_hooks.py` e a fixture `e51-wt-ponto-argumento-pipe-aninhado-libera.json`. As linhas mudadas nos três primeiros são exatamente as do E50 (#734, `f96ede50`, já aprovado no pedido próprio): os diffs `0f6034e..f96ede5` e `b22efaa..6aa5b7b`, só com as linhas `+`/`-`, são idênticos; o merge não resolveu conflito no domínio. Próprio do E51 no delta: só a fixture (`96c0215..6aa5b7b`), que troca `*docs/reviews*` por `*docs/regras*` no `find .`, sem mudar o hook.

Gatilhos: hook de conformidade (controle que analisa comando), R-MAIN, R-VERIFY, R-FLUXO (push para a integração, tag v*).

## Estado dos achados anteriores
- A1 (E51.12) e A2 (E51.20): corrigidos nas rodadas E51.16 e E51.24; nada no delta os toca.

## O que foi conferido
- **A fixture continua provando a guarda.** No head, `tests.test_hooks.HookSessaoDoForge.test_travas_do_conformidade` passa; com o mutante M43 (`na_posicao_de_programa` → `return True`, spec `-7`) aplicado, falha exatamente nesta fixture (`2 != 0`): o mutante é barrado. Com a fixture antiga (`docs/reviews`) e o hook do head, a saída é 2 pela barreira de papel do E50 (`parecer_no_texto` na recusa "o hook não modela"), o que deixaria o M43 vivo: a troca para `docs/regras`, fora de `PARECER_NO_TEXTO`, é a necessária e não afrouxa nada.
- **A soma E50 + E51 só aperta** (confirmação escrita para o rótulo, decisões do dono das 19:09 e 19:55). Estrutura: em `GuardaDaProva.barrar` o E51 só acrescenta um `if self.travas and trava_da_sessao_do_forge(...)` independente; as recusas do E50 (`recusa_do_estado` com `CAMINHOS_DE_PARECER` e `parecer_no_texto`, `parecer_no_topo` em `caminho_barrado`, a recusa da linha ilegível que cita pasta de parecer em `prova_fora_de_projeto`) seguem intactas e antes dela. Prova: as 55 fixtures `e51-*` do head rodadas com os `hooks/` da `develop` (`f96ede50`, só E50): 40 falham, todas `bloqueia` (0 na base, 2 no head), e nenhuma `libera` (nenhum 2→0). No head, `Hooks.test_fixtures_do_parecer_pelo_papel` (E50) e `HookSessaoDoForge` (E51): OK, 3 testes.
- **Custo:** o teto da soma (+3252 = 1084 + 2168, abaixo do aviso de +3300) não muda neste delta; conferido pelo QA em E51.32.
- **CI:** no head, `bateria (passos)`, `bateria (verificações longas)`, `instalação` e `árvore já provada` verdes; a suíte em andamento quando este parecer foi gravado; `bateria (pareceres)` espera este parecer; a Catraca recusa por falta do rótulo `afrouxa-regra` (`hooks/conformidade.py` é controle), que o dono autorizou para o E51 e aplica depois do último push. Quem mescla confere o CI verde.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do delta, mutante M43 e fixtures pela máquina de `tests/test_hooks.py` em cópias por `git archive`. Faltaram no PATH: gitleaks, semgrep e zizmor (o delta não toca segredo nem workflow).
