---
tipo: review
contrato: 1
pedido: release-0.42.0
branch: melhoria/release-0.42.0
commit: 7a189d413dce70cf200d74f0a4a29d97fd2d704c
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-07
---
# Review: release-0.42.0

Review da leva da 0.42.0 contra a main 0.34.0 (`a74c752..7a189d4`): os PRs #460 (brief-forma-aceita), #461 (push-parecer-ja-no-remoto) e #462 (uniao-035-042, o lote 0.35 a 0.42) da develop `a64c99a` e o commit de release `7a189d4`. Cada PR já passou pelos próprios portões; aqui só a coerência da leva (E1, E2, E3), sem refazer o review de cada um. Revisor sem autoria na leva.

## Achados
- A1 (recomendado) CHANGELOG.md:57 · entrada parcial de EST-M4: diz que a classificação de delta de texto entra "ainda sem uso", mas a linha 59 da mesma seção a põe em uso; na release o "ainda sem uso" fica falso. Sugestão para PR seguinte (ou na própria release, se o autor quiser): juntar a 57 na 59, como foi feito com as parciais de ACELERA-P2 neste commit.
- A2 (recomendado) CHANGELOG.md:48 · o PR homolog → main (E1.7) deve destacar no corpo as entradas que afrouxam controle ou mudam fronteira: pre-push que não roda a suíte com o remoto já no commit (48), parecer que não envelhece por delta de texto (59, afrouxa R-QA e R-REVIEW), `scripts/arvore-testada.py` que decide pular a suíte (34) e o teste-oráculo que muda a fronteira de escrita de um papel (12).

## Parecer
Aprovado no head `7a189d4`. Nenhum bloqueante; A1 e A2 são recomendações e não devolvem.

**Escopo da leva (E1).** `git log --first-parent a74c752..7a189d4`: exatamente os merges #460 (`86724d7`), #461 (`bb45aac`), #462 (`a64c99a`) e o commit de release `7a189d4`; nada fora do escopo. 224 arquivos, +12661 -215. Pareceres de cada PR aprovados e ainda válidos para o head mesclado: entre o commit de cada parecer e o head do PR só entraram pareceres (`9e87a91..979c372`: os 4 pareceres da uniao-035-042; `7374443..5e1370b`: pareceres da brief-forma-aceita; `d2460c9..a8fba0e`: pareceres da push-parecer-ja-no-remoto). Review, segurança, devops e QA da uniao-035-042 aprovados em `9e87a91`.

**Commit de release (E2).** Toca só `CHANGELOG.md`, os dois `plugin.json` e remove `changelog.d/brief-forma-aceita.md` e `changelog.d/uniao-035-042.md`. O fragmento do #461 (`push-parecer-ja-no-remoto.md`) já tinha sido juntado no `uniao-035-042.md` pelo `109ecb1`, e a entrada PUSH-PARECER-JA-NO-REMOTO está na seção (CHANGELOG.md:48). `bin/forge-changelog conferir-release`: "ok: changelog.d/ sem fragmentos pendentes"; `## [Não publicado]` vazio. Seção 0.42.0 com 62 entradas: nenhuma linha `- ` repetida dentro dela nem igual a uma da 0.34.0 (`comm` das linhas ordenadas: 0); nenhum ID da seção (padrão `XXX-YYY`) aparece nas seções antigas. IDs com mais de uma entrada (EST-M4, PAR-P2, M15, LAC-L2, ACELERA-P2) descrevem passos diferentes, salvo a parcial do A1. Sem seções intermediárias 0.35 a 0.41, como decidiu o dono (17:29).

**Versão (E3).** 0.42.0 em `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json`; o `marketplace.json` não carrega versão. Minor está certo: melhorias compatíveis e correções, sem quebra de contrato dos projetos.

**Testes rodados (D-5, só o que o commit de release toca):** `python3 -m unittest tests.test_changelog tests.test_forge.Manifestos`: 56 testes, OK, em `7a189d4`. A suíte inteira é do QA (E1.5) e do CI do PR; o push de `7a189d4` rodou 1190 testes afetados OK, 26 pulados.

**Outros portões:** segurança (E1.3), devops (E1.4, a leva toca `.github/`) e QA (E1.5) têm parecer próprio; não refeitos aqui.
