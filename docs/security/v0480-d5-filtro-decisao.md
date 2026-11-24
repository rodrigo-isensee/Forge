---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-d5-filtro-decisao
commit: 6c4a7dcc9856c3718599c0bdb06185a58afcbdcf
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0478 (D5, filtro de decisão, PR #863, E173.7)

Gatilhos: controle de conformidade que analisa entrada (o decisor lê um parecer e decide no lugar do dono, R-DECISAO), registro de decisões em `docs/kanban/decisoes-obvias.jsonl`.

Base `8a6f5907` × head `6c4a7dcc`: `bin/forge_decisor.py`, `bin/forge_dono.py`, `bin/forge-check` (anotar e decisoes), testes e mutantes. O remoto andou até `ab498b06` só com o parecer do review (`docs/reviews/`), fora do código revisado.

## Achados
- A1 (bloqueante) bin/forge_decisor.py:56 · O decisor aceita arquivo forjado: lê a árvore de trabalho, sem exigir o arquivo no git nem frontmatter `tipo: revisao-seguranca`, `parecer: aprovado`, `revisor: forge:security-engineer`. Texto solto ou parecer reprovado com "só aperta" decide (S1, S2, S8).
- A2 (bloqueante) bin/forge_decisor.py:60 · A confirmação não se prende à decisão: 73 pareceres já na develop casam (S9 com release-0.47.15.md, cujo "Só aperta?" é título). Exigir `pedido:` igual ao --pedido e uma linha própria que nomeie a porta (mesmo ponto do A1 do review).
- A3 (bloqueante) bin/forge_decisor.py:31 · A busca solta lê pergunta e negação como confirmação: "## Só aperta?", "não é só aperta", "não" e "só aperta" em linhas seguidas, "não  só aperta" decidem (S3 a S6). Trocar a busca por linha ancorada de formato fixo, sem procurar a frase no texto.

## Sondas
- S1 · docs/security/f.md fora do git, sem frontmatter, com "qualquer coisa" e "só aperta"; decisoes registrar com --so-aperta sim --seguranca docs/security/f.md · espera: rc 1, pergunta ao dono · obtido: rc 0, decisoes: decidida D0001
- S2 · f.md com frontmatter tipo: revisao-seguranca, parecer: reprovado e "Só aperta? Não: afrouxa." · espera: rc 1, pergunta ao dono · obtido: rc 0, decisoes: decidida D0001
- S3 · f.md com "## Só aperta?" e na linha seguinte "Não. Aceita mais." · espera: rc 1, pergunta ao dono · obtido: rc 0, decisoes: decidida D0001
- S4 · f.md com "A mudança não é só aperta: afrouxa." · espera: rc 1, pergunta ao dono · obtido: rc 0, decisoes: decidida D0001
- S5 · f.md com "não" e "só aperta" em linhas seguidas · espera: rc 1, pergunta ao dono · obtido: rc 0, decisoes: decidida D0001
- S6 · f.md com "não  só aperta" (dois espaços) · espera: rc 1, pergunta ao dono · obtido: rc 0, decisoes: decidida D0001
- S8 · f.md com frontmatter tipo: review, pedido: outro e "só aperta" · espera: rc 1, pergunta ao dono · obtido: rc 0, decisoes: decidida D0001
- S9 · cópia literal de docs/security/release-0.47.15.md (parecer de outro item) como --seguranca de uma decisão do pedido p1 · espera: rc 1, pergunta ao dono · obtido: rc 0, decisoes: decidida D0001

## Detalhe dos achados
Todas as sondas rodaram `bin/forge-check --raiz <tmp> decisoes registrar` do head, numa raiz temporária com um parecer só, os fatos todos em `sim`/`nao` de porta aberta e `--so-aperta sim`. O controle de sanidade S7 ("não só aperta") deu rc 1, como esperado.

**A1, arquivo forjado.** Evidência: `bin/forge_decisor.py:50-60` confere só o nome (`:30`), link simbólico, tamanho e a frase. Caminho de ataque: o agente que quer seguir sem esperar o dono (o risco que a regra do dono de 24/11 trata) grava `docs/security/<x>.md` por qualquer caminho que a barreira de papel não modele, ou nem grava (A2), e cita o arquivo; o decisor imprime `decidido:` e o commit-msg (`.githooks/commit-msg:9`) só confere a forma da linha. Severidade: alta (anula o portão da R-DECISAO que o item cria). Correção mínima: ler o parecer pelo git (`git show HEAD:<caminho>`, recusando arquivo fora do índice ou com diferença na árvore) e exigir no frontmatter, pelo leitor de frontmatter que o `forge-check docs` já usa, `tipo: revisao-seguranca`, `parecer: aprovado`, `revisor: forge:security-engineer` e `pedido:` igual ao `--pedido`. Esforço: P. Dono: tech-lead.

**A2, confirmação sem vínculo.** Evidência: `bin/forge_decisor.py:60`; a sonda `sonda_existentes` sobre o clone acha 73 arquivos de `docs/security/` que casam a regex (74 com este parecer reprovado, que também confirmaria), entre eles pareceres cujo "Só aperta?" é só o título da seção (`release-0.47.14.md`, `release-0.47.15.md`, `release-0.47.16.md`, `v0479-release-04714.md`) e um cuja resposta é "neutro" (`v0480-tempo-fixture.md`). Caminho de ataque: qualquer decisão futura cita um desses e decide, sem nenhuma confirmação nova da segurança. Severidade: alta. Correção mínima: linha de formato fixo no parecer, por exemplo `Só aperta: <porta>` ancorada (`^Só aperta: (.+)$`, fullmatch), com a porta igual ao `--porta` normalizado, além do `pedido:` do A1; o `_modelo.md` ganha a linha. Esforço: P. Dono: tech-lead.

**A3, frase solta.** Evidência: `bin/forge_decisor.py:31`; o lookbehind só pega `não ` e `nao ` coladas com um espaço. Caminho de ataque: o parecer que conclui "não é só aperta" ou pergunta "Só aperta?" vira confirmação. Severidade: média (some com a correção do A2, que troca a busca pela linha ancorada; se a busca ficar, é bloqueante por si). Correção mínima: a do A2; os textos de S3 a S6 entram como casos de teste que precisam virar pergunta. Esforço: P. Dono: tech-lead.

Recomendações (fora do delta, pré-existentes, não bloqueiam): o `decidido:` do commit não é conferido contra o registro (`.githooks/commit-msg:9` só olha a forma), e `--raiz` aceita qualquer pasta, então a decisão pode ser tirada numa raiz temporária; casar a linha `decidido:` com uma entrada `decidida` do registro da raiz do repositório fecharia isso. Vai como cartão ao tech-lead.

**Só aperta ou neutro, por escrito:** o delta só aperta em relação à base. Antes dele, o decisor decidia com as quatro condições; agora pede também `--so-aperta sim` e a confirmação, e `anotar --tipo pergunta` passa a recusar pergunta sem tipo ou com opção única. Nada que a base recusava passa a ser aceito. A reprovação é por requisito: a confirmação que o item promete (regra do dono de 24/11, D5) não é real, porque o decisor pode ser enganado por arquivo forjado ou alheio.

Suíte: o PR #863 não tem check run no head (`gh pr view 863`: rollup vazio); rodei só os testes dos arquivos tocados (`tests.test_decisor`, `tests.test_forge_dono`, `tests.test_anotar`: 121 testes, OK). Sem CI para citar; a revalidação cita o CI do head novo.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, sondas locais em raiz temporária (biblioteca padrão), unittest dos arquivos tocados. Nenhuma ferramenta externa foi necessária.
