---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-vigia-trava-critica
commit: aa0f55f8ae0829ad1e958c543e259d5ff6cb6b92
parecer: aprovado
escopo: incremental
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

## Revalidação por delta (v0478 E169.8, head aa0f55f8)
`forge-check parecer delta` (cf8b8f69..aa0f55f8, sem o que veio da develop): domínio do QA em `docs/hooks-fixtures.md`, `tests/mutantes/heredoc-donos.json` e `tests/test_hooks_volta_propriedades.py` (do commit 160ab342, E169.6); `test_hooks.py` e o ADR 0003 vieram da develop, fora do pedido.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Prazo vencido sem marcador recusa (E169.1), agora também no teste da develop | `test_t_vigia_de_prazo_recusa_com_marcador_e_libera_sem`, subteste "sem marcador": rc 2 e regra do hook | marcador ausente, passo lento de 60 s | passou (`-k vigia`: Ran 2 tests, OK) |
| D11 e D12 realinhados à fonte morrem | `heredoc-donos.json` D11 e D12 | `hook.marcado is False` (linha 2860) e texto da mensagem (linha 2863) | morreram |
| Índice de fixtures em dia | `scripts/indice-fixtures.py --conferir` | contagem 3516 e linhas de `conformidade`, `errointerno`, `vigia` | em dia, rc 0 |

Sem `skip`, `skipIf` nem `expectedFailure` nas linhas do delta. O subteste só passou a exigir a recusa: sem o código de E169.1 ele cai (rc 0 em vez de 2), o mesmo vermelho já registrado acima.

Saída de `bin/forge-mutante tests/mutantes/heredoc-donos.json` no head:
```
forge-mutante: pedido=HEREDOC-DONOS rev=aa0f55f8ae08 spec=bd184f80f14fe65bf246b91fc249589c2b6d7079884d23634a1ddbbd87d293b6
D1 a D10 · morreu
D11 · morreu · hooks/_comum.py:2860
D12 · morreu · hooks/_comum.py:2863
D13 · morreu · hooks/conformidade.py:2141
D14 · morreu · hooks/conformidade.py:2193
D15 · controle vermelho · hooks/conformidade.py
D16 · morreu · hooks/_comum.py:1665
```
D15 não é do delta: o teste declarado `tests.test_hooks.Hooks.test_fixtures` não existe desde as fatias da develop (#785, `test_fixtures_fatia_1` a `_4`); o controle cai em 6,8 s por teste inexistente (`errors=1`), igual em `origin/develop`. Com as quatro fatias, numa spec em `$TMPDIR`, a rodada passou de 9 min e estourou meu limite: sem veredito, não afirmo que D15 morre. Em `test_hooks.py -k test_fixtures` no head: `Ran 41 tests in 1185.836s, OK (skipped=4)`, as skips herdadas da develop.

Suíte inteira: do CI do PR (check-run `bateria` do mesmo sha), não rerrodada aqui.

## Achados
- A1 (recomendado) tests/mutantes/heredoc-donos.json:D15 · `testes` cita `Hooks.test_fixtures`, que não existe desde as fatias (#785); o controle fica vermelho e o mutante nada prova. Trocar pelas fatias 1 a 4. Dívida da develop, fora do delta; vira cartão.
