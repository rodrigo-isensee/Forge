---
tipo: revisao-seguranca
contrato: 1
pedido: lote-fechar2
branch: melhoria/lote-fechar2
commit: 7c926e42a3a6b333c46bf4967dadac9e18724f5b
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-26
---
# Review de segurança: lote-fechar2 (revalidação, volta 2)

Escopo: revalidação por delta do parecer anterior (commit revisado `0315561`, parecer `2dc5cb2`) até `7c926e4`, pela decisão B do dono (2026-10-26): `bin/forge-fechar:136-141` (validação do sha no ajudante `remoto_exato`, entrou em `403bdc1`), `tests/test_fechar.py:594`, `tests/test_fechar_base_andou.py`, `tests/mutantes/lote-fechar2.json`, `tests/mutantes/lote-fechar2-2.json`, `changelog.d/lote-fechar2.md`. O intervalo pedido no brief, `68f1006..7c926e4`, não toca `bin/forge-fechar` nem `.github/` (só testes, mutantes e pareceres de outros papéis).

## Gatilhos
Controle do Forge (`R-SEGURANCA`): o `forge-fechar` decide abrir e mesclar o PR (passo 2 e passo 2b) e apagar a branch remota (limpeza).

## Achados

## Detalhe dos achados
Sem bloqueante e sem recomendação nova. Verificações, com evidência:

1. **Validação da coluna 1 (a recomendação do parecer anterior, implementada em `bin/forge-fechar:141`).** A linha com a coluna 2 exata só devolve a coluna 1 se ela tem 40 ou 64 caracteres em `[0-9a-f]`; senão o `awk` sai com rc 1, e os quatro chamadores tratam rc 1 como leitura que falhou, em falha fechada: passo 2 para (`:600`), passo 2b para (`:514`), limpeza deixa a branch remota `pendente` sem apagar (`:462-464`) e a conferência depois do delete falho também a deixa `pendente` (`:475`, ramo `else`). Sonda local (código mudou desde o parecer anterior) em `gawk` 5.3 e `mawk`: sha válido sai com rc 0; maiúsculas, hexadecimal curto, `z`x40 e 120 caracteres saem com rc 1 e sem saída; nome diferente, entrada vazia e coluna 2 com `\r` saem vazios com rc 0 (ausente, como antes). O `END { exit ruim }` com `ruim` não inicializado sai 0, então ref ausente continua distinta de leitura falha. `busybox awk` não estava no ambiente.
2. **Nenhuma asserção afrouxou.** `tests/test_fechar.py:594` tirou o filtro `"printf" not in l`: a contagem passa a ver mais linhas, então o teste ficou mais estrito, não mais frouxo. O mutante M1 de `tests/mutantes/lote-fechar2.json:9-10` mudou só o trecho para casar o `awk` novo e continua tirando o filtro da coluna 2 (mesma guarda). Os testes de `tests/test_fechar_base_andou.py` só foram acrescentados (`criss_cross` ganhou o parâmetro opcional `arquivos`, padrão `False`, que mantém o teste anterior igual).
3. **Laço sobre todos os pontos de partida (`bin/forge-fechar:526`) e guardas finais (`:533`, `:536`).** O teste novo `test_arquivo_em_comum_so_no_diff_do_segundo_ponto_de_partida_para_e_lista_os_dois` monta um criss-cross com um arquivo por ponto de partida e exige rc 1, os dois arquivos listados e nenhum PR criado nem mesclado. Rodei `bin/forge-mutante tests/mutantes/lote-fechar2-2.json` neste commit: M1 a M5 morreram (`:527`, `:528`, `:526`, `:533`, `:536`). O módulo `tests.test_fechar_base_andou` (17 testes) e os testes `lsremote` e `shellcheck` de `tests.test_fechar` (6) passaram; `shellcheck bin/forge-fechar` limpo (rc 0).
4. **Superfície nova dos testes.** O `comm` e o `git` falsos (`tests/test_fechar_base_andou.py:12-29`) só existem no PATH temporário da suíte e não chegam ao script de produção.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `shellcheck`, `gawk`, `mawk`, `bin/forge-mutante` e `forge-check delta`, todos locais. Faltaram no ambiente, e ficam como lacuna: `gitleaks`, `zizmor` e `actionlint` (o delta não traz credencial nem mudança de workflow).
