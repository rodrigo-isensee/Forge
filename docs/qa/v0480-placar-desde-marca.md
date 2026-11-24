---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-placar-desde-marca
commit: 752cf974ae6918a4e3103c4bc05f2fed13d293e6
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-23
---
# QA: v0478 (E138.3, placar desde a marca anterior na develop)

Escopo: `scripts/placar-mutacao.py --desde` aceita a marca (último commit que mudou a versão do manifesto) sem aviso; a release do `bin/forge-changelog` sugere a marca ou a tag dela. Sem suíte local; a suíte inteira é do check-run `bateria` do PR.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| `--desde` na marca não avisa | PlacarDaRelease.test_marca_anterior_na_develop_vale_como_a_tag_sem_aviso | marca vs. commit comum (HEAD segue avisando) | passou |
| Sem tag na marca, sugere o commit | ReleaseAvisaMedidasDaVersao.test_sem_tag_na_marca_sugere_o_commit_da_marca | tag ausente | passou |
| Sem marca, pede a mão | ReleaseAvisaMedidasDaVersao.test_sem_marca_pede_a_marca_anterior_a_mao | histórico vazio de manifesto | passou |
| Tag fora da develop cede à marca | ReleaseAvisaMedidasDaVersao.test_tag_fora_da_develop_cede_a_marca_anterior_na_develop | tag ancestral antiga | passou |
| Tag na marca vence o commit | test_no_forge_imprime_o_placar_desde_a_tag_anterior_e_o_bench | tag e marca no mesmo commit | passou |
| Specs de mutante conferem com a fonte | ConferirTodas.test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes | `de` fora da fonte | FALHOU no head |

## Execução (head 752cf974)
- `python3 -m unittest tests.test_changelog tests.test_forge_mutante.PlacarDaRelease` (da raiz, sem -I): Ran 98 tests, OK.
- Vermelho: `bin/forge-testes --vermelho 0e59c446 --modulos tests.test_changelog,tests.test_forge_mutante`, rc 1. Saída: `vermelho: base=0e59c44642a8 head=752cf974ae69`; revertidos à base: bin/forge-changelog, changelog.d/..., scripts/placar-mutacao.py. Provam (asserção, H=ok B=falha): os 3 testes novos de ReleaseAvisaMedidasDaVersao e PlacarDaRelease.test_marca_anterior_na_develop_vale_como_a_tag_sem_aviso. Contagem: `falha da entrega=1; não prova (passa na base)=232; prova (asserção)=4`. O rc 1 vem do teste que falha no HEAD (A1).
- Mutação: `bin/forge-mutante --base 0e59c446 tests/mutantes/v0480-placar-desde-marca.json`: `base=0e59c44642a8 mb=0e59c44642a8 rev=752cf974ae69`; PDM1, PDM2, PDM6 (scripts/placar-mutacao.py:61, :61, :95) e PDM3, PDM4, PDM5 (bin/forge-changelog:284, :285, :285) `morreu`; nenhum sobrevivente.
- `forge-mutante --cobertura --base 0e59c446`: linhas 284, 285 (changelog) e 61, 95 (placar) cobertas; a linha apagada da base (282) sai `apagada`, sem guarda nova.
- Suíte inteira: check-run `bateria` do PR no mesmo sha (não rodada local).

## Bug
BUG-1 (alta): o diff muda `scripts/placar-mutacao.py` (`if aviso := aviso_do_desde(raiz, a.desde, a.versao):`) e `bin/forge-changelog` (`if tag.returncode == 0 and tag.stdout.strip() else`), mas não realinha as specs antigas que têm essas linhas no `de`. `python3 -m unittest tests.test_forge_mutante.ConferirTodas` falha com `tests/mutantes/v047-placar-mutacao.json: M7` e `tests/mutantes/v046-mutacao-bench-2.json: M10`; as duas linhas existiam na base e não existem mais no head. Os nomes não estão em `tests/fixtures/mutantes-pendentes.txt`. A `bateria` do CI cai por isso. Corrige o autor (dev): atualizar o `de` das duas specs (e o `para`, se preciso) no mesmo commit que muda a linha.

## Achados
- A1 (bloqueante) tests/mutantes/v047-placar-mutacao.json:57 · o `de` do M7 saiu da fonte com o diff; idem v046-mutacao-bench-2.json:19 (M10). ConferirTodas cai no head e a bateria também. Alinhar as duas specs no mesmo commit.
