---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/f22-release-v2
commit: 6f515746d02de6ec78a9e591043ba147e49fd3dc
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-04
---
# Review: versao-033 (F22, PR de release)

## Achados
- A1 (recomendado) docs/regras/R-FLUXO.md:15 · o PR para a main também roda bateria, segredo e parecer (ci.yml); "os checks são" só dois é incompleto; escrever "entre eles" (R-FLUXO).
- A2 (recomendado) tests/config.json:421 · nenhum invariante cobre "um só por candidato" nem "nunca --base"; sugerir um em PR próprio (R-FLUXO).

## Parecer
Aprovado. Só texto, 5 arquivos, 5 linhas de .md (M14 não conta). Conferido contra `ci.yml` (Nada pula degrau, versão e CHANGELOG, `main` só da `homolog`), `release.yml` (só após merge do usuário) e `bin/forge-fechar` (recusa base main, R-MAIN): batem. Nenhuma regra com ID contradita; R-MAIN e R-DECISAO preservadas. Conflito em `agents/tech-lead.md`: diff contra a develop é só a linha nova; texto atual preservado. Fragmento presente. Devops aprovado (21c31c3), citado, não refeito. `test_forge.py` e `neutralidade.py`: rc=0.
