---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-k152-sem-skip
commit: 1600898d0c5dbf16b3ea1ab3bc88f7fc63b6a291
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0479-k152-sem-skip

Etapa E85.2 do pedido v0478 (K152-SEM-SKIP). Diff de `ad3b3b6f` (base `develop`) a `1600898d`: `tests/test_prepush_k152.py` (+23/-4) e o fragmento `changelog.d/v0479-k152-sem-skip.md`. Sem código de produção; sem guarda nova de produção (não há mutante a declarar).

## O que foi lido
- `path_sem_pronto` monta uma pasta só com links para os programas que o envio usa (`PROGRAMAS_DO_ENVIO`, obrigatórios, com `assertIsNotNone`) e os opcionais que o hook confere com `command -v` (`OPCIONAIS_DO_ENVIO`, entram só se existem); `ruff` e `mypy` nunca entram. O `skipTest` sai: o teste roda igual em toda máquina.
- `self.env` é por instância (montado no `setUp`), então trocar o `PATH` não vaza para outros testes.
- A nova asserção `assertNotIn("command not found", ...)` prova que o PATH controlado não corta o hook no meio; a mensagem do `assertNotEqual` passa a trazer o `stderr`.
- Fragmento do changelog em "Corrigido", texto fiel ao diff.

## Provas executadas (só o teste do item; a suíte inteira fica no CI, `R-REVIEW`)
- `python3 -m unittest tests.test_prepush_k152 -v`: 10 testes, OK, sem pulado.
- Com `ruff` e `mypy` falsos à frente do PATH herdado: `EnvioDaCopiaNova` roda e passa (antes do item, se pulava nessa máquina).
- Mutante à mão (`ruff` e `mypy` somados à lista de links do PATH controlado), com os falsos no PATH herdado: `EnvioDaCopiaNova` FALHA (failures=1); o teste mata o vazamento. Arquivo restaurado, cópia limpa.

## Parecer
Aprovado. Faz o que o E85 pede, nem mais nem menos: o teste ponta a ponta deixa de depender da máquina, com PATH controlado, e continua provando que a cópia nova sem as ferramentas barra o envio explicando. A queda dos pulados da `develop` de 38 para 37 fica conferida pelo CI do PR (`R-REVIEW`), sem rerrodar aqui.
