---
tipo: qa
contrato: 1
pedido: dv-5
branch: melhoria/dv-5
commit: 90014ae265c00c8129b9af1d1d465f4e828bd03f
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-20
---
# QA - dv-5 (trava de release em `forge-check sobreposicao --ref`)

Sem UX nem API. Diff `87dbbad...90014ae` (bin/forge-check, R-FLUXO, tests/config.json, testes `TravaDeRelease`, fragmento). Não escrevi o diff. Os commits depois de `90014ae` até o HEAD `47b8497` só trazem os pareceres de review e de segurança (`git diff --stat 90014ae HEAD`: dois arquivos em docs/). Review e segurança com `parecer: aprovado` nesse commit.

## Obrigação -> teste -> resultado
| ID | Obrigação (pedido, E1 e E3) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|---|
| Q-1 | Release em curso e branch de fora: rc 1 com o motivo | `test_release_em_curso_e_branch_de_fora_barra`; à mão: rc 1 e mensagem "release 0.24.0 em curso ... espere a promoção" | `--ref` fora da release | passou |
| Q-2 | `melhoria/release-<versão da develop>` passa | `test_branch_da_release_passa` (nome simples e `origin/`); à mão rc 0 | igualdade exata do nome | passou |
| Q-3 | Release de outra versão não passa | `test_release_de_outra_versao_nao_passa`; à mão com `release-0.25.0` rc 1 | logo fora do limite | passou |
| Q-4 | Sem `--ref`, informativo rc 0, mesmo com release em curso | `test_sem_ref_nada_muda_mesmo_com_release_em_curso`; à mão rc 0 | ausência do argumento | passou |
| Q-5 | Sem release em curso, nada muda (iguais e develop menor) | `test_sem_release_em_curso_nada_muda`; à mão homolog=develop rc 0 sem aviso | igualdade e inversão de versões | passou |
| Q-6 | Versão ilegível ou ausente só avisa (rc 0) | `test_versao_ilegivel_so_avisa`, `test_versao_ausente_so_avisa`; à mão com texto não JSON: aviso e rc 0 | JSON inválido, ref ausente | passou |
| Q-7 | Comparação numérica, não textual | `test_versao_numerica_compara_por_numero_nao_por_texto`; à mão develop 0.10.0 x homolog 0.9.0: barra (rc 1) | 0.9 x 0.10 | passou |
| Q-8 | R-FLUXO e invariante novos não quebram a fábrica | suíte completa (inclui o teste de invariantes) | trecho protegido | passou |

## Execução
- `python3 -m unittest discover -s tests -q` na worktree (pgrep do R-TETO vazio antes): `Ran 941 tests in 206.118s`, `OK`. Nenhum teste falhou e passou de novo; nenhum flaky observado (rodada única).
- `scripts/validar-plugin.sh`: `Validation passed` (todos os manifestos).
- Roteiro à mão em repositório descartável em `$TMPDIR`, sem rede, `origin/develop` e `origin/homolog` criados por `update-ref`: oito casos acima, todos com o rc esperado.
- Vermelho antes do verde: `bin/forge-check` da develop (`git show 87dbbad:bin/forge-check`) no lugar do novo, `python3 -m unittest tests.test_sobreposicao_quadro.TravaDeRelease`: `Ran 8 tests`, `FAILED (failures=7)` (ex.: `AssertionError: 2 != 0`, o argumento `--ref` nem existe). O oitavo, `test_sem_release_em_curso_nada_muda`... passa sem a trava por ser o comportamento antigo; é a garantia de não regressão. Código novo restaurado; árvore limpa.
- Mutação: a stack do Forge não declara ferramenta gratuita de mutação; não rodada. Os casos de fronteira acima (igual, menor, outra versão, numérico) cobrem as mutações óbvias de `<=`, `==` e comparação textual.

## Observações (não bloqueiam, já nos pareceres anteriores)
- A trava lê `origin/develop` e `origin/homolog` locais; sem `git fetch` pode errar (documentado por review e segurança, R1 a R4).

## Achados
