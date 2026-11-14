---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-hook-estado-ilegivel
commit: bc129c11739dbaa9a3d0d12951adcbb7fe9bcae9
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 1
bugs_baixos: 0
data: 2026-11-14
---
# QA: v047-hook-estado-ilegivel

Pedido v047, etapa E1.231, lote A (classe C, `hooks/agentes.py`): HOOK-ESTADO-ILEGIVEL-LIBERA, plano de segurança `docs/security/v047-serie-hooks-pos-550.md` (R1 a R6). Intervalo `origin/develop..bc129c11` (base `7fff73e4`). Sem especificação de UX nem contrato de API: as obrigações são as linhas R1 a R6 e a tabela de fixtures do plano. Acessibilidade e E2E: n/a.

## Achados
- A1 (bloqueante) hooks/agentes.py:286 · `ler_estado` captura só OSError e ValueError: agentes.json com `[` repetido 200000 vezes (abaixo de 1 MiB) lança RecursionError, que escapa e libera o disparo com rc 0, sem teto; reproduzido; R-TETO
- A2 (recomendado) tests/test_estado_ilegivel.py:1 · falta a fixture `estado-ilegivel-selado-bloqueia` da tabela do plano (brief selado com estado ilegível dá R-TETO, não R-BRIEF); sem prova própria do ramo; R-TETO
- A3 (recomendado) tests/mutantes/v047-hook-estado-ilegivel.json:1 · sem mutante para a captura de exceções do json.loads (linha 286); por isso os 15 mutantes morrem e o A1 passa; ao corrigir, somar mutante que tire a nova captura; R-QA

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| R1 leitura estrita: texto, vazio, raiz lista, `agentes`/`lapides` não lista | fixtures `estado-ilegivel-{texto,vazio,lista-na-raiz,agentes-numero,agentes-texto,lapides}-bloqueia` | vazio, tipo da raiz, tipo das chaves | passou (rc 2, R-TETO) |
| R1 pasta, link para `/dev/null`, link para JSON válido | `estado-ilegivel-{pasta,link-dev-null,link-valido}-bloqueia` | não seguir link, não abrir pasta | passou |
| R1 arquivo ausente segue válido; chave ausente libera | `estado-sem-chave-agentes-libera` e fixtures de começo | ausência legítima | passou |
| R1 teto de 1 MiB | `ler_estado` (mutante M2) | limite máximo | passou (mutante morto); sem fixture dedicada |
| R1 JSON com aninhamento fundo | nenhum | JSON profundo abaixo do teto | **falhou**: RecursionError escapa (A1) |
| R2 mensagem curta sem conteúdo do arquivo | fixtures acima (`stderr`) | vazamento de conteúdo | passou |
| R3 SubagentStart e SubagentStop não regravam e saem 0 | `estado-ilegivel-{inicio,fim}-nao-regrava-libera` | evento sem veto | passou |
| R3 retomada recusa | `estado-ilegivel-retomada-bloqueia` | RETOMADA | passou |
| R4 erro ao fixar a pasta do estado recusa depois do R-BRIEF | `erro-interno-clone-sem-estado-explore-bloqueia`, `erro-interno-estado-corrompido-sem-brief-bloqueia` | ordem R-BRIEF antes do estado | passou |
| R5 `.forge/config.json` ilegível ou raiz lista | `config-ilegivel-bloqueia`, `config-raiz-lista-bloqueia`, `config-ilegivel-fim-libera` | config corrompida | passou |
| R6 ADR 0003 e `docs/hooks.md` | diff | n/a | presente |
| Selado com estado ilegível (plano) | nenhum | R-TETO, não R-BRIEF | lacuna (A2) |

## Provas

**Testes locais** (`python3 -m unittest tests.test_estado_ilegivel tests.test_agentes_clone`): `Ran 26 tests in 25.811s`, `OK`. A suíte inteira roda só no CI do PR; o check-run `bateria` deste sha não consultei (sem `gh` no ambiente), nenhuma citação de CI.

**Vermelho (à mão)**: `forge-testes --vermelho origin/develop` passou de 180 s e foi para segundo plano, sem veredito até esta entrega (nunca vale como vermelho). À mão: cópia do HEAD em `$TMPDIR` com `hooks/agentes.py` trocado pelo de `origin/develop`; `python3 -m unittest tests.test_estado_ilegivel` deu `Ran 8 tests`, `FAILED (failures=18, errors=6)` (ex.: `AssertionError: 0 != 2`). Com o código do lote, os mesmos 8 passam. Os testes provam a mudança.

**Mutação** (`bin/forge-mutante tests/mutantes/v047-hook-estado-ilegivel.json tests/mutantes/v047-hook-estado-ilegivel-2.json --processos 4`): rc 0; `forge-mutante: pedido=v047-hook-estado-ilegivel rev=bc129c11739d`; M1 a M15 `morreu` (15 de 15). Cobertura (`--cobertura --base origin/develop`): `base=7fff73e4… mb=7fff73e4… rev=bc129c11…`, 9 condições `coberta`; nenhuma sem mutante, nenhum sobrevivente. A captura da linha 286 não é condição mudada que a lista cubra (A3).

**Sonda do A1** (`ler_estado` sobre arquivo com `[` x 200000): saída `ESCAPA RecursionError` (esperado `EstadoIlegivel`). Confirma a sonda S1 do parecer de segurança (`e915233e`): rc 0 pelo hook, erros.log `RecursionError`. Bug: média (ator interno, `R-TETO` contornável pelo agente que escreve o `agentes.json`).

**Delta** (`forge-check parecer delta`): remoto avançou com `e915233e` (só `docs/security/v047-hook-estado-ilegivel.md`); fora do domínio do QA.

## Para a revalidação
Corrigir a captura em `ler_estado` (ex.: `Exception` em torno de `os.open` até `json.loads`, ou somar `RecursionError`); fixture `estado-ilegivel-profundo-bloqueia` (`"[" * 200000`, Explore, rc 2, arquivo intacto) e `estado-ilegivel-selado-bloqueia`; mutante da captura. Responsável: tech-lead (autor do lote A). Reteste: `forge-check parecer delta docs/qa/v047-hook-estado-ilegivel.md`.
