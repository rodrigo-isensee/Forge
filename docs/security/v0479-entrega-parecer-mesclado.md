---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-parecer-mesclado
commit: aebace7125b5873038e1c4ffefbb512cd7e111b2
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: A5, variável no alvo e linha sem leitura nas pastas de parecer (v0478 E50.13, revalidação)

Delta lido (`forge-check parecer delta`, `8cff35a0..aebace71`): no domínio, `hooks/conformidade.py` (`PARECER_NO_TEXTO`, `GuardaDaProva.parecer_alheio_no_texto`, o ramo novo de `prova_fora_de_projeto`), `docs/hooks.md`, as 13 fixtures `pp-sessao-forge-*` novas e o teste delas em `tests/test_hooks.py`. Fora do domínio, nada relido. `bin/forge-check` não mudou no delta. A rodada anterior está no git (`d1946709`, parecer no `8cff35a0`).

Gatilhos: controle do Forge (hook `conformidade`), afrouxa-regra com condições do dono (DECISÃO DO DONO 2026-11-20 10:59 e 13:21).

## Achados
- A6 (bloqueante) hooks/conformidade.py:3794 · na sessão do Forge, o dono de uma pasta de parecer passa livre na variável no alvo e alcança a pasta vizinha: `d=docs/security; echo x > $d/aceites/n.md` (seguranca) e `d=docs/reviews; echo x > $d/../qa/n.md` (tech-lead) liberam. Em projeto, as duas linhas são recusadas.

## Sondas
- S13 · hook conformidade, CLAUDE_PROJECT_DIR = clone do Forge, cwd = ~/.forge-contrib/wt/x, agent_type forge-python:python-backend, Bash `d=docs/reviews; printf x > "$d/n.md"` · espera: rc 2 · obtido: rc 2
- S15 · contexto da S13, agent_type forge:dev, Bash `f=docs/qa/n.md; echo x > $f` · espera: rc 2 · obtido: rc 2
- S16 · contexto da S13, agent_type forge:jarvis, Bash `d=docs/security/aceites; printf x > "$d/n.md"` · espera: rc 2 · obtido: rc 2
- S17 · contexto da S13, agent_type forge:security-engineer, Bash `d=docs/security; echo x > $d/aceites/n.md` · espera: rc 2 · obtido: rc 0 (em projeto: rc 2)
- S18 · contexto da S13, agent_type forge:tech-lead, Bash `d=docs/reviews; echo x > $d/../qa/n.md` · espera: rc 2 · obtido: rc 0 (em projeto: rc 2)
- S19 · contexto da S13, agent_type forge:qa-engineer, Bash `d=docs/qa; echo x > $d/../security/aceites/n.md` · espera: rc 2 · obtido: rc 0 (em projeto: rc 2)

## Detalhe dos achados
**Achados anteriores.**
- A1 e A2: seguem. O delta não toca `bin/forge-check`, então `:3020` (`revisado != de`) e `:3002` (cada tipo só na própria pasta, fora de `docs/security/aceites/`) estão como na rodada anterior.
- A3 e A4: seguem corrigidos. O delta não mexe nessas guardas.
- A5: corrigido para as formas que a correção mínima pedia. `parecer_alheio_no_texto` (`hooks/conformidade.py:3789-3796`) recusa a variável no alvo e a linha sem leitura quando a linha cita uma pasta de parecer de outro papel. S13, S15 e S16 dão rc 2. A correção mínima que eu pedi deixava o dono livre na própria pasta, e é por esse ponto que entra o A6.

**Matriz de papéis, refeita no hook real da branch** (lançador de `tests/test_hooks.py`, sessão do Forge, worktree em `~/.forge-contrib/wt/x`, HOME temporário):
- 9 papéis (`tech-lead`, `devops`, `qa`, `seguranca`, `jarvis`, `doc`, `dev` do núcleo, `dev` de stack e a sessão principal sem `agent_type`) × 5 pastas (`docs/reviews/`, `docs/qa/`, `docs/devops/`, `docs/security/`, `docs/security/aceites/`) × 16 formas: Write, Edit, Bash `>`, `cp`, `tee`, interpretador com `-c`, variável com o arquivo, variável com a pasta, `cd` antes, caminho absoluto, `..`, `git checkout -- <arq>`, `mv`, `sed -i`, `sh -c` e a linha que o hook não lê.
- Resultado: 720 casos. Nas 4 células do dono, os 64 casos liberam. Nas 41 células de papel não dono, os 656 casos barram.
- Dimensão nova, que a matriz não tinha: a variável que guarda a pasta do dono e alcança outra pasta a partir dela, por `/aceites/` ou por `/../<pasta>/` (S17, S18 e S19). Isso é o A6.
- Corpus de legítimos: liberam `git merge`, `pull --rebase`, `switch`, `stash pop`, `cherry-pick`, leitura (`cat`, `grep`, `git log`, `git diff`), `git add`, `commit` e push do parecer pela segurança, `git merge --no-ff` pelo Jarvis, `git worktree add`, a variável do dono na própria pasta e `f=src/x; echo x > $f`.
- Fora do escopo, e igual em projeto (rc 0 nos dois contextos, fica com a BP-5): `d=docs; echo x > $d/reviews/n.md`, `p=qa; echo x > docs/$p/n.md`, aspas ou barra no meio da pasta (`docs/'qa'`, `doc\s/qa`), `docs//qa`, `./docs/./qa`, `$(echo docs/qa)` e curinga (`docs/q?`, `docs/[q]a`).

**A6, caminho de ataque.**
- Quem: o dono de uma pasta de parecer, por atalho ou por alucinação. O `tech-lead` é o autor dos itens de hook do Forge, então ele é o sujeito da condição (2). De onde: a worktree em `~/.forge-contrib/wt/`. O que ganha: o `tech-lead` grava o parecer de QA (`$d/../qa/`); a segurança, ou o QA, grava o aceite de risco, que é do usuário (`$d/aceites/`, `$d/../security/aceites/`).
- Evidência: `hooks/conformidade.py:3794` libera o casamento quando o papel é dono da pasta citada no texto, mas o alvo real é outro. `PARECER_NO_TEXTO` casa `docs/security` sem o `/aceites` quando a variável guarda só a pasta-mãe. A docstring (`:3791`) e `docs/hooks.md` dizem "como no projeto", mas em projeto as linhas de S17 a S19, e a variável do dono na própria pasta, dão rc 2.
- Severidade: média (controle de processo interno; o aceite forjado contorna a decisão do usuário, `R-DECISAO`).
- Correção mínima, a mesma regra do projeto: na sessão do Forge, a variável no alvo e a linha sem leitura são recusadas quando a linha cita qualquer uma das cinco pastas, dono incluído: `docs/reviews/`, `docs/qa/`, `docs/devops/`, `docs/security/aceites/` e `docs/security/`. O dono grava a própria pasta pelo caminho literal (Write, Edit ou Bash sem variável no alvo), como em projeto. Isso também fecha `d=DOCS/QA; echo x > ${d,,}/n.md`, que libera no Forge e é recusado em projeto. Se a escolha for manter o dono livre, a alternativa é recusar também quando a linha tem `..` ou quando o dono de `docs/security/` cita `aceites`, mas essa via é mais frágil.
- Teste de abuso: S17, S18 e S19 como fixtures `pp-sessao-forge-*` com rc 2. Com a correção que recomendo, `pp-sessao-forge-wt-seguranca-variavel-security-libera` passa a `-bloqueia`, e a forma literal do dono segue com rc 0.
- Esforço: P. Dono: tech-lead (hook; `tests/hooks/` só em `melhoria/*`).

**Condição (1) do dono, os dois apertos entraram.** Sim, e o delta não os toca. O parecer tem de citar exatamente a versão revisada (`bin/forge-check:3020`), e cada tipo só vale na própria pasta, fora dos aceites (`bin/forge-check:3002`).

**Condição (2) do dono, o autor não grava nas pastas de parecer na sessão do Forge.** Ainda não posso confirmar por escrito. As 41 células de papel não dono barram nas 16 formas, e a variável e a linha sem leitura agora barram (S13, S15 e S16). Mas o dono de uma pasta alcança a pasta vizinha pela variável (A6), e o `tech-lead`, autor dos itens de hook, grava `docs/qa/` assim (S18).

**Condição (3) do dono: a mudança só aperta, ou o que aceita a mais.**
- Este delta só aperta. `recusa_do_estado` ganha um `or` que só soma recusas, e `prova_fora_de_projeto` ganha um `barrar` novo. Nada que barrava passou a liberar: as 656 células alheias barram, e S13, S15 e S16 saíram de rc 0 para rc 2.
- Ele também aperta o que é legítimo, do mesmo jeito que o projeto já faz. Na sessão do Forge, a linha com variável no alvo que cita pasta de parecer alheia agora é recusada, mesmo quando só lê o parecer. Exemplos: `cp docs/reviews/x.md $TMPDIR/r.md`, `git show HEAD:docs/qa/x.md > $TMPDIR/q.md`, `forge-check parecer delta docs/security/x.md > "$TMPDIR/d.txt"` (Jarvis) e o laço `for f in docs/reviews/*.md; ...> "$TMPDIR/c.txt"`. Em projeto, as quatro dão rc 2. A saída é o caminho literal da pasta temporária. É custo de uso, não é brecha.
- O afrouxamento do item continua o que o rótulo declara: na volta, o parecer de outro papel commitado só com a pasta dele sai como anexo do portão pela forma do git. Ele depende da barreira de papel, que tem a brecha do A6.
- O resíduo declarado na rodada anterior segue: na sessão do Forge, `~/.forge-contrib/docs/pedidos/` e `docs/briefs/` não têm guarda de papel. Ele não vem deste delta e está com o Jarvis como item próprio.

## Riscos aceitos e ferramentas
Nenhum risco aceito. O rótulo `afrouxa-regra` segue condicionado ao A6 neste PR (condição (2)).

Sondas: o hook rodou pelo lançador de `tests/test_hooks.py` (`Fixture.montar` e `rodar`), em pastas temporárias. Para a coluna "em projeto", usei a mesma entrada com `.forge/versao` e sem `CLAUDE_PROJECT_DIR` de clone.

Suíte inteira: fica com o CI do PR. Não conferi o CI em `aebace71`, porque o `gh` não lê credenciais no sandbox.

Lacuna: gitleaks, semgrep, zizmor e actionlint estão fora do PATH. O delta não toca workflow nem dependência.
