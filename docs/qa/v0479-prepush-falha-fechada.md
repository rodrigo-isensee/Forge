---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-prepush-falha-fechada
commit: 99a4fc3037f5a34958b83c474e6c1cc6c7e7ba56
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: PREPUSH-MODELO-FALHA-ABERTA (v0478 E82.4)

Proposta `docs/propostas/prepush-modelo-falha-aberta.md` (patch do `templates/projeto/.githooks/pre-push`, que só o dono aplica) e `tests/test_prepush_falha_fechada.py`. Patch testado em cópias em `$TMPDIR`, sem gravar em `.githooks`. Só o módulo do recorte rodou; suíte inteira fica para o CI do PR.

## Achados
- A1 (bloqueante) tests/test_prepush_falha_fechada.py:150 · `@unittest.skipUnless(shutil.which("python3"), ...)` na classe RegistrosSemPython sobe os pulos de tests/ de 37 para 38 e a catraca (R-CONFORMIDADE) barra o PR. Remova o decorator (o teste não precisa dele) ou peça o rótulo ao dono.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| dirname ausente barra | DirnameAusente.test_sem_dirname_barra_o_envio | utilitário ausente | passou |
| dirname com erro ou saída vazia barra | test_dirname_com_erro..., test_dirname_com_saida_vazia_barra | saída vazia, rc != 0 | passou |
| sem tr o limite vale | LimiteSemTr.test_sem_tr_o_limite_encerra_a_checagem_longa | FORGE_PREPUSH_TIMEOUT=1 | passou |
| sem python3 com a chave barra; sem a chave segue | RegistrosSemPython (3 testes) | com e sem a chave | passou |
| controles com tudo no PATH | 2 testes de controle | n/a | passou |

## Cenários e resultado real
- Vermelho antes do verde, `forge-testes --vermelho 2097f9bf --modulos test_prepush_falha_fechada`: `vermelho: base=2097f9bf23bd head=99a4fc3037f5 módulos=test_prepush_falha_fechada (restrito por --modulos)`; 8 testes `H=ok · B=erro · prova (API ausente)`, rc 0. Na base a proposta nem existe, então a prova do ferramental não separa controle de teste de defeito.
- Hook sem o patch (cópia com o diff da proposta trocado por um no-op de comentário): `Ran 8 tests ... FAILED (failures=6)`; os dois controles (`test_controle_com_tudo_no_path_a_checagem_roda`, `test_controle_com_python3_os_registros_rodam`) passam. Confirma 6 de 8.
- Patch aplicado no modelo (`git apply --check` rc 0, `git apply` rc 0, cópia): `Ran 8 tests ... OK`; `bash -n` rc 0. shellcheck ausente nesta máquina (o CI roda).
- Mutantes, `bin/forge-mutante tests/mutantes/v0479-prepush-falha-fechada.json`: `forge-mutante: pedido=v0479-prepush-falha-fechada rev=99a4fc3037f5`; M1 a M8 `morreu`, rc 0. Um mutante por linha `+` de guarda do patch (lider_vivo, dirname erro/vazio/exit, if python3, return 1, case, return 0): coberto.
- Sondas da seção 4 da proposta, refeitas por mim (antes = 2097f9bf, depois = cópia com patch): antes `A sem dirname rc=0`, `B sem python3 rc=0`, `C sem tr rc=0`; depois os três `rc=1`; os demais iguais ao antes.
- Catraca (`catraca.regra_testes_enfraquecidos(2097f9bf, HEAD)`): pulos 37 -> 38, regra dispara (A1).
