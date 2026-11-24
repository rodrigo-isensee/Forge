---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-g1-2-delta
commit: 14c7e31ede621eff8a7b3d3f63044f05bb9ab115
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0478 G1.2, revalidação por delta no head ca6cf392 (E140.21)

Delta desde o parecer anterior (55a57bde): só `tests/test_parecer_fora_do_delta.py` mudou no domínio do QA (E140.18); o commit ca6cf392 só toca o parecer do review. Sem código de produção novo. Sem suíte local; a inteira é do CI do PR.

## Mudança
`test_recomendado_fora_do_delta_passa` agora leva o bloqueante repetido A1 ao lado do recomendado A2, de modo que o laço de `fora_do_delta` roda e chega ao recomendado. Antes, a lista só com recomendado saía antecipada e não exercia o laço (o mutante FD10 sobrevivia).

## Provas
- `python3 -I -m unittest discover -s tests -p test_parecer_fora_do_delta.py` → `Ran 29 tests`, `OK`.
- `bin/forge-mutante tests/mutantes/v0480-g1-2-delta-2.json` no head ca6cf392:

```
forge-mutante: pedido=v0480-g1-2-delta rev=ca6cf3921809 spec=e38ff9a1473a49b228bb4819b9f4e1bbb3b8276cf1f7c487dcd9cbd1bf332fb5
FD9 · morreu · bin/forge-check:4200 · (erro) o teste declarado deu erro sob o mutante e passa sem ele
FD10 · morreu · bin/forge-check:4192
FD11 · morreu · bin/forge-check:2046
FD12 · morreu · bin/forge-check:481
FD13 · morreu · bin/forge-check:4200
FD14 · morreu · bin/forge-check:480
FD15 · morreu · bin/forge-check:4127
FD16 · morreu · bin/forge-check:4160 · (erro) o teste declarado deu erro sob o mutante e passa sem ele
```

Oito de oito mortos; FD10, o sobrevivente da rodada anterior, morre agora. O vermelho do teste é a própria morte do FD10 (o teste falha sob o mutante e passa sem ele); `forge-testes --vermelho` não foi esperado até o fim (excedeu o prazo da chamada).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| G1.2: recomendado fora do delta não é recusado, mesmo com bloqueante repetido | `Revalidacao.test_recomendado_fora_do_delta_passa` | laço exercido com bloqueante + recomendado | passou; FD10 morreu |
| G1.2: demais recusas por delta | `tests.test_parecer_fora_do_delta` | n/a | passou (29) |

## Observações
Nada bloqueante. Sem bug registrado.
