---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-parecer-mesclado
commit: cdf62e0a29a1dabf34c600bb0b802e9fd65bcf55
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: E50.5, volta do parecer mesclado (v0478 E50.3, revalidação)

Delta lido (`forge-check parecer delta`, `48153733..cdf62e0a`): no domínio só `bin/forge-check` (`commit_so_de_parecer`, `parecer_mesclado_na_volta` e a frase da ajuda). Fora do domínio, lidos para a conferência: `tests/test_selo_e_entrega.py` (4 testes novos de abuso e o do rev-list), três specs de mutante e o fragmento do changelog. Por causa da DECISÃO DO DONO de 2026-11-20 10:59, li também a política e o caminho de decisão do hook `conformidade` (`hooks/conformidade.json:69-73`, `hooks/conformidade.py:3870-3900`), que ficam fora do delta.

Gatilhos: controle do Forge (`forge-check entrega`), afrouxa-regra com condições do dono (DECISÃO DO DONO 2026-11-20 10:59).

## Achados
- A3 (bloqueante) hooks/conformidade.py:3896 · na sessão do Forge (raiz no clone, pasta em ~/.forge-contrib/wt/*) o hook só avalia papel com lista: tech-lead, devops e dev gravam docs/reviews/, docs/qa/, docs/security/ por Write, Edit e Bash (72 de 72 liberadas). A condição (2) do dono falha.
- A4 (bloqueante) hooks/conformidade.json:69 · o autor do E50 é o tech-lead, dono de docs/reviews/: mesmo em projeto, a barreira por papel não separa o autor do revisor, e o review forjado com commit: = Desde sai anexo do portão (S12).

## Sondas
- S6 · volta: código N, depois um commit só de docs/security/x.md, aprovado, `commit:` = Desde, sem parecer anterior do portão; `forge-check entrega --etapa codigo` · espera: rc 1, fora do declarado · obtido: rc 0, `escopo: ok (anexo do portão: parecer de seguranca ...)`
- S12 · igual à S6 em docs/reviews/x.md (tipo review), depois do reprovado do portão sobre a 1.a entrega · espera: rc 1, fora do declarado · obtido: rc 0, `escopo: ok (anexo do portão: parecer de tech-lead commitado na volta só com parecer)`
- S9 · hook conformidade, CLAUDE_PROJECT_DIR = clone do Forge, cwd = ~/.forge-contrib/wt/x, agent_type forge:tech-lead, Write docs/qa/x.md · espera: rc 2 (barra) · obtido: rc 0 (libera)
- S10 · mesmo contexto, agent_type de agente de stack (papel dev), Bash `printf x > docs/reviews/x.md` · espera: barra · obtido: libera
- S11 · mesmo contexto, agent_type forge:devops-engineer, Edit docs/security/x.md · espera: barra · obtido: libera

## Detalhe dos achados
**Achados anteriores.**
- A1 (bloqueante, `commit:` aceitava qualquer sha do intervalo): corrigido em `bin/forge-check:3018` (`revisado != de` recusa). Refiz S1 e S3: rc 1, `fora do declarado no brief "docs/reviews/x.md"`. Testes: `test_autor_que_forja_aprovado_citando_o_proprio_codigo_segue_fora` e `test_reprovado_do_portao_trocado_por_aprovado_com_outro_commit_segue_fora`.
- A2 (recomendado, um commit forjava várias pastas e o aceite): corrigido em `bin/forge-check:3002` e `:3020` (só a pasta do tipo, fora de `docs/security/aceites/`). Sondas: S2 rc 1 (as três pastas fora), S7 (aceite junto) rc 1, S8 (parecer de tipo `review` gravado em `docs/security/`) rc 1. Testes: `test_um_commit_com_pareceres_de_varias_pastas_segue_fora` e `test_parecer_de_seguranca_com_aceite_no_mesmo_commit_segue_fora`.
- Outras conferências: o rev-list que falha recusa (`bin/forge-check:3022`, `test_rev_list_que_falha_recusa`). S4 (veredito trocado no mesmo `commit:`) rc 1. S5 (caso real, `commit:` = Desde, gravado pelo portão) rc 0: o conserto se mantém.

**Condição (1) do dono, os dois apertos entraram.** Sim, os dois, com testes de abuso (acima).

**Condição (2) do dono, o hook barra o autor pelo papel nas pastas de parecer.** Não se cumpre. Sondei o hook real da branch (`hooks/conformidade.py` pelo lançador de `tests/test_hooks.py`). Combinações: 4 papéis de autor (`forge:tech-lead`, `forge:devops-engineer`, um agente de stack (papel `dev`), `forge:dev`) × 3 pastas (`docs/reviews/`, `docs/qa/`, `docs/security/`) × 6 formas de escrita (Write, Edit, Bash `>`, Bash `cp`, Bash `git show >`, Bash `python3 -c open(...)`). Rodei em dois contextos:
- Projeto (raiz com `.forge/versao`): 69 de 72 barradas. As 3 liberadas são do tech-lead em `docs/reviews/` (Write, Edit e `python3 -c`); a política faz dele o dono dessa pasta.
- Sessão do Forge (raiz = clone do Forge sem `.forge/versao`, pasta em `~/.forge-contrib/wt/*`, o contexto deste pedido): 0 de 72 barradas. `identificar_sessao` devolve False, e `principal` só leva à guarda completa os papéis com lista (`aq`, `conferente`, `leitura`). Os demais caem em `prova_fora_de_projeto`, que só confere a prova da suíte (`hooks/conformidade.py:3896`); a ADR 0009, seção 6, desenha isso assim. O registro de autoria (PostToolUse) também não roda nesse contexto.

Isso corrige o parecer anterior, que citava o hook como "a barreira principal": no Forge essa barreira não existe.

**A3, caminho de ataque.** Quem: o agente autor da volta (alucinação ou atalho). De onde: a worktree em `~/.forge-contrib/wt/`. O que ganha: grava e commita sozinho `docs/<pasta>/<pedido>.md` aprovado, com `commit:` = Desde, e a conferência o aceita como anexo do portão (S6).
- Severidade: média (controle de processo interno, sem segredo nem dado pessoal).
- Correção mínima, no mesmo PR e antes do rótulo (condição do dono): na sessão do Forge, com a pasta corrente num clone ou worktree do Forge (`~/Forge`, `/workspaces/Forge` e `~/.forge-contrib/wt/*`), aplicar às pastas de parecer, para todo papel, a regra de caminhos protegidos por papel, nas ferramentas Write, Edit, MultiEdit, NotebookEdit e Bash. A lista inteira: `docs/reviews/` (só `tech-lead`), `docs/qa/` (só `qa`), `docs/devops/` (só `devops`), `docs/security/aceites/` (nenhum agente), `docs/security/` (só `seguranca`).
- Teste de abuso: S9, S10, S11 e a matriz acima (4 papéis × 4 pastas × Write, Edit e Bash) com rc 2. Corpus de legítimos: cada portão gravando a própria pasta, com rc 0.
- Esforço: M. Dono: tech-lead (política e hook; `hooks/conformidade.json` só muda em `melhoria/*`).

**A4, caminho de ataque.** Mesmo com a barreira de A3, o tech-lead é autor do E50.1 e do E50.5 e é o dono de `docs/reviews/`, e uma barreira por papel não distingue a instância autora da revisora. Um review forjado gravado só em `docs/reviews/`, com `commit:` = Desde, passa mesmo depois do reprovado do portão sobre a 1.a entrega (S12), porque a regra só olha a forma do git.
- Severidade: média.
- Correção mínima: em `parecer_mesclado_na_volta`, quando o papel do parecer (`PAPEL_DO_PARECER[tipo]`) for o papel do autor da entrega (o `Agente destino` do brief da volta), não aceitar pela forma do git. Exigir uma âncora que o autor não grava: uma linha do Jarvis no `## Histórico` com papel e sha do parecer, como o `parecer conferido`.
- Teste de abuso: S12 com autor tech-lead, rc 1; o caso real (portão de outro papel) segue com rc 0.
- Esforço: P. Dono: tech-lead.

**Condição (3) do dono, o afrouxamento que sobra, medido.** Com A1 e A2 corrigidos, a conferência aceita sem âncora uma forma só, que precisa de todos estes pontos:
- um commit (ou merge sem resolução à mão) que muda só a pasta do tipo, fora de `docs/security/aceites/`;
- frontmatter da pasta, da branch e do pedido, com veredito;
- `commit:` igual ao Desde;
- nenhum veredito diferente para o mesmo `commit:` desde o Base-sha.

Medida: das 9 sondas de `forge-check entrega` desta rodada, 8 são forjadas e 1 legítima. Das forjadas, 2 passam (S6 e S12, a mesma forma em duas pastas) e 6 são recusadas (S1, S2, S3, S4, S7, S8). A legítima (S5) passa.

Quem consegue produzir S6 e S12 hoje: no Forge, qualquer papel em qualquer pasta (A3); em projeto, só o tech-lead em `docs/reviews/` (A4).

O que fica fora do afrouxamento:
- o `forge-check pr` vê o aprovado forjado no Desde como desatualizado quando a volta muda código do domínio depois dele (conferido na rodada anterior);
- `veredito_trocado` e `pareceres_divergentes` pegam o forjado quando o portão já gravou um veredito para o mesmo Desde.

Com A3 e A4 corrigidos, S6 e S12 passam a exigir o papel dono da pasta numa instância diferente da autora, que é o que o dono pediu.

## Riscos aceitos e ferramentas
Nenhum risco aceito. O rótulo `afrouxa-regra` segue condicionado ao A3 e ao A4 no mesmo PR (DECISÃO DO DONO 2026-11-20 10:59).

Sondas: rodei `ParecerMescladoNaVolta` estendido fora da branch (22 testes verdes, entre eles os 5 novos do E50.5) e o hook pelo lançador de `tests/test_hooks.py`, em repositórios temporários com HOME temporário.

Suíte inteira: fica com o CI do PR. Não conferi o estado do CI em `cdf62e0a` (o `gh` não lê credenciais no sandbox).

Lacuna: gitleaks, semgrep, zizmor e actionlint fora do PATH; o delta não toca workflow nem dependência.
