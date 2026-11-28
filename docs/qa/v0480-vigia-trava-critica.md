---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-vigia-trava-critica
commit: cf8b8f696d2acb4431d62506b5f0667f25fad698
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: VIGIA-PRAZO-TRAVA (v0478 E169.4, PR #853)

## Critério → teste → resultado
| Critério (E169.1, decisão do dono de 24/11) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Prazo vencido em linha sem o marcador crítico, sem corpo pendente, sessão vigiada: recusa (antes liberava) | `test_vigia_prazo_trava_sem_marcador_recusa_e_fora_da_sessao_vigiada_libera`; fixtures `conformidade/vigia-prazo-trava-gh-com-aspas-bloqueia` (`"g"h repo create`), `errointerno-prazo-sem-escrita-bloqueia` (`cat`) | marcador ausente (`marcado` False) | passou |
| Fora da sessão vigiada, hook sem marcador (`critico` None) e depois da ferramenta (PostToolUse): só a linha no erros.log | mesmo teste (fora da sessão e `None`); `test_prazo_vencido_com_corpo_de_heredoc_pendente_recusa` (PostToolUse) | sessão não vigiada, `None`, evento | passou |
| Corpo de heredoc pendente segue citando os corpos; sem pendente cita "a chamada com ação crítica" | `test_prazo_vencido_com_corpo_de_heredoc_pendente_recusa` | pendentes 2 e 0 | passou |
| Comando legítimo sem marcador não passa a ser recusado com o prazo de produção (3 s) | medição abaixo | linha de 50 KB, heredoc de 3000 linhas | passou |

## Cenários e resultado real
- Só os arquivos tocados (sem suíte local; a suíte inteira é do CI do PR): os 3 testes novos ou alterados passam no head (`Ran 3 tests, OK`). Sem `skip`, `skipIf` nem `expectedFailure` nas linhas novas.
- `-k prazo -k vigia` em `tests/test_hooks.py` no head: 17 testes, 3 falhas, todas em `test_prazo_do_merge` (fixtures `parecer/v0455-...`, `v0456-...depois-de-env`, `v0456-...por-caminho`: "não decidiu em 8 s", esperado 0). Não é regressão do diff: com a máquina em load average 18 a 24, o mesmo teste falha igual com o `_comum.py` da base (cópia em `$TMPDIR`, `Ran 2 tests, FAILED (failures=3)`). Esses merges levam o marcador crítico, então o código antigo e o novo decidem igual; o `git` lento da fixture (4 s) estoura o prazo de 8 s sob carga. Dependente de carga, a conferir no CI do PR (check-run `bateria` do mesmo sha).

## Medição com o prazo de produção (comando legítimo sem marcador)
Os hooks `conformidade` e `parecer` rodados como o Claude Code os roda (`python3 -s -E hooks/<hook>.py`, stdin PreToolUse, papel `forge:tech-lead`), vigia de 3 s ativo, no head. Linhas sem marcador: `ls docs`, `cat docs/pedidos/v0478.md`, `git status`, `git log --oneline -5`, `python3 -m unittest ...`, `git diff --stat`, `grep -rn`, `echo` com 50 000 caracteres, heredoc de 3000 linhas. Todas saem rc 0, nenhuma recusa por prazo. Tempo: de 0,12 s a 0,69 s com a máquina carregada; pior caso 1,11 s com load average 24 (`echo` de 50 KB em `conformidade`), cerca de 2,7 vezes de folga sobre os 3 s. Única recusa vista (`git commit` de 20 KB, rc 2) é a regra `R-CONTRIB` de sessão de projeto, não prazo. Risco residual, aceito pelo dono na decisão de 24/11: máquina muito carregada recusa linha legítima ("separe o comando em chamadas menores"), em vez de liberar.

## Vermelho antes do verde
Cópia em `$TMPDIR` com `hooks/_comum.py` da base 0f4a7791 e os testes do head:
```
FAIL: test_fixtures_do_vigia_prazo_trava (fixture='conformidade/errointerno-prazo-sem-escrita-bloqueia')
FAIL: test_fixtures_do_vigia_prazo_trava (fixture='conformidade/vigia-prazo-trava-gh-com-aspas-bloqueia')
FAIL: test_prazo_vencido_com_corpo_de_heredoc_pendente_recusa
FAIL: test_vigia_prazo_trava_sem_marcador_recusa_e_fora_da_sessao_vigiada_libera
Ran 3 tests ... FAILED (failures=4)
```
No head: `Ran 3 tests ... OK`. `forge-testes --vermelho 0f4a7791... ` sem `--modulos` abre 121 módulos (o diff toca `hooks/_comum.py`, que todos importam) e, com `--modulos test_hooks --prazo 500`, estourou o prazo (rc 124, módulo de 2 a 4 min por cópia sob load 18+): sem veredito do comando; a prova acima é a cópia à mão, na forma da skill.

## Mutantes
`bin/forge-mutante tests/mutantes/v0480-vigia-trava-critica.json`, saída 0:
```
forge-mutante: pedido=v0480-vigia-trava-critica rev=cf8b8f696d2a spec=365cad50b138753830265151128a9809e0406941775ab30ec094aad3efa02928
M1 · morreu · hooks/_comum.py:2860
M2 · morreu · hooks/_comum.py:2860 · (erro) o teste declarado deu erro sob o mutante e passa sem ele
M3 · morreu · hooks/_comum.py:2860 · (erro) o teste declarado deu erro sob o mutante e passa sem ele
M4 · morreu · hooks/_comum.py:2860 · (erro) o teste declarado deu erro sob o mutante e passa sem ele
M5 · morreu · hooks/_comum.py:2863
```
`--cobertura --base 0f4a7791...`: as duas condições mudadas (linhas 2860 e 2863) saem `coberta` (M1 a M4 e M5), sem `não coberto` nem `isenta velha`. M1 a M5 morrem. Conferência da lista contra o diff: as duas linhas de guarda mudadas em `prazo_vencido` têm mutante; o resto do diff é comentário e docstring.

## Observações
- M2 a M4 morrem por erro do teste sob o mutante (o controle sem o mutante passa), não por falha de asserção; vale como morte pela regra do `forge-mutante`, e o teste exercita as três saídas (sessão, `None`, PostToolUse), por isso sem achado.
