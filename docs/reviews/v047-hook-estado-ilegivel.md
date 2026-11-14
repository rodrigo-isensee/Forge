---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-hook-estado-ilegivel
commit: c3f86d7ac652408171ad3f356f4582161e6d9805
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-14
---
# Review: v047 · HOOK-ESTADO-ILEGIVEL-LIBERA (E1.229)

Intervalo revisado `origin/develop` (7fff73e4, contida no head) `..bc129c11`. Classe C, lote A do plano de segurança da série (`docs/security/v047-serie-hooks-pos-550.md`, A1 a A3). Instância que não fez a entrega.

## Achados
- A1 (recomendado) hooks/agentes.py:833 · resolvido em c3f86d7a: `CONFIG_ILEGIVEL` agora cita a configuração ou a raiz e remete ao erros.log (R-TETO).
- A2 (recomendado) hooks/agentes.py:937 · 236 linhas de código e teste nos caminhos que contam (M14), acima das 150, uma classe só com corpus próprio; o corpo do PR precisa de `teto: excedido, 236 linhas, <motivo>`, do endurecimento 0→2 dos dois fixtures e da medida do erros.log pedida no plano.

## Sondas

## Revalidação (E1.249)
Delta lido: `forge-check parecer delta docs/reviews/v047-hook-estado-ilegivel.md`, intervalo `bc129c11..c3f86d7a`, domínio código e testes: `hooks/agentes.py`, `tests/test_estado_ilegivel.py`, `tests/hooks/agentes/estado-ilegivel-{profundo,selado}-bloqueia.json`, `tests/mutantes/v047-hook-estado-ilegivel{,-2,-3}.json`, `docs/hooks-fixtures.md` (índice regenerado, 2481 fixtures). Instância que não fez a entrega.
- `ler_estado` (`hooks/agentes.py:287-290`): `except EstadoIlegivel: raise` antes de `except Exception`, então link, FIFO e teto saem com a mensagem própria e qualquer outro erro do leitor (o `RecursionError` do aninhado fundo, sondas S1 e S2 da segurança) vira `EstadoIlegivel`; nunca escapa nem libera. `Exception` não pega `KeyboardInterrupt`/`SystemExit`; o `MemoryError` cai no lado seguro.
- Testes: `test_json_aninhado_fundo_e_ilegivel` (raiz e `agentes` aninhados, 200000 `[`, abaixo do teto de 1 MiB); FIFO agora confere a mensagem exata (mata o M17); fixture `estado-ilegivel-profundo-bloqueia` (ponta a ponta, rc 2, intacto) e `estado-ilegivel-selado-bloqueia` (QA A2: brief selado passa o R-BRIEF e recusa por R-TETO, `stderr_sem` R-BRIEF).
- Mutantes: M5 reescrito para a nova linha, M16 (volta a `(OSError, ValueError)`) e M17 (tira o `raise` do `EstadoIlegivel`), um por guarda mudada.
- Provas rodadas por mim: `python3 -m unittest tests.test_estado_ilegivel`, 9 testes, OK; `bin/forge-mutante --processos 1 --base bc129c11` nas três specs: M1 a M17 morreram, nenhum sobrevivente; `--cobertura --base bc129c11`: só "spec editada", sem condição mudada fora das declaradas. Sem PR aberto, não há CI a citar; a suíte inteira fica para o CI do PR.

## Parecer
Aprovado no head c3f86d7a. Do review anterior (bc129c11): Requisitos do plano conferidos no código e nos testes:
- R1: `ler_estado` (`hooks/agentes.py:271-294`) abre com `O_NOFOLLOW | O_NONBLOCK`, confere `S_ISREG` pelo `fstat`, lê até `LIMITE_DO_ESTADO + 1` (1 MiB), e lança `EstadoIlegivel` em JSON inválido ou vazio, raiz que não é objeto, `agentes` ou `lapides` que não é lista e `OSError`. Ausente segue `{"agentes": []}`; `{}` libera (fixture `estado-sem-chave-agentes-libera`). Fica em `agentes.py`, como o plano pede.
- R2: `recusar_ilegivel` (`:832-836`) recusa só no `PreToolUse`, disparo e retomada, com R-TETO numa linha sem conteúdo do arquivo; o erro vai ao `erros.log`. O R-BRIEF segue antes e independente (`errointerno-estado-corrompido-sem-brief-bloqueia`; selo em dia com estado ilegível recusa por R-TETO em `tests/test_selo_e_entrega.py`).
- R3: com `EstadoIlegivel`, nenhum evento regrava; `SubagentStart` e `SubagentStop` saem com 0 e o arquivo fica intacto (`contem` nos fixtures, inclusive nos de rc 2).
- R4: a exceção de `fixar_estado_do_clone` marca `pasta_ilegivel` e recusa depois do R-BRIEF; o `return False` legítimo segue liberando. Fixture renomeado para `errointerno-clone-sem-estado-explore-bloqueia`.
- R5: `.forge/config.json` não JSON ou com raiz lista recusa com "configuração ilegível" (fixtures e `test_config_ilegivel_no_clone_recusa_sem_gravar`); no `SubagentStop` sai com 0.
- R6: ADR 0003, item 4, e `docs/hooks.md` no mesmo branch; fragmento em `changelog.d/`.
- Casos de teste da tabela do plano presentes (link para `/dev/null` e para JSON válido, pasta, FIFO, teto, `PermissionError` por monkeypatch, AR-4). Guardas mudadas com um mutante por linha (15, em duas specs de até 8). `bin/forge-testes` põe `test_estado_ilegivel` no mapa de `hooks/` e em `REAPROVEITAM_O_LOTE`; a contagem do `forge-check` foi a 83.

Provas rodadas por mim: `tests.test_estado_ilegivel` e `tests.test_agentes_clone`, 26 testes, OK (25 s). `bin/forge-mutante --base 7fff73e4` nas duas specs: M1 a M15 morreram, nenhum sobrevivente; `--cobertura --base 7fff73e4` sem condição mudada fora das declaradas. Sem PR aberto, não há CI a citar; a suíte inteira fica para o CI do PR.
