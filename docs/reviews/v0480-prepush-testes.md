---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-prepush-testes
commit: 94c0e13ebcf30b89358b992bf5a418cca15a6902
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 (E137.4, testes do envio local; revalidação E139.2)

Base 0e59c446, head 94c0e13e (volta E137.23). Item só de teste: por decisão do dono, este review é o único parecer. PR #824 (rascunho).

## Revalidação por delta
Delta lido (`forge-check parecer delta`): 8ceaaa99..94c0e13e, no domínio `changelog.d/v0480-prepush-testes.md` e `tests/test_pre_push_afetados.py` (+16 -3). `.githooks/pre-push` intocado.

- A1 resolvido. `flock_falso` (`tests/test_pre_push_afetados.py:294`) põe na frente do PATH do hook um `flock` que registra os argumentos e chama o verdadeiro; `reprova_sem_esperar` afirma o registro vazio (`:316`) e mantém as asserções de estado da trava. `NeutralidadeECaminhoCedo` herda o mesmo método (`:404`), então os casos de neutralidade e caminho cedo ganham a mesma prova.
- Mutante da S1 contra o teste novo: reprova (S1). Hook restaurado depois da sonda.
- Testes dos arquivos tocados no head: `ChecagensBaratasAntesDaTrava` e `NeutralidadeECaminhoCedo`, 11 testes, OK (1 pulado: shellcheck fora do PATH), 5,0 s. Suíte inteira só no CI do PR (`R-REVIEW`): as cinco partes da suíte, a instalação e a catraca do #824 no head estão verdes; o `bateria (pareceres)` vermelho lê o parecer reprovado anterior e deve passar a ler este.
- Fragmento do changelog atualizado para o mecanismo novo; texto consistente com o teste.

## Sondas
- S1 · mutante `flock -w 18 "$(trava_arquivo criar)" true || true` antes de `checagens_baratas` (`.githooks/pre-push:397`), test_sintaxe_python_reprova_antes_da_trava no head 94c0e13e · espera: reprova · obtido: FAILED em 18,1 s, registro `-w 18 .../forge-suite-0.lock true` != ''

## Parecer
Aprovado. O A1 do parecer 53508d1f está resolvido: a espera silenciosa curta na trava agora reprova, sem depender de relógio. O teste do processo morto segue como aprovado no parecer anterior.
