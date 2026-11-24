---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-teto-fora-desenho
commit: 2234208a6e338811ee6f658b8ad6be1372146c2d
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 · desenho TETO-FORA-DO-GIT (E159.2, PR #842)

Review do head 2234208a, base develop 789fc141. Diff: `docs/propostas/teto-fora-do-git.md` (novo, 84 linhas) e o fragmento `changelog.d/v0480-teto-fora-desenho.md`. Classe T, só texto: sem código, guarda nem mutante. Testes dos arquivos tocados: `test_changelog` e `test_clareza`, 100 testes, OK; a suíte inteira fica no CI do PR.

## Achados
- A1 (bloqueante) docs/propostas/teto-fora-do-git.md:36 · o leitor único lê `raiz_declarada()` (`CLAUDE_PROJECT_DIR`), que não existe no Bash nem no terminal do dono (S1; `hooks/_comum.py:147-148`): `forge-check`, `suite-partes` e `forge-ritmo` não acham o `limites.json`, e a C1 (e) e (f) não fecham. Diga a raiz dos scripts sem a sessão.
- A2 (recomendado) docs/propostas/teto-fora-do-git.md:20 · a linha "ficam" omite leitores do `config.json` na develop: `arquivos_do_forge_no_git` (`bin/forge-init:233-240`), `caminhos_extra` em `templates/projeto/.githooks/pre-push:231-248`, `hooks/doutor.py:305` e `hooks/meta.py:72`, e a mensagem de `hooks/conformidade.py:4195`.
- A3 (recomendado) docs/propostas/teto-fora-do-git.md:47 · a C2 não diz que o modelo `templates/projeto/.forge/config.json` perde `pesados` e `ritmo`, e `Hook.config` o usa como base dos padrões (`hooks/_comum.py:2652`); "padrões do modelo" (:37) fica sem fonte. Diga de onde vêm os padrões depois da C1.
- A4 (recomendado) docs/propostas/teto-fora-do-git.md:68 · o argumento da D1 está invertido: `git clean -fdx` apaga justamente os ignorados (`-x`); só o `denyWrite` protege, e só dentro do sandbox. Corrija o motivo; a recomendação (a) se sustenta pelos outros dois.

## Sondas
- S1 · `echo "CPD=${CLAUDE_PROJECT_DIR:-<vazio>}"` no Bash da sessão · espera: a raiz da sessão, para o leitor da linha 36 achar o arquivo · obtido: `CPD=<vazio>`

## Conferência pedida no brief
- **Leitores do `.forge/config.json` contra a develop:** `git grep -n 'config\.json' 789fc141 -- hooks bin scripts templates/projeto .claude/settings.json .gitignore` e o grep das chaves (`teto_agentes`, `piso_memoria_gb`, `pesados`, `expiracao_horas`, `ritmo`, `.config()`). Todos os leitores das chaves que saem estão na tabela (`Hook.config`, `agentes`, `pesado`, `forge-check` 490-503/4745/4760-4771, `suite-partes:259`, `forge-ritmo`, `forge-init`); as linhas citadas conferem no head. Faltam só leitores de chaves que ficam (A2). `vigia.py` e `forge-pesado` citam `expiracao_horas` só em texto ou pela `Hook.config`.
- **Decisão do dono de 19/11 08:28 (b):** `docs/pedidos/v0478.md:782`, "b: o teto vai para um arquivo fora do controle de versão". O desenho a segue (§3) e cita a de 08:28 (a), prova no sandbox real, como cartão à parte (§8, linha 783 do pedido).
- **Decisões com recomendação:** D1 a D4 trazem opções e "Recomendo" com motivo; a D1 com o motivo a corrigir (A4).
- **R-DECISAO:** critério de reversão com prazo, como e medida (§5); cada fatia diz se é trava e qual sai (regra do dono de 21/11, item 3). Custo zero (`R-CUSTO`).

## Parecer
Reprovado por A1. O desenho segue a decisão (b), cobre os leitores das chaves que saem e tem reversão e recomendações; mas a peça central, o leitor único pela raiz da sessão, não funciona para os três scripts que a tabela manda importá-lo: no Bash e no terminal não há `CLAUDE_PROJECT_DIR` (S1), e o `forge ritmo` roda no terminal do dono (linha 39). Sugestão: para os scripts, a raiz é a cópia principal do diretório comum do git (`diretorio_comum`, `hooks/_comum.py:153`), como o `bin/forge-copia` acha o projeto de dentro de uma cópia; e a C1 ganha o caso "fora da sessão". A2 a A4 são texto e viram cartão se não entrarem na volta.
