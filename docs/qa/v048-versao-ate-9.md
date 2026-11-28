---
tipo: qa
contrato: 1
pedido: v048
branch: melhoria/v048-versao-ate-9
commit: c727c89722a5a68b336f7e7e296d02ffa5272cc9
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-27
---
# QA: v048-versao-ate-9 (#951, VERSAO-PATCH-ATE-9)

- ci: c727c89722a5a68b336f7e7e296d02ffa5272cc9 verde

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| contador: depois de X.Y.9 vem X.(Y+1).0 | `LinhaDaVersao.test_versao_corta_no_9` (0.47.9, 0.48.9) | patch 9 (limite) | passou (M1 e M2 morrem) |
| contador: patch antigo acima de 9 também corta | idem (0.47.19 dá 0.48.0) | logo acima do limite | passou |
| contador: abaixo de 9 só soma 1 | idem (0.48.0 dá 0.48.1; 0.48.8 dá 0.48.9) | patch 8, mínimo 0 | passou |
| release recusa patch acima de 9, sem gravar, mensagem com a versão certa | `Release.test_versao_com_patch_acima_de_9_e_recusada_sem_mexer` (0.47.10 e 0.47.20: rc 1, "vem 0.48.0", CHANGELOG, plugin.json e fragmento intactos) | 10 (logo fora) e 20 | passou (M3 morre) |
| release aceita o patch 9 | `Release.test_patch_9_ainda_e_aceito` (0.1.9, rc 0) | patch 9 (limite) | passou (M4 morre) |
| `--anexar` não mudou | testes de `--anexar` já existentes, sem edição no diff | n/a | passou (119 testes OK) |
| testes antigos 1.4.9 esperam 1.5.0 | `test_conta_fragmentos_sem_readme_e_sobe_o_patch`, `test_readme_com_caixa_mista_nao_conta` | patch 9 | passou |

## Cenários e resultado real
- Diff contra a base b414714c: 9 linhas de código (`bin/forge-contador`, `bin/forge-changelog`), testes, spec de mutantes e fragmento de changelog. Nada fora do escopo.
- Afetados rodados à mão: `python3 -m unittest tests.test_forge_contador tests.test_changelog`: 119 testes, OK.
- Sonda minha (repositório temporário, `--ref HEAD`): 0.47.09 dá 0.48.0; 0.47.99 dá 0.48.0; 0.9.9 dá 0.10.0; 10.9.9 dá 10.10.0, todos rc 0.
- Vermelho antes do verde: `bin/forge-testes --vermelho b414714cd2ba676734f6c94dd8d0029598ff5cf2 --modulos test_forge_contador,test_changelog`: rc=0, "prova (asserção)=4" (`test_versao_corta_no_9`, `test_conta_fragmentos_sem_readme_e_sobe_o_patch`, `test_readme_com_caixa_mista_nao_conta` e o de patch acima de 9 no changelog), H=ok nos quatro.
- Mutantes `bin/forge-mutante tests/mutantes/v048-versao-ate-9.json` (`rev=c727c89722a5`): M1 morreu · bin/forge-contador:49; M2 morreu · bin/forge-contador:49; M3 morreu · bin/forge-changelog:191; M4 morreu · bin/forge-changelog:191; rc=0.
- Cobertura `bin/forge-mutante --cobertura --base b414714cd2ba676734f6c94dd8d0029598ff5cf2`: as duas linhas de guarda mudadas (`bin/forge-changelog:191`, `bin/forge-contador:49`) têm mutante declarado; nenhuma sem mutante.
- Limites conferidos: 8 (soma), 9 (corta), 10 e 19/20 (recusa/corta); `>= 9` no contador e `> 9` na release são coerentes (a release só recebe a versão que o contador devolve, que nunca passa de 9).
- CI do PR #951 no head c727c89722a5: todos os checks verdes (partes 1 a 5 da suíte, python 3.14, instalação, catraca, passos, verificações longas, teto de pulados); `bateria` e `bateria (pareceres)` falham só porque esperam os pareceres, como o brief prevê.
- Logs: `/root/.forge-contrib/wt/v048-qa-logs-2/`.
