---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-indice-forge
commit: 7bd4913edcb31af54510071cb86fe53a07087174
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 (E8.3, índice do Forge, H7 primeira parte)

## Achados
- A1 (bloqueante) scripts/indice-forge.py:84 · A coluna Testes e a contagem (linha 94) mudam com teste novo, texto de teste e mapa de outra trilha: o índice venceria em 5 de 15 merges da develop (S1). Toda trilha teria de regravar o docs/indice-forge.md, arquivo comum: a sobreposição as põe em fila (R-FLUXO, ordem do dono das 13:18).
- A2 (recomendado) bin/forge-testes:218 · O plano dirigido de bin/, hooks/ e scripts/ não traz o test_indice_forge (--listar bin/forge-check: 0): o índice vencido só aparece no CI pago (R-CUSTO). Ponha o módulo em VARREM_A_PASTA.

## Sondas
- S1 · scripts/indice-forge.py do head gerado em cada um dos 16 últimos commits da develop (first-parent, a1674911..4182a6b9) · espera: índice estável fora da trilha dona do arquivo · obtido: mudou em 5 de 15 merges; sem a coluna Testes e a contagem, em 2, ambos a trilha que criou o arquivo

## Parecer
Reprovado por A1. O código lê bem, as guardas têm teste do ramo de falha e mutante declarado, e o teste novo passa no head (`python3 -m unittest tests.test_indice_forge`: 18 testes OK; `--conferir`: em dia). Suíte inteira: fica para o CI do PR.

Risco apontado pelo autor (primeira linha de doc mudada por outra trilha): é real, mas pequeno; a primeira linha muda quase só na trilha dona do arquivo, e a diretriz 33 já dá uma trilha por arquivo. O risco grande é outro: a coluna Testes vem do plano dirigido, que lê o texto de todo `tests/test_*.py` (convenção, `leitores`, `quem_importa`). Teste novo que cita ou importa um arquivo, arquivo novo em `bin/`, `hooks/` ou `scripts/` e mudança no `MAPA` vencem o índice. Na amostra (S1), mudou em 23928603, 31b29052, 71f280f2, 038249c5 e 9ae3e442, sobretudo pela coluna Testes (`test_forge_fechar`, `test_maquina` e `test_forge_copia` entrando). Com quatro ou mais trilhas abertas, cada merge desses deixa vermelho o CI das outras, porque o PR roda sobre a develop nova, e obriga cada uma a regravar o mesmo arquivo. Duas regravações conflitam no texto (a linha "Os N arquivos" e as linhas vizinhas), e o `forge-check sobreposicao` põe as trilhas em fila. Isso trava as trilhas paralelas, contra a ordem do dono de manter o máximo de trilhas.

Remédio (correção do autor, antes dos portões): o arquivo versionado fica só com o arquivo e a primeira linha da doc, sem a coluna Testes e sem a contagem no cabeçalho. Os testes de um arquivo já têm comando, `bin/forge-testes --listar <arquivo>`, que o cabeçalho cita e que o brief pode citar no lugar da coluna. Com isso, o índice só muda quando um arquivo entra, sai ou muda a primeira linha da doc, e isso cabe à trilha dona do arquivo (S1: 2 de 15, ambos na trilha que criou o arquivo). Junto, A2: o teste no plano dirigido da pasta deixa a trilha ver o índice vencido antes do envio. Se o arquiteto quiser manter a coluna, a alternativa é não versionar o índice e gerá-lo na hora do brief (segunda parte do H7). Isso muda a estrutura e fica com ele e comigo em ADR.

Revalidação: na volta, leio o delta de `scripts/indice-forge.py`, `docs/indice-forge.md`, `tests/test_indice_forge.py` e `bin/forge-testes` e a S1 refeita no head novo.
