---
tipo: qa
contrato: 1
pedido: v0457
branch: melhoria/v0457-refs-push
commit: b12f6d9be42f4b3b5f00bce51be535b567207483
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-12
---
# QA: v0457 3b (política de refs PREPUSH-REFS, PR #506)

Diff revisado: 8b5a44d5..b12f6d9b. Obrigação: D2 de `docs/security/ameacas/v0457-hook-shell-pipe.md` (ref fora de heads/tags, mais de uma branch com código, mais de uma remoção) nos dois hooks de envio.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| D2-1 ref remota fora de refs/heads e refs/tags recusa | PoliticaForge/Modelo.test_ref_remota_fora_de_heads_e_tags_recusa; EnvioDeVerdade*.test_ref_de_notas_recusa | refs/remotes, notes, stash, pull; `refs/heads/` sem nome | passou (cai sem o patch) |
| D2-2 mais de uma branch com código por envio | test_duas_branches_com_codigo_recusa; EnvioDeVerdade*.test_branches_e_mirror_recusam_sem_mudar_o_remoto (--all, --branches, --mirror, duas branches) | uma branch passa; duas recusam; remoto intacto | passou (cai sem o patch) |
| D2-3 mais de uma remoção por envio | test_duas_remocoes_recusa (branch+branch, branch+tag, tag+tag); EnvioDeVerdade*.test_prune_com_curinga_nao_apaga_em_massa; test_pre_push_trava (uma passa, duas recusam) | uma remoção passa; duas recusam | passou (cai sem o patch) |
| Contadores não herdados do ambiente | test_contadores_nao_vem_do_ambiente (Forge e Modelo) | variável de ambiente pré-definida | passou (cai sem o patch) |
| Controles: uma branch e branch mais remoção seguem | testes "uma branch ok" (2 por classe) | limite inferior | passou (passam também sem o patch, como controle) |
| Os dois hooks iguais em política | classes Forge e Modelo espelhadas (10 métodos x 2) | n/a | passou |

## Cenários e resultado real
- Patch do dono: o diff de `.githooks/pre-push` e `templates/projeto/.githooks/pre-push` no intervalo vem só do commit 3d4a884f (o log dos dois arquivos lista só ele), e as linhas +/- dele são idênticas às de `/root/.forge-contrib/patches/refs-push.patch` (comparação linha a linha, sem diferença). Nenhum commit posterior toca os hooks.
- `python3 -m unittest tests.test_prepush_refs` no head, árvore limpa: `Ran 20 tests ... OK`.
- Vermelho à mão com os hooks do 45812242 (sem o patch) e `tests/test_prepush_refs.py` do head: `Ran 20 tests ... FAILED (failures=36)`; 16 dos 20 testes caem (8 métodos x 2 classes, com subtestes); os 4 restantes são os controles de caso permitido, que passam nos dois estados. (No 45812242 puro, o arquivo daquele commit pula as classes: `Ran 0 tests, skipped=4`.)
- `bin/forge-mutante` das duas specs (16 mutantes, 8 por hook): todos morreram. Lista conferida contra o diff: Forge L139 (contadores), L171-172 (case de ref), L176, L179-180 (contagem), L185-186 (limites); Modelo L4, L34-35, L39, L42-43, L48-49: uma condição por linha de guarda mudada, nenhuma guarda sem mutante. `--cobertura` não rodei (a flag cobre só Python e a lista foi conferida à mão).
- Módulos do diff, um por vez, no head: test_pre_push_trava (50 OK, 4 pulos de ambiente root/sandbox), test_pre_push_afetados (36 OK), test_pre_push_ja_no_remoto (2 OK), test_pre_push_parecer (21 OK), test_pre_push_segredo (10 OK), test_prepush_so_docs (62 OK, 9 pulos de ambiente). Asserções em test_pre_push_trava: 217 no head e 217 na base 8b5a44d5.
- Ajustes nos módulos: só o caso que a política muda (duas remoções recusam; duas branches viram branch mais tag); nenhuma asserção afrouxada para passar.
- CI do PR #506 (run 43288706245): `catraca` pass, `instalação (python 3.14)` pass, `árvore já provada na develop` pass; `bateria` fail só no passo "Parecer de review (e de QA para a homolog) quando o PR toca código que governa os agentes" (exige os pareceres que estão sendo gravados; as partes da suíte ficaram `skipping` por causa dele). A bateria completa só vale com novo run no mesmo sha depois dos pareceres; não a cito como verde.
- Decisões do dono: rótulo `afrouxa-regra` presente no PR (confirmado); a regra de uma branch por envio vale também para as pessoas nos projetos (aceita pelo dono, registrada no brief). O merge espera a tag (fora do meu escopo). Estado do PR: BLOCKED (pareceres e bateria pendentes).

## Provas
```
forge-mutante: pedido=v0457-refs-push rev=b12f6d9be42f
M1..M16 · morreu (M1 .githooks/pre-push:139 ... M16 templates/projeto/.githooks/pre-push:49), nenhum sobrevivente
tests.test_prepush_refs (head): Ran 20 tests OK
tests.test_prepush_refs (hooks do 45812242 + testes do head): Ran 20 tests FAILED (failures=36)
```
