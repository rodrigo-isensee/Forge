---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-ae2-quadro-anda
commit: cbf24de557ea23a5bf6a5c7e43942a239b3f8aba
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0481 (AE2, #875, E10.2)

Escopo: diff `bbbe2d88..cbf24de5` (`bin/forge-check` `cmd_movimento`, `secao_de_destino`, `linha_movida`, `mover_no_quadro`; `bin/forge-fechar` `cartoes_do_corpo`; testes, specs de mutante, docs, changelog). Classe C. Primeiro parecer de review da branch (sem delta anterior).

## Achados
- A1 (bloqueante) bin/forge-check:5265 · linha_movida casa como cartão o cabeçalho e o separador da tabela: cartão `ID` (qualquer caixa) ou `---` apaga o cabeçalho ou o separador da última tabela e grava rc 0; `Cartão: ID` no corpo do PR passa a forma do forge-fechar. Excluir `c == COLUNAS` e separador, como linhas_de_cartao.
- A2 (recomendado) bin/forge-check:5275 · Cartão duplicado em duas seções: só a última linha sai, a outra fica na coluna velha e o quadro mostra o cartão em dois lugares (reproduzido, S3). Tirar todas as linhas do cartão antes de inserir.
- A3 (recomendado) bin/forge-fechar:952 · O aviso ecoa `${id:0:80}` vindo do corpo do PR sem tirar caractere de controle (`[^[:space:]]` deixa passar ESC); filtrar com `tr -d '[:cntrl:]'` antes do echo.
- A4 (recomendado) bin/forge-fechar:950 · Cartão: do corpo que não existe no quadro (erro de digitação, linha em bloco de código) nasce em Pronto com `—`; mover só o que já tem coluna e avisar o resto (mesmo A2 do parecer de segurança).

## Sondas
- S1 · movimento --de "Em andamento" --para Pronto -- ID (quadro com 2 tabelas) · espera: cabeçalho de Pronto intacto, linha nova do cartão ID · obtido: rc 0, Pronto começa por `|---|` e o cabeçalho virou `| ID | Cartão | Pedido | Responsável | Entrou | <hora> | custo total: lacuna |`
- S2 · movimento --de "Em andamento" --para Pronto -- --- · espera: separador de Pronto intacto · obtido: rc 0, separador virou `| --- | --- | --- | --- | --- | <hora> | custo total: lacuna |`
- S3 · movimento K-1 --de "Code review" --para Pronto (K-1 em Em andamento e em Code review) · espera: K-1 só em Pronto · obtido: K-1 fica em Em andamento e aparece em Pronto

## Parecer
**Reprovado** por A1: o brief pede, em especial, que o movimento não corrompa o quadro, e ele corrompe com um nome de cartão que passa por todas as formas (inclusive a do `forge-fechar`). O mesmo defeito está no A1 do parecer de segurança (`docs/security/v0481-ae2-quadro-anda.md`); reproduzi-o à parte (S1, S2). A correção é uma condição no laço de `linha_movida` (a mesma exclusão de `linhas_de_cartao`, `bin/forge-check:5152`) e um teste com `ID`, `id` e `---`, com o mutante dessa guarda declarado.

Pontos que o brief pede:
- **`a · b` fora da lista de recusas (`tests/test_sobreposicao_quadro.py:398`): não afrouxa.** A troca `·` por `-` só no `--titulo` (`bin/forge-check:5224`) roda antes de `erro_dos_atributos`, que segue recusando `·` em todo atributo; o valor gravado nunca leva `·`, então não forja a marca ` · atributos: `, e o `ler_marca` continua recusando `·` no valor lido do histórico. A recusa virou normalização com a mesma garantia; o teste novo prova o valor gravado (`titulo=AE2 - quadro`), e `a; b`, `a=b`, `a|b` e invisíveis seguem recusados.
- **Cartão errado:** a busca casa o nome inteiro por `chave_do_cartao` (casefold, sem prefixo nem substring); `K-1` não pega `K-10`. O único casamento errado é o do A1.
- **Só depois do merge confirmado:** `cartoes_do_corpo` roda em `bin/forge-fechar:1923`, depois das guardas do passo 6 (MERGED, head igual ao conferido, base igual ao alvo, commit de merge) e só com `ja_mesclado=0`; o alvo dessa via é sempre a `develop` (`--promover` tem caminho próprio). O teste confere a ordem `gh pr merge` antes do movimento e que PR já mesclado não lê o corpo. O falso do `gh` devolve título e corpo como o `--jq '.title, .body'` real (item 12 do checklist: sem folga).
- **Escrita do quadro:** trava (C-10), leitura sem seguir link (C-1) e troca por temporário e `os.replace` (C-2), iguais às do `kanban --gerar`, testadas (link, trava que não abre). A reescrita com U+FFFD em byte inválido é a mesma do `kanban --gerar` (A4 da segurança), fora deste item.

Ferramentas e suíte: `forge-mutante --conferir --base bbbe2d88`: specs no lugar; `--cobertura`: rc 0 (as linhas "sem mutante" que ela lista são condições de ternário e de gerador; a catraca do CI decide). Rodei os testes do item no head: `test_sobreposicao_quadro` 72 OK e `test_fechar_move_cartao` 18 OK. CI do PR (`catraca`) ainda pendente na leitura; a suíte inteira fica com ele. Tamanho (H1): cerca de 86 linhas de código em `bin/`, um comportamento (o quadro anda com o movimento), dentro do teto. Commits limpos, Conventional Commits em português; docs (`fechamento-integrador.md`, `kanban-scrum`) e fragmento do changelog acompanham.

A2 a A4 não devolvem; viram cartão depois do merge, salvo se o autor os corrigir na mesma volta do A1.
