---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-parecer-mesclado
commit: 5376b86d2b441a17f4aba8b05c37d94e8a5e94a4
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: A6, variável do dono e linha sem leitura nas pastas de parecer (v0478 E50.17, revalidação)

Delta lido (`forge-check parecer delta`, `aebace71..5376b86d`): no domínio, `hooks/conformidade.py` (`PARECER_NO_TEXTO` com `re.I` e sem o ramo `security/aceites`, `GuardaDaProva.parecer_no_texto` no lugar de `parecer_alheio_no_texto`, a mensagem do ramo de `prova_fora_de_projeto`), `docs/hooks.md`, as fixtures `pp-sessao-forge-*` (8 novas ou trocadas, 2 apagadas por virarem `-bloqueia`) e o piso de 25 recusas em `tests/test_hooks.py`. Fora do domínio, nada relido (`changelog.d/`, `tests/mutantes/`). `bin/forge-check` não mudou no delta. A rodada anterior está no git (`f749c598`, parecer no `aebace71`).

Gatilhos: controle do Forge (hook `conformidade`), afrouxa-regra com condições do dono (DECISÃO DO DONO 2026-11-20 10:59 e 13:21).

## Sondas
- S17 · hook conformidade, CLAUDE_PROJECT_DIR = clone do Forge, cwd = ~/.forge-contrib/wt/x, agent_type forge:security-engineer, Bash `d=docs/security; echo x > $d/aceites/n.md` · espera: rc 2 · obtido: rc 2 (em projeto: rc 2)
- S18 · contexto da S17, agent_type forge:tech-lead, Bash `d=docs/reviews; echo x > $d/../qa/n.md` · espera: rc 2 · obtido: rc 2 (em projeto: rc 2)
- S19 · contexto da S17, agent_type forge:qa-engineer, Bash `d=docs/qa; echo x > $d/../security/aceites/n.md` · espera: rc 2 · obtido: rc 2 (em projeto: rc 2)

## Detalhe

**Achados anteriores.**
- A1 e A2: seguem corrigidos. O delta não toca `bin/forge-check`: `:3020` (`revisado != de`) e `:3002` (cada tipo só na própria pasta, fora de `docs/security/aceites/`).
- A3, A4 e A5: seguem corrigidos. O delta não afrouxa essas guardas; o A5 ficou mais largo (dono incluído).
- A6: corrigido. `PARECER_NO_TEXTO` (`hooks/conformidade.py:3727`) casa as quatro raízes em qualquer caixa, e `docs/security` cobre `docs/security/aceites`; `parecer_no_texto` (`:3791-3795`) não tem mais a exceção do dono. S17, S18 e S19 saíram de rc 0 para rc 2, igual ao projeto. Fixtures de abuso: `pp-sessao-forge-wt-seguranca-variavel-mae-aceites-bloqueia` (S17), `pp-sessao-forge-wt-tech-lead-variavel-vizinha-qa-bloqueia` (S18), `pp-sessao-forge-wt-qa-variavel-vizinha-aceites-bloqueia` (S19), `pp-sessao-forge-wt-tech-lead-variavel-caixa-qa-bloqueia` (caixa), `pp-sessao-forge-wt-seguranca-variavel-security-bloqueia` e `pp-sessao-forge-wt-tech-lead-teto-reviews-bloqueia` (dono pela variável e acima do teto).

**Matriz de papéis, refeita no hook real do head** (lançador de `tests/test_hooks.py`, sessão do Forge, worktree em `~/.forge-contrib/wt/x`, HOME temporário):
- 9 papéis (`tech-lead`, `devops`, `qa`, `seguranca`, `jarvis`, `doc`, `dev` do núcleo, `dev` de stack e a sessão principal sem `agent_type`) × 5 pastas (`docs/reviews/`, `docs/qa/`, `docs/devops/`, `docs/security/`, `docs/security/aceites/`) × 16 formas: Write, Edit, Bash `>`, `cp`, `tee`, interpretador com `-c`, variável com o arquivo, variável com a pasta, `cd` antes, caminho absoluto, `..`, `git checkout -- <arq>`, `mv`, `sed -i`, `sh -c` e a linha que o hook não lê.
- Resultado: 720 casos. Nas 41 células de papel não dono, os 656 casos barram. Nas 4 células do dono, as 12 formas literais liberam (48 casos), e as 4 que o hook não modela (variável com o arquivo, variável com a pasta, `sh -c` e a linha sem leitura) barram (16 casos), como em projeto (o `sh -c` do dono dá rc 2 nos dois contextos). Na rodada anterior, essas 16 liberavam.
- Dimensão do A6, agora na matriz (a variável que guarda a pasta do dono e alcança a vizinha ou a aninhada): os 4 donos × as 4 outras pastas × alvo por `$d/../<pasta>/`, `$d/../../docs/<pasta>/` e, para a aninhada (`docs/security` → `aceites`), `$d/aceites/` e `${d}/aceites/`, cada um em `echo >`, `cp` com a pasta terminada em barra e `printf >` entre aspas: 102 casos, 102 barram. Também barram `d=docs/devops; … $d/../reviews/`, `d=docs/security; … $d/../qa/`, `d=Docs/Security; … ${d,,}/aceites/` e `D=docs/REVIEWS; … ${D,,}/../qa/`.
- Corpus de legítimos: liberam `git merge`, `pull --rebase`, `switch`, `stash pop`, `cherry-pick`, leitura (`cat`, `grep`, `git log`, `git diff`), `git add`, `commit` e push do parecer pela segurança, `git merge --no-ff` pelo Jarvis, `git worktree add`, `f=src/x; echo x > $f` e o dono gravando a própria pasta pelo caminho literal no Bash (os quatro donos, rc 0).
- Fora do escopo, e igual em projeto (rc 0 nos dois contextos, fica com a BP-5): `d=docs; echo x > $d/reviews/n.md`, `p=qa; echo x > docs/$p/n.md`, aspas ou barra no meio da pasta (`docs/'qa'`, `doc\s/qa`), `docs//qa`, `./docs/./qa`, `$(echo docs/qa)` e curinga (`docs/q?`, `docs/[q]a`). Sem mudança desde a rodada anterior.

**Condição (1) do dono, os dois apertos entraram.** Sim. O parecer tem de citar exatamente a versão revisada (`bin/forge-check:3020`, `revisado != de`), e cada tipo só vale na própria pasta, fora dos aceites (`bin/forge-check:3002`). O delta não os toca.

**Condição (2) do dono, o autor não grava nas pastas de parecer na sessão do Forge.** Confirmo por escrito: o hook barra pelo papel. Nas 41 células de papel não dono, as 16 formas barram. A variável e a linha sem leitura barram para todo papel, dono incluído (S13, S15 e S16 da rodada anterior; S17, S18 e S19 desta). O dono não alcança a pasta vizinha nem a aninhada pela variável (102 de 102). O `tech-lead`, autor dos itens de hook, não grava `docs/qa/`, `docs/devops/`, `docs/security/` nem os aceites. O resíduo é o mesmo do projeto e fica com a BP-5: as construções listadas acima em "Fora do escopo", que o texto da linha não deixa ver.

**Condição (3) do dono: a mudança só aperta, ou o que aceita a mais.**
- Este delta só aperta. A exceção do dono saiu (`parecer_alheio_no_texto` virou `parecer_no_texto`, sem o teste de papel), e a regex ganhou `re.I`. As duas mudanças só somam recusas. Nada que barrava passou a liberar: as células alheias seguem barrando, e as duas fixtures que liberavam (`…-seguranca-variavel-security-libera` e `…-tech-lead-teto-reviews-libera`) viraram `-bloqueia`.
- O que fica mais caro para o uso legítimo, igual ao projeto: o dono não grava mais a própria pasta por variável no alvo, por `sh -c` nem numa linha acima do teto. A leitura de parecer para um caminho com variável (`cp docs/reviews/x.md $TMPDIR/r.md`, `forge-check parecer delta … > "$TMPDIR/d.txt"`) também dá rc 2 nos dois contextos. A saída é o caminho literal. É custo de uso, não é brecha.
- O que o item aceita a mais continua só o que o rótulo declara. Na volta, o parecer de outro papel commitado só com a pasta dele vale como anexo do portão pela forma do git, preso ao `commit:` igual ao `de` e à própria pasta (condição 1). Agora ele se apoia numa barreira de papel sem a brecha do A6.
- O resíduo declarado antes segue, e não vem deste delta: na sessão do Forge, `~/.forge-contrib/docs/pedidos/` e `docs/briefs/` não têm guarda de papel. Está com o Jarvis como item próprio.

## Riscos aceitos e ferramentas
Nenhum risco aceito. As três condições de segurança para o rótulo `afrouxa-regra` estão cumpridas neste head.

Sondas: o hook rodou pelo lançador de `tests/test_hooks.py` (`Fixture.montar` e `rodar`), em pastas temporárias. Para a coluna "em projeto", usei a mesma entrada com `.forge/versao` e sem `CLAUDE_PROJECT_DIR` de clone.

Suíte inteira: fica com o CI do PR. Não conferi o CI em `5376b86d`, porque o `gh` não lê credenciais no sandbox; o merge depende do CI verde.

Lacuna: gitleaks, semgrep, zizmor e actionlint estão fora do PATH. O delta não toca workflow nem dependência.
