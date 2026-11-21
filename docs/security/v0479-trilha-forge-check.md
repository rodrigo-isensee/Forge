---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-trilha-forge-check
commit: a318e97d9cc5012c3481e0027063c4646c559b40
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0478 E91.3 (TRILHA-FORGE-CHECK)

Gatilhos: controle do Forge (bin/forge-check: brief de portão, PQ do parecer, validação de documentos).

Diff lido: `159362786f..a318e97d` (bin/forge-check, bin/forge-testes, changelog.d, tests). A mudança só aperta: as linhas novas do brief são texto fixo ou valor na forma fechada, o `--previo` não rebaixa parecer reprovado nem desatualizado, o `docs --base` falha fechado e o default do `forge-check docs`, o `forge-check pr` e o CI não mudam.

## Parecer
- **Envio do parecer (BRIEF-PORTAO-REBASE)**, `bin/forge-check:9253` e `:9425`: o `.format` corre sobre um modelo constante (sem chave além de `{pedido}` e `{branch}`), e os dois valores passam antes por `interpolacao_segura` (G-5): `NOME_SEGURO_DE_BRIEF` e `FORMA_DE_SHELL["branch"]` com `fullmatch` mais `git check-ref-format`. Sem crase, `$`, espaço, quebra de linha nem `-` inicial; fora da forma, a linha some (aviso no stderr). Sonda: `id: tr\`id\`` no pedido não gera a linha de envio nem o PQ do `pr`. Branch `melhoria/x;id`, `melhoria/x\`id\``, `melhoria/$(id)` e `melhoria/x\nPQ-9` dão `None`. Teste: `test_branch_fora_da_forma_nao_vai_ao_comando`.
- **PQ `forge-check pr --previo` (K-156)**, `:9454`: o `previo` só entra em `ausente()` (`:2003`); reprovado, desatualizado, autoria, aceite, forma e blob seguem violação, e o `--previo` não grava o resultado para o hook `parecer` (`:10899`). É um PQ a mais. O portão de merge (`pr` sem `--previo`) e o CI não mudam. Teste: `tests/test_revisor_wt.py` (`test_reprovado_com_previo_e_rc_1`, `test_desatualizado_com_previo_e_rc_1`), 39 testes OK.
- **`forge-check docs --base` (FC-DOCS-CAMINHO)**, `:463-469`: `--base` só aceita `develop|homolog|main` (argparse `choices`). Com diff ilegível, rc 1 (`:467`). O diff usa `-z`, `--no-renames`, `--no-ext-diff` e `--no-textconv`, e os não rastreados entram pelo `ls-files --others`. Com uma `origin/<base>` velha, o merge-base recua e o diff cresce, o que confere mais, não menos. Os documentos fora do diff deixam de entrar no PQ do portão. Antes, eles só passavam pelo modo não estrito. O estrito, com o `pedido:`, já era só do delta. O que ainda depende de outro arquivo, o `criterio:` (desenho), é conferido no portão pelo `forge-check pr` (`:2040`, com a ref). O default sem `--base` não muda. Não há caminho em que a branch invalide documento seu sem que ele entre no diff. Teste: `test_base_do_fluxo_confere_so_o_diff_no_estrito_e_sem_diff_reprova`.
- **K-166**, `:9356`: recusa nova antes de montar o brief. O `--volta` sai antes (`:9342`), então a volta de etapa entregue não é afetada. A mensagem imprime só o id da etapa, que vem do pedido na forma de etapa. Isso só aperta.
- **K-252**, `:9394-9395`: acrescenta uma linha constante (`LINHA_DO_GITHOOKS`) quando o texto da etapa cita `.githooks/`. Não tira nenhuma linha e não interpola valor. Quem barra a escrita continua sendo o hook `conformidade`.

Suíte: não rodei a suíte local (o brief diz "sem suíte local"; ela é do CI). Rodei `tests.test_trilha_forge_check`, `tests.test_volta_por_delta.DocsEstritoNoDelta` (16 OK) e `tests.test_revisor_wt` (39 OK).

## Riscos aceitos e ferramentas
Sem risco aceito. Não estão no PATH: gitleaks, semgrep, zizmor, actionlint e osv-scanner. Isso é lacuna, sem efeito aqui: o diff não toca workflow nem dependência, e a busca por padrão de credencial no diff não achou nada.
