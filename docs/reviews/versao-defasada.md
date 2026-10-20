---
tipo: review
contrato: 1
pedido: versao-defasada
branch: melhoria/versao-defasada
commit: 4c078a96a811e88d4e1d8bc35b12a6b031283d9c
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-20
---
# Code review: versão defasada (E2.2, revalidação da volta 3)

Rodada 3, por delta: `136c4cb..4c078a9` (1 commit, 7 arquivos, 29+/26-). Revisor diferente do autor (D-ETAPAS-INST). A segurança de `hooks/`, `bin/` e `scripts/` é da E2.3 (`security-engineer`, R-SEGURANCA), em paralelo, e não é refeita aqui.

Delta lido (`forge-check delta --parecer docs/reviews/versao-defasada.md`, intervalo `ac07db3..4c078a9`, que inclui só o parecer anterior `136c4cb` além da volta): `docs/hooks.md:19`; `hooks/parecer.py:17,161-165,175,186`; as 3 fixtures de `tests/hooks/parecer/` (linha 68); `tests/test_forge.py:2288-2312`; `tests/test_hooks.py:288,318-332`. Já lido nas rodadas 1 e 2 e não relido: a guarda no `bin/forge-check` (`avaliar_versao`, `comparar_com_o_forge`, `comparar_com_o_cache_do_projeto`, só consultada para confirmar que o cache não depende da data), o doutor, o `jarvis-forge`, o `README.md` e o apoio `tests/apoio_versao_defasada.py`.

Ferramentas rodadas em 4c078a9 (clone local em `$TMPDIR`, para não tocar a worktree compartilhada): `python3 -m unittest tests.test_hooks tests.test_forge.HookParecerGuardaDaVersaoNoProjeto tests.test_forge.HookParecerGuardaDaVersaoNoForge` → `Ran 37 tests in 51.321s OK`. Mutação: com `guarda_de_versao(fc, raiz)` trocada por `pass` em `hooks/parecer.py`, `test_projeto_com_copia_atrasada_barra_o_pr_de_ponta_a_ponta` falha (`AssertionError: 0 != 2`, subteste `atrasada=True`). A suíte inteira e o `scripts/validar-plugin.sh` não foram refeitos (R-TETO): o autor declarou 923 OK e validar-plugin OK, e o QA os refaz no head. Shellcheck: ausente na máquina; já é critério do merge (E2.5).

## Achados

## Detalhe dos achados
**A2 (bloqueante na rodada 2): resolvido.** Com código 0 o hook `parecer` não escreve nada. `guarda_de_versao` só chama `bloquear("R-CONFORMIDADE", ...)` quando o nível é `bloqueio`, e não devolve texto. O `print` no stderr e o `import sys` saíram (não há outro `sys.` no arquivo). O runner de `tests/test_hooks.py:288` voltou ao contrato antigo: código 0 exige `stderr == ""`, sem exceção para o hook `parecer`. As 3 fixtures do clone voltaram a `codigo: 0` sem `stderr`. Nada foi afrouxado. Os testes de `HookParecerGuardaDaVersaoNoProjeto` e `...NoForge` passaram a exigir silêncio (`(None, "")`, e retorno `None` sem `SystemExit`), o que é mais estrito do que antes. A ADR 0003 fica como está.

**R4 (recomendado na rodada 2): resolvido.** `test_projeto_com_copia_atrasada_barra_o_pr_de_ponta_a_ponta` parte da fixture de projeto `pr-com-pareceres-aprovados` (review e QA aprovados). Ele grava o cache `versao-nova` com `atual` igual à versão do `plugin.json`. Com `defasado: true`, o hook sai com código 2 e uma linha que começa com `R-CONFORMIDADE: forge-check`. Com `defasado: false`, libera em silêncio. O hook roda de ponta a ponta pelo mesmo `executar_fixture`, e a mutação acima mostra que o teste falha se a guarda sair de `verificar`.

**Aviso no Forge.** Continua chegando pelo `forge-check`, em todos os subcomandos, com código inalterado (conferido na rodada 2). Chega também pelo `forge-fechar`, cujo passo 1 é o `forge-check pr` (`bin/forge-fechar:5,45-51`). A decisão D do dono (no Forge a guarda só avisa) e a DECISÃO TÉCNICA do Jarvis de 2026-10-20 (hook mudo com código 0) estão cumpridas. `docs/hooks.md:19` diz o mesmo: a guarda vale "para bloquear, no hook `parecer`", e no Forge o hook "fica mudo com código 0 (ADR 0003, item 1)".

**R5 (recomendado, cosmético).** `tests/test_hooks.py:316-317` tem duas linhas em branco dentro da classe antes do método novo; o resto do arquivo usa uma. O `time.strftime("%Y-%m-%d")` do cache não pesa no resultado, porque `comparar_com_o_cache_do_projeto` não lê `data`, então o teste segue determinístico. Pode ficar para a próxima mudança no arquivo; não pede volta.

## Texto único e invariantes
- `tests/config.json` está fora do delta, então nenhum invariante saiu. `hooks/parecer.py` segue com `avaliar_versao` e `R-CONFORMIDADE`, e `docs/hooks.md`, com `a guarda só avisa`.
- O fragmento `changelog.d/versao-defasada.md` não diz que o hook avisa no Forge, só que ele termina com erro nos projetos. Fica como está.
- As regras são citadas pelo ID (ADR 0003 item 1, R-CONFORMIDADE) no docstring, no `docs/hooks.md` e nos comentários dos testes. Nenhum trecho de regra entre aspas (AntiDuplicacao).

## Commits
Um, `fix(versao): hook parecer mudo com código 0 e fixture de ponta a ponta`, em Conventional Commits em português, com corpo e rodapé de autoria. Limpo.

## Parecer
Aprovado. A2 e R4 estão resolvidos; R5 é cosmético e não pede volta.
