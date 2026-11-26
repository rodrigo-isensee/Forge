---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-rotulo-base-alheia
commit: 5c21b249e8612ceda94e015fd436cba2156ce757
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 E17.6 (#906, ROTULO-NAO-CAI-COM-BASE-ALHEIA), 2ª rodada por delta

Revalidação (H3): li só `forge-check parecer delta docs/reviews/v0481-rotulo-base-alheia.md` (`revalida: sim`, motivo `tests/mutantes/v0481-rotulo-base-alheia.json mudou depois do parecer`) e o `git diff 48034214..5c21b249`. Código do delta: 1 commit (`5c21b249`), `tests/test_catraca.py` (+9, 1 teste) e a spec `tests/mutantes/v0481-rotulo-base-alheia.json` (+10, RB3); o resto do delta são os pareceres de QA, segurança e este. Nenhum código de controle mudou (`tests/catraca.py` e `bin/forge-check` iguais ao `48034214`). Não houve merge da develop no delta: não há resolução de conflito a conferir.

## Delta lido
- O teste `test_aceites_da_catraca_igual_ao_aceites_do_usuario_do_forge_check` responde ao A1 da segurança: lê o `bin/forge-check` por `ast`, pega a atribuição de topo `ACEITES_DO_USUARIO` (hoje `bin/forge-check:2298`), exige exatamente uma e compara com `catraca.ACEITES` por `assertEqual`. Valor literal por `ast.literal_eval`, sem executar o script. Se a atribuição virar anotada ou sumir, o teste falha pela contagem, com mensagem; não passa à toa.
- O teste lê a fonte, mas é teste de paridade de duas constantes, não de comportamento de guarda: o ramo de falha do `ACEITES` segue provado pelo teste de comportamento do RB1. Aceito.
- RB3 (`tests/catraca.py:45`, `aceites/` para `aceite/`) troca a constante; a spec lista o teste novo e o mutante morre.

## Testes e mutantes
- `python3 -m unittest test_catraca.RotuloSobreviveAoConteudo` (em `tests/`): 24 testes OK.
- `bin/forge-mutante --processos 1 tests/mutantes/v0481-rotulo-base-alheia.json` (rev=5c21b249e861): `RB1 · morreu · tests/catraca.py:1394`, `RB2 · morreu · tests/catraca.py:44`, `RB3 · morreu · tests/catraca.py:45`.
- `bin/forge-mutante --cobertura --base 48034214`: `spec editada`; nenhuma linha de código nova no delta.

## CI
- ci: 5c21b249e8612ceda94e015fd436cba2156ce757 verde via 25f41578416c2c7020ad98b9db985396cabeefd0
- O run do `5c21b249` (45819056129) foi cancelado pelo envio do parecer de segurança (`25f41578`, só `docs/security/v0481-rotulo-base-alheia.md`). No run 45819574090 do `25f41578`: as 10 partes da suíte, `bateria (python 3.14)`, `bateria (passos)`, `bateria (verificações longas)`, `instalação`, `árvore já provada` e os 2 `teto de pulados` verdes.
- Vermelhos que esperam o portão, lidos no log: `bateria (pareceres)` (R-REVIEW, parecer de review desatualizado pela spec; este o renova), `bateria` (agregador, cai por ela) e `catraca` (R-CONFORMIDADE, `tests/catraca.py`, espera o rótulo `afrouxa-regra` do dono depois do último push).

## Achados
- A1 (recomendado) tests/catraca.py:45 · (da 1ª rodada, segue aberto) ACEITES cobre só aceites/; o forge-check (PASTAS_RECUSADAS_DE_PARECER) e o forge-changelog tratam docs/security/ameacas/ como não parecer. Um modelo de ameaças tocado antes do rótulo fica livre depois. Vira cartão depois do merge.

## Parecer
Aprovado. O delta fecha o A1 da segurança com o teste de paridade e o mutante RB3 que ele mata, sem mexer em código de controle. O A1 deste review não bloqueia e vira cartão.
