---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae4-ordens
commit: 916ccb02ece58f2a21179aebdf25e6e40a894d6c
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0479-ae4-ordens (AE4.1, revalidação E58.76)

Volta por delta. Rodada anterior: d99faab9, que aprovou 18d6d2f4 (fica no git). Delta lido por `forge-check parecer delta`: `18d6d2f4..916ccb02`, no domínio só `bin/forge-check` (`quadro_do_texto` extraído de `quadro_por_coluna` sem mudar a leitura; `recusa_do_apontador` lê o KANBAN uma vez por `_ler_regular` e filtra o cartão pela coluna Pedido; `cmd_anotar` passa `id_do_pedido(arq.name)`). Também li `_ler_regular` (`bin/forge-check:4841`), que o delta passa a usar. Fora do domínio (changelog, proposta, mutantes, testes): não relido.

## Gatilhos
Gatilhos: controle do Forge (guarda de gravação do registro do dono no `bin/forge-check`), mudança no `bin/forge-check` sujeita à catraca `afrouxa-regra`.

## Estado dos achados anteriores
- A1 (recomendado, KANBAN conferido e aberto em duas vezes): **corrigido**. Uma abertura com `O_NOFOLLOW|O_NONBLOCK`, `fstat` regular e teto de 1 MiB (`bin/forge-check:5039`, `:4844`). Corrida refeita: troca contínua link/arquivo em 60 chamadas, 0 gravadas (46 recusas por link, 14 por cartão fora do quadro); antes, 12 de 60. FIFO recusado em 0,19 s (antes travava); link para `/dev/zero` recusado; quadro acima do teto recusado.
- A2 (recomendado, cartão de outro pedido aceito): **corrigido**. `bin/forge-check:5045` só aceita colunas de cartões cujo `id_do_pedido` é o pedido anotado. `OUT-1` de `outro-pedido` recusado; pedido em maiúsculas e célula vazia recusados; cartão meu em `Fechado sem entrega` mais cartão aberto de outro pedido com o mesmo ID: recusado (fechado). Aceita quem cita o próprio pedido com caminho (`docs/pedidos/<id>.md`, `x/../<id>`): o nome final é o pedido; exige editar o quadro, sem achado.

## Só aperta? (confirmação escrita para a catraca)
Confirmo: a mudança **não cria caminho de ataque novo**, mas **não é só aperto no sentido estrito**, por causa da leitura com troca de caracteres:
- **ID que só casa depois da troca: não existe.** O `--cartao` passa antes por formato ASCII fechado; a troca só produz U+FFFD, que não é ASCII e cujo `casefold` é ele mesmo; ela não cria nem remove `|` ou quebra de linha (sequência truncada antes de `|` e `\n` preserva os separadores). Sondas: byte inválido no ID, no lugar do hífen, codificação longa de `-` e de `|`, surrogate codificado, UTF-16 inteiro e byte inválido na coluna Pedido: todas recusadas.
- **Dois casos passaram de recusa a aceite:** (a) quadro com cartão válido e lixo fora de UTF-8 em outra linha (`ABC-1` grava; antes "ilegível"); (b) cabeçalho `## Fechado<byte inválido> sem entrega` deixa de ser a coluna fechada e o `FECH-1` grava. Cada um equivale a um quadro em UTF-8 válido com U+FFFD no mesmo lugar, que a base já aceitava (é a dimensão "nome de coluna variante" registrada na rodada anterior): o conjunto de quadros aceitos não cresceu, só o de bytes que levam a eles. Quem faz isso já escreve o KANBAN. Recomendo devolver o fail-closed (A4) para que a afirmação "só aperta" valha à letra.
- O resto aperta: teto novo, FIFO e não regular recusados sem travar, link recusado sem janela, cartão de outro pedido recusado; `quadro_por_coluna` mantém `read_text(encoding="utf-8")` estrito para os outros chamadores.

## Achados
- A3 (recomendado) bin/forge-check:4847 · KANBAN.md diretório: os.fdopen falha antes do fstat e o anotar cai com IsADirectoryError, rc 1 e rastreio (na base, rc 2 "ilegível"). Nada é gravado. Conferir fstat no fd antes do fdopen (ou capturar OSError) e devolver "não é arquivo regular".
- A4 (recomendado) bin/forge-check:5039 · leitura com troca (errors=replace, :4853) aceita KANBAN fora de UTF-8 que a base recusava: cartão válido com lixo em outra linha e cabeçalho Fechado com byte inválido gravam. Sem ganho para atacante; recusar texto com U+FFFD na conferência do cartão.

## Sondas

## Detalhe dos achados
Sondas em fixture própria efêmera em `/dev/shm` (fora de repositório git e de `/tmp/claude-0`; cada raiz com `git init` próprio, `TMPDIR` na mesma pasta, ambiente limpo, Python `-I`), KANBAN e pedido de `tests/test_ordens.py`, forge-check do head. Pasta de controle não tocada (`git status --porcelain` vazio). IDs forjados refeitos: `ABC-10`, `ABC-1-2`, `ABC`, `ABC-1 `, `АBC-1` (A cirílico), `ABC‐1` (hífen Unicode), `abc-1`, `E1.1 `, `E١.١`, `E1.1b`, `E1.10`, `E11`, `E01.1`, `E2.1`, `E9.9`, `FECH-1`, `OUT-1` e sem `--cartao`: todos rc 2, nada gravado; `ABC-1` e `E1.1` gravam.

A3 · evidência `bin/forge-check:4847` (`os.fdopen` antes de `os.fstat` em `:4848`), chamado de `:5039` · sonda: `KANBAN.md` diretório, `anotar --tipo ordem --cartao ABC-1` · espera rc 2 "não é arquivo regular" · obtido rc 1, `IsADirectoryError` (o pedido fica intacto: fail-closed); base 18d6d2f4: rc 2 "ausente ou ilegível". O mesmo `_ler_regular` serve o `kanban gerar` (`:4886`) · severidade baixa (robustez; sem gravação) · correção mínima: `fstat` no fd e fechar o fd antes do `fdopen` quando não é regular · esforço P · dono: tech-lead.

A4 · evidência `bin/forge-check:4853` (`decode("utf-8", errors="replace")`) usado em `:5039` · sondas: quadro com cartão `ABC-1` válido mais a linha `\xc3\x28 lixo` grava (base recusa); cabeçalho `## Fechado\xff sem entrega` com `FECH-1` grava (base recusa) · severidade baixa (catraca: afrouxa à letra, sem caminho de ataque) · correção mínima: em `recusa_do_apontador`, se `"�" in texto`, recusar com "KANBAN.md fora de UTF-8" (o `kanban gerar` segue com a troca) · esforço P · dono: tech-lead.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Suíte: sem PR nem CI no head (o brief pede sem suíte local); rodei só as sondas acima. Ferramentas: `forge-check parecer delta`, leitura estática, sondas locais contra head e base (`git archive 18d6d2f4 bin`).
