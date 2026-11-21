---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae4-ordens
commit: df0cf4d96cdf642b624c1468245010619410d9d1
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0479-ae4-ordens (AE4.1, revalidação E58.90)

Volta por delta. Rodada anterior: o parecer que aprovou b1cd22ec (fica no git). Delta lido por `forge-check parecer delta`: `b1cd22ec..df0cf4d9`, com a develop separada por `git diff c9d69234 HEAD`.
- Merge da develop (27596e7d, pais bcb4bdc2 e c9d69234): o diff próprio da branch contra a develop em `bin/forge-check` e `bin/forge-testes` é linha a linha igual ao de b1cd22ec contra a base anterior 821db42e (comparação dos `+`/`-` de `git diff -U0`: zero diferenças). Nada de resolução à mão; o código da develop veio pelos PRs dela (#752, #755, #757) e não é relido aqui.
- `agents/jarvis.md:13`: "a ordem leva" vira "ordem com" no item do recibo; mesma regra (`--cartao <ID|E<n>>`), só texto.
- `tests/mutantes/est-m12-gerar.json:29`: o `de` do M3 passa a 4 espaços, igual à linha de `_ler_regular` agora (`bin/forge-check:4893`), com ocorrência única.

## Gatilhos
Gatilhos: controle do Forge (guarda de gravação do registro do dono no `bin/forge-check`), mudança no `bin/forge-check` sujeita à catraca `afrouxa-regra`.

## Estado dos achados anteriores
- A1, A2, A3, A4 (rodadas anteriores): corrigidos, sem mudança no delta.

## Só aperta? (confirmação escrita para a catraca)
Confirmação: só aperta. O delta desta rodada não muda comportamento de guarda: o código próprio da branch no `bin/forge-check` é idêntico ao aprovado em b1cd22ec (só aperta frente à develop, rodada anterior); o resto é reescrita de texto no `agents/jarvis.md` com a mesma regra e o realinhamento de um mutante, que volta a matar a guarda C-1 em vez de não aplicar.

## Detalhe
- M3 aplicado numa cópia do head por `git archive` (fora do repositório): `de` encontrado 1 vez; o teste `tests.test_sobreposicao_quadro.KanbanGerar.test_link_grande_fifo_ou_ausente_recusa_com_o_quadro_e_o_alvo_intactos` cai (FAILED, failures=1); sem o mutante, passa (OK). Com o `de` antigo (8 espaços) o mutante não casava com a linha nova.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Suíte: sem PR nem CI no head (o brief pede sem suíte local); rodei só o teste do M3, com e sem o mutante. Ferramentas: `forge-check parecer delta`, `git diff`, leitura estática.
