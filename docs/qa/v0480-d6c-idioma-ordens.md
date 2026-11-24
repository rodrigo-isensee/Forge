---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-d6c-idioma-ordens
commit: 0c7e8f0c09c3347f8f0e32cf02635ebb2fee359e
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA (delta): idioma das mensagens ao dono na linha fixa das ordens (v0478 E174.14, PR #866)

Delta `748f2975..0c7e8f0c` (fix E174.12): `except (OSError, ValueError, RecursionError)` em `hooks/ordens.py:78`, caso aninhado em `test_idioma_torto_sai_none_sem_erro`, fixture `idioma-config-aninhada-no-forge-ordens-seguem`, mutante M8 (M2 e M3 acompanham a guarda). Fora do delta, o parecer anterior (E174.7, reprovado só pelo A1) vale.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A1 anterior: config aninhada (RecursionError) não cala as ordens | `test_idioma_torto_sai_none_sem_erro` (caso `"[" * 20000 + "]" * 20000`); fixture `idioma-config-aninhada-no-forge-ordens-seguem` | JSON profundo abaixo de 64 KiB | passou |
| Demais critérios do parecer anterior (idioma na lista, ausente, fora da lista, FIFO, JSON inválido, teto) | `OrdensEmVigor` inteiro | lista de códigos, config torta | passou |

## Provas
- Head: `python3 -I -m unittest discover -s tests -p test_hooks.py -k OrdensEmVigor`: 23 testes, OK.
- Vermelho antes do verde (recuo manual, cópia do head em `$TMPDIR` com `hooks/ordens.py` devolvido a 748f2975): `test_idioma_torto_sai_none_sem_erro` ERROR no subteste aninhado; no head passa. `forge-testes --vermelho` não rodado (o módulo `test_hooks` estourou o prazo no parecer anterior).
- Mutantes: `bin/forge-mutante tests/mutantes/v0480-d6c-idioma-ordens.json --base 748f2975c6cf77ce2c14d58a435a82c91901f99f`: M1 a M8 `morreu`, nenhum sobrevivente (M8, M2 e M3 por erro do teste sob o mutante com o controle verde).
- `forge-mutante --cobertura --base aabc476c5dbad3b3efced688e578bb5c71c5f722`: linhas 77, 80, 81 e 124 cobertas; a 78 tem M2, M3 e M8 (rodados acima).
- CI: a suíte inteira não rodou aqui; o check-run `bateria` do PR #866 no mesmo sha segue obrigatório para o merge.
