---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae4-ordens
commit: b1cd22ec7933e02b3e45af9a67d8ec25afc1dda1
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0479-ae4-ordens (AE4.1, revalidação E58.80)

Volta por delta. Rodada anterior: 0d5c9b24, que aprovou 916ccb02 com A3 e A4 recomendados (fica no git). Delta lido por `forge-check parecer delta`: `916ccb02..b1cd22ec`, no domínio só `bin/forge-check`: `_ler_regular` confere o `fstat` no fd e fecha o fd antes do `os.fdopen` (`bin/forge-check:4847`), e `recusa_do_apontador` recusa texto com U+FFFD (`bin/forge-check:5043`). `_ler_regular` também serve o `kanban --gerar` (`:4887`), relido nesse ponto. Fora do domínio (changelog, mutantes, `tests/test_ordens.py`): não relido.

## Gatilhos
Gatilhos: controle do Forge (guarda de gravação do registro do dono no `bin/forge-check`), mudança no `bin/forge-check` sujeita à catraca `afrouxa-regra`.

## Estado dos achados anteriores
- A1, A2 (rodadas anteriores): corrigidos, sem mudança no delta.
- A3 (recomendado, KANBAN pasta cai com `IsADirectoryError`): **corrigido**. Pasta no lugar do KANBAN: anotar com `ABC-1` sai rc 2 "KANBAN.md não é arquivo regular", nada gravado (916ccb02: rc 1 com rastreio). No `kanban --gerar`, pasta no lugar do `KANBAN.md` ou do `docs/kanban/historico.md`: rc 1 "não é arquivo regular; quadro intacto", pasta intacta (develop, base e 916ccb02: rc 1 "Is a directory; quadro intacto"; só muda a mensagem). O fd é fechado no ramo de recusa (sem vazamento).
- A4 (recomendado, KANBAN fora de UTF-8 aceito): **corrigido**. Os dois quadros da rodada anterior e mais três variantes passam de aceite (916ccb02) a recusa rc 2 "KANBAN.md fora de UTF-8", igual à base 18d6d2f4 (que recusava como "ilegível").

## Só aperta? (confirmação escrita para a catraca)
Confirmo: **frente à develop 821db42e, a mudança só aperta**, agora à letra.
- Contra a develop: lá `anotar --tipo ordem` grava sem cartão em todos os casos sondados (inclusive KANBAN pasta ou fora de UTF-8); no head, a ordem exige `--cartao` e grava só com cartão do pedido em quadro regular, UTF-8 e fora de `Fechado sem entrega`, ou com etapa do pedido. No `kanban --gerar`, mesmo rc e mesmo "quadro intacto"; só a mensagem fica mais clara.
- Contra a base 18d6d2f4: nenhum caso sondado passa de recusa a aceite. Um passa de aceite a recusa: quadro em UTF-8 válido com o caractere U+FFFD literal (a base gravava `ABC-1`; o head recusa). É aperto; quadro legítimo com U+FFFD é improvável e a etapa `E<n>` continua valendo.
- A conferência por etapa (`E1.1`) não lê o KANBAN e grava com quadro pasta ou fora de UTF-8 em base e head: inalterado.

## Detalhe
Sondas em fixture própria efêmera em `/dev/shm` (fora de repositório git; cada raiz com `git init` próprio, `TMPDIR` na mesma pasta, ambiente limpo, Python `-I`), KANBAN e pedido de `tests/test_ordens.py`, forge-check de 821db42e, 18d6d2f4, 916ccb02 e b1cd22ec por `git archive`. Pasta de controle não tocada (`git status --porcelain` vazio). Resultado (develop / base / 916ccb02 / head, rc e gravou):
- cartão `ABC-1` com linha `| LIXO-\xff | x |`, com `\xc3\x28 lixo`, com `| é |` em latin-1: 0 grava / 2 / 0 grava / 2.
- `FECH-1` com `## Fechado\xff sem entrega` e com `## Fechado sem entrega\xff`: 0 grava / 2 / 0 grava / 2.
- quadro inteiro em UTF-16: 0 grava / 2 / 2 / 2.
- U+FFFD literal em UTF-8 válido: 0 grava / 0 grava / 0 grava / 2.
- KANBAN pasta com `ABC-1`: 0 grava / 2 / 1 (rastreio) / 2; com `E1.1`: grava nas quatro.
- quadro limpo com `ABC-1` e `E1.1`: grava nas quatro.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Suíte: sem PR nem CI no head (o brief pede sem suíte local); rodei só as sondas acima. Ferramentas: `forge-check parecer delta`, leitura estática, sondas locais contra develop, base, head anterior e head.
