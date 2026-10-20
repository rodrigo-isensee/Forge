---
tipo: review
contrato: 1
pedido: tl-1
branch: melhoria/tl-1
commit: 52d52218fa884e70d23dfb60066f19bc2a884fac
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-19
---
# Code review: TL-1 (um push por rodada de pareceres)

Diff revisado: `e9c81e0...52d5221` (4 arquivos, 5 inserções, 3 remoções): `agents/tech-lead.md`, `agents/qa-engineer.md`, `agents/security-engineer.md`, `changelog.d/tl-1.md`. Ferramentas: nenhuma rodada nesta revisão (só texto de agente e fragmento; a suíte de 865 testes é prova do autor, R-TETO).

## Contra o E1
- Local certo: a frase mudou na própria linha "Commite o parecer na branch revisada", onde a regra de push já estava. O parecer continua commitado só com o próprio arquivo e `git add` explícito; só o push passou a sair uma vez por rodada, quando o último gate do mesmo SHA termina.
- Conferência prévia pedida pelo E1: `forge-check pr` resolve o commit por `rev-parse` e `merge-base --is-ancestor` locais (`bin/forge-check`, `cmd_pr`), sem consultar o remoto; por isso a regra vale para review, segurança e QA, e o texto avisa o caso da worktree vizinha (`git fetch` local). O hook `pre-push` só confere fast-forward, não presença de parecer.
- Texto curto: um acréscimo por arquivo, sem regra nova duplicada (a mesma frase repete o padrão já existente nos três agentes).
- Fragmento `changelog.d/tl-1.md` presente, neutro (R-NEUTRO), sem tocar `CHANGELOG.md` nem a versão.
- Invariantes: `tests/config.json` não foi tocado; nenhum trecho protegido saiu ou mudou. Nenhum teste referencia a frase alterada (grep em `tests/`).
- Critério de reversão e "Por que o existente não basta": não se aplicam (ajuste de redação de prática, sem mecanismo novo).

## Achados
- A1 (recomendado) agents/devops-engineer.md:18 · a mesma frase "para o parecer entrar no mesmo push da entrega" ficou sem a regra de rodada única; o parecer do devops também é gate da rodada. Alinhar numa próxima volta ou num cartão, sem bloquear este merge.
