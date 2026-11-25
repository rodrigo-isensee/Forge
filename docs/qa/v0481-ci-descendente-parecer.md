---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-ci-descendente-parecer
commit: aa26249f6f12bb20aa2b8d3023bd820293eaad48
parecer: reprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: v0481-ci-descendente-parecer (E8.16, G3.7), volta única do #895

Clone `/root/.forge-contrib/wt/v0481-ci-descendente-parecer-qa`, no head `aa26249f` (igual ao remoto). Delta `2364a43b..aa26249f`: `bin/forge-check` (`so_pareceres_ate` com saída em bytes, `nomes_z` e `--ignore-submodules=none`), 2 skills encurtadas, 2 specs de mutantes, 2 testes novos. A lógica está correta; o que reprova é o CI do PR: outro teto estoura.

## Achados
- A1 (bloqueante) skills/engineering-practices/SKILL.md:54 · `test_metricas_texto.test_nenhuma_metrica_passa_do_teto` cai: engineering-practices 7113 caracteres, teto 6982 (+131); qa-testing 11774, teto 11761 (+13). Base eeb81062 passa. Suítes 3.12 e 3.14 parte 1/5 e `bateria` falham; encurte, sem subir teto.

## Critério -> teste -> resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Branco inicial do 1º caminho não some (A1 do #895) | `LeOCiVia.test_branco_no_inicio_do_caminho_nao_vale` | espaço, tab, quebra de linha no início | passou; vermelho no código de `2364a43b` (3 falhas) |
| `diff.ignoreSubmodules` não esconde gitlink | `LeOCiVia.test_gitlink_fora_das_pastas_nao_some` | gitlink em `bin/sub` com config `all` | passou; vermelho no código de `2364a43b` |
| Regras anteriores da linha `via` | `LeOCiVia` inteiro, módulo `test_forge_check_pr` | descendente, renomeação, rc do git | 71 testes OK local |
| Encurtamento das skills não tira regra nem invariante | `test_orcamento_instrucao` (8 OK local); `tests/config.json` e `docs/regras` sem mudança no delta | qa-engineer 21477 de 21480; tech-lead 56 de 56 | passou |
| Skills citam `via` e G3.7 | `ChecksForaDaLinhaDoCi.test_brief_esqueleto_e_skills_citam_a_forma_via` (dentro dos 71) | n/a | passou |
| Tetos de texto das skills | `test_metricas_texto.test_nenhuma_metrica_passa_do_teto` | teto por skill | FALHOU (A1) |
| CI do PR verde no head | check-runs do run 45589057763 | n/a | FALHOU: `suíte (3.12 e 3.14, parte 1/5)`, `bateria`, `bateria (python 3.14)`; `bateria (pareceres)` e `catraca` falham e ficam fora da linha |

Frase tirada do QA ('A suíte inteira roda no CI do PR', 'a ele e à segurança'): a regra continua na skill engineering-practices e no trecho `PARECER-LE-O-CI`; nenhum trecho de `invariantes` sumiu (`config.json` intocado e `test_orcamento_instrucao` verde).

## Sondas S1 (chamando `so_pareceres_ate`, em arquivo, repo descartável)
Recusaram (False): ` docs/qa/x.py` (espaço), `\tdocs/qa/x.py` (tab), `\ndocs/qa/x.py` (quebra de linha), gitlink com `diff.ignoreSubmodules=all`. Aceitou (True, correto): `docs/qa/ok.md`.

## Vermelho antes do verde
Código de `bin/forge-check` de `2364a43b` com o `test_forge_check_pr.py` do head, `-k branco -k gitlink`: `FAILED (failures=4)` (3 do branco, 1 do gitlink); no head, os 71 testes passam. `forge-testes --vermelho` não rodado (suíte lenta); o equivalente por cópia fica registrado acima.

## Mutantes (`bin/forge-mutante` das 2 specs, rev aa26249f)
```
M1 · morreu · bin/forge-check:2188
M2 · morreu · bin/forge-check:2196
M3 · morreu · bin/forge-check:2198
M4 · morreu · bin/forge-check:2199
M5 · morreu · bin/forge-check:2199
M6 · morreu · bin/forge-check:2206
M7 · morreu · bin/forge-check:2205
M8 · morreu · bin/forge-check:2228
M9 · morreu · bin/forge-check:2204 · (erro) o teste declarado deu erro sob o mutante e passa sem ele
M10 · morreu · bin/forge-check:2198
M11 · morreu · bin/forge-check:2198
```
Nenhum sobrevivente; M10 e M11 cobrem as 2 linhas novas de guarda. `forge-mutante --conferir --todas` no head e na base (eeb81062, cópia) produz a mesma saída (26 linhas de trechos repetidos de specs antigas, rc 1 nos dois; nenhuma é das specs do v0481).

## Revalidação
`- ci:` não gravado: as suítes falham (A1). Corrigido A1 e com o `gh pr checks` do novo `commit:` verde fora das 3 checagens da linha, o parecer seguinte grava `- ci: <sha40> verde` (ou `via`, só de pareceres).
