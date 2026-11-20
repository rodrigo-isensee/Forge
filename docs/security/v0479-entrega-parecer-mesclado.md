---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-parecer-mesclado
commit: 8cff35a0a8a65134b83fbd3841c4f3bb290269bc
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: E50.6 e E50.7, barreira de papel e âncora do Jarvis (v0478 E50.9, revalidação)

Delta lido (`forge-check parecer delta`, `cdf62e0a..8cff35a0`): no domínio, `bin/forge-check` (`autores_da_volta` e a âncora em `parecer_mesclado_na_volta`), `hooks/conformidade.py` (`CAMINHOS_DE_PARECER`, `GuardaDaProva.parecer_no_topo`, `recusa_do_estado`), `docs/hooks.md` e as 20 fixtures `pp-sessao-forge-*` com o teste delas em `tests/test_hooks.py`. Fora do domínio, lidos para a conferência: os 5 testes novos de `ParecerMescladoNaVolta`, os três specs de mutante e o fragmento do changelog. Também li `prova_fora_de_projeto` e `principal` (`hooks/conformidade.py:3790-3925`), que decidem quando a `GuardaDaProva` vale.

Gatilhos: controle do Forge (hook `conformidade` e `forge-check entrega`), afrouxa-regra com condições do dono (DECISÃO DO DONO 2026-11-20 10:59 e 13:21).

## Achados
- A5 (bloqueante) hooks/conformidade.py:3784 · na sessão do Forge, a recusa "o hook não modela" (variável no alvo com ação crítica) só vale se a linha cita o estado dos hooks; em projeto vale sempre. Todo papel grava qualquer pasta de parecer por `f=docs/qa/x.md; echo x > $f` (41 de 41 células).

## Sondas
- S13 · hook conformidade, CLAUDE_PROJECT_DIR = clone do Forge, cwd = ~/.forge-contrib/wt/x, agent_type de agente de stack (papel dev), Bash `d=docs/reviews; printf x > "$d/n.md"` · espera: rc 2 (barra) · obtido: rc 0 (libera)
- S14 · mesma linha da S13 numa sessão de projeto (raiz com `.forge/versao`), agent_type forge:dev · espera: rc 2 · obtido: rc 2, a referência que a sessão do Forge não alcança
- S15 · contexto da S13, agent_type forge:dev, Bash `f=docs/qa/n.md; echo x > $f` · espera: rc 2 · obtido: rc 0
- S16 · contexto da S13, agent_type forge:jarvis, Bash `d=docs/security/aceites; printf x > "$d/n.md"` · espera: rc 2 · obtido: rc 0

## Detalhe dos achados
**Achados anteriores.**
- A1 e A2 (rodada de `48153733`): seguem no head, `bin/forge-check:3020` (`revisado != de`) e `bin/forge-check:3002` (só a pasta do tipo, fora de `docs/security/aceites/`). Os testes deles seguem verdes (`ParecerMescladoNaVolta`, 14 de 14, rodados aqui).
- A3 (barreira de papel na sessão do Forge): corrigido para as formas que o hook lê, com uma lacuna (A5). `GuardaDaProva` agora recusa as pastas de parecer para todo papel não dono (`hooks/conformidade.py:3748-3761`, `:3778-3780`), pela forma da raiz da sessão e pela do topo da cópia do Forge que contém o alvo. S9, S10 e S11 da rodada anterior: rc 2. Fixtures: `test_fixtures_do_parecer_pelo_papel` verde (20 de 20).
- A4 (mesmo papel do autor): corrigido em `bin/forge-check:3022`. O parecer do papel de um autor da volta (o `Agente destino` dos briefs selados de codigo; sem nenhum, falha fechada) só vale com o blob do último `parecer conferido`. S12 refeita pelos testes `test_mesmo_papel_sem_linha_do_jarvis_segue_fora`, `test_parecer_conferido_de_outra_versao_nao_ancora`, `test_sem_autor_conhecido_falha_fechada` e `test_brief_de_outro_pedido_nao_e_autor_da_volta`: rc 1. O caso legítimo, `test_mesmo_papel_com_parecer_conferido_do_jarvis_e_anexo`, passa. Ressalva de contexto na condição (3).

**Condição (1) do dono, os dois apertos entraram.** Sim. O `commit:` do parecer tem de ser exatamente a versão revisada que abre a volta (`bin/forge-check:3020`), e cada tipo só vale na própria pasta, fora dos aceites (`bin/forge-check:3002`). Os testes de abuso das duas regras estão verdes no head.

**Condição (2) do dono, o autor não grava nas pastas de parecer na sessão do Forge.** Ainda não posso confirmar por escrito, por causa do A5. Prova da matriz, rodada no hook real da branch pelo lançador de `tests/test_hooks.py` (sessão do Forge, worktree em `~/.forge-contrib/wt/x`):
- 9 papéis (`tech-lead`, `devops`, `qa`, `seguranca`, `jarvis`, `doc`, `dev` do núcleo, `dev` de stack e a sessão principal sem `agent_type`) × 5 pastas (`docs/reviews/`, `docs/qa/`, `docs/devops/`, `docs/security/`, `docs/security/aceites/`) × 14 formas: Write, Edit, Bash `>`, `cp`, `tee`, interpretador com `-c`, variável no alvo, `cd` antes, caminho absoluto, `..`, `git checkout -- <arq>`, `mv`, `sed -i` e `sh -c`.
- Resultado: 630 casos. Nas 4 células do dono (56 casos), tudo libera, como deve. Nas 41 células de papel não dono (574 casos), 533 barram e 41 liberam, todos na forma da variável no alvo (A5).
- Corpus de legítimos na mesma sessão, 18 de 18 liberados: `git merge`, `pull --rebase`, `switch`, `checkout <branch>`, `stash pop`, `cherry-pick`, leitura (`cat`, `grep`, `git log`, `git diff`), cópia de parecer para `$TMPDIR`, `git add` e `commit` do parecer, `forge-check docs`, `git worktree add`, o push da segurança e a variável no alvo do próprio dono (`f=docs/security/x.md; printf x > $f`, papel `seguranca`).
- Fora do escopo da condição, e igual em projeto: o hook não modela `$(echo docs/reviews)` no alvo, curinga no redirecionamento, laço que monta o caminho (`for p in reviews qa; do echo x > docs/$p/n.md; done`) nem caminho montado em tempo de execução dentro do interpretador. Esses casos passam nos dois contextos, ficam com a BP-5 (`docs/hooks.md`) e não são achado deste delta.

**A5, caminho de ataque.**
- Quem: o agente autor da volta, por atalho ou por alucinação. De onde: a worktree em `~/.forge-contrib/wt/`. O que ganha: grava `docs/<pasta>/<pedido>.md` de outro papel com `f=...; echo ... > $f`, a forma mais comum de shell, e o `forge-check entrega` o aceita como anexo do portão (S6 da rodada anterior), porque para outro papel a conferência confia na barreira do hook.
- Evidência: em `GuardaDaProva.recusa_do_estado` (`hooks/conformidade.py:3784`), a recusa da construção que o hook não modela só vale quando a linha cita `ESTADO_NO_TEXTO`. O mesmo acontece no ramo de linha ilegível ou erro interno de `prova_fora_de_projeto` (`hooks/conformidade.py:3805`). Em projeto, a `Guarda` recusa essa construção sempre (S14).
- Severidade: média (controle de processo interno, sem segredo nem dado pessoal).
- Correção mínima: nas duas linhas, além de `ESTADO_NO_TEXTO`, recusar quando a linha (já com as continuações juntadas) cita uma pasta de parecer de que o papel não é dono. A lista inteira: `docs/reviews/` (só `tech-lead`), `docs/qa/` (só `qa`), `docs/devops/` (só `devops`), `docs/security/aceites/` (nenhum agente), `docs/security/` (só `seguranca`). O papel dono segue livre na própria pasta.
- Teste de abuso: S13, S15 e S16 como fixtures `pp-sessao-forge-*` com rc 2, e a variável no alvo de um papel não dono em cada uma das 5 pastas. Legítimos que seguem com rc 0: a variável do dono na própria pasta e uma variável que não cita pasta de parecer (`f=src/x; echo x > $f`).
- Esforço: P. Dono: tech-lead (hook; `tests/hooks/` só em `melhoria/*`).

**Condição (3) do dono: o que a mudança aceita a mais, e por quê.**
- As peças novas deste delta só apertam. `caminho_barrado` devolve `achado or parecer_no_topo(...)` e `recusa_do_estado` ganha um `True` antes dos outros testes, então o hook só soma recusas. Em `bin/forge-check:3022` entra um `return False` a mais. O corpus de 18 legítimos segue livre.
- O afrouxamento do item é o que o rótulo declara: na volta, o parecer de outro papel commitado só com a pasta dele, com `commit:` igual ao Desde e sem veredito trocado, sai como anexo do portão pela forma do git. Isso destrava o caso real (S5) e depende da barreira de papel do hook. Com o A5 aberto, essa barreira tem uma brecha.
- O parecer do mesmo papel do autor só vale com o `parecer conferido` do Jarvis. Em projeto, o `## Histórico` fica em `docs/pedidos/`, que o hook guarda (só `jarvis`). Na sessão do Forge, a cópia do pedido em `~/.forge-contrib/docs/pedidos/` não tem guarda de papel: sondei Write, Edit e Bash `>>` de `forge:tech-lead` e Write de `forge:dev` ali, e os 4 liberam (rc 0). O mesmo vale para `docs/briefs/`.
- Por isso, na sessão do Forge, o tech-lead autor ainda consegue forjar o próprio review se gravar duas coisas de propósito: o parecer e a linha do Jarvis. Isso não vem deste delta: é a mesma ausência de guarda que já vale para as linhas `conferida`, `patch do dono` e `DECISÃO DO DONO` na sessão do Forge. Também não está na condição (2), que fala só das pastas de parecer. Fica como resíduo declarado e vai ao Jarvis como item próprio (guarda de papel de `docs/pedidos/` e `docs/briefs/` na sessão do Forge, `R-DECISAO`).

## Riscos aceitos e ferramentas
Nenhum risco aceito. O rótulo `afrouxa-regra` segue condicionado ao A5 neste PR (condição (2), DECISÃO DO DONO 2026-11-20 10:59 e 13:21).

Sondas: o hook rodou pelo lançador de `tests/test_hooks.py` (`Fixture.montar` e `rodar`), em pastas temporárias com HOME temporário; o `forge-check` rodou pela classe `ParecerMescladoNaVolta` (14 testes verdes).

Suíte inteira: fica com o CI do PR. Não conferi o estado do CI em `8cff35a0`, porque o `gh` não lê credenciais no sandbox.

Lacuna: gitleaks, semgrep, zizmor e actionlint fora do PATH. O delta não toca workflow nem dependência.
