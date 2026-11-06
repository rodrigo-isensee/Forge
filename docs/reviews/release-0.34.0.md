---
tipo: review
contrato: 1
pedido: release-0.34.0
branch: melhoria/release-0.34.0
commit: 7ce2cd98054e50f7713c917799543a2f9e5d5c72
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-06
---
# Review: release-0.34.0

Review da leva da 0.34.0 contra a main 0.33.0 (`3e148a0..7ce2cd9`): os 8 PRs da develop 3011d84 (#449 a #456), o commit de release b34410b e a correção 7ce2cd9. Cada PR já passou pelos próprios portões; aqui só a coerência da leva (E1, E2, E3), sem refazer o review de cada um.

## Achados
- A1 (recomendado) CHANGELOG.md:10 · resolvido em 7ce2cd9: as 5 entradas já publicadas na 0.33.0 saíram da seção 0.34.0; comparação das linhas `- ` das duas seções: 0 iguais (era bloqueante na rodada de b34410b).
- A2 (recomendado) CHANGELOG.md:10 · resolvido em 7ce2cd9: PERMISSAO-AGENTES-MD ficou numa entrada só, a que diz o que a skill diz (avisar quando a regra não estiver configurada).
- A3 (recomendado) CHANGELOG.md:26 · resolvido em 7ce2cd9: ACHADO-TETO-DOC ficou só na entrada que cobre security-engineer e qa-engineer.
- A4 (recomendado) CHANGELOG.md:15 · segue: o PR homolog → main (E1.7) deve destacar no corpo as entradas que afrouxam controle ou mudam texto protegido (BRIEF-HEAD-LOCAL, BRIEF-MENSAGEM-LIMPA em R-BRIEF, VOLTA-ETAPA-NOVA).

## Parecer
Aprovado no head `7ce2cd9`. A rodada anterior (head `b34410b`, commits `763210a` e `62021d6`) reprovou por A1; a correção `7ce2cd9` (volta do review) é só texto do `CHANGELOG.md`.

**Revalidação por delta.** `bin/forge-check delta --parecer docs/reviews/release-0.34.0.md`: intervalo `b34410b..7ce2cd9`, `"CHANGELOG.md" +0 -7`, linhas 10, 14, 17, 31 e 47. Lido só esse delta: saíram as 5 entradas do A1 (ATO-GITHUB-ENTREGA, QA-TESTE-E-PARECER-SEPARADOS, TEMPO-B2, CONF-MERGE-APOS-SQUASH, CONFERIDA-DESDE-POR-BRANCH), a segunda PERMISSAO-AGENTES-MD (A2) e a ACHADO-TETO-DOC parcial (A3); nada entrou. Seção 0.34.0 sem entrada repetida dentro dela nem com a 0.33.0. Já lido na rodada anterior, sem mudança no delta: o escopo da leva, os arquivos tocados por mais de um PR, versões e manifestos (abaixo). `bin/forge-changelog conferir-release`: "ok: changelog.d/ sem fragmentos pendentes". `python3 -m unittest tests.test_changelog tests.test_forge.Manifestos`: 56 testes, OK, em `7ce2cd9`.

**Escopo da leva.** `git log 3e148a0..b34410b` traz exatamente os 8 PRs do E1 (#449 a #456: TESTES-SEM-CLAUDE-ANCESTRAL, L09, pilha de hooks, estoques A, B e C, BHL, L10) e o commit de release; nada fora do escopo confirmado. O TESTES-NO-SANDBOX ficou para a 0.35, como o dono decidiu em 2026-11-05 14:59.

**Arquivos que mais de um PR tocou** (lidos só onde se juntam):
- `bin/forge-check` (#450, #453, #456): trechos disjuntos (`cmd_brief_mensagem`; `remoto_da_branch`/`estado_do_commit`; `gerar_volta`/`conferir_volta`). Sem conflito lógico.
- `docs/regras/R-BRIEF.md` e `agents/conferente.md` (#450, #453): a mensagem só com caminho e hash, um bloco por mensagem (#450), e o head local à frente do remoto só com pareceres nas etapas review e segurança (#453) se somam; nenhum contradiz o outro.
- `hooks/parecer.py` (#451, #452): a leitura das formas que o shell roda (#451) e as dicas de Write/Edit nas recusas de heredoc (#452) mexem em pontos diferentes; o #452 declara que nada passa a ser liberado.
- `bin/forge-testes` (#450, #452, #454, #456): `-k`, aviso cedo do MAPA e módulo sem mapa (#452) mais entradas de mapa dos demais.
- `.github/` (#455): parecer próprio do devops (E1.4), não refeito aqui.

**CHANGELOG e versão (E2, E3).** `bin/forge-changelog conferir-release`: "ok: changelog.d/ sem fragmentos pendentes"; `## [Não publicado]` vazio; os 8 fragmentos removidos estão na seção 0.34.0 (as 5 repetidas do A1 vinham do próprio fragmento lote-l10 e saíram em 7ce2cd9). Versão 0.34.0 em `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json`; o `marketplace.json` não carrega versão. Minor está certo: melhorias compatíveis e correções; a troca do runner para ubuntu-26.04 é do CI do Forge, não dos projetos.

**Testes rodados (D-5, só o que o commit de release toca):** `python3 -m unittest tests.test_changelog tests.test_forge.Manifestos` (56 testes, OK). A suíte inteira é do QA (E1.5); o push de b34410b rodou 1119 testes OK.

**Outros portões:** QA (E1.5) tem parecer próprio; não refeito aqui. A4 é recomendação e não devolve; segurança e devops ficam pulados nesta release pela decisão do dono de 2026-11-06 13:16.
