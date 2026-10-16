---
tipo: review
contrato: 1
pedido: processo-pronto-develop-instancias
branch: melhoria/processo-pronto-develop-instancias
commit: 694edc7a2d1a2d5574a541cfc06f3941b88bec30
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-15
---
# Code review: processo (definição de pronto, develop antes do review, instâncias por gargalo), volta 1

Escopo: E2 do pedido `k2-e-processo` (`~/.forge-contrib/docs/pedidos/k2-e-processo.md`), com S-11 e TA-2. Diff da entrega inteira sobre a develop atual, `930d6bb...694edc7`: `agents/jarvis.md`, `agents/tech-lead.md`, `bin/forge-check`, `hooks/pesado.py`, `docs/regras/R-FLUXO.md`, `docs/regras/R-REVIEW.md`, `docs/regras/R-WIP.md`, `skills/engineering-practices/SKILL.md`, `skills/kanban-scrum/SKILL.md`, `tests/config.json`, `tests/test_forge.py`, `tests/test_hooks.py`, `changelog.d/processo-pronto-develop-instancias.md`. Diff da volta: `5f3a6c4..694edc7`. Revisor independente; não escrevi a branch. Substitui o parecer anterior (reprovado sobre `61b4382`).

O `pedido:` do frontmatter passa de `k2-e-processo` para `processo-pronto-develop-instancias`, o mesmo do parecer de segurança e do nome do arquivo: `forge-check pr` casa os pareceres pelo campo `pedido`, e o hook `parecer` junta os pedidos de todos os pareceres da branch (`pedidos_da_branch`); com dois valores, cada pedido ficaria sem o parecer do outro e o `gh pr ready` seria barrado.

## Conferido (sem rodar a suíte completa; o autor a rodou, 657 OK, e o QA roda de novo)
- Classes rodadas: `python3 -m unittest tests.test_forge.Neutralidade tests.test_forge.NeutralidadeDoNucleo tests.test_forge.RegrasInviolaveis tests.test_forge.AntiDuplicacao tests.test_forge.RegrasComId tests.test_forge.ForgeCheck tests.test_hooks.Hooks.test_suite_do_forge_e_pesada tests.test_changelog` → `Ran 73 tests ... OK`.
- `git diff --numstat 930d6bb..HEAD -- tests/config.json` → `23	0`: só acréscimos sobre a develop. As 6 remoções de `bad3edd..HEAD` vêm da K1 (develop `930d6bb`), não desta branch.
- `git merge-base --is-ancestor 930d6bb HEAD` → contém. Resolução do conflito em `agents/jarvis.md` (merge `fbb1dd6`, item 5 do prompt-padrão): mantém o formato `· espera: ...` do PQ `cmd` da K1 e acrescenta "rodado da raiz do repositório" e "documentação afetada ... atualizada"; o item 3 e o parágrafo do conferente ficaram como na develop. Nada aprovado se perdeu.
- Contrato novo do `forge-check kanban`, conferido também à mão num quadro temporário: 2 cartões do mesmo agente com `worktree:` distintos e `{"teto_agentes": 1}` → barra (`limite 1 instâncias por agente (R-WIP, R-TETO)`, rc=1); com `{"teto_agentes": 2, "teto_maximo": 5}` → passa (rc=0). Limite = min(3, `teto_maximo`, `teto_agentes`), lido só do arquivo, sem medir carga; acima dele, barra mesmo com worktrees distintos; até ele, barra sem o campo ou com nome repetido. `hooks/quadro.py` chama `cmd_kanban` e herda a regra sem mudança.
- Contrato novo do hook `pesado`: `PESADOS_DO_FORGE` só se soma quando `e_clone_do_forge(raiz)` (manifesto do Forge e sem `.forge/versao`); em projeto continua valendo só `pesados` da config (o teste cobre os dois lados, e também `unittest tests.test_forge` e `echo ... discover`, que não são pesados). A trava fica em `.forge/run/` da cópia principal (`Hook.run`), compartilhada pelas worktrees de `~/.forge-contrib/wt/`; o código da branch não grava nada novo em `.forge/` do repositório.
- Neutralidade (`R-NEUTRO`): o comando da suíte em `hooks/pesado.py` é do próprio Forge e só vale no clone dele; textos de regra e skills sem nome de projeto nem ferramenta de stack. Testes `Neutralidade` verdes.
- Fragmento `changelog.d/processo-pronto-develop-instancias.md`: nome = branch sem prefixo, `### Alterado`, cobre forge-check, hook e invariantes; `CHANGELOG.md` intocado.
- Commits: Conventional Commits em português, um por item, com trailers.
- Parecer de segurança `docs/security/processo-pronto-develop-instancias.md` (`commit: 694edc7...`, `parecer: aprovado`, ainda não versionado na worktree): citado, não refeito. Sem pipeline, contêiner nem IaC: sem parecer de devops.

## Achados do review anterior e itens do brief da volta
| Item | Onde | Situação |
|---|---|---|
| Bloqueante 1 / item 1 / I2 | `R-FLUXO.md:24-26` (`## No Forge e no projeto`); `tech-lead.md:23-24` (`## No Forge e nos projetos`), com `**uma vez, antes do review**` literal e citando `R-FLUXO` | resolvido |
| Item 2 (M1) | `bin/forge-check:179-210`; `R-WIP.md:10`; `jarvis.md:46`; testes `test_instancias_worktrees_distintas_passam`, `test_cartoes_sem_worktree_barram`, `test_instancias_acima_do_teto_barram`; invariante "1 cartão..." intacto | resolvido (ver recomendado 1) |
| Item 3 (M2) | `R-FLUXO.md:26` e `tech-lead.md:24`: patch que diverge invalida (`commit_vale`), quem resolveu não decide o alcance, quem deu o parecer revalida | resolvido |
| Recomendado 2 / item 5 (B1) | `R-WIP.md:11`: teto de agentes, 2 worktrees, pesadas uma por vez, extras em trabalho leve | resolvido |
| Recomendado 3 / item 4 (M3) | `tests/config.json`: "sem folga no teto, a fila espera", o `R-TETO` inteiro, o máximo de 3, "Depois do QA só se atualiza...", revalidação, pronto da raiz no prompt-padrão e na skill | resolvido |
| Item 6 (B2) | `R-REVIEW.md:12` (regra) e `R-WIP.md:11` (cita `R-REVIEW`) | resolvido |
| Recomendado 4 / item 7 (I1) | `engineering-practices/SKILL.md:30`: não abre rodada de review (regra 1), não conta como volta de `R-QA`, quem confere é o Jarvis pela `PQ-n` | resolvido |
| Item 9 (S-11) | `jarvis.md:37` (passo 5) e `kanban-scrum/SKILL.md:93` (seção de bugs e retrabalho, "Fluxo") | resolvido |
| Item 9b (TA-2) | `hooks/pesado.py:27-33,104-105`; `test_suite_do_forge_e_pesada` | resolvido |
| Item 10 | merge da develop `930d6bb` (`fbb1dd6`) | resolvido |
| Item 11 | fragmento atualizado | resolvido |

## Achados

### Bloqueia
Nenhum.

### Recomendado
1. `docs/regras/R-WIP.md:10` e `changelog.d/processo-pronto-develop-instancias.md:3` · problema: o texto diz "no máximo 3 ... menos se `teto_maximo` ... for menor", mas `teto_instancias` (`bin/forge-check:183-195`) também reduz o limite por `teto_agentes`. O código é mais estrito que a regra (não afrouxa nada), mas o texto único não descreve o comportamento real, e o caminho de `teto_agentes` não tem teste (`test_instancias_acima_do_teto_barram` só cobre `teto_maximo`). · sugestão: "menos se `teto_maximo` ou `teto_agentes` de `.forge/config.json` for menor" nos dois arquivos e um caso com `teto_agentes` no teste. Pode ir num próximo PR da fábrica; não pede nova volta desta entrega. · severidade: recomendado.

### Informativo
2. `docs/regras/R-WIP.md:10`: "a Obs. de cada cartão do agente traz `worktree: <nome>`", lido sozinho, parece obrigatório também com um cartão só; a frase seguinte ("Com mais de um cartão ... todos trazem o campo") e o código exigem só com mais de um. Coerente; pode ficar mais claro.
3. `hooks/pesado.py:23`: `timeout` não está em `LANCADORES`, então `timeout 600 python3 -m unittest discover` escapa da trava. Comportamento anterior à branch, vale para qualquer item de `pesados`.
4. A trava vive em `.forge/run/` da cópia principal de cada clone: as worktrees de `~/.forge-contrib/wt/` dividem a mesma trava, mas uma suíte no clone do dono e outra em `~/.forge-contrib` não se enxergam. Aceitável para o objetivo do TA-2 (as instâncias do time rodam em `~/.forge-contrib/wt/`).
5. `R-WIP` limita Code review e QA a 2 cartões por coluna; instâncias extras de revisor ou de QA não passam disso (já dito no review anterior; segue coerente).

## Veredito
**Aprovado.** O bloqueante e os recomendados do review anterior e os itens 1 a 11 e 9b do brief da volta estão resolvidos; os contratos novos do `forge-check kanban` e do hook `pesado` batem com o brief (limite 3 = diretório principal mais as 2 worktrees de `R-TETO`) e estão cobertos por teste; invariantes só acrescentam; neutralidade preservada. O recomendado 1 é ajuste de texto e de teste, sem risco de afrouxamento. Segue para o QA (`R-QA`). O PR leva o rótulo de protegido porque toca `bin/forge-check` (E3.4/E3.5).
