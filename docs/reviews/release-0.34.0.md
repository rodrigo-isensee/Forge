---
tipo: review
contrato: 1
pedido: release-0.34.0
branch: melhoria/release-0.34.0
commit: b34410be1ab6e5a0f0a232447a6d0041f519c53d
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-06
---
# Review: release-0.34.0

Review da leva da 0.34.0 contra a main 0.33.0 (`3e148a0..b34410b`): os 8 PRs da develop 3011d84 (#449 a #456) e o commit de release. Cada PR já passou pelos próprios portões; aqui só a coerência da leva (E1, E2, E3), sem refazer o review de cada um.

## Achados
- A1 (bloqueante) CHANGELOG.md:16 · a seção 0.34.0 republica, com texto idêntico, 5 entradas já publicadas na 0.33.0 (linhas 16, 35, 36, 53, 54 = 59, 62, 63, 72, 73: ATO-GITHUB-ENTREGA, QA-TESTE-E-PARECER-SEPARADOS, TEMPO-B2, CONF-MERGE-APOS-SQUASH, CONFERIDA-DESDE-POR-BRANCH), vindas do fragmento lote-l10; tirá-las da 0.34.0, fica só o VOLTA-ETAPA-NOVA.
- A2 (recomendado) CHANGELOG.md:10 · PERMISSAO-AGENTES-MD aparece duas vezes (linhas 10 e 11, "exige" e "pode exigir") para uma linha só em skills/trabalho-em-paralelo/SKILL.md; deixar uma entrada, a que diz o que o texto da skill diz.
- A3 (recomendado) CHANGELOG.md:20 · ACHADO-TETO-DOC aparece duas vezes (linha 20, só security-engineer, e linha 29, security-engineer e qa-engineer); a 29 cobre a 20; deixar só ela.
- A4 (recomendado) CHANGELOG.md:18 · entradas que afrouxam controle ou mudam texto protegido (BRIEF-HEAD-LOCAL, linha 18; BRIEF-MENSAGEM-LIMPA em R-BRIEF, linha 33; VOLTA-ETAPA-NOVA, linha 34): o PR homolog → main (E1.7) deve destacá-las no corpo para o dono ver ao mesclar.

## Parecer
Reprovado, por A1: a seção `## [0.34.0]` diz como novas 5 mudanças que a 0.33.0 já entregou (o código delas está em `3e148a0`: `ato-github` e `entrega conferida` já existem em `bin/forge-check` da main). É defeito provado no artefato da release (ADR 0006: a seção da versão é o que ela traz). A correção é de texto, só no `CHANGELOG.md`, sem tocar código: remover as 5 linhas e, no mesmo commit, A2 e A3. A revalidação lê só o delta do `CHANGELOG.md`.

**Escopo da leva.** `git log 3e148a0..b34410b` traz exatamente os 8 PRs do E1 (#449 a #456: TESTES-SEM-CLAUDE-ANCESTRAL, L09, pilha de hooks, estoques A, B e C, BHL, L10) e o commit de release; nada fora do escopo confirmado. O TESTES-NO-SANDBOX ficou para a 0.35, como o dono decidiu em 2026-11-05 14:59.

**Arquivos que mais de um PR tocou** (lidos só onde se juntam):
- `bin/forge-check` (#450, #453, #456): trechos disjuntos (`cmd_brief_mensagem`; `remoto_da_branch`/`estado_do_commit`; `gerar_volta`/`conferir_volta`). Sem conflito lógico.
- `docs/regras/R-BRIEF.md` e `agents/conferente.md` (#450, #453): a mensagem só com caminho e hash, um bloco por mensagem (#450), e o head local à frente do remoto só com pareceres nas etapas review e segurança (#453) se somam; nenhum contradiz o outro.
- `hooks/parecer.py` (#451, #452): a leitura das formas que o shell roda (#451) e as dicas de Write/Edit nas recusas de heredoc (#452) mexem em pontos diferentes; o #452 declara que nada passa a ser liberado.
- `bin/forge-testes` (#450, #452, #454, #456): `-k`, aviso cedo do MAPA e módulo sem mapa (#452) mais entradas de mapa dos demais.
- `.github/` (#455): parecer próprio do devops (E1.4), não refeito aqui.

**CHANGELOG e versão (E2, E3).** `bin/forge-changelog conferir-release`: "ok: changelog.d/ sem fragmentos pendentes"; `## [Não publicado]` vazio; os 8 fragmentos removidos estão na seção 0.34.0 (fora o A1, que vem do próprio fragmento lote-l10, não da junção). Versão 0.34.0 em `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json`; o `marketplace.json` não carrega versão. Minor está certo: melhorias compatíveis e correções; a troca do runner para ubuntu-26.04 é do CI do Forge, não dos projetos.

**Testes rodados (D-5, só o que o commit de release toca):** `python3 -m unittest tests.test_changelog tests.test_forge.Manifestos` (56 testes, OK). A suíte inteira é do QA (E1.5); o push de b34410b rodou 1119 testes OK.

**Outros portões:** segurança (E1.3), devops (E1.4) e QA (E1.5) têm parecer próprio; não refeitos aqui. A2 a A4 são recomendações e não devolvem.
