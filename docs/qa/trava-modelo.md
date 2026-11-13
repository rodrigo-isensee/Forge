---
tipo: qa
contrato: 1
pedido: v0457
branch: melhoria/trava-modelo
commit: 5c38e04ea8d010b3250b2c934278a66e94eff43e
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-13
---
# QA: trava-modelo (4b, E23.111, sobre a E23.29)

Head 5c38e04e (base ee608198). Parecer APROVADO. Escopo: a isenção do modelo em `hooks/conformidade.py` contra as condições C1 a C10 do parecer E23.28 e os 22 casos de abuso (fixtures `trava-modelo-a01` a `a22`). A suíte inteira roda no CI do PR (sem PR ainda); aqui, só os testes afetados.

## Achados
- A1 (recomendado) tests/mutantes/trava-modelo-2.json:1 · as três specs trazem `pedido` diferente (trava-modelo, -2, -3), então `forge-mutante` recusa a rodada única ("specs de pedidos diferentes"); use o mesmo `pedido` nas três. Cada spec roda sozinha, 22 de 22 morreram.
- A2 (recomendado) tests/mutantes/trava-modelo-3.json:1 · M21 (hooks/conformidade.py:1172) morreu por erro do teste sob o mutante, não por asserção; aceito, mas um teste que falhe por asserção prova mais.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| C1 lista exata pós-realpath, `.claude/` do modelo segue travado | fixtures a09 (subpasta), a10 (.claude), a11 (versao); `test_c7` | só `.githooks/<um nome>` e `.forge/config.json` | passou |
| C2 só clone do Forge (sessão ou ~/.forge-contrib) | a03, a21; `test_c2` | projeto e clone fora do contrib | passou |
| C3 o modelo não vale (PLUGIN, core.hooksPath) | a22; `test_c3_plugin`, `test_c3_hookspath_com_erro_do_git` | erro do git conta como "vale" | passou |
| C4 só Write e Edit (Bash e MultiEdit barrados) | a18, a19, a20; `test_copia_do_modelo_isenta...` | Bash, MultiEdit | passou |
| C5 caminho absoluto, normalizado, sem variável, til nem `..` | a14, a15, a16, a17 | forma do caminho | passou |
| C6 sem link no caminho dentro do clone, nlink 1 | a01 a08 (link para raiz, para dentro, físico) | link simbólico e físico | passou |
| C7 isenção como dado validado, falha fechada | `test_c7`, `test_erro_na_conferencia_nao_isenta` | dado malformado, exceção | passou |
| C8 22 casos de abuso como fixtures e mutantes | `test_fixtures_da_trava_modelo` (27 fixtures: 22 barram, 5 liberam); 22 mutantes | 22 abusos; 5 usos legítimos | passou |
| C9 PR com afrouxa-regra e destaque | `changelog.d/trava-modelo.md` traz o rótulo; o PR não existe ainda | n/a | pendente do PR (tech-lead) |
| C10 risco residual para o dono | citado no changelog e no relato da E23.29 (troca por link entre a conferência e a escrita, baixo) | TOCTOU | declarado, aceite do dono no PR |

Os 22 casos montados pelo autor cobrem a ameaça nomeada no E23.28 (`ln -s ../.. templates/projeto/r`): a01, a02, a04 a07. Os testes de abuso passam também na base, porque a base já barra tudo: são guardas de regressão. O que prova a mudança são os 5 que liberam e os 6 testes da classe `TravaModelo`.

## Cenários e resultado real
Vermelho antes do verde (base reposta só no `hooks/conformidade.py`, numa cópia): `python3 -m unittest tests.test_hooks.Hooks.test_fixtures_da_trava_modelo tests.test_hooks.TravaModelo` deu `FAILED (failures=5, errors=6)`: as 5 fixtures `*-libera` falham e os 6 testes de `TravaModelo` dão erro, sem o código. No head: `Ran 7 tests ... OK`. `forge-testes --vermelho ee608198...` abriu com `vermelho: base=ee608198b094 head=5c38e04ea8d0` e `revertidos à base: changelog.d/trava-modelo.md, hooks/conformidade.py`; o código de saída ficou mascarado pelo pipe, por isso o veredito acima é o da prova manual.

Mutação (`bin/forge-mutante`, por spec): trava-modelo.json M1 a M8 morreram; trava-modelo-2.json M9 a M16 morreram; trava-modelo-3.json M17 a M22 morreram. Nenhum sobrevivente, 22 de 22. Mutantes conferidos contra as linhas de guarda mudadas no diff de `hooks/conformidade.py` (917 a 920, 1172, 1182 a 1210, 2680 e 2681): todas têm mutante.

Limite: as 6 falhas de `test_hooks` do sandbox (pid e sessão) citadas pelo autor não são deste diff e não foram rerrodadas; a suíte completa é do CI.
