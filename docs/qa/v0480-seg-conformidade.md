---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-seg-conformidade
commit: a4266c77896643b544328310ae6deee34665d6c1
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-22
---
# QA: v0478 (E113.4) S22, A20 e RESTO-SOBE no hooks/conformidade.py

Passada única, head a4266c77, base b0895f6cc. Só os testes afetados, as specs de mutante e as sondas do QA; a suíte inteira fica para o CI do PR (`R-QA`).

## Achados
- A1 (bloqueante) hooks/conformidade.py:2230 · S22 não vê a negação `!`: `! git switch -c x && git push origin` na main sai liberado, mas o push roda só quando a troca falhou. Sonda no head e na base, rc 0 em vez de 2 (R-MAIN). Mesma classe do cartão (a troca só vale com operador que garante).
- A2 (recomendado) hooks/conformidade.py:1768 · A20: `d=.gi; d+=t; cp ev/config "$d/c"` (atribuição com `+=`) sai liberado, igual na base; o hook não calcula o `+=`. Cobrir com fixture ou recusar o `+=` com valor parcial do `.git`.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| S22: troca de branch só vale com `&&` que garante | test_s22_... (7 fixtures: 5 recusam, 2 liberam) | `\|\|`, `\|`, `;`, quebra de linha, `&&` simples | passou; lacuna na `!` (A1) |
| A20: resto com barra depois do opaco no `.git` recusa | test_a20_... (8 fixtures: 6 recusam, 2 liberam) | `$d/.`, `$(echo .git)/.`, `"$@"/c`; variável fora do `.git` libera | passou; lacuna `+=` (A2) |
| RESTO-SOBE: `..` depois do opaco vale resolvido | test_resto_sobe_... (6 fixtures: 5 recusam, 1 libera) | sobe e desce, sobe duas vezes, `TMPDIR` exportado, nome livre | passou |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_conformidade_seg_v0480.py`: 3 testes, OK, três rodadas seguidas (8 s, 8 s, 5 s).
- Mutantes: `bin/forge-mutante tests/mutantes/v0480-seg-conformidade.json tests/mutantes/v0480-seg-conformidade-2.json`, 13 de 13 `morreu` (S22a-f, A20a-d, RS1-RS3), nenhum sobrevivente, sem equivalentes. Rev a4266c778966.
- `forge-mutante --cobertura --base b0895f6cc`: toda condição mudada de `hooks/conformidade.py` aparece `coberta` (linhas 840, 842, 1768, 1776, 1778, 1847, 2228, 2230, 2612, 2613); `apagada` só `chave in ramos` (2568 da base, trocada pela forma nova). `não coberto: tests/pesos-d4.json` é dado, não guarda.
- Vermelho: o `forge-testes --vermelho` não rodou, porque a trava de tarefa pesada estava com outra sessão (R-TETO; duas tentativas bloqueadas pelo hook; a primeira, sem `--modulos`, ia para a suíte completa e foi cancelada). Substituto equivalente: o teste e as 21 fixtures novas sobre o `hooks/conformidade.py` da base (`git archive b0895f6cc` em cópia descartável): 3 testes, `FAILED (failures=16)`; as 16 fixtures que recusam caem (A20: 6, RESTO-SOBE: 5, S22: 5) e as 5 que liberam passam. O autor ainda deve colar o `--vermelho` oficial.
- Sondas do QA (29 comandos, esperado recusa): 27 recusados; liberaram `! git switch -c x && git push origin` (A1) e a do `+=` (A2); ambas liberam igual na base, são lacunas e não regressão. Recusadas, entre outras: `git switch -c x || push`, `x & push`, `x |& cat && push`, `x && echo a || push`, `if ! git switch ...; then push; fi`, `$X/.git/../hooks`, `$X/a/../.git`, `$X/a/../../.git`, `$d//c`, `$d/./c`, `for d in .git`, `read d <<< .git`, `$(printf .git)/c`, `TMPDIR=.git/a` com `../..`. Controle `{ git switch -c x; } && git push` libera, como deve.

## Fixture pesado/mesma-sessao-libera
Não é instável. Ela não está no diff (última mudança em #747) e roda em série, por depender de PID e da trava global. Sozinha: 10 de 10 aprovadas, 0,20 a 0,30 s cada. O estouro do autor é prazo sob carga (suíte paralela e outras sessões na mesma máquina), não resultado que oscila. Nenhum `skip`; sem cartão.

## Resultado
Reprovado por A1 (alta, segurança com gatilho: push na main liberado). Devolver ao autor com fixture `S22: ! git switch ... && git push` e mutante para a guarda nova; depois `forge-check parecer delta docs/qa/v0480-seg-conformidade.md`.
