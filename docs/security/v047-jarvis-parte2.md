---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-jarvis-parte2
commit: cfeff5ef7c54fab62418a34e085d316623d72581
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-13
---
# Review de segurança: v047-jarvis-parte2 (E4.2, diretrizes 2, 11 e 16)

## Gatilhos
Regra de processo em `docs/regras/README.md` e em duas skills (`R-WIP`, `R-FLUXO`, `R-REVIEW`): nenhum código de produção, hook, workflow, segredo nem permissão tocados. Revisão por segurança do que a edição poderia afrouxar.

## Achados
- A1 (recomendado) docs/regras/README.md:10 · âncoras das 5 regras de R-LIMITES.md removidas dos links: a navegação cai no topo do arquivo, sem perda de regra; opcional restaurar o link do R-MAIN.

## Sondas
- S1 · `python3 -I -m unittest discover -s tests -p test_forge.py -k DiretrizesDoDonoNaRWip -k RegrasInviolaveis -k RegrasComId -k TextosDoAgenteEDaRegra -k AntiDuplicacao` (head 17c66fb2) · espera: OK · obtido: Ran 13 tests OK (o FAIL de 65cf916b em tests/test_forge.py:626 está resolvido)

## Detalhe dos achados
- A1: informativa, esforço P, dono tech-lead. Os 5 links apontam para `R-LIMITES.md` (existe); o texto de cada regra segue em `R-LIMITES.md`, só a âncora saiu.
- Conferido sem achado: as regras cortadas (validade e medida, `R-WIP` 1 cartão por agente, gargalo, teto, limites de coluna, `origem:` nunca validação do usuário) estão todas no texto novo; o corte de "AV5", da exceção `anti_duplicacao.excecoes` e de "(pedido do usuário)" é só referência. "Portão sem retorno em 53 min: confira que parou e relance" mantém a conferência antes de relançar. A integração na `develop` segue exigindo pareceres da classe aprovados e CI verde, agora por PR próprio. "Vaga livre não espera a versão" vale só para começar (desenho, plano de teste, ameaças, item sem arquivo em comum): o merge continua pelo fluxo, sem pular portão; "parado não se abandona" não cria atalho de aprovação.

## Revalidação (delta 1c3e34f2..65cf916b, E3.20)
Lido só `forge-check parecer delta`: skills/kanban-scrum/SKILL.md e skills/trabalho-em-paralelo/SKILL.md (tests/test_reval_delta.py é só lista, fora do domínio). Nenhuma regra afrouxou: o PR passou a abrir com pareceres aprovados no head (mais estrito), o corte de "serializam", "gargalo" e dos relógios D-4 é só redação, o acréscimo de triagem é adição. Sem achado de segurança novo; a reprovação é só por A2.
- A2: defeito provado, esforço P, dono tech-lead (teste) ou autor da skill. Correção mínima: alinhar a asserção de tests/test_forge.py:626 à frase nova da skill, isto é, exigir `entra na `develop` por PR próprio, sem juntar frentes (`R-FLUXO`)` (ou a frase inteira "o PR abre com os pareceres da classe aprovados no head e a entrega conferida; com CI verde, entra na `develop` por PR próprio, sem juntar frentes (`R-FLUXO`)"), mantendo a exigência de PR próprio e do ID `R-FLUXO`, sem remover a asserção. Rodar `DiretrizesDoDonoNaRWip`.
- Os outros 12 testes do conjunto afetado (`RegrasInviolaveis`, `RegrasComId`, `TextosDoAgenteEDaRegra`, `AntiDuplicacao` e o resto de `DiretrizesDoDonoNaRWip`) passam. Suíte inteira não rodada (carga, diretriz 15); sem PR aberto.

## Revalidação (delta 65cf916b..17c66fb2, E3.24)
Lido `forge-check parecer delta` (domínio: skills/kanban-scrum/SKILL.md e skills/trabalho-em-paralelo/SKILL.md; tests/test_forge.py fora). Aprovado, sem achado novo.
- A2 resolvido: tests/test_forge.py:626 agora exige `com CI verde, entra na `develop` por PR próprio, sem juntar frentes (`R-FLUXO`)`, mantendo PR próprio, CI verde e o ID `R-FLUXO`; asserção não removida nem afrouxada.
- skills/kanban-scrum/SKILL.md:73 devolve a linha dos dois relógios (D-4, `relogios:`): adição, nenhuma regra afrouxa. skills/trabalho-em-paralelo/SKILL.md:10 volta "(serializam)": só redação, a série por arquivo em comum, o lote e a espera do primeiro seguem.
- O head da branch (442b90ed) só acrescenta docs/qa depois de 17c66fb2; fora do domínio.

## Revalidação (delta 17c66fb2..cfeff5ef, E3.32)
Lido `forge-check parecer delta` (domínio: docs/regras/README.md e skills/kanban-scrum/SKILL.md; tests/test_forge.py fora). Aprovado, sem achado novo. Diretriz 25 conferida: nenhuma regra antiga saiu nem foi resumida.
- docs/regras/README.md (R-WIP): "sem junção de frentes" virou "sem juntar frentes (`R-FLUXO`)": só redação, PR próprio e o ID mantidos.
- skills/kanban-scrum/SKILL.md:39: os dois bullets (bloqueio/espera do dono e devolvido no review/QA) viraram um; a coluna de origem, a volta, "nunca vira proposta de abandono (`R-WIP`)" e o retorno a "Em andamento" como retrabalho seguem. Nada afrouxou.
- tests/test_forge.py:626 acompanha o texto novo e mantém PR próprio, CI verde e `R-FLUXO`.
- Os outros arquivos do intervalo vieram da `develop` (merge), fora da entrega e do domínio desta branch.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodados no head cfeff5ef (13 testes, OK): `RegrasInviolaveis`, `RegrasComId`, `TextosDoAgenteEDaRegra`, `DiretrizesDoDonoNaRWip`, `AntiDuplicacao` (13 testes, OK). Suíte inteira não rodada local (carga, diretriz 15); fica ao CI do PR, ainda não aberto. Sem ferramentas de varredura necessárias (só texto).
