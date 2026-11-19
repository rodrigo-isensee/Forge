---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0478-promocao-pr
commit: 6ab1228acf7d1560b1d43541c59438a9e01ffcac
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0478 promoção por marca (E31.5)

Escopo: E31 PROMOCAO-PR-RELEASE. `forge-check pr --base main|homolog` trata como promoção o head que foi a ponta da develop/homolog (cadeia de primeiros pais), não só a ponta atual. Base do diff: `738424449`. Sem suíte local (E31.5); a bateria inteira é o check-run `bateria` do CI no mesmo sha.

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E31: marca com item mesclado depois passa sem E7 e sem H1 (main e homolog, e `pr_da_cli` com PR sem a linha do teto) | `test_marca_com_item_depois_promove_sem_conferencia_e_sem_teto` | marca = 366 linhas, não é mais a ponta | passou |
| E31: item comum de 366 linhas segue reprovado (E7 e H1) | `test_item_comum_de_366_linhas_segue_medido_e_reprovado` | 366 > teto 150 | passou |
| E31: head de branch mesclada (2º pai) não vira promoção | `test_branch_mesclada_na_develop_nao_vira_promocao` | primeiro × segundo pai | passou |
| E31: sem ponta ou git falhando, não é promoção (falha fechada) | `test_sem_ponta_ou_com_o_git_falhando_nao_e_promocao` | ponta None, rev-list rc 128 | passou |
| Mapa do forge-testes inclui o módulo novo | `test_testes_tocados` (162, 1 skip da base) | contagem 102 | passou |
| Não regride a promoção da L08 | `test_forge.ConferenciaPresaAoHead` (11) | A9/A10 | passou |

## Caso de ponta a ponta
No clone do head: `python3 -I scripts/promover-homolog.py --conferir-ref b407f8f7d697b7c118c420ce5b7ae747be410625` (a marca da 0.47.8; a develop já anda com o #682):
```
pareceres: 30 arquivo(s) da promoção, todos aprovados
versão: homolog 0.47.7 | develop 0.47.8
CHANGELOG: entrada [0.47.8] presente, [Não publicado] vazio, changelog.d/ sem fragmentos
forge-check pr release-0.47.8 --ref b407f8f7d697b7c118c420ce5b7ae747be410625 --base main
forge-check pr: pareceres de review e QA de release-0.47.8 valem contra a main
conferir-ref: b407f8f7d697b7c118c420ce5b7ae747be410625 promovível para a homolog   (rc=0)
```
Contraprova: o mesmo comando num clone local em `$TMPDIR` com `bin/` e `scripts/` da base `738424449` sai rc=1 (`tamanho: 366 linhas de código, acima do teto de 150 por item`). O item comum de 366 linhas segue reprovado com o head (teste 2, CLI real `pr` em repositório temporário: rc 1, `sem o pedido`, `acima do teto de 150`).

## Vermelho antes do verde (`R-QA`)
`forge-testes --vermelho 738424449 --modulos test_promocao_por_marca --prazo 400`, rc 0:
```
vermelho: base=738424449cf9 head=d836c43521f8 módulos=test_promocao_por_marca (restrito por --modulos)
revertidos à base: bin/forge-check, bin/forge-testes, changelog.d/v0478-promocao-pr.md, tests/pesos-d4.json
test_branch_mesclada_na_develop_nao_vira_promocao · H=ok · B=ok · não prova (passa na base)
test_item_comum_de_366_linhas_segue_medido_e_reprovado · H=ok · B=ok · não prova (passa na base)
test_marca_com_item_depois_promove_sem_conferencia_e_sem_teto · H=ok · B=falha · prova (asserção)
test_sem_ponta_ou_com_o_git_falhando_nao_e_promocao · H=ok · B=erro · prova (API ausente)
contagem: não prova (passa na base)=2; prova (API ausente)=1; prova (asserção)=1
```
Os dois que passam na base são guardas de não regressão (item e branch mesclada seguem item, por desenho); a correção em si é provada pelos outros dois.

## Mutação
`bin/forge-mutante tests/mutantes/v0478-promocao-pr.json`, rc 0:
```
M1 · morreu · bin/forge-check:1582
M2 · morreu · bin/forge-check:1589 · (erro) o teste declarado deu erro sob o mutante e passa sem ele
M3 · morreu · bin/forge-check:1592
M4 · morreu · bin/forge-check:1591
```
`--cobertura --base 738424449`: `coberta` para 1582, 1589 e 1592 (a 1591 é argumento do rev-list, coberta por M4); `não coberto: tests/pesos-d4.json` (dado, não guarda). A spec `lote-l08-e7b.json` foi editada (M52 acompanha o novo texto da linha 1582): `M52 · morreu · bin/forge-check:1582`.

## Cenários rodados (local, só os arquivos tocados)
- `test_promocao_por_marca.py`: 4 testes, OK, 5 s.
- `test_testes_tocados.py`: 162 testes, OK (skipped=1), 72 s.
- `test_forge.py -k ConferenciaPresaAoHead`: 11 testes, OK, 29 s.
- CI: o check-run `bateria` do sha `d836c435` é a prova da suíte inteira; não o consultei daqui (sem rede à API do GitHub no sandbox).

## Revalidação no head 1e0c50a7 (E31.9, delta sobre d836c435)
Delta (`forge-check parecer delta`): `bin/forge-check` (nova `ponta_da_integracao`: só a ponta remota usa a cadeia de primeiros pais; sem remoto, igualdade com a ponta local, para o ff não promover o commit intermediário do item; E31.6), o teste `test_avanco_rapido_na_develop_local_sem_remoto_nao_vira_promocao`, specs de mutantes e o fragmento do changelog.

| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E31.6: com avanço rápido na develop local sem remoto, o commit intermediário do item não é promoção; a ponta atual segue | `test_avanco_rapido_na_develop_local_sem_remoto_nao_vira_promocao` | intermediário na cadeia de primeiros pais × ponta | passou |

Vermelho: `forge-testes --vermelho d836c43521f8 --modulos test_promocao_por_marca --prazo 400`, rc 0: `test_avanco_rapido_na_develop_local_sem_remoto_nao_vira_promocao · H=ok · B=falha · prova (asserção)`; os outros 4 passam na base (guardas, por desenho).

Mutação, `--base d836c435`: `v0478-promocao-pr.json` rc 0 (M1, M5, M6, M2, M3, M4 · morreu). `lote-l08-e7b.json` rc 1: M37, M50, M51, M52 morreram, M36 equivalente, M56 sobreviveu em `bin/forge-check:1552`. M56 está fora do delta (linha não tocada) e sobrevive igual na base `738424449` (pré-existente): vira recomendado, sem bloquear.

Ponta a ponta: `python3 -I scripts/promover-homolog.py --conferir-ref b407f8f7d697b7c118c420ce5b7ae747be410625` rc 0 (`conferir-ref: b407f8f7… promovível para a homolog`). Local: `test_promocao_por_marca.py` OK. CI: `bateria` do sha é a prova da suíte inteira (não consultada daqui, sem rede à API).

## Revalidação no head 6ab1228a (E31.13, delta sobre 1e0c50a7)
Delta (`forge-check parecer delta`): `bin/forge-check` (nova `avisar_rebase_merge`, chamada só no ramo de promoção do `pr_da_cli`; só avisa quando `gh api repos/{owner}/{repo}` traz `allow_rebase_merge: true`; E31.10), docstring de `ponta_da_integracao`, `docs/fechamento-integrador.md`, fragmento do changelog, mutante M7 e o teste `test_promocao_avisa_quando_o_repositorio_permite_rebase_merge`. O remoto avançou (só pareceres de review e segurança, de3efd3a); trazido por merge.

| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E31.10: promoção avisa se o repositório permite rebase-merge e não muda o veredito | `test_promocao_avisa_quando_o_repositorio_permite_rebase_merge` | True, False, `{}`, None e lista (5 subTests); retorno `[]` | passou |

Vermelho: `forge-testes --vermelho 1e0c50a715ebd00251278c278722b7be3819bb3c --modulos tests.test_promocao_por_marca --prazo 400`, rc 0:
```
vermelho: base=1e0c50a715eb head=6ab1228acf7d módulos=test_promocao_por_marca (restrito por --modulos)
tests.test_promocao_por_marca.PromocaoPorMarca.test_promocao_avisa_quando_o_repositorio_permite_rebase_merge · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=5; prova (asserção)=1
```
Os 5 que passam na base são os guardas já provados nas rodadas anteriores.

Mutação, `bin/forge-mutante tests/mutantes/v0478-promocao-pr.json --base 1e0c50a715ebd00251278c278722b7be3819bb3c`, rc 0 (`base=1e0c50a7… rev=6ab1228a…`): M1, M5, M6, M2, M3, M4 e M7 · morreu (M7 em `bin/forge-check:1591`, a condição `allow_rebase_merge is True`).

Ponta a ponta: `python3 -I scripts/promover-homolog.py --conferir-ref b407f8f7d697b7c118c420ce5b7ae747be410625` rc 0 (`conferir-ref: b407f8f7… promovível para a homolog`). CI: `bateria` do sha é a prova da suíte inteira (não consultada daqui, sem rede à API). O A1 anterior segue aberto como cartão (fora do delta).

## Achados
- A1 (recomendado) bin/forge-check:1552 · mutante M56 de lote-l08-e7b.json sobrevive (teste test_pr_parecer_da_branch_da_ref_vale_sobre_o_de_outra_branch não pega a perda do fallback branch_do_sha); pré-existente, fora do delta; vira cartão.
