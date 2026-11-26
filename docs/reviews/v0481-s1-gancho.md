---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-s1-gancho
commit: 0ad62d85b2e03ae72f1d1cb369e635786acea285
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 (E20.14, #920, hook estado)

1ª rodada completa do #920 no head `0ad62d85`, sobre a base `3c833f3f`. Cobre E20.11 (hook `estado`, emenda da ADR 0003 itens 1 e 2) e E20.12 (conserto do CI).

## Escopo conferido
- Entregar contra os commits: E20.11 em `f7bd4997`, `3032e766`, `0b26e43a` e `72e2f3b0`; E20.12 em `0ad62d85`. Nenhum item sem commit.
- Tamanho (H1): 82 linhas de código (`hooks/estado.py` 70, `hooks/hooks.json` 10 líquidas, `bin/forge-testes` 2), um comportamento; dentro do teto.
- Faz o que o pedido pede: só no `UserPromptSubmit`, só pergunta curta do estado, comando fixo do plugin (`python3 -I <plugin>/bin/forge-check status --raiz <raiz>`), nada da mensagem no argv, só linhas `status:` com teto e `sem_controle`, linha fixa na falha, sai sempre com 0.
- ADR 0003, emenda: traz "Por que o existente não basta" com evidência, o que afrouxa (itens 1 e 2 e os três invariantes de teste, nenhum de `tests/config.json`), critério de reversão e leituras com dono. O título do PR traz `[afrouxa-regra: ADR 0003 itens 1 e 2]`; o rótulo é do dono.
- Neutralidade (`R-NEUTRO`): a emenda cita "um projeto que usa o Forge", sem nome (E20.12).
- Mapa do `bin/forge-testes`, peso em `tests/pesos-d4.json`, `docs/hooks-fixtures.md`, `docs/indice-forge.md` e fragmento `changelog.d/v0481-s1-gancho.md` atualizados.
- Segurança (injeção do texto do GitHub no contexto pelas linhas `status:`) fica com o parecer do `security-engineer` (E20.15, `R-SEGURANCA`); não refeito aqui.

## Verificações
- ci: 0ad62d85b2e03ae72f1d1cb369e635786acea285 verde
  - `gh pr checks 920`, run 45879386715 no head `0ad62d85`: suíte 3.12 e 3.14 (partes 1 a 5), instalação, passos, verificações longas, teto de pulados e árvore provada verdes; `bateria`, `bateria (pareceres)` e `catraca` esperam os pareceres e o rótulo.
- Testes do diff, rodados com ambiente limpo: `tests.test_hook_estado`, `test_hooks.Hooks.test_hooks_json`, `test_hooks.Hooks.test_cada_hook_tem_caso_que_passa_e_que_bloqueia`, `test_doutor.HookDoutor.test_hooks_json_registra_o_doutor_so_em_sessionstart_e_stop`: `Ran 18 tests ... OK`.
- Mutantes declarados (`bin/forge-mutante --processos 1` com as duas specs): M1 a M15, 15 de 15 morreram. `--cobertura --base 3c833f3f`: toda guarda de `hooks/estado.py` coberta; só o `__name__ == '__main__'` sem mutante.
- Prazo: `forge-check status` real no clone levou 3,41 a 3,72 s (3 rodadas), abaixo do `PRAZO_S` de 8 s e dos 10 s do `hooks.json`.
- Shell: nenhum arquivo de shell no diff.
- Teste com subprocesso: ambiente limpo; usa `-s -E` (a forma do `hooks.json`) em vez de `-I`, com o motivo escrito na docstring (o `-I` tira a pasta do script, de onde vem o `_comum`). Aceito.

## Achados
- A1 (recomendado) hooks/estado.py:61 · No clone do Forge, `hooks_desligados: ["estado"]` não silencia o hook (`_comum.py:2655`, o manifesto vence), e a emenda (regra 5) diz que hook desligado na config fica em silêncio. Ajuste o texto da emenda ou a checagem do desligado para o estado.
- A2 (recomendado) hooks/estado.py:18 · `estado` e `status` casam ordens curtas ("atualize o estado do cartão"), e cada uma paga uns 3,5 s do `forge-check status` (medido no clone). Some a contagem de disparos por mensagem à leitura da emenda para medir o falso positivo.

## Parecer
Aprovado. O hook faz só o que a emenda descreve, as guardas têm teste de comportamento do ramo de falha e mutante morto, e o CI do head está verde fora dos checks que esperam o parecer e o rótulo. A1 e A2 viram cartão depois do merge. O merge espera o rótulo `afrouxa-regra` do dono e os pareceres do QA e da segurança.
