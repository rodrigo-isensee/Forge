---
tipo: review
contrato: 1
pedido: limpeza-pos-merge
branch: melhoria/limpeza-pos-merge
commit: 4e19ca0
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Parecer de autor: limpeza depois do merge

Escopo: `docs/regras/R-FLUXO.md` (passo "Depois do merge"), citações em `agents/tech-lead.md`, `agents/jarvis.md` e `skills/contribuir-com-o-forge/SKILL.md`, invariante novo em `tests/config.json` e linha em `[Não publicado]` do `CHANGELOG.md`.

Conferido: 250 testes verdes; `scripts/validar-plugin.sh` passa. Sem mudança em hooks, catraca ou `.github/`. O invariante só acrescenta proteção, então não exige rótulo. Texto sem termos de projeto (`R-NEUTRO`) e sem custo (`R-CUSTO`).

Parecer de autor, feito pelo mesmo agente que escreveu a mudança; o review independente fica a cargo do `tech-lead` no PR.

## Review independente
Revisor: `forge:tech-lead`, segunda leitura sobre o commit 4e19ca0.

- A regra em `R-FLUXO` é clara e proíbe apagar `develop`, `homolog` e `main`; cobre remota, worktree e branch local, na ordem certa, e trata o "Device or resource busy" com `git worktree prune` para o dono.
- Os invariantes protegem o título da regra, a proibição das três branches e o comando `git worktree prune`.
- `tech-lead`, `jarvis` e `contribuir-com-o-forge` citam `R-FLUXO`, "Depois do merge", numa frase curta, sem repetir os comandos (ADR 0002).
- 250 testes verdes no checkout do PR. Checks do CI verdes, com os testes estruturais ainda pendentes na hora da leitura. `pr-texto` passou.
- Achados: nenhum que bloqueie.

Parecer: aprovado.
