---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-adr0008-link-sessao
commit: 7dc47a7e908a2c3feafe0e9ab06c7c48bf670f86
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 (E172.13, PR #856, emenda da ADR 0008)

## Achados
- A1 (recomendado) docs/adr/0008-governanca-de-contribuicoes.md:72 · o gitleaks não acha o link de sessão com as regras padrão, nem lê corpo de PR; a varredura do item (b) pede regra própria do gitleaks ou um `git log --grep` e `gh pr list --json body` com o padrão do link; dizer qual no dia do gatilho
- A2 (recomendado) docs/adr/0008-governanca-de-contribuicoes.md:95 · o C3 do desenho BP10 tem também a linha em `## Regras da fábrica` de templates/projeto/CLAUDE.md e .claude/CLAUDE.md (repositório público sem o link de sessão); a emenda só põe a mensagem do hook como cartão: abrir cartão também para essa linha

## Parecer
Aprovado. Item só de texto: emenda datada da ADR 0008 (Estado, item (b) da seção 5 e seção nova no fim) e fragmento `changelog.d/v0480-adr0008-link-sessao.md`.

- Pedido: cumpre o E172.5 (DECISÃO DO DONO de 24/11, item 14 da triagem, BP10 C3, resposta "Sim."; conferido na ordem das 16 respostas do bloco do pedido). Nem mais nem menos: sem trava nova, o hook e o `scripts/verificar-contribuicao.sh` não mudam.
- ADR e regras: emenda datada no molde das anteriores, com Estado atualizado e critério de reversão (linha 97), como pede `R-DECISAO`. Não afrouxa nada: só acrescenta um item à varredura do gatilho.
- Fatos citados conferidos na fonte: `gh_trava` e a tupla `publico` existem em `hooks/conformidade.py` (linhas 3403 e 3409); F3 e C3 estão em `docs/propostas/bp10-higiene-segredo.md` (linhas 31 e 42).
- Commit: um só, Conventional Commits em português, mensagem com o motivo; fragmento de changelog presente.
- Suíte: CI do PR verde no head 7dc47a7e (run 45422852421: bateria, catraca, suíte 3.12 e 3.14 nas 5 partes, instalação, teto de pulados); não rerrodada. Sem teste novo nem guarda mudada: nada a mutar.
- Tamanho (H1): 0 linhas de código; só documentação.

Os dois achados são recomendações para cartão depois do merge; nenhum bloqueia.
