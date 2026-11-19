---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-conformidade
commit: bdbdc257dd492ee2ec6f79af7614b3a5d82e57e2
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0478 (E1: AGENTES-JSON-SEM-GUARDA e CONFIG-TETO-SEM-GUARDA, parte do hook)

Diff contra a base 4182a6b9: `hooks/conformidade.py` (`GuardaDaProva` com `no_clone`, `ESTADO_DOS_HOOKS`, `ESTADO_NO_TEXTO`), comentário em `hooks/agentes.py`, 6 fixtures `estadoclone-*`, `tests/test_conformidade_verde.py` (classes `EstadoDoAgentesNoClone` e `ConfigDoTetoNoClone`), duas specs de mutantes e o fragmento de changelog. A suíte inteira não rodou aqui (fica no CI do PR; cite o check-run `bateria` do mesmo sha).

## Achados
- A1 (recomendado) tests/mutantes/z075-uma-delegacao-por-branch.json:1 · M12 (hooks/agentes.py:784, `if False`) sobrevive e M3, M6 e M7 saem inválidos (trecho 2 vezes). Igual no base b0ffec8, fora do delta: vira cartão, não bloqueia.

## Critério → teste → resultado
Sem especificação de UX; as obrigações vêm do escopo E1 do pedido (C9 e C10 do modelo de ameaças).

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: escrita, remoção e link no estado `.git/forge/` recusam para todo papel no clone (jarvis incluído) | `EstadoDoAgentesNoClone.test_escrita_remocao_e_link_no_estado_recusam_para_todo_papel`, `test_de_fora_do_clone_pelo_caminho_absoluto_recusa` | pasta corrente fora do clone, caminho absoluto, Write e Edit | passou |
| C10: linha que o hook não lê e cita o estado recusa (falha fechada) | `test_linha_que_o_hook_nao_le_e_cita_o_estado_recusa`, `test_linha_que_o_hook_nao_le_e_cita_o_config_recusa` | teto de 5001 palavras, barra final, aspa aberta | passou |
| A prova da suíte do pre-push (nome com prefixo parecido ao do estado) segue com a recusa R-VERIFY | `test_prova_da_suite_na_linha_que_o_hook_nao_le_segue_com_a_recusa_propria` | nome inteiro `.git/forge` contra prefixo | passou |
| Leitura e resto do clone livres | `test_leitura_e_resto_do_clone_seguem_livres` | cat, ls, Write em docs, `$d` sem citar o estado | passou |
| Fora do clone do Forge a guarda não se estende | `test_fora_do_clone_do_forge_a_guarda_nao_se_estende` | sem `plugin.json` | passou |
| CONFIG-TETO: escrita em `.forge/config.json` da raiz recusa para todo papel | `ConfigDoTetoNoClone.test_escrita_no_config_da_raiz_recusa_para_todo_papel` | Bash, Write, Edit, `rm -rf .forge` | passou |
| CONFIG-TETO: modelo `templates/projeto/.forge/config.json` e config de outra pasta livres; leitura livre | `test_modelo_e_config_de_outra_pasta_seguem_livres` | caminho fora da raiz da sessão | passou |
| Regressão do padrão: linha ilegível com heredoc segue bloqueando (R-VERIFY) | fixtures `rverify-fp-verdadeiro-linha-ilegivel-*` (4) | barra no fim, case, chaves, crase | passou |
| Fixtures novas do clone | `estadoclone-*` (6: 4 libera, 2 bloqueia) | n/a | passou |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_conformidade_verde.py`: Ran 25 tests, OK (122 s).
- Fixtures por `executar_em_lote` (4 `rverify-fp-verdadeiro-linha-ilegivel-*` mais 6 `estadoclone-*`): 10 de 10, OK.
- Vermelho antes do verde: `forge-testes --vermelho 4182a6b9` estourou meu prazo (rc=124, sem veredito; não conta). Refeito à mão numa cópia em `$TMPDIR` com os testes do head e `hooks/conformidade.py` e `hooks/agentes.py` da base: `Ran 9 tests, FAILED (failures=5)`: `test_escrita_no_config_da_raiz_recusa_para_todo_papel`, `test_linha_que_o_hook_nao_le_e_cita_o_config_recusa`, `test_de_fora_do_clone_pelo_caminho_absoluto_recusa`, `test_escrita_remocao_e_link_no_estado_recusam_para_todo_papel`, `test_linha_que_o_hook_nao_le_e_cita_o_estado_recusa`. Os 4 testes de "livre" passam na base, como esperado.
- Mutação: `forge-mutante --cobertura --base 4182a6b9` lista as condições mudadas (3511 a 3562) como cobertas por M1 a M14. `forge-mutante` das duas specs (`--processos 4`): M1 a M14 todos `morreu`, nenhum sobrevivente.
- Exploração fora dos testes do autor (jarvis e tech-lead, todos rc 2): `cd .git && echo x > forge/run/agentes.json`, `tee`, `cp`, `sed -i`, `os.remove` em python, `cd .forge && echo > config.json`, `.forge/../.forge/config.json`, `./.forge//config.json`, `mv .forge/config.json`.
- Sem skip, skipIf nem expectedFailure no código novo.

## Revalidação incremental (head b3312958, base aprovada b0ffec81)
`forge-check parecer delta` lista no domínio: `hooks/agentes.py` (`pasta_da_config`), `hooks/conformidade.py` (find, tar, chmod e afins; config da raiz), `tests/test_conformidade_verde.py`, specs de mutantes 3 a 6 (M15 a M45), duas specs editadas, `docs/hooks.md` e o changelog.
- `python3 -I -m unittest discover -s tests -p test_conformidade_verde.py`: Ran 32 tests, OK (169 s). Não rodei `tests.test_hooks` inteiro (máquina carregada).
- Vermelho antes do verde (cópia em `$TMPDIR` com os testes do head e `hooks/conformidade.py` e `hooks/agentes.py` de b0ffec8): `Ran 7 tests, FAILED (failures=5)`: `test_sessao_e_pasta_corrente_na_mesma_raiz_nao_consultam_o_clone`, `test_sessao_na_worktree_le_o_config_dela`, `test_teto_da_worktree_nao_vale_com_a_sessao_no_clone`, `test_find_tar_e_chmod_no_config_da_raiz_recusam`, `test_comando_que_escreve_ou_remove_por_opcao_recusa`; os 2 de "livre" passam na base, como esperado.
- Mutação: `forge-mutante --processos 2` nas specs 3 a 6 (rev=b3312958a3c2): M15 a M45 todos `morreu`, nenhum sobrevivente, nenhum inválido. `--cobertura --base b0ffec81`: só linhas `coberta`; as duas specs editadas (`v047-hook-estado-ilegivel-2` e `z075`) avisadas como editadas. `v047-hook-estado-ilegivel-2`: M9 a M16 `morreu`. `z075` com o mutante editado (M1 e M2) `morreu`; ver A1 para os demais.
- Sem skip, skipIf nem expectedFailure no delta.

## Revalidação incremental (head 848dd5ec, base aprovada b3312958)
Delta no domínio: `hooks/agentes.py` (`pasta_da_config` basta a sessão no clone; cache zerado em `ler_config`), `hooks/conformidade.py` (`ler_opcoes`, `EXTRATORES`: tar, bsdtar, gtar, cpio, unzip, 7z e o applet repassado), `tests/test_conformidade_verde.py`, specs de mutantes 3 a 9, `docs/hooks.md` e changelog.
- `python3 -I -m unittest discover -s tests -p test_conformidade_verde.py`: Ran 34 tests, OK (209 s). Não rodei `tests.test_hooks` inteiro (máquina carregada).
- Vermelho antes do verde (cópia em `$TMPDIR` com `hooks/conformidade.py` e `hooks/agentes.py` de b3312958, testes do head): `Ran 3 tests, FAILED (failures=2)`: `test_extrator_e_tar_por_opcao_recusam` e `test_versao_na_worktree_nao_deixa_o_config_dela_no_cache`; o teste de "livre" passa na base, como esperado.
- Mutação: `forge-mutante --processos 2 --base b3312958 <specs 3 a 9>` (`base=b3312958 rev=848dd5ecd7bc`): M15 a M65 todos `morreu`, nenhum sobrevivente, nenhum inválido. `--cobertura --base b3312958`: só `coberta`, mais `spec editada` (specs 3 a 6) e `apagada` (linhas do `alvos_do_tar` antigo, substituído por `ler_opcoes`).
- Casos legítimos pelo hook direto: `unzip -l`, `7z l`, `cpio -it` rc 0; `tar -xf a.tar -C docs` recusa por `docs/security/aceites/` (guarda própria, R-SEGURANCA), não por falso positivo do extrator. Os casos livres do teste (`unzip -d docs`, `cpio -id` em docs, `7z x -odocs`, `ls` pelo applet, `-- -C.git/forge`) passam.
- Sem skip, skipIf nem expectedFailure no delta. O remoto avançou (c42b8d97, só o parecer de segurança); trazido por fast-forward.

## Revalidação incremental (head bdbdc257, base aprovada 848dd5ec)
Delta no domínio: `hooks/conformidade.py` (catálogo `DESTINOS`: `--one-top-level=`, `--transform`/`--xform`, `--volno-file`, `--cd` e `-s` do bsdtar, `-w` e `-u…!` do 7z, chaves do 7z em qualquer caixa, toybox como o busybox), `tests/test_conformidade_verde.py` (classe `CatalogoDosDestinos`, `test_opcoes_do_catalogo_recusam` e `..._fora_do_estado_seguem_livres`), specs de mutantes 6 a 9 editadas e a 10 nova, `docs/hooks.md` e changelog.
- `python3 -I -m unittest discover -s tests -p test_conformidade_verde.py -k CatalogoDosDestinos -k EstadoDoAgentesNoClone`: Ran 14 tests, OK (29 s). Não rodei `tests.test_hooks` inteiro nem a suíte (CI do PR).
- Vermelho antes do verde (cópia em `$TMPDIR` com os testes do head e `hooks/conformidade.py` e `hooks/agentes.py` de 848dd5ec): `Ran 5 tests, FAILED (failures=3)`: `test_toda_opcao_de_caminho_da_ajuda_do_tar_esta_no_catalogo`, `test_toda_opcao_do_catalogo_do_tar_existe_na_ajuda`, `test_opcoes_do_catalogo_recusam`; os de "livre" e o do `--one-top-level` real do tar passam na base, como esperado.
- Mutação: `forge-mutante --processos 3` nas specs 6 a 10 (`rev=bdbdc257dd49`): 33 linhas, M39 a M71 todas `morreu`, nenhum sobrevivente, nenhum inválido, rc 0. `--cobertura --base 848dd5ec`: só `coberta` e `spec editada` (specs 6 a 9, editadas e rerrodadas acima); cada guarda nova (1148 a 1200, 2292) tem mutante.
- Guarda contra suíte vazia: os testes da ajuda do tar afirmam mínimo (20 opções de caminho, 25 no catálogo). Há um único `skipTest`, condicional à ausência do GNU tar no PATH e com o motivo; aqui o GNU tar 1.35 existe e os 3 testes rodaram (não pularam).
- O remoto avançou (6a3e3983, só o parecer de segurança); trazido por fast-forward, sem mudança de código.
