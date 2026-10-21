---
tipo: review
contrato: 1
pedido: s-16-promocao-develop
branch: melhoria/s-16-promocao-develop
commit: f804072b4d48680bd65e8d38f2bf6cfb36517f9f
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-20
---
# Review: S-16-PROMOCAO-DEVELOP, rótulo já posto em PR mesclado por squash vale na promoção develop → homolog

Escopo: `0f480c8..571bba0` (base 0f480c884f8a3f5af1ea8eba861fb937d61f9619), 3 arquivos em 2 commits (`dbf01e1` código e testes, `571bba0` fragmento). O revisor não é o autor (D-ETAPAS-INST). Comparei o diff com E1 e E2 do pedido, com as decisões do dono de 2026-10-16 e 2026-10-20 e com M1 a M7 e B1 a B17 do modelo de ameaças (`~/.forge-contrib/docs/propostas/security/s-16-promocao-develop.md`).

Veredito sobre `571bba0`: **REPROVADO** por um achado de teste (A1): o código cumpre M1 a M7, mas o único teste que prova M4 (B8) só discrimina quando dois commits caem no mesmo segundo do relógio.

## Ferramentas (citadas, não refeitas)
- `python3 -m unittest tests.test_catraca.RotuloDePrSquash tests.test_catraca.RotuloDePrMesclado tests.test_catraca.FonteDoGithub` numa cópia em `$TMPDIR` (`git archive 571bba0`): `Ran 48 tests in 9.602s` / `OK`.
- Suíte completa: 1105 OK no relatório do autor (E1.1); o pre-push deste parecer a roda de novo. `scripts/validar-plugin.sh` fica com o QA e o CI.
- Segurança (`R-SEGURANCA`, a catraca é controle) tem parecer próprio em paralelo (E1.3); não o refiz. O diff não toca `.github/` (`git diff --stat 0f480c8 571bba0 -- .github` vazio), então não há parecer de devops a citar.

## Conferência de E1 (M1 a M7 no código)
1. **M1:** `buscar_cabeca_do_pr` (`tests/catraca.py:732`) monta o número só de `int(n)`, busca `refs/pull/<n>/head:refs/catraca/pull/<n>` com `--no-tags --no-recurse-submodules --no-write-fetch-head`, sem `+` (não força atualização), só de `origin`, sem checkout; os objetos trazidos só passam por `rev-parse`, `cat-file`, `merge-base` e `ls-tree`. Manutenção desligada na própria chamada (`maintenance.auto=false`, `gc.auto=0`).
2. **M2:** S continua vindo só de `commit_do_rotulo` (dados do servidor). Em `prova_do_squash` (`:747`), `head.sha` da API é validado como SHA de 40 hex; depois do fetch, o ref trazido tem de ser igual a ele e S tem de existir; por fim S ancestral do head final. Se S e o head final já estão locais, o fetch não roda e a comparação do ref é dispensada: correto, porque o SHA da API identifica o conteúdo.
3. **M3:** o substituto só é avaliado quando o caminho atual falha (`:795`): M com um pai só e, por arquivo coberto, `mesmo_arquivo(M, S)` além do `mesmo_arquivo(head, S)` que já existia (`:822-824`, condicionado a `squash`). O caminho do merge commit fica como era (`test_merge_commit_com_ancestralidade_nao_busca_nada` afirma que nenhum fetch roda).
4. **M4:** M na cadeia de primeiro pai de `base..head`, só no caminho do squash; no do merge commit segue o `intervalo` de antes, como o modelo pede.
5. **M5:** `_ou_none` da `FonteGithub` (`:626`) passa a capturar `http.client.HTTPException`; `liberado_por_pr_mesclado_ou_none` (`:834`) troca `TimeoutExpired` e `OSError` do git por aviso e "sem rótulo"; a chamada em `_main` (`:984`) usa o invólucro. O fetch só roda depois que a API confirmou merge, base, rótulo do dono e S.
6. **M6:** nada em `.github/workflows/`; nenhum token passado ao git; remoto fixo `origin`.
7. **M7:** os filtros da S-16 não mudaram (o diff de `sha_rotulado_do_mesclado` só troca o final); `R-CUSTO` e violações sem arquivo seguem fora (`if not custo and not liberado`).

## Conferência de E2 (B1 a B17)
- Mutações numa cópia em `$TMPDIR`, uma por vez, com `RotuloDePrSquash`: sem o primeiro pai (M4) falha só `test_b8`; sem o "um pai só" (M3) falha só `test_b9`; sem `mesmo_arquivo(M, S)` (M3) falha só `test_b3`; sem a igualdade do ref com `head.sha` (M2) falha só `test_b4`; sem a ancestralidade de S no head final (M2) falha só `test_b7`. Bate com o que o autor declarou como não guarda.
- Os que o autor chamou de guarda são guardas mesmo: cada um passa pelo filtro que diz, que já existia antes desta entrega. B2 e B12 caem em `mesmo_arquivo(head, S)` (o head tem o conteúdo novo); B5 cai em `tem_commit(S)` depois do fetch (sem ele o `merge-base` com objeto ausente também falha); B10, B11, B13 e B16 caem nos filtros da S-16 (base, fork, `merged_at`, reescrita, dono e app); B15 em `arquivo_da_violacao` e `custo`; B17 em `mesmo_arquivo(head, S)`. Os extras `test_sem_head_sha_da_api_pede` e `test_b1_head_com_varios_commits_no_pr_passa` também conferem.
- B6 (código de saída e `TimeoutExpired`), B14 (refs de `refs/heads`, `refs/remotes` e `refs/tags` iguais antes e depois, sem `FETCH_HEAD`) e `test_m1_...` (argumentos exatos do fetch) provam M1 e M5. `test_resposta_cortada_da_api_e_none` restaura `catraca.requisicao` pelo `setUp` da classe.
- Exceção: B8, ver A1.

## Isenção do catraca.py em tests/test_ambiente_git.py
O texto de `EXCECOES["catraca.py"]` (`tests/test_ambiente_git.py:29-31`) diz que o arquivo só lê o repositório, sem criar; com o fetch novo ele grava objetos e o ref `refs/catraca/pull/<n>`, então a frase ficou falsa. O motivo da isenção continua de pé: a única escrita liga `-c maintenance.auto=false -c gc.auto=0` na própria chamada, logo não dispara a manutenção que o teste protege. É recomendação (A2), com cartão, porque o arquivo está fora do escopo.

## Achados

## Detalhe dos achados (rodada sobre 571bba0, mantido)
- A1 (bloqueante) `tests/test_catraca.py:1678-1689` · Prova: na cópia em `$TMPDIR`, com `time.sleep(1.2)` antes de `checkout -b lateral` e o filtro de primeiro pai removido de `prova_do_squash`, `test_b8` dá `OK`; sem o sleep, a mesma mutação falha. A causa: `self.pull["merge_commit_sha"] = self.squash(ROTULADO)` cria um M novo, mas `branch -f lateral self.m` e o `assertIn(self.m, ...)` usam o M do `setUp`; os SHAs só coincidem quando árvore, pai, mensagem e data em segundos são iguais. Quando o segundo vira, o M do pull fica fora de `base..head` e o caso para no filtro antigo do intervalo, não em M4. Vai contra a prática de testes determinísticos, sem dependência da hora atual (skill `engineering-practices`). Sugestão: `self.m = self.squash(ROTULADO)`, `self.pull["merge_commit_sha"] = self.m` e manter as duas asserções sobre esse M (ou fixar `GIT_AUTHOR_DATE` e `GIT_COMMITTER_DATE` no fixture). Correção de teste, volta ao autor.
- A2 (recomendado, fora do escopo; cartão CATRACA-ISENCAO-AMBIENTE) `tests/test_ambiente_git.py:29-31` · reescrever o motivo da isenção: o catraca.py lê e, na promoção com squash, faz um fetch com a manutenção desligada na chamada; não dispara a manutenção. Sem ação nesta entrega.
- A3 (recomendado) `tests/catraca.py:803-806` · o docstring de `liberado_por_pr_mesclado` ainda descreve só o caminho do merge commit; o do módulo (`:10-12`) e o de `sha_rotulado_do_mesclado` já falam do squash. Uma frase basta, pode ir junto com A1.
- A4 (informativo) o prazo total do fetch somado às chamadas de API segue no cartão CATRACA-PRAZO-API, como o autor registrou; `git()` fora do invólucro continua sem capturar `TimeoutExpired` nos outros modos (mesmo cartão).

## Commits
Dois commits coerentes, Conventional Commits em português; fragmento `changelog.d/s-16-promocao-develop.md` com `### Alterado`, neutro (`R-NEUTRO`), sem editar o `CHANGELOG.md`. Nada de `docs/regras/`, `hooks/`, `tests/config.json` nem invariantes tocado; nada que custe dinheiro (`R-CUSTO`): fetch anônimo do repositório público e GETs com o token do run.

## Volta 1 (delta 571bba0..f804072, parecer aprovado)
Delta lido com `forge-check delta`-equivalente por `git diff 571bba0 f804072 -- tests/`: só `tests/test_catraca.py` (+7 -4); o resto do diff entre os SHAs são os pareceres (review e segurança). Já lido e inalterado: `tests/catraca.py` e demais arquivos da rodada anterior.
- **A1 corrigido:** `test_b8` agora faz `time.sleep(1.2)` antes do squash, cria o próprio M (`m = self.pull["merge_commit_sha"] = self.squash(ROTULADO)`), afirma `assertNotEqual(m, self.m)`, aponta `lateral` para esse M e as duas asserções de `rev-list` usam `m`. Nada mais muda no delta (o import de `time` é o único acréscimo fora do teste).
- **Prova (cópia em `$TMPDIR` de `git archive f804072`):** sem o filtro de primeiro pai (M4) em `prova_do_squash`, `RotuloDePrSquash` falha (`FAILED (failures=1)`, duas execuções seguidas); com o código original, `Ran 21 tests` / `OK`. O teste deixou de depender do segundo do relógio.
- A2, A3 e A4 seguem como recomendações/cartões da rodada anterior, sem bloqueio.
- Suíte completa: a do pre-push deste commit, esperando a trava (`R-TETO`).
