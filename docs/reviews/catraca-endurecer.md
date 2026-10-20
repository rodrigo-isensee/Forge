---
tipo: review
contrato: 1
pedido: catraca-endurecer
branch: melhoria/catraca-endurecer
commit: fb5028ea246f6f884260c96ad6ed9e24019093cc
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-20
---
# Review: CATRACA-ENDURECER, falha fechada sem diff e regra de release protegida

## Revalidação por delta (volta 1, `fb5028e`)
Veredito sobre `fb5028e`: **APROVADO**. O A1 está resolvido e as recomendações R1 e R2 foram atendidas. Quem revisa não é o autor (E1.2, D-ETAPAS-INST).

- **Delta lido** (`bin/forge-check delta --parecer docs/reviews/catraca-endurecer.md`, intervalo `60328da..fb5028e`): só `tests/test_catraca.py` (+40 -3), linhas 14, 440, 445, 454-468 e 1182-1204. `tests/catraca.py` e `changelog.d/catraca-endurecer.md` não mudaram desde `60328da`.
- **Já lido** (rodada 1, sem mudança): `tests/catraca.py` inteiro do diff, o fragmento de changelog e o resto de `tests/test_catraca.py`; a seção "O que está conforme" abaixo segue valendo.
- **A1, resolvido.** `test_git_diff_falho_com_base_valida_e_rotulo_do_dono_nao_libera` (`tests/test_catraca.py:454-468`) usa base válida (dono lido do config), rótulo da dona depois do último push e `alterados` trocado por um que levanta `ErroDeDiff`; afirma rc 1, a mensagem e a ausência de "liberada". Mutação numa cópia em `$TMPDIR` (`git archive fb5028e`), tirando `or SEM_LISTA in x` de `tests/catraca.py:911`: `FAIL: test_git_diff_falho_com_base_valida_e_rotulo_do_dono_nao_libera` / `FAILED (failures=1)`, só ele. Sem a mutação: `Ran 161 tests` / `OK`. O teste antigo foi renomeado para o que prova (`test_base_inexistente_deixa_a_catraca_vermelha_mesmo_com_rotulo`).
- **R1, atendido.** `test_git_diff_falho_no_head_rotulado_nao_libera_pelo_conteudo` (`:1182-1204`) roda primeiro o controle (git funcionando, rótulo por conteúdo vale, rc 0) e depois o diff falhando só no head rotulado (rc 1 e a mensagem). O controle garante que o vermelho vem da falha de diff, não da preparação.
- **R2, atendido.** As duas linhas de preparação inútil saíram de `test_git_diff_com_erro_vira_violacao` (`:440`).
- Observação sem achado: o `addCleanup` de `:1187` usa `[...] and pasta.rmdir()`, que só apaga a pasta porque a lista não fica vazia; funciona, mas é esperto demais. Não bloqueia nem pede volta.
- Segurança (E1.3) revalida em paralelo no parecer próprio do `security-engineer`; não refeito aqui.

## Rodada 1 (`60328da`, reprovado), mantida como histórico
Escopo: `ef71b3c...60328da` (base ef71b3c08913cf119396559c23fa9b0478e4607a), 3 arquivos num commit (`tests/catraca.py`, `tests/test_catraca.py`, `changelog.d/catraca-endurecer.md`). Quem revisa não é o autor (E1.2, D-ETAPAS-INST). Comparei com o Escopo E1 a E3 do pedido e com a DECISÃO TÉCNICA do Histórico (o rótulo não libera a violação de diff).

Veredito sobre `60328da`: **REPROVADO**. O código faz o que o pedido pede e falha fechado em todos os caminhos, mas o teste que diz provar que o rótulo não libera a violação de diff passa sem a guarda que faz isso (1 bloqueante, 2 recomendados). Volta ao autor; este revisor não corrige o diff.

## Ferramentas (saída citada, não refeita)
- `python3 -m unittest tests.test_catraca` sobre `60328da` (cópia em `$TMPDIR` por `git archive`): `Ran 159 tests` / `OK`.
- Os mesmos testes com o `tests/catraca.py` de `ef71b3c` (vermelho antes do verde): `FAILED (failures=4, errors=1)`, nos 4 testes novos e no subteste `scripts/conferir-release.py`; bate com o "E1.1 ENTREGUE".
- A suíte completa e o `scripts/validar-plugin.sh` ficam com o pre-push, o QA e o CI; esta revisão não os rodou.
- Segurança (E1.3) tem parecer próprio do `security-engineer` em paralelo; não refeito aqui.

## O que está conforme
- E1, em todos os caminhos que chamam `alterados()` (`tests/catraca.py:94-100`, que agora levanta `ErroDeDiff`):
  - `regra_protegidos` e `regra_arquivos_de_regras`, por `violacoes_das_regras` (`:433-437`): a exceção vira a violação R-CONFORMIDADE com a mensagem clara (o quê, por quê, como corrigir).
  - `_violacoes_de_pareceres` (`:831-835`): o mesmo.
  - `so_troca_sha_de_acoes` (dependabot, `:816`), chamada em `_main` fora dos invólucros: propaga ao `main` (`:870-876`), que imprime e devolve 1. Antes, a lista vazia dava `False`; agora fica vermelho, o que é mais rígido.
  - O rótulo por conteúdo da S-16, em `pareceres_do_pedido` (`:500`), dentro de `rotulo_vale_pelo_conteudo`: propaga ao `main` e dá rc 1. No mesmo caminho, `violacoes_das_regras(raiz, base, sha)` com diff falho devolve só a violação de diff, então toda violação atual sai "nova" em `violacoes_novas` e o rótulo não vale. Falha fechada.
  - O caminho do PR mesclado, em `regra_protegidos` dentro de `liberado_por_pr_mesclado` (`:773`): propaga ao `main` e dá rc 1.
  - Exceção de `subprocess.TimeoutExpired` no `git()` (`:59`) segue sem tratamento: sai com traceback e código diferente de zero, que também é vermelho. Não é regressão.
- E2: `scripts/conferir-release.py` está em `PROTEGIDOS` (`:39-41`) e o subteste em `test_mudanca_em_arquivo_protegido_barra` e `test_regra_de_release_e_protegida` provam o bloqueio (vermelhos com a develop).
- A decisão de o rótulo não liberar a violação de diff está no código (`:911`, `SEM_LISTA in x` junto do `R-CUSTO:`), e a sonda abaixo confirma que a guarda funciona. O que falta é o teste (A1).
- Fragmento `changelog.d/catraca-endurecer.md` com o nome da branch, sem editar o `CHANGELOG.md`. Commit único em Conventional Commits em português. Nada custa dinheiro (R-CUSTO) e nada afrouxa: só fecha caminhos.

## Detalhe dos achados da rodada 1 (A1 resolvido em `fb5028e`)
- **A1 (bloqueante), evidência de execução.**
  - Mutação: tirei `or SEM_LISTA in x` de `tests/catraca.py:911` numa cópia em `$TMPDIR` e `tests.test_catraca` seguiu `Ran 159 tests` / `OK`.
  - Sonda com base válida (`--base HEAD`, `dono` lido do config), `catraca.alterados` trocado por um que levanta `ErroDeDiff` e rótulo da dona depois do último push. Sem a guarda: `rc 0 catraca: 1 violação(ões) liberada(s) pelo rótulo `afrouxa-regra` do dono (aplicado depois do último push).` Com a guarda (60328da): `rc 1 R-CONFORMIDADE: não consegui listar os arquivos alterados entre b e h ...`.
  - A guarda é, portanto, a única coisa que impede o rótulo de liberar a falha de diff quando o config é legível, e nenhum teste falha se ela some. Num arquivo protegido que é o próprio controle, isso bloqueia (checklist 7 e E3, "os testes provam o que dizem").
  - **Sugestão:** um teste com base válida e `dono` legível em que o diff falha (por `unittest.mock.patch.object(catraca, "alterados", ...)` levantando `ErroDeDiff`, ou trocando `catraca.git` só para o subcomando `diff`), com rótulo da dona depois do último push, e que afirme `rc == 1` e a mensagem. Confirme o vermelho tirando a guarda. O teste atual pode ficar, só com o nome ajustado ao que prova (base inexistente fica vermelha).
- **R1 (recomendado)** · `tests/test_catraca.py` · o caminho do rótulo por conteúdo (S-16) com diff falho, em `pareceres_do_pedido` e em `violacoes_das_regras(raiz, base, sha)` dentro de `rotulo_vale_pelo_conteudo`, está correto pela leitura, mas sem teste. Sugestão: um caso com `--execucoes` e o diff falhando só no SHA rotulado, que afirme rc 1. Cabe na mesma volta do A1, se o autor quiser.
- **R2 (recomendado)** · `tests/test_catraca.py:440-441` · em `test_git_diff_com_erro_vira_violacao`, escrever e commitar `tests/catraca.py` é enfeite: com a base inexistente, `regra_protegidos` sai cedo (`ler` da base dá `None`) e quem levanta é `regra_arquivos_de_regras`. O teste prova o que diz, mas a preparação sugere outro caminho. Sugestão: tirar as duas linhas ou dizer na docstring de onde vem a exceção.

## Achados
