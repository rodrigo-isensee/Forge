---
tipo: review
contrato: 1
pedido: impl-n-cat1
branch: melhoria/impl-n-cat1-2
commit: c6413c69240e0bd17768b9db7679619918a727de
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-22
---
# Review: impl-n-cat1

Revisor: tech-lead (instância de review, E1.2; não é o autor, D-ETAPAS-INST = A). Diff lido: `a3dbe22..c6413c6` (a base é a `origin/develop` atual, sem integração pendente), 4 arquivos: `tests/catraca.py`, `tests/test_catraca.py`, `docs/adr/0008-governanca-de-contribuicoes.md` e `changelog.d/impl-n-cat1-2.md`. Referências: §2 (itens 1, 3, 4, 5 e 6) e §3.1 do desenho `n-cat1.md`, medidas M1 a M3 de `n-cat1-medidas.md` e o modelo de ameaças `docs/security/ameacas/n-cat1.md`. Primeira rodada: sem delta.

## Achados

## Parecer
**Aprovado.** Os 5 itens seguem o desenho, um commit por item na ordem do §3.1 (o item 2 fica fora, P-CAT1-1 = B), e o fragmento de changelog está num commit próprio, como pediu a decisão técnica de 2026-10-22 09:36. `tests/config.json` não foi tocado (`git diff --stat a3dbe22 c6413c6 -- tests/config.json` vazio). A concordância "o violação" não aparece mais (`git grep` em `tests`, `docs/adr` e `changelog.d` no HEAD: 0), e o comentário sobre o `cmd_pr` em `tests/catraca.py:1033` está correto.

Evidência de execução (cópia própria em `$TMPDIR`, HEAD da worktree intocado):
- `python3 -m unittest tests.test_catraca`: base `a3dbe22` 184 testes OK; HEAD `c6413c6` 222 testes OK (+38).
- **Reversão de cada commit sozinho no HEAD (P3 = B)**: `git revert --no-commit` de `f1ce2af`, `82773a2`, `aecd1c3`, `63f99d9`, `52ae7fa` e `c6413c6`, um de cada vez a partir do HEAD: os 6 sem conflito. Com cada um dos 5 itens revertido, `tests.test_catraca` fica verde (214, 217, 216, 209 e 216 testes).
- **Vermelho antes do verde por item**: com o código do item revertido e os testes do HEAD mantidos, os testes do próprio item falham: item 1, 2 falhas e 7 erros (todos em `FalhaFechadaDoGit`); item 3, 3 falhas e 4 erros; item 4, 6 erros; item 5, 8 falhas; item 6, 12 falhas e 1 erro.
- **Mutantes do desenho**: todos morrem. A guarda do rótulo voltando a `SEM_LISTA` dá 3 falhas; sem `.so` na `FORMA_COMPILADA`, 3 falhas; `min(30, restante)` trocado por 30 fixo, 1 falha; a introdução voltando a `ler(...) is None`, 2 falhas.
- Modo `pareceres` sobre a árvore real (314 arquivos de parecer): 0,6 s. O item 5 não pesa no job.

Leitura por item:
- **Item 1** (`tests/catraca.py:72-128`, `:454-457`, `:479-483`, `:1049`): `listar` e `existe` levantam `ErroDeGit` quando o código de saída não é 0. `existe` usa `--literal-pathspecs` e `--`. `ErroDeDiff` passa a ser um caso de `ErroDeGit`, e a mensagem antiga se mantém. `FALHAS_DO_GIT` é nominal, sem `except Exception`. A guarda passa a procurar a marca `NAO_LIBERAVEL`, presente nas duas mensagens de falha do git: um caminho que contenha o texto continua sem liberação, o que é mais rígido (a R3 ficou fora, como o §4 pede).
- **Item 3** (`:624-680`): `api()` delega a `api_com_teto`, uma fonte só para a paginação. As três funções capturam `ERROS_DA_API`, a mesma tupla da `FonteGithub`, e avisam com uma linha. `TETO_PAGINAS = 3` segue a M2.
- **Item 4** (`:574-616`, `:1070`): o prazo usa `time.monotonic` por `relogio()` (dá para trocar por dublê), começa na primeira chamada e é reiniciado por execução em `_main`. `PrazoDaApiEsgotado` é `OSError` e o aviso sai uma vez só. Os 240 s seguem a M1. O teste estrutural lê o `timeout-minutes` do job `catraca`.
- **Item 5** (`:985-1035`): segue o §2 do desenho: o último parecer de cada tipo, pela chave `(data, caminho)` do `cmd_pr`, com o mesmo critério para `riscos-aceitos`. Usa só as funções do `bin/forge-check` da base, sem editá-lo, e a promoção continua fora. A exigência não cresce (`test_nao_regressao_sem_parecer_e_sem_arquivo_sensivel_passa`). Na deduplicação por texto (`:1034`), um descasamento só pode duplicar uma linha, nunca tirar uma: o ramo em que ela age sempre devolve `sem_parecer`, que já barra.
- **Item 6** (`:460-466`): regra própria, somada em `_violacoes_das_regras`, sem tocar `regra_protegidos`. A âncora `(^|/)__pycache__/` e os sufixos fixos seguem o desenho, que vale para o repositório inteiro, e os testes cobrem o negativo de âncora. Atende à M3: o teste confere a árvore real (`git ls-files`, mínimo de 100 itens, checklist 11).
- **ADR 0008**: cada nota entra no commit do seu item. Commits em Conventional Commits, em português, um por mudança coerente.

Pareceres de outros papéis: o de segurança (E1.3, `security-engineer`) corre em paralelo e decide os pontos do modelo de ameaças. Não o refaço aqui. Este PR pede o rótulo `afrouxa-regra` do dono, porque mexe em `tests/catraca.py`, que está em `PROTEGIDOS`.

## Recomendações (não bloqueiam)
- `tests/catraca.py:1049`: `main` captura só `ErroDeGit`. No modo `regras`, um `TimeoutExpired` do git no caminho do rótulo por conteúdo (`rotulo_vale_pelo_conteudo` → `pareceres_do_pedido` → `alterados`, ou `mesmo_diff`) ainda sai com rastro de pilha. Fecha (rc 1), mas a nota nova da ADR 0008 fala em "sem rastro de pilha" nos dois modos. Sugestão para um lote seguinte (o N-CAT2 já mexe nesse arquivo): `main` capturar `FALHAS_DO_GIT` com `violacao_de_git`.
- Divergências entre o desenho, que foi seguido, e o modelo de ameaças, para o `security-engineer` julgar no E1.3:
  - o C1 pede "sem o mais recente ganha", o critério "tocado no diff" e frontmatter ilegível barrando; o item 5 usa o último por `(data, caminho)` e ignora documento com `contrato: 0` ou ilegível, como o `cmd_pr`;
  - o C4 pede `min(60, restante)` também no `git fetch` de `buscar_cabeca_do_pr` (`:819`), e isso não entrou;
  - o C5 cobre só `hooks/`; o item 6 cobre o repositório inteiro, que é mais rígido.

  O ORDEM-PARECER-EMPATE já está apontado para o N-FC-CONF (§7 do desenho).
- A suíte imprime avisos `catraca: ...; vale como sem rótulo.` fora do `redirect_stdout` em testes antigos (`ExecucoesDoPr` e afins). É ruído de saída, não erro.
- Integrador (E1.5): pelo C6 do modelo de ameaças, depois do merge toda branch em voo com parecer reprovado commitado fica vermelha no próximo push. Avise quem está com elas.
