---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-k152-sem-skip
commit: 1600898d0c5dbf16b3ea1ab3bc88f7fc63b6a291
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: v0479-k152-sem-skip (E85.4)

Escopo: `tests/test_prepush_k152.py` (diff `ad3b3b6f..1600898d`, 2 arquivos: o teste e o fragmento de changelog). O teste ponta a ponta `EnvioDaCopiaNova` deixa de se pular conforme `ruff`/`mypy` na máquina e passa a rodar com PATH controlado (`path_sem_pronto`: links só para git, bash, python3 e utilitários do envio). Código de produção não mudou.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Roda sempre, sem skip | `grep -n skip tests/test_prepush_k152.py` vazio; `discover -s tests -p test_prepush_k152.py`: 10 testes, OK, também com `ruff` e `mypy` falsos no PATH comum | PATH da máquina com ferramentas | passou |
| Pulados 38 para 37 sem achado | `catraca.forca_dos_testes`: base `(15641, 38, 0)`, head `(15643, 37, 0)`; `regra_testes_enfraquecidos('.', 'origin/develop', 'HEAD')` = `[]` (origin/develop = ad3b3b6f) | asserções não caem (15641 para 15643) | passou |
| Com ruff e mypy falsos no PATH controlado o teste reprova | cópia do teste com `ruff` e `mypy` somados a `OPCIONAIS_DO_ENVIO` e fakes (`exit 0`) no PATH: `test_copia_nova_sem_dependencias_barra_o_envio_explicando` falha com `AssertionError: 0 == 0 : sem as ferramentas o envio não passa` | ferramentas presentes | passou (reprova como deve) |
| Mutantes | ver abaixo | n/a | passou |

A cópia mutada do teste foi restaurada; `git status` limpo.

## Mutantes (`bin/forge-mutante` nas duas specs)
```
forge-mutante: pedido=v0479-k152-prepush-sem-deps rev=1600898d0c5d spec=b2626e44bc37... spec=75a75053...
M1 · morreu · bin/forge-init:71
M2 · morreu · bin/forge-init:72
M3 · morreu · bin/forge-init:171
M4 · morreu · docs/propostas/k152-pre-push.md:37
M5 · morreu · docs/propostas/k152-pre-push.md:52
M6 · morreu · docs/propostas/k152-pre-push.md:53
M7 · morreu · docs/propostas/k152-pre-push.md:55
M8 · morreu · docs/propostas/k152-pre-push.md:57
M9 · morreu · docs/propostas/k152-pre-push.md:47
M10 · morreu · docs/propostas/k152-pre-push.md:47
```
Nenhum sobrevivente. O diff deste head só toca teste e changelog, sem linha de guarda nova em `bin/`, `hooks/`, `.githooks/`; a lista cobre o controle já existente.

Sem suíte local (o `bateria` roda no CI do PR).
