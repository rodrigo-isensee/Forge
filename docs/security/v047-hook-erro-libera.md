---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-hook-erro-libera
commit: 804c96124a10056bd58c621c6e7e2aa5274a0cd5
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: v047-hook-erro-libera

Pedido v047, etapa E3.45: segurança por delta `9666b6bf..804c9612` (E3.42, dois testes vermelhos corrigidos), sobre o parecer aprovado da E3.40. Lido: `forge-check parecer delta` (no domínio: `tests/test_hooks_volta_corpus.py`; fora: `docs/hooks-fixtures.md` e `tests/apoio_volta_unica.py`, lidos mesmo assim) e `git diff 9666b6bf 804c9612 -- hooks bin scripts .githooks .github` (vazio). Rodado no head: `test_driver_do_lote_chama_o_executar_como_o_main_de_cada_hook` (verde). CI do head 804c9612 (run 43597198892): suíte nas 6 partes (3.12 e 3.14), verificações longas, instalação e teto de pulados verdes; vermelhos só `bateria (pareceres)` (pareceres desatualizados, que este parecer e o da E3.44 renovam) e `catraca` (mudança em controle, exige o rótulo `afrouxa-regra` do dono; já sabida, `hooks/` igual ao da E3.40).

## Delta
- Nenhum controle mudou: `hooks/`, `bin/`, `scripts/`, `.githooks/` e `.github/` byte a byte iguais aos da E3.40; A1 e A2 seguem fechados, C1 a C8 seguem cumpridos.
- `tests/apoio_volta_unica.py` e `tests/test_hooks_volta_corpus.py`: o driver do lote passa ao `_comum.executar` o `MARCADOR` do conformidade (`MarcadorDaPolitica(CRITICO, conformidade.json)`, hooks/conformidade.py:2893), o mesmo do `__main__` (hooks/conformidade.py:2959), em vez do `CRITICO` cru. O teste do A2 da segurança volta a provar a igualdade driver = produção; o corpus passa a rodar com o marcador real, então a prova fica mais fiel, não mais frouxa.
- `docs/hooks-fixtures.md`: índice regerado (2449 para 2463 fixtures; `errointerno-*` 17 para 31). Só documentação gerada; nenhuma fixture removida.

Sem bloqueante neste delta, sem sonda nova: as S1 a S10 da E3.36 valem, pois `hooks/` não mudou.

## Achados
- A3 (recomendado) hooks/conformidade.py:2878 · Sem mudança: termo só literal, `cp x docs//pedidos/v1.md` e formas ofuscadas passam com erro ou prazo (S7 a S9 da E3.36); exige ofuscação deliberada.
- A4 (recomendado) hooks/_comum.py:2791 · Sem mudança: declarar no PR o número medido na E3.17 e a limitação do erros.log (C5).
- A5 (recomendado) hooks/conformidade.py:2831 · Sem mudança: cartão para a guarda normal sobre troca de base por opção ou variável (`env -C`, `git --work-tree`, `GIT_WORK_TREE`, `git -C <dir> apply`, `git apply --directory`).
- A6 (recomendado) hooks/conformidade.py:2874 · Sem mudança: `git reset --hard origin/x` na develop passa com erro ou prazo; pre-push e proteção do remoto seguram o envio.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Risco declarado antes (configuração corrompida recusa escrita na raiz, disponibilidade) segue igual e vai ao dono pelo Jarvis. `gitleaks`, `zizmor` e `actionlint` não aplicáveis (sem segredo, workflow ou dependência no delta).
