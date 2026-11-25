---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-perfil-fifo
commit: dba51ddfb97745dfcab0f74df93471e376aaf8fc
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: v0481 (E7.17 e E7.21), #886: texto da recusa sem FIFO no perfil nem git

Classe C, correção sem especificação de UX nova (sem plano antecipado). Obrigações: `R-VERIFY`, `R-MAIN`, ADR 0003 (fixtures), A2 e S3 da segurança no #885: com FIFO em `.forge/perfil`, a recusa sai com a regra certa, sem esperar, e o prazo vencido na escolha do texto não vira liberação.

## Achados
- A1 (recomendado) hooks/conformidade.py:1582 · `Hook.iniciante` (read_text) ainda espera o FIFO em `perguntar` e na guarda de escrita do perfil (1740): 3 s e, no projeto, recusa "não decidiu"; na sessão do Forge a escrita ao perfil libera após 3 s. Item próprio.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Push na main, `--force`, `--no-verify` recusam com a regra certa, FIFO no perfil, sessões Forge e projeto | `RecusaComFifoNoPerfil.test_recusa_com_a_regra_dela_e_sem_prazo_vencido` (6 subtestes) | FIFO no perfil, sem `não decidiu` | passou |
| Leitura do perfil não espera o FIFO nem chama git | `test_fifo_no_perfil_nao_espera_e_vale_experiente` (alarme 5 s, Popen proibido) | FIFO; valor `Iniciante` com caixa | passou |
| Worktree com FIFO lê o perfil da cópia principal, sem git | `test_worktree_com_fifo_le_o_perfil_da_copia_principal` | FIFO na cópia, perfil na principal | passou |
| Prazo vencido na escolha do texto cai no texto técnico e a recusa segue | `test_prazo_vencido_na_escolha_do_texto_recusa_com_o_texto_tecnico` + fixture `trava-prazo-no-perfil-bloqueia-iniciante` | prazo forçado em `perfil_iniciante` | passou |
| Nada deixa de barrar; iniciante ainda recebe o texto simples | `test_perfil_iniciante_recebe_o_texto_simples` | perfil regular, `iniciante` | passou |

## Cenários e resultado real
- Classe rodada (não o módulo inteiro): `python3 -m unittest tests.test_hooks.RecusaComFifoNoPerfil` -> `Ran 5 tests ... OK` (1,4 s).
- Vermelho antes do verde, à mão (o `forge-testes --vermelho` com `--modulos test_hooks` roda o módulo inteiro, fora do que o brief permite; sem `--modulos`, estourou meu prazo de 580 s sem veredito, então não vale): cópia em `$TMPDIR` com `hooks/conformidade.py` da base `5fb8e328`: `Ran 5 tests ... FAILED (failures=4, errors=2)`. Os 4 subtestes de push na main e `--force` (Forge e projeto) falham; `perfil_iniciante` ausente derruba 2 testes por `AttributeError`. O `--no-verify` já passava na base.
- Mutação: `bin/forge-mutante tests/mutantes/v0481-perfil-fifo.json --processos 2` -> rc 0, M1 a M7 `morreu` (linhas 1516, 1519, 1523, 1524, 1573, 1575, 1577). `forge-mutante --cobertura --base 5fb8e328`: as 5 condições do diff `coberta`, nenhuma `não coberta`. Sem mutante: o limite de 64 bytes (`os.read(fd, 64)`), que não muda o resultado de nenhum valor lido (sem consequência na decisão).
- Sonda extra (arquivo `sonda_fifo.py` no scratchpad, contra a árvore do PR), FIFO em `.forge/perfil`: push na main (R-MAIN), `--force` e `--no-verify` (R-VERIFY) recusam com a regra certa, 0,2 a 0,3 s, nas duas sessões. Controle com perfil regular `experiente` e `iniciante`: mesmas decisões de antes, `git reset --hard` pergunta só no projeto iniciante.
- Resíduo (A1): ainda com FIFO, `git reset --hard` no projeto recusa em 3,2 s por "não decidiu" (perfil experiente liberaria; falha fechada) e `Write` em `.forge/perfil` leva 3,2 s (Forge: libera; projeto: recusa por prazo). Nenhuma recusa que existia deixou de existir; o resíduo é o `Hook.iniciante` que o item deixou de fora, então não bloqueia este PR. Resposta ao brief: não precisa entrar neste item, mas pede cartão próprio (trocar `Hook.iniciante` pela mesma leitura sem espera e decidir o prazo vencido nesses dois pontos).
- CI do sha 8dfe968f: `bateria (python 3.14)` success (check-run 138975314335), suítes 3.12 e 3.14 verdes, tetos de pulados verdes. `bateria (pareceres)` e `catraca` falham no mesmo run do sha: não li o log (cache de `gh` somente leitura); `bateria (pareceres)` é o esperado antes dos pareceres desta etapa. Quem mescla confere os dois depois dos pareceres.

## Delta E7.21 (de 8dfe968f a 517f80fd)
`git diff 8dfe968f..517f80fd`: `hooks/_comum.py` ganha `ler_marca_do_git` (O_NONBLOCK, só arquivo regular, até 4096 bytes), usada por `diretorio_comum` no `.git`, `gitdir` e `commondir`; `tests/test_hooks.py` tira o `skipUnless` da classe e ganha dois testes; `tests/mutantes/v0481-perfil-fifo-2.json` (M8, M9); fragmento do changelog. Obrigação nova: FIFO em `.git`, `gitdir` ou `commondir` da worktree não espera e não vale (A1 da segurança no #886). As obrigações acima seguem.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| `.git` da worktree que é FIFO não trava | `test_fifo_no_ponto_git_da_worktree_nao_espera` | FIFO em `.git` | passou |
| FIFO com conteúdo certo no `gitdir` não vale | `test_fifo_com_conteudo_no_gitdir_nao_vale` | só arquivo regular | passou |

- Classe: `python3 -m unittest tests.test_hooks.RecusaComFifoNoPerfil` -> `Ran 7 tests ... OK` (1,5 s).
- Vermelho (à mão, cópia em `$TMPDIR` do head com `hooks/_comum.py` de `8dfe968f`): os dois testes novos -> `Ran 2 tests ... FAILED (failures=2)`, "a leitura do perfil esperou o FIFO" (10 s).
- Mutação: `bin/forge-mutante tests/mutantes/v0481-perfil-fifo.json tests/mutantes/v0481-perfil-fifo-2.json --processos 2` -> M1 a M9 `morreu` (M8 `_comum.py:156`, M9 `_comum.py:158`), rc 0. `--cobertura --base 5fb8e328`: `_comum.py:158` e as 5 linhas de `conformidade.py` `coberta`; nenhuma `não coberta`. A linha 156 (`os.open`) não é condição Python, e M8 a cobre.
- Sonda (`sonda_fifo.py`, FIFO em `.forge/perfil`, árvore do head): push na main, `--force` e `--no-verify` recusam com a regra certa em 0,1 a 0,2 s nas duas sessões; igual à rodada anterior, o resíduo A1 (`Hook.iniciante`: `reset --hard` no projeto e `Write` no perfil, 3,1 s) segue, sem mudança.
- Catraca: `catraca.forca_dos_testes` por AST, (asserções, pulos, vazios): base `5fb8e328` (17169, 38, 0); `8dfe968f` (17178, 39, 0); `517f80fd` (17183, 38, 0). Os pulos voltaram a 38 e nenhum teste perdeu asserção. No CI do sha `517f80fd` o check `catraca` está `failure` (check-run 138979586409); não li o log (cache do `gh` somente leitura), então não atribuo a causa; quem mescla confere o log. `bateria (pareceres)` também falha, esperado até os pareceres desta etapa entrarem. As suítes 3.12 e 3.14 estavam em andamento na leitura.

## Delta E7.34 (de afa98e1a a dba51ddf)
`git diff afa98e1a..dba51ddf`: um arquivo, `tests/mutantes/v0475-mp1-mp7.json`, só o `de` e o `para` da M3. `hooks/` e `tests/test_*.py` não mudaram; os testes da M3 são os mesmos dois (`test_ativos_em_link_fifo_grande_ou_com_nomes_demais_nao_mede`, `test_ativos_em_fifo_com_escritor_e_json_valido_nao_vale`) e a guarda é a mesma (`hooks/_comum.py:123`, `if not stat.S_ISREG(os.fstat(fd).st_mode):` seguido de `return None`). Obrigação: a M3 aplica (trecho único) e morre, sem mexer em guarda (A2 da segurança).

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| O par `if ... S_ISREG ...:` mais `return None` aparece uma vez em `_comum.py` | contagem do par no head: 1 (o `if` sozinho aparece 2) | trecho único do `de` | passou |
| A M3 morre | `bin/forge-mutante tests/mutantes/v0475-mp1-mp7.json --ids M3` | só arquivo regular é lido | `M3 · morreu · hooks/_comum.py:123`, rc 0 |
| `--conferir --todas` não piora | `bin/forge-mutante --conferir --todas` no head, na base `5fb8e328` e em `afa98e1a` | spec com trecho no lugar | head igual à base `5fb8e328` (diff vazio); contra `afa98e1a` só some a linha da M3 ("aparece 2 vezes") |

- As demais linhas que o `--conferir --todas` lista (v0451-n1n3 A5, v0457-escopo-ponto-3 M17 e M20, z075-prepush-relogio M1 e M2) são as mesmas da base e de outros pedidos.
- ci: head `dba51ddf`, check-runs: suíte 3.12 e 3.14 (partes 1 a 5) success (a parte 4/5, que caía por A2, passa), teto de pulados 3.12 e 3.14 success, bateria (python 3.14) success, bateria (verificações longas) success. Falham `bateria (pareceres)` (esperado até este parecer entrar), `catraca` (log lido: só o rótulo `afrouxa-regra` do dono para `hooks/_comum.py` e `hooks/conformidade.py`, ADR 0008; decisão do dono, não defeito) e o agregado `bateria`, que depende deles. As partes que contam para o meu domínio estão verdes.
- Sem achado novo. O A1 do parecer anterior (`Hook.iniciante`) segue recomendado, para cartão depois do merge.
