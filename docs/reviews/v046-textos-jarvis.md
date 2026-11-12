---
tipo: review
contrato: 1
pedido: v046
branch: melhoria/v046-textos-jarvis
commit: be5bb7ee32898578994ab389c8b257cf54ba7034
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-12
---
# Review: v046 (E21.2, textos do Jarvis)

Diff lido: `origin/develop...be5bb7ee` (base a1318e88), 4 arquivos, 18 linhas a mais e 16 a menos, só texto (`agents/jarvis.md`, `docs/regras/README.md` no parágrafo R-WIP, `skills/trabalho-em-paralelo/SKILL.md`, fragmento `changelog.d/v046-textos-jarvis.md`). Revisor: instância que não fez a entrega (E21.1). Fontes conferidas: diretrizes 18 e 19 em `docs/diretrizes-do-dono.md` (~/.forge-contrib) e os cartões DIRETRIZ-18-PARALELO e DIRETRIZ-19-ANDA-SOZINHO.

Ferramentas (citadas, não refeitas): `tests.test_orcamento_instrucao` 8 testes OK; `tests.test_metricas_texto` 2 testes OK (rodados um por vez no be5bb7ee, R-TETO).

## Achados
- A1 (recomendado) skills/trabalho-em-paralelo/SKILL.md:19 · a espera com run_in_background contradiz a regra 2 da skill esperar-estado (não usar run_in_background para esperar); dizer que vale para o Jarvis e que o subagente segue esperar-estado, ou ressalvar lá
- A2 (recomendado) skills/trabalho-em-paralelo/SKILL.md:19 · a pausa por limite de uso perdeu 'nada novo é disparado', 'grave onde parou' e o retomar em segundo plano; a frase ficou sem verbo e lê como lista (mesmo ponto do A2 da segurança)
- A3 (recomendado) skills/trabalho-em-paralelo/SKILL.md:19 · o laço until não traz o prazo no próprio comando (mesmo ponto do A1 da segurança); sugerir a forma com contador ou deadline
- A4 (recomendado) docs/regras/README.md:29 · da diretriz 18 faltam o 'sem ela, instância nova com o mesmo brief' da volta e a medida (espera do item pronto até o portão; vagas livres com fila parada = zero)
- A5 (recomendado) skills/trabalho-em-paralelo/SKILL.md:10 · o corte de 'na junção' deixa 'se serializam: a segunda começa já', contraditório; a diretriz 18 diz que dois autores no mesmo arquivo vão juntos ou um espera o outro; alinhar a frase
- A6 (recomendado) skills/trabalho-em-paralelo/SKILL.md:17 · o corte de 'cerca de' e 'sem travar' faz as 150 linhas soarem como limite fixo; a decisão M14 diz orientação, não trava por volume

## Sondas

## Parecer
**Aprovado**, com seis recomendados para a volta única já prevista depois de E21.3 e E21.4.

Diretriz 18: o parágrafo R-WIP (`docs/regras/README.md:29`) diz uma instância por item à espera do mesmo papel, ao mesmo tempo, dentro do `R-TETO`; item independente com branch própria e sem arquivo em comum; volta à instância que fez; portão usa o CI do PR quando cobre; um por vez no arquivo comum, merge na `develop`, `KANBAN.md`, pipeline e mesmo módulo, ADR, modelo de ameaças ou tela; o "nunca revisa o que escreveu" já estava (`R-REVIEW`). A skill (`SKILL.md:11`) e o `agents/jarvis.md:49` repetem o essencial. Faltam o fallback da volta e a medida (A4). O cartão aponta `docs/regras/R-WIP.md`, que não existe desde aff98b17; o brief retificado aceita o parágrafo do README.

Diretriz 19: `agents/jarvis.md:49` e `SKILL.md:19` dizem anda sozinho, nunca pede para ser chamado, espera hora ou estado em segundo plano com prazo, enche as vagas; ao dono só decisão, rótulo, merge na `main` e comando em arquivo travado; medida zero "me chame"/"continue". Fiel ao texto do dono; A1 e A3 são de consistência com a skill de espera.

Frases cortadas no `jarvis.md`: "O time de agentes faz todo o resto e aprende com os próprios erros" (descrição), "como Jarvis" (a identidade está na frase anterior), "honesto" (coberto por `R-PROVA` e pela tabela pedido × entregue), "sozinhas" (o verbo "barram" segue) e o parêntese dos lotes (o conteúdo segue na skill, linhas 15 e 16): nenhuma carregava regra. Na skill, as podas de estilo mantêm o sentido, salvo A2, A5 e A6.

Neutralidade (`R-NEUTRO`): nenhum nome, regra de negócio ou stack de projeto no diff. Orçamento: jarvis.md no teto (7795/7795), sem folga para A1 a A6 nele; os ajustes cabem na skill e no README.
