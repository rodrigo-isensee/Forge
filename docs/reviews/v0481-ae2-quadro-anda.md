---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-ae2-quadro-anda
commit: 8087e23dbec99aefc234a9735132c8c5721d164d
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0481 (AE2, #875, E10.6)

Escopo: revalidação por delta, `cbf24de5..8087e23d` (volta única E10.5). Delta lido: `forge-check parecer delta` deu `revalida: sim` (o parecer anterior, no `cbf24de5`, reprovou). Arquivos de código do delta: `bin/forge-check` (`celulas_de_cartao` nova, `montar_quadro`, `_ler_regular(estrito)`, `linhas_de_cartao`, `erro_dos_atributos`, `linha_movida`, `mover_no_quadro`) e `bin/forge-fechar` (`cartoes_do_corpo`); testes, specs `-3.json` e `-4.json` (AE19 a AE32), docs e changelog.

## Achados
- A1 (recomendado) bin/forge-fechar:939 · coluna_do_cartao, no KANBAN.md, casa o cabeçalho: `Cartão: ID` no corpo passa a forma e o filtro novo (coluna = a seção da 1ª tabela, não `—`) e o movimento, que agora exclui o cabeçalho, cria o cartão `ID` em Pronto. Excluir a linha de cabeçalho e o separador no awk (por leitura).

## Sondas
- S1 · movimento --de "Em andamento" --para Pronto -- ID (quadro com 3 tabelas) · espera: cabeçalhos intactos, linha nova `ID` em Pronto · obtido: rc 0, 3 cabeçalhos antes e depois, última linha de Pronto `| ID | — | — | — | ...`; o mesmo com `id`
- S2 · movimento --de "Em andamento" --para Pronto -- --- · espera: separadores intactos · obtido: rc 0, 3 cabeçalhos e separadores antes e depois, linha nova `| --- | — | ...`
- S3 · movimento K-1 --de "Code review" --para Pronto (K-1 em Em andamento e em Code review) · espera: K-1 só em Pronto · obtido: uma linha de K-1, em Pronto, a de Code review (`dup`); nenhuma antes de Pronto
- S4 · movimento K-1 com byte 0xFF no KANBAN.md · espera: rc 0, aviso, bytes intactos · obtido: rc 0, `aviso: KANBAN.md não é UTF-8 válido; quadro intacto; o histórico foi gravado`, arquivo igual
- S5 · movimento K-3 cuja linha tem 6 colunas · espera: a linha de outra largura não é cartão · obtido: rc 0, linha de 6 colunas intacta

## Parecer
**Aprovado.** Os achados do parecer anterior estão resolvidos no head:
- **A1 (bloqueante):** `celulas_de_cartao` (`bin/forge-check:5073`) é agora o filtro único de linha de cartão (cabeçalho, separador, outra largura, fora de tabela), usado pelo quadro gerado, pelo aviso de edição à mão e pelo movimento; S1 e S2 não reproduzem mais. Teste com `ID`, `id` e `---` e mutantes AE19, AE20 e AE28 declarados.
- **A2:** todas as linhas do cartão saem (`reversed(achadas)`), a última achada é a que anda (S3; AE21, AE31).
- **A3:** o aviso passa por `tr -d '[:cntrl:]'`; o teste prova que o ESC não chega à saída (AE24).
- **A4:** cartão do corpo com coluna `—` só avisa; cartão novo nasce só pelo `--cartao` (AE25). O caso de borda `ID` que ainda passa ficou no A1 acima, recomendado: precisa de um corpo de PR com `Cartão: ID` e não corrompe o quadro (S1), só cria um cartão a mais.
- **UTF-8 inválido** (A4 da segurança): leitura estrita só no movimento; o `kanban --gerar` segue com `replace`, como antes. Só avisa, com rc 0 e o quadro intacto (S4).
- `erro_dos_atributos` deixa de listar `·` na recusa do `--titulo` e mantém a recusa; a garantia descrita no parecer anterior continua a mesma.

Ferramentas: `forge-mutante --conferir --base cbf24de5`: specs no lugar. `--cobertura --base cbf24de5`: toda condição mudada em `bin/forge-check` tem mutante declarado; `bin/forge-fechar` sai "não coberto" pela ferramenta, mas as duas guardas novas têm AE24 e AE25. Rodei AE19, AE20, AE21, AE25 e AE28: todos morreram. Testes do item no head: `test_sobreposicao_quadro` e `test_fechar_move_cartao`, 96 OK. Não há `shellcheck` nesta máquina; o CI decide. CI do PR na leitura: instalação e bateria verdes, a suíte (parte 5/5) ainda pendente; a suíte inteira fica com ele. Tamanho (H1): o delta soma cerca de 30 linhas de código, dentro do teto. Commit único `fix(movimento)`, Conventional Commits em português; `fechamento-integrador.md`, `kanban-scrum` e o fragmento do changelog acompanham.

A1 não devolve: vira cartão depois do merge.
