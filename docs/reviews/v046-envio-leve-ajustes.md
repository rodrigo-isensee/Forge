---
tipo: review
contrato: 1
pedido: v046
branch: melhoria/envio-leve-ajustes
commit: 1beb0d5aee9f14ae6db5a1fd1b4053ddd581caaf
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-12
---
# Review: v046 (E19.1, recomendados do envio leve), volta 1

Head revisado: 73d0017a. Parecer anterior: reprovado no c3e271e5 (A1 bloqueante, A2 e A3 recomendados).

Delta lido: `git diff c3e271e5..73d0017a` mostra um commit, 2 arquivos, +3/-2. O `forge-check parecer delta` não serviu nesta raiz ("commit c3e271e5... não existe", porque a raiz dos pareceres não tem o histórico da branch), então o delta foi lido pelo `git diff` no clone.
- `tests/test_pre_push_leve.py:108-109`: o commit "token" grava também `scripts/verificar-contribuicao.sh` com `#!/bin/bash\nexit 0`. É a correção sugerida para A1, e o comentário explica por quê.
- `README.md:68`: "Só com o opt-in há uma exceção curta (o envio leve sai antes dela)". Isso resolve A2.

O diff continua sem mudar guarda (`.githooks/pre-push` fica intocado), então não há mutante a declarar.

## Achados
- A3 (recomendado) docs/regras/R-TETO.md:16 · segue sem mudança: "o envio local não roda teste" é absoluto, mas com `FORGE_PREPUSH_SUITE=afetados` ou `=1` roda. Sugestão: "por padrão, o envio local não roda teste". Não bloqueia e não é motivo de nova volta.
- A4 (bloqueante) bin/forge-testes:139 · resolvido em 1beb0d5a; o mapa não aponta `test_pre_push_leve` para `scripts/verificar-contribuicao.sh`, que o teste lê e grava (linhas 47 e 109). O CI do #503 cai em `test_testes_tocados`. O defeito já estava no 73d0017a. Correção: incluir o módulo na tupla.

## Sondas
- S1 · pre-push:212 `segredo_no_delta || true`; test_segredo_no_delta_ainda_barra_sem_imprimir_o_valor no head 73d0017a · espera: FAILED · obtido: FAILED (failures=1, `(0, False) != (1, False)`)
- S2 · controle: o mesmo mutante no c3e271e5 · espera: OK (mutante vivo, como na volta 0) · obtido: OK
- S3 · CI do PR #503, run 43225790681, suíte parte 2/3 (3.12 e 3.14) · espera: OK · obtido: FAIL `test_todo_arquivo_lido_por_um_modulo_roda_esse_modulo` (modulo='test_pre_push_leve', caminho='scripts/verificar-contribuicao.sh')

## Parecer
Reprovado no 528abfd4 por A4, o defeito que o CI provou. Abaixo, o que a volta 1 já tinha resolvido.
- **A1 resolvido:** o teste prova a barreira da base. Com a guarda da linha 212 mutada, ele cai no head 73d0017a. No head anterior, o mesmo mutante sobrevive (S2), o que mostra que é a mudança do teste que mata o mutante.
- **A2 resolvido:** o README agora diz que a exceção do `so_parecer` só vale com o opt-in, o que bate com pre-push:380 (o envio leve sai antes).
- **A3:** continua recomendado, sem bloquear.
- **Commit:** a mensagem segue Conventional Commits em português e cita os achados.

Execução no head (worktree destacada, ambiente limpo com `TMPDIR` mantido): `python3 -m unittest tests.test_pre_push_leve` deu `Ran 8 ... OK`. `tests.test_metricas_texto`, `tests.test_achado_teto_doc` e as classes `Referencias`, `Neutralidade` e `RegrasInviolaveis` de `tests.test_forge` também deram OK. Sem o `TMPDIR`, 2 testes caem por `mktemp` em `/tmp` só leitura: é efeito do ambiente, não da branch. A suíte inteira não foi rodada; o CI do PR é o portão.

## Integração (E19.2)
Merge da origin/develop (d3453407) em 528abfd4, sem rebase. Conflito só de texto em `docs/economia-de-tokens.md` (item 5) e `docs/regras/R-TETO.md:16`: ficou o texto da develop (TEMPO-A, exceção do `--duas-partes`) com a frase da ENVIO-LEVE inserida e "o envio local não roda teste" no lugar de "roda os afetados". Nenhum código nem teste mudou na resolução; o diff contra a develop segue nos 6 arquivos da E19.1. Rodados no merge: `test_pre_push_leve` (8 OK), `test_suite_paralela` (61 OK), `test_prepush_so_docs` (62 OK, 9 skip).

Revalidação por delta no head 528abfd4: o `forge-check parecer delta` (escopo sem o que veio da develop) lista só `docs/economia-de-tokens.md` e `docs/regras/R-TETO.md`, que são a resolução descrita acima. O `.githooks/pre-push` que o `forge-check pr` aponta mudou só pelo que veio da develop, já integrado e revisado lá. A resolução não tem achado. O CI do PR #503, porém, provou A4, que já vinha da E19.1: o parecer passa a reprovado.

## Revalidação por delta (E19.4), head 1beb0d5a
Instância que não fez a volta. Delta lido: `forge-check parecer delta docs/reviews/v046-envio-leve-ajustes.md` (intervalo 528abfd4..1beb0d5a) põe no domínio só `bin/forge-testes`; `git diff 55ea12e5..1beb0d5a` é um commit, 1 arquivo, +1/-1.
- **A4 resolvido:** bin/forge-testes:139 passa a listar `test_pre_push_leve` na tupla de `scripts/(validar-plugin|configurar-ambiente-local|preparar-estacao|verificar-contribuicao)\.sh`. Os cinco módulos que já estavam (`test_forge`, `test_pre_push_segredo`, `test_pre_push_afetados`, `test_testes_tocados`, `test_salvar_desfazer`) seguem lá, e a regex não mudou. O módulo vale também para os outros três scripts da linha: sobra seleção, não falta.
- Nenhuma guarda mudou (é um dado do MAPA), então não há mutante a declarar. Os AR-1 a AR-12 de `achados-recorrentes.md` não alcançam o delta.
- Execução: `python3 -m unittest tests.test_testes_tocados` no head deu `Ran 149 tests ... OK (skipped=1)`. A suíte inteira fica para o CI do PR #503.

Veredito: **aprovado** no 1beb0d5a. A3 continua recomendado, sem bloquear.
