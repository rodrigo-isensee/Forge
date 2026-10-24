---
tipo: review
contrato: 1
pedido: PREPUSH-DELETE
branch: melhoria/prepush-delete
commit: 96bf396f61d49163a5083cfa6f11f5719985816c
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-23
---
# Review: PREPUSH-DELETE

## Achados

## Parecer
Aprovado. Diff de 2 commits sobre `origin/develop` lido inteiro (hook, testes, README, `docs/hooks.md`, `docs/fechamento-integrador.md`, fragmento de changelog).

- **Só o push de remoção pula a suíte:** `n_envios` conta as refs com `local_sha` não zerado (`case *[!0]*`); o desvio novo exige `n_refs > 0` e `n_envios == 0` fora do modo `--suite`, e fica depois do laço e antes da trava. Sem trava, sem fila, saída 0.
- **Remoção de `main`, `homolog` e `develop` continua recusada:** a checagem está dentro do laço, antes do desvio, e vale também para remoção (testes `test_apagar_main_homolog_ou_develop_segue_barrado` e a remoção comum com `develop` junto).
- **Push misto e push com código seguem iguais:** uma ref com código basta para `n_envios > 0`; o teste cobre remoção antes e depois do envio. A checagem de não fast-forward (R-VERIFY) não mudou e segue só para ref que envia.
- **Shellcheck:** `shellcheck .githooks/pre-push` sem saída, código 0. `python3 -m unittest tests.test_pre_push_trava`: 29 testes, OK. A suíte completa fica para o QA.
- Documentação (README, `docs/hooks.md`, `fechamento-integrador.md`) e fragmento de changelog coerentes com o comportamento novo.

Observações sem bloqueio (não pedem volta):
- `.githooks/pre-push:132-133`: o comentário de PREPUSH-JA-NO-REMOTO ainda diz que "o push que apaga ref traz uma linha e segue rodando a suíte"; ficou obsoleto com esta mudança. Vale ajustar numa próxima passagem pelo arquivo.
- `changelog.d/suite-paralela-d4.md:3` registra "o push que só apaga continua rodando"; é o fragmento histórico da outra entrega e a nova entrada o supera na release.
- Desvio de `R-VERIFY` já registrado no pedido (um commit com `--no-verify`, refeito com `--amend` antes do envio); o commit final 96bf396 passou pelo hook. Fica com o dono do processo, sem efeito sobre o código.
- Afrouxa a regra protegida (pre-push roda a suíte): o PR leva `afrouxa-regra` no título e o rótulo é do dono; segurança (E2.2) tem parecer próprio.
