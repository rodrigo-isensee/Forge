---
tipo: review
contrato: 1
pedido: v046
branch: melhoria/v046-textos-jarvis
commit: cf172a29279f27ac29e1a4cfe843efd35057ea51
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-12
---
# Review: v046 (E21.2 e revalidação E21.6, textos do Jarvis)

Revalidação por delta (E21.6), instância que não fez a entrega nem o review E21.2. Delta lido: `forge-check parecer delta docs/reviews/v046-textos-jarvis.md` deu o intervalo `be5bb7ee..afdaa3ab`, com quatro arquivos no domínio: `changelog.d/v046-textos-jarvis.md`, `docs/regras/README.md`, `skills/trabalho-em-paralelo/SKILL.md` e `tests/test_jarvis_nucleo.py`. O `agents/jarvis.md` não mudou no delta. Lido por `git diff be5bb7ee afdaa3ab` numa worktree destacada própria.

Ferramentas (citadas, não refeitas), rodadas uma por vez no afdaa3ab (`R-TETO`): `tests.test_orcamento_instrucao` 8 testes OK; `tests.test_metricas_texto` 2 testes OK; `tests.test_jarvis_nucleo` 17 testes OK.

## Achados

## Sondas

## Parecer
**Aprovado.** Os seis recomendados do E21.2 (A1 a A6, no commit be5bb7ee) foram atendidos na volta E21.5:

- A1: `SKILL.md:19` diz que a espera em segundo plano vale para o Jarvis e que o subagente segue a skill `esperar-estado`; some a contradição com a regra 2 dela.
- A2: a pausa por limite de uso (`SKILL.md:19`) volta a dizer que nada novo é disparado, manda gravar onde parou e retomar com a cota nova; a frase tem verbo de novo.
- A3: o laço traz o prazo no próprio comando (`fim=$((SECONDS+N))` com a saída pelo `SECONDS`), e manda conferir o estado ao vencer.
- A4: o parágrafo `R-WIP` (`docs/regras/README.md:29`) ganha a volta a uma instância nova com o mesmo brief, quando a que fez não existe mais, e as medidas da diretriz 18 (espera até cada portão; vagas livres com fila parada igual a zero).
- A5: `SKILL.md:10` troca o "se serializam: a segunda começa já" por: itens com arquivo em comum vão juntos no lote ou o segundo espera o primeiro; inclui "depois de conferir" no relançamento do portão.
- A6: `SKILL.md:17` volta a "cerca de 150 linhas ... sem travar", fiel à decisão M14.

Cortes para caber (skill no teto, núcleo abaixo do teto, `jarvis.md` sem mudança): conferidos um a um, nenhum tirou regra. Na skill, a frase da volta à mesma instância e do CI do PR saiu porque a fonte única é o `R-WIP` do README, que a mantém; o resto é poda de estilo (descrição, "na volta ao autor", "por script" no `R-CONFORMIDADE`, "dos" e "deles"). No README, a célula da tabela perdeu o "só o hook quadro a verifica", que segue no título do parágrafo; a frase das worktrees perdeu o "dentro de R-TETO", que segue duas vezes no mesmo parágrafo (teto de agentes e o `R-TETO` inteiro); a frase do "um por vez" foi reescrita com a mesma lista de casos (arquivo comum, pipeline, quadro, merge na `develop`, mesmo módulo, ADR, tela, modelo de ameaças), só em outra ordem, por causa do `AntiDuplicacao`.

Teste novo `Diretrizes18e19` (`tests/test_jarvis_nucleo.py:156`): três testes de presença das frases que carregam as diretrizes 18 e 19 (anda sozinho, prazo no comando, subagente na `esperar-estado`, pausa, instância por item, volta, medidas, série por arquivo). É teste de texto, adequado a mudança só de texto; sem guarda de código no delta, sem mutante a declarar (AR-1, AR-2 não se aplicam). Conferidos os itens de `docs/engineering/achados-recorrentes.md`: nenhum alcança o delta (AR-9 limite antigo: as 150 linhas batem com a M14).

Neutralidade (`R-NEUTRO`): nada de projeto no delta. Fragmento de changelog atualizado com o mesmo sentido.

## Revalidação E21.10 (volta E21.9)
Delta lido: `forge-check parecer delta docs/reviews/v046-textos-jarvis.md`, intervalo `afdaa3ab..cf172a29` (sem o que veio da `develop` com #518 a #520), dois arquivos no domínio:
- `skills/trabalho-em-paralelo/SKILL.md`: a descrição perde "hora ou estado" e o texto devolve "(serializam)" na série por arquivo. Só texto; nenhuma regra sai, e a volta é fiel ao A5 (itens com arquivo em comum vão juntos ou o segundo espera).
- `tests/test_reval_delta.py:135`: registra a citação `tests/test_jarvis_nucleo.py` -> `README.md` (motivo `teste-le`, 1) em `CITACOES_CONHECIDAS`; coerente com o comentário da R-WIP logo acima e com o teste que lê `docs/regras/README.md`.

Testes afetados rodados no cf172a29, um por vez: `test_reval_delta` 10 OK, `test_orcamento_instrucao` 8 OK, `test_jarvis_nucleo` 17 OK. A suíte inteira fica no CI do PR. Sem guarda de código no delta: sem mutante a declarar. Sem achados novos; `agents/jarvis.md` sem mudança.

**Aprovado** no head cf172a29.
