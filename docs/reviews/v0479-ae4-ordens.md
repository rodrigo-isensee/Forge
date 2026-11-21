---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae4-ordens
commit: df0cf4d96cdf642b624c1468245010619410d9d1
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0479-ae4-ordens

Code review do AE4.1 no head 18d6d2f4 (branch melhoria/v0479-ae4-ordens, base develop 821db42e), v0478 E58.71, contra o desenho `docs/propostas/v0479-melhorias-anti-erro.md` (AE4, opção a).

## Achados
- A1 (recomendado) bin/forge-check:10260 · o subparser `ordens` (3 linhas) entrou no meio dos argumentos do `decisoes`: o `de.add_argument("--resposta", ...)` da linha 10263 ficou depois dele; mova o bloco `od` para depois do `--resposta`, sem mudar comportamento.

## Parecer
Aprovado (revalidação no head df0cf4d9, v0478 E58.91; o A1 recomendado segue para cartão).

## Revalidação (head df0cf4d9)
- Delta lido: `forge-check parecer delta docs/reviews/v0479-ae4-ordens.md`, intervalo b1cd22ec..df0cf4d9, no domínio: `agents/jarvis.md`, `bin/forge-check`, `bin/forge-testes`, `tests/mutantes/est-m12-gerar.json`, `tests/pesos-d4.json`, `tests/test_anotar.py`. Separado da develop por `git diff c9d69234 HEAD`: `bin/forge-check`, `bin/forge-testes`, `tests/pesos-d4.json` e o trecho novo de `test_anotar.py` vieram do merge da develop (27596e7d), sem resolução à mão no domínio; do item, só `agents/jarvis.md` e `est-m12-gerar.json` (df0cf4d9). Nada fora disso relido.
- `agents/jarvis.md:13`: `; a ordem leva` virou `; ordem com`, mesmo sentido, linha 3 caracteres menor (287 para 284 bytes).
- `tests/mutantes/est-m12-gerar.json` M3: o `de` acompanha a guarda reindentada em `bin/forge-check:4893` (fora do `fdopen`); `bin/forge-mutante --processos 1 --rev df0cf4d9 --ids M3`: `M3 · morreu · bin/forge-check:4893`.
- Testes (ambiente limpo, `env -i`, TMPDIR em /dev/shm): `python3 -m unittest tests.test_ordens tests.test_anotar tests.test_orcamento_instrucao tests.test_metricas_texto`: `Ran 47 tests ... OK`.
- Suíte inteira: fica com o CI do PR (`R-REVIEW`).

## Revalidação (head b1cd22ec)
- Delta lido: `forge-check parecer delta docs/reviews/v0479-ae4-ordens.md`, intervalo 916ccb02..b1cd22ec, no domínio: `bin/forge-check`, `changelog.d/v0479-ae4-ordens.md`, `tests/mutantes/v0479-ae4-ordens-4.json`, `tests/test_ordens.py`. Nada fora disso relido.
- `_ler_regular` (bin/forge-check:4841-4853): o `fstat` sai de dentro do `fdopen` e vem antes dele, fechando o fd no ramo de recusa; pasta no lugar do quadro dá "não é arquivo regular" em vez de `IsADirectoryError` (A3). O outro chamador, `cmd_kanban_gerar` (4887), já trata o `erro` e deixa o quadro intacto com rc 1.
- `recusa_do_apontador` (5043): texto com U+FFFD recusa "KANBAN.md fora de UTF-8" antes do parse (A4); desfaz a troca aceita na revalidação anterior, agora pelo lado seguro. Um quadro UTF-8 válido que traga U+FFFD literal também recusa: aceito, a saída indica a etapa `E<n>`.
- Funções de módulo sem nome repetido: `grep -oE '^def [A-Za-z_0-9]+' bin/forge-check | sort | uniq -d` vazio.
- Tamanho (H1): 6+/3- em `bin/forge-check`.
- Testes (ambiente limpo, `env -i`, TMPDIR em /dev/shm): `python3 -m unittest tests.test_ordens tests.test_anotar tests.test_decisoes`: `Ran 47 tests ... OK`; `test_quadro_pasta_recusa_com_rc_2` e `test_quadro_fora_de_utf8_recusa` verdes, por comportamento (rc e texto da recusa).
- Mutantes: `bin/forge-mutante --processos 1 --rev b1cd22ec tests/mutantes/v0479-ae4-ordens-4.json`: M25 `morreu` (4847), M26 `morreu` (5043). `--cobertura --base 916ccb02`: 5043 coberta (M26); a 4847 não aparece na cobertura (guarda movida, mesmo texto), mas tem o M25 declarado e morto.
- Suíte inteira: fica com o CI do PR (`R-REVIEW`).

## Revalidação (head 916ccb02)
- Delta lido: `forge-check parecer delta docs/reviews/v0479-ae4-ordens.md`, intervalo 18d6d2f4..916ccb02, no domínio: `bin/forge-check`, `changelog.d/v0479-ae4-ordens.md`, `docs/propostas/v0479-melhorias-anti-erro.md`, as 3 specs de mutantes, `tests/test_decisoes.py`, `tests/test_ordens.py`. Nada fora disso relido.
- `recusa_do_apontador` (bin/forge-check:5033-5051) abre o KANBAN.md uma vez por `_ler_regular` (O_NOFOLLOW, O_NONBLOCK, fstat de arquivo regular, teto `TETO_DA_TABELA`), o mesmo leitor já usado pelo quadro (4886); `quadro_do_texto` separa o parse do `quadro_por_coluna`, que segue com a mesma saída. Cartão de outro pedido (coluna Pedido por `id_do_pedido`, comparada a `id_do_pedido(arq.name)`) recusa (A2 da segurança).
- Mudança de comportamento declarada: KANBAN.md fora de UTF-8 passa a ser lido com troca de caracteres (`errors="replace"`) em vez de recusar. Aceita: a leitura só confere; byte inválido no ID não casa e cai em `cartão fora do KANBAN.md`, sem gravar.
- Funções de módulo sem nome repetido: `grep -oP '^def \K\w+' bin/forge-check | sort | uniq -d` vazio.
- Tamanho (H1): 31 linhas mudadas em `bin/forge-check` no delta.
- Testes com `git init` na raiz temporária (ambiente limpo), rodados aqui com TMPDIR fora de repositório git: `python3 -m unittest tests.test_ordens tests.test_anotar tests.test_decisoes`: `Ran 45 tests ... OK`.
- Mutantes: `bin/forge-mutante --processos 1 --rev 916ccb02` nas 3 specs: M1 a M24 `morreu` (M24 por erro do teste sob o mutante: a leitura do FIFO trava e estoura o timeout de 20 s, que é a prova). `--cobertura --base 18d6d2f4`: guardas mudadas cobertas (M7, M9, M23); a guarda `is_symlink` apagada virou o O_NOFOLLOW do `_ler_regular` (M6).
- Suíte inteira: fica com o CI do PR (`R-REVIEW`).

- Desenho (AE4 a): `forge-check ordens [--pedido] [--desde]` reusa `cmd_decisoes` com `frase` ORDEM DO DONO e `linhas_sem_cartao` com `etapas` (bin/forge-check:7849-7896); `registro_da_frase` gera o padrão das duas frases, e `DECISAO_DO_REGISTRO` segue o mesmo (7505-7510). Nenhuma lógica de cruzamento nova; a marca `· cartão: <ID|E<n>>` no fim da linha é o apontador da ordem, e a etapa do pedido vale como cartão.
- `anotar --tipo ordem` exige `--cartao` no formato `APONTADOR` (5062), confere em `recusa_do_apontador` (5028-5043) contra as etapas (`E5` não casa `E51.1`, `e_etapa_do_pedido`) ou o KANBAN.md da raiz do pedido (link simbólico e quadro ilegível recusam; `Fechado sem entrega` recusa) e grava a marca no fim (5098). `--cartao` fora da ordem recusa, como o `--confere` (E8). A recusa não grava (teste confere o arquivo intacto); a quebra de linha no `--cartao` cai no `fullmatch`.
- Decisões não mudam: `decisoes --sem-cartao` não lê a marca (`etapas is None`), coberto por `test_decisoes_seguem_sem_as_ordens`; `test_anotar` passa `cartao="E1.1"` só para a ordem.
- Funções de módulo sem nome repetido: `grep -oP '^def \K\w+' bin/forge-check | sort | uniq -d` vazio.
- Tamanho (H1): 73+/22- em `bin/forge-check`, 1/1 em `bin/forge-testes` e `agents/jarvis.md`, abaixo do teto de 150; um comportamento (ordem aponta para cartão: listar e exigir).
- `agents/jarvis.md:13`: só o trecho `; a ordem leva --cartao <ID|E<n>>`; `test_jarvis_nucleo` verde (teto). Neutralidade verde.
- Testes: `tests/test_ordens.py` cobre listagem (sem-cartao, sem-id, aviso, `--desde`) e cada ramo de recusa do anotar por comportamento, com subprocesso de ambiente limpo e `-I`; registrado em `bin/forge-testes` (FORGE_CHECK) e em `tests/pesos-d4.json`.
- Mutantes: 21 declarados em 3 specs (8+8+5), um por guarda mudada; `bin/forge-mutante --processos 1` nas 3 specs no rev 18d6d2f4: M1 a M21 `morreu`, nenhum sobrevivente.
- Rodado aqui (ambiente limpo): `python3 -m unittest tests.test_ordens tests.test_anotar tests.test_decisoes tests.test_jarvis_nucleo tests.test_forge.Neutralidade`: `Ran 88 tests ... OK`. Suíte inteira: fica com o CI do PR (`R-REVIEW`).
- Fragmento `changelog.d/v0479-ae4-ordens.md` presente, em português.
