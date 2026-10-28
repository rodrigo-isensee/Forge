---
tipo: review
contrato: 1
pedido: aq1-forge-check
branch: melhoria/aq1-forge-check
commit: 7ae7606228d7723ea4ec95919856ec919f65cbf9
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-28
---
# Review: AQ1-FORGE-CHECK, decisões do Depende de, DECISÃO TÉCNICA da recomendação, AR do QA e origem do escape

Escopo: `a83de9e...7ae7606` (base `a83de9e24908195fef0c92ebfcb1603518b58390`), 6 commits: E1 `7238a07`, E2 `e7e022d`, E3 `fec306b`, E4 `baea95b`, o merge `6bed86b` com a develop `a83de9e` e `7ae7606` (M17 a M20 e dois testes). Comparei com o Escopo E1 a E4 de `AQ1-FORGE-CHECK.md`, com as propostas P2, P3, P5 de `aq-ciclo-1-2026-10-27.md` e com as decisões do pedido (dono 14:10 e 14:34 de 2026-10-27; técnicas 15:27 e 2026-10-28 14:18). Quem revisa não é o autor.

Veredito sobre `7ae7606`: **APROVADO**. Os quatro itens fazem o que o escopo pede, os conflitos do merge mantêm as duas partes e os 20 mutantes morrem. Nenhum bloqueante; três recomendações que não devolvem.

## Ferramentas (saída citada, não refeita)
- Testes do item, na worktree em `7ae7606`: `python3 -m unittest tests.test_forge -k aq1 -k depende_de -k recomendacao_incluida -k decisao_tecnica -k origem -k gerar_copia -k achado_recorrente -k escape`: `Ran 19 tests` / `OK`; `tests.test_erros_no_brief tests.test_medidas_m14b` com os mesmos filtros: `Ran 5 tests` / `OK`.
- `bin/forge-mutante tests/mutantes/aq1-forge-check.json tests/mutantes/aq1-forge-check-2.json tests/mutantes/aq1-forge-check-3.json`: rc=0, M1 a M20 `morreu`.
- `bin/forge-mutante --cobertura --base a83de9e...`: rc=0, toda condição mudada `coberta` (nenhuma descoberta).
- `bin/forge-check docs`: rc=0; `problemas_dos_achados` sobre `docs/engineering/achados-recorrentes.md`: `[]`.
- A suíte completa e o `scripts/validar-plugin.sh` ficam com o pre-push (2198 OK no relatório da entrega) e o CI; não rodados aqui. Segurança (E2.1) e QA (E3.1) correm em paralelo, com parecer próprio; não refeitos.
- Teto M14: `git diff --numstat --no-renames a83de9e...7ae7606` em `bin/` e `tests/*.py`: 66+20 + 21+2 + 128+2 + 50+3 = 292 linhas, abaixo de 400. Nenhum arquivo de `hooks/` nem de `PROTEGIDOS`.

## O que está conforme
- **E1 (P2).** `decisoes_cobradas` (`bin/forge-check:4251-4269`) segue um nível o `Depende de:` com `dependencias_do_texto` (o leitor antigo virou duas funções sem mudar o comportamento de `dependencias_do_pedido`, `:1661-1680`), divide o `TETO_DE_FONTES` com os registros citados e não repete fonte (`vistos`). Nome fora de `REGISTRO_VALIDO` e registro ausente saem informativos; registro grande demais reprova, como no ramo do registro citado. No `-REV`, a dependência do pedido de origem entra antes do bloco G1, que a pula por `vistos`: sem fonte duplicada. Texto de `agents/conferente.md:50` e `agents/jarvis.md:65` como na proposta.
- **E2 (P5).** `tem_decisao_tecnica` (`:1316-1319`) usa a regra única `e_linha_de_decisao(..., FRASE_TECNICA)`, só no `## Histórico`, e o id como palavra inteira; `conferir_volta` (`:1477-1480`) reprova com a mensagem da proposta, com ou sem `--ref`; `gerar_volta` (`:1433-1434`) imprime o PREENCHER na forma `<tipo> <sha7> <id>`. `agents/conferente.md:49` passa a "o comando confere ... e você copia a linha dele".
- **E3 (P3, código).** `ACHADO_RECORRENTE` (`:2127`) aceita `qa` e a classe com espaços simples, até 70 caracteres e sem `·`; sondas: `Lista` (maiúscula inicial), `-x`, espaço duplo e classe com `·` são recusados; 70 caracteres passam. As 5 linhas AR são as da proposta, literais.
- **E4 (T3).** `--origem` com padrão `nao-classificado`, validado na mesma lista dos outros campos (a recusa cita o campo, não o valor); a coluna vai depois da `nota`, e `origem_do_escape` lê a linha antiga de 7 colunas e o valor desconhecido como `nao-classificado`. `docs/melhoria-continua.md:18` como na proposta.
- **Merge `6bed86b`** (`git show --remerge-diff`): em `agents/conferente.md` ficaram o "num pedido `<X>-REV` ou `<X>-PR`" e o item 3 da develop junto das frases do lote; em `agents/jarvis.md`, a linha da develop com as duas inserções do lote. O diff contra a base mostra só as frases do lote.
- **`7ae7606`.** M6 e M15 ajustados à cobertura nova da develop; M17 a M20 cobrem nome inválido, registro grande, registro ausente e contagem por origem, e os dois testes novos matam M17 e M18.
- Fragmento `changelog.d/aq1-forge-check.md`, sem tocar o `CHANGELOG.md`. Commits em Conventional Commits em português, um por item. Nada específico de projeto (`R-NEUTRO`), nada pago (`R-CUSTO`); o lote só acrescenta cobrança, nada afrouxa.
- Observação sem achado: `docs/engineering/achados-recorrentes.md:10` e `:12` ainda dizem `review|seguranca` e não listam o QA como quem escreve, embora o regex e as linhas AR-1 e AR-2 já tragam `qa`. Essa parte é o E2 do AQ1-TEXTO (`AQ1-TEXTO.md:10`), fora deste lote; o texto e o dado ficam desalinhados até ele entrar.

## Achados
- A1 (recomendado) bin/forge-check:1318 · tem_decisao_tecnica casa só o id: uma DECISÃO TÉCNICA que cita o A1 do review cobre também o A1 da segurança na mesma volta (sonda: True); exigir o tipo junto do id, na forma que o PREENCHER já pede
- A2 (recomendado) bin/forge-check:2567 · a docstring de cmd_escape_resumo e o help do resumo (:5231) ainda dizem por gravidade e controle, sem a origem que o comando agora conta
- A3 (recomendado) bin/forge-check:2508 · o cabeçalho de 8 colunas só entra no escapes.md novo; no arquivo antigo, a linha nova tem uma célula a mais que o cabeçalho e a origem some na tabela renderizada (o resumo a lê); dizer isso no texto do comando ou acrescentar a coluna ao cabeçalho antigo

## Parecer
Aprovado. Síntese por achado (nenhum devolve):
- A1 · `bin/forge-check:1318` · a cobrança da P5 é por id, como diz o escopo, mas ids repetem entre pareceres (A1 do review e A1 da segurança). Sonda: Histórico com `DECISÃO TÉCNICA ...: incluir review abc1234 A1` e `tem_decisao_tecnica(p, "A1")` devolve `True` para a recomendação da segurança. Sugestão: casar `<tipo> ... <id>` na mesma linha, o risco que a própria P5 apontou. Severidade: recomendado.
- A2 · `bin/forge-check:2567` e `:5231` · texto de ajuda desatualizado. Sugestão: acrescentar "e por origem". Severidade: recomendado.
- A3 · `bin/forge-check:2508` · arquivo de escapes existente com cabeçalho de 7 colunas. Sugestão: uma frase no texto do `escape registrar` ou atualizar o cabeçalho quando faltar a coluna. Severidade: recomendado.
