---
tipo: qa
contrato: 1
pedido: lote-m8-prepush
branch: melhoria/lote-m8-prepush
commit: a15a5697609a207eb56aca0b0c64e6f26c1a1e1d
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-24
---
# QA: lote-m8-prepush

Escopo: EST-M8 (o pre-push de `melhoria/*` roda só os testes afetados, com recuo à suíte inteira), REVERSAO-MAPA e FORGE-TESTES-CAMINHOS. Plano antecipado não houve (pedido de controle sem especificação `CA-n`; as obrigações são os itens E1 a E3 do pedido e a decisão do dono de 2026-10-23, "A").

## Achados
- A1 (bloqueante) tests/test_pre_push_afetados.py:107 · mutante M3 sobrevive: sem a guarda de árvore limpa (.githooks/pre-push:251) nada falha, pois o teste suja com arquivo sem mapa. Sujar um arquivo mapeado (tests/test_b.py) mata o mutante.
- A2 (bloqueante) tests/mutantes/lote-m8-prepush.json:1 · o diff muda guardas em .githooks/pre-push e bin/forge-testes sem a spec de mutantes declarados do autor (forge-mutante); sem ela a saída 0 não se confere contra o diff.
- A3 (recomendado) .githooks/pre-push:249 · a metade `! -L bin/forge-testes` da guarda não tem teste (mutante M7 sobrevive; a metade `-f` é redundante com o plano falhando fechado). Fica como recomendação: o link só desvia para outra ferramenta do próprio repositório.
- A4 (recomendado) .githooks/pre-push:252 · mutante M4 (verificação de `origin/develop`) sobrevive por equivalência: sem a base o `--listar` cai em "suíte completa" e `dirigido` devolve 1 do mesmo jeito. Guarda redundante, sem comportamento a provar.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 só o módulo afetado roda, sem anotar árvore verde | `PrePushAfetados.test_so_o_modulo_afetado_roda_e_nao_anota_a_arvore_verde` | caminho mapeado | passou |
| E1 falha em módulo afetado barra, em não afetado não | `test_falha_em_modulo_nao_afetado_nao_barra_e_no_afetado_barra` | limite do afetado | passou |
| E1 recuo à suíte inteira (sem mapa, sem base, sem ferramenta, árvore suja, HEAD diferente, várias refs, ref não branch) | sete testes `test_*_roda_a_suite_inteira` | falha fechada | passou (árvore suja: A1) |
| E1 bloqueios de conteúdo antes do filtro | `test_bloqueios_de_conteudo_valem_antes_do_filtro` | main, force, fluxo | passou |
| E2 mapa de `conferir-reversao.py` e lista de scripts de aviso | `MapaCobreOQueOsTestesLeem.test_conferir_reversao_...`, `NaoEPortao.test_so_script_de_aviso_...` | script fora da suíte completa | passou |
| E3 caminhos, fora do repositório, hífen, `--completa`/`--vermelho` | seis testes de `Execucao` e `test_manifesto_do_plugin_de_dev_...` | limite do repositório, vazio | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_pre_push_afetados tests.test_testes_tocados -q`: 86 testes, OK.
- Testes do pre-push (`test_pre_push_parecer`, `test_pre_push_trava`, `test_pre_push_shellcheck`): 52 testes, OK. `forge-check docs`: sem saída de erro.
- Vermelho/verde (`forge-testes --vermelho 3c66b88 --modulos test_pre_push_afetados,test_testes_tocados`, rc=0):
  `vermelho: base=3c66b881af31 head=a15a5697609a` / `revertidos à base: .githooks/pre-push, bin/forge-testes, changelog.d/lote-m8-prepush.md`; `contagem: não prova (passa na base)=74; prova (asserção)=12`. Os 12 que provam (3 do pre-push, 9 do mapa e dos caminhos) caem na base e passam no head; os de recuo à suíte inteira passam na base de propósito (a base sempre rodava tudo) e guardam o recuo.
- Mutação (spec minha em `$TMPDIR`, 8 mutantes sobre as guardas do diff; `forge-mutante`): M1 (uma ref), M2 (HEAD = enviado), M5 (só `refs/heads`), M6 (só a suíte inteira anota a prova verde), M8 (caminho fora do repositório): morreu. M3 (árvore limpa): sobreviveu (A1). M4 e M7: sobreviveram por equivalência/metade sem teste (A3, A4).
- À mão, clone de brinquedo em `$TMPDIR/qa-engineer-lote-m8-prepush/toy` com o hook e o `forge-testes` reais: push que muda só `tests/test_a.py` rodou só `test_a` (`forge-testes: dirigido (test_a)`, marca `rodou-a`); push que muda `.githooks/pre-push` rodou a suíte inteira (`rodou-a rodou-b`); arquivo mapeado sujo (`tests/test_b.py`) também rodou a inteira.
- Acessibilidade e E2E: n/a (ferramenta de linha de comando). Achados recorrentes (PA-7): lista vazia, nada a conferir.
