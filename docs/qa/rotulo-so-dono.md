---
tipo: qa
contrato: 1
pedido: rotulo-so-dono
branch: melhoria/rotulo-so-dono
commit: d6b9b352af4b1ee40f4d3d2e06b20909a3321546
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-20
---
# QA - rotulo-so-dono (R-CONTRIB: o rótulo afrouxa-regra só do dono), revalidação da volta 3

Sem UX nem API. Revalidação por delta da volta 3 (`3b266e4...d6b9b35`, só `tests/`): 10 fixtures da sessão do Forge que citam o rótulo trazem o gh falso (conta dona) e o teste estrutural `test_fixtures_da_sessao_do_forge_que_citam_o_rotulo_usam_o_gh_falso` exige isso. Não escrevi o diff. O review aprovou (`856eac1`, só parecer depois de `d6b9b35`). Este parecer substitui o anterior (`6ec5095`, aprovado); o hook e a regra R-CONTRIB não mudaram na volta 3, então as linhas E1 a E3 do parecer anterior valem e foram reexecutadas na suíte inteira.

## Obrigação -> teste -> resultado
| ID | Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|---|
| E1 a E3 | Regra, permissão do dono, barreira a outra conta, falha fechado, sem rótulo sem rede, sessão de projeto, fragmento | suíte completa (fixtures `rotulo-so-dono-*`, `formas_alternativas`, `volta_2_*`, changelog) | permissão (dono, outra conta, projeto) | passa |
| V3 | Resultado das fixtures não depende da credencial da máquina | `test_fixtures_da_sessao_do_forge_que_citam_o_rotulo_usam_o_gh_falso` (10 achadas, mínimo 10) | gh falso executável e à frente no PATH; guarda de suíte vazia | passa |

## Execução (HEAD `d6b9b35` mais o parecer do review, gh sem credencial)
- `mkdir -p "$TMPDIR/gh-vazio" && env -u GH_TOKEN -u GITHUB_TOKEN GH_CONFIG_DIR="$TMPDIR/gh-vazio" python3 -m unittest discover -s tests -q`: `Ran 884 tests in 208.016s`, `OK`.
- `scripts/validar-plugin.sh`: `Validation passed` (as duas validações). Chamadas de rede negadas pelo sandbox não afetam o resultado.

## Vermelho antes do verde
Cópia em `$TMPDIR` (`git archive HEAD`), sem tocar a worktree: removi `bin/gh` de `arquivos` e de `executaveis` nas 10 fixtures da sessão do Forge que citam o rótulo, e rodei `python3 -m unittest tests.test_hooks -k fixtures_da_sessao_do_forge_que_citam` com o gh sem credencial.
- Sem o gh falso: `FAIL` em subTest para as fixtures alteradas (`assertIn("bin/gh", ...)`); com a fixture original no mesmo teste: `Ran 1 test`, `OK`.

## Mutação
Sem ferramenta de mutação gratuita para Python na stack; o vermelho acima mostra que o teste novo falha quando o gh falso some da fixture.

## Achados
