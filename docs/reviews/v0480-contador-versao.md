---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-contador-versao
commit: 362b45ad31e23cc33af7abe42f7d08758ba7e37c
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-22
---
# Review: v0478 (E103.8, CONTADOR-DA-VERSAO, revalidação da volta única)

Revalidação (H3, R-REVIEW): li só `forge-check parecer delta docs/reviews/v0480-contador-versao.md`, intervalo fb4d5390..362b45ad; no domínio: `bin/forge-contador`, `changelog.d/v0480-contador-versao.md`, `skills/fluxo-do-pedido/SKILL.md`, `tests/mutantes/v0480-contador-versao{,-2,-3,-4,-5}.json`, `tests/test_forge_contador.py`. Parecer anterior: d0d01139 (reprovado no head fb4d5390, A1 e A2 bloqueantes).

Ferramentas citadas, sem refazer: `forge-check pr v0478` no head 362b45ad: classe C, sem a linha de tamanho acima do teto (A2 resolvido; 123 linhas não vazias no arquivo). Teste do item: `python3 -m unittest tests.test_forge_contador`, 24 testes, OK. Suíte inteira e mutação: CI do PR e QA.

Conferência dos achados anteriores:
- A1 resolvido: `entregues` (bin/forge-contador:51) cai, sem `changelog.d/`, na contagem dos PRs mesclados (merge `#n` ou squash `(#n)`) por first-parent desde a última marca, e diz "sem contagem" quando há commits e nenhum é de PR. Sonda S1 refeita: `1.2.1: 3 de 20`. No Forge, `--raiz /workspaces/Forge` segue `0.47.15: 6 de 20`.
- A2 resolvido: a ferramenta não aponta mais o teto H1.
- A3 resolvido: a guarda da linha separadora ganhou mutante (`-4.json`), e cada guarda nova (`any(nomes)`, `assuntos and not prs`, `historico and not quadro`, `OverflowError`, UTF-8) tem mutante e teste do ramo de falha.
- A4 resolvido: a skill cita `forge-contador` pelo PATH do plugin.

## Sondas
- S1 · repo develop com tag v1.2.0 e 3 commits "feat: item N (#N)", sem changelog.d; `forge-contador --raiz <repo>` · espera: 1.2.1: 3 de 20 · obtido: 1.2.1: 3 de 20
- S2 · repo com tag v1.0.0 e 1 commit sem PR, sem changelog.d · espera: sem contagem · obtido: 1.0.1: sem contagem de 20
- S3 · repo com tag v2.0.0 e nenhum commit depois · espera: 2.0.1: 0 de 20 · obtido: 2.0.1: 0 de 20

## Parecer
Aprovado no head 362b45ad. O delta fecha os quatro achados sem abrir defeito novo no domínio.
