---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v047-hook-estado-ilegivel
commit: a99c1a9fbb88229ad6b5d24dd25d2f664d0309e6
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-17
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

## Revalidação (E2.132)
Delta lido: `forge-check parecer delta docs/reviews/v047-hook-estado-ilegivel.md`, intervalo `c3f86d7a..b09916f7` (junção da `origin/develop` bf475209, lote A), sem o que veio da base. Instância que não fez a entrega.
- Domínio: `bin/forge-testes` e `tests/test_selo_e_entrega.py` chegam iguais à develop; contra bf475209 o único delta próprio é `tests/test_testes_tocados.py:67`, a contagem de 83 para 85 e o comentário com `test_conferencia_dois_pedidos` (E1.277) e `test_estado_ilegivel`. Sem guarda mudada; as specs de mutante não mudaram.
- Prova rodada por mim: `python3 -m unittest tests.test_testes_tocados`, 151 testes, OK (skipped=1). Sem PR aberto, não há CI a citar; a suíte inteira fica para o CI do PR.

## Revalidação (E2.424)
Delta lido: `forge-check parecer delta docs/reviews/v047-hook-estado-ilegivel.md`, intervalo `b09916f7..05d68fce` (junção da `origin/develop` 5e74c70e), sem o que veio da base. Instância que não fez a entrega.
- Domínio: `bin/forge-testes`, `docs/hooks.md`, `docs/hooks-fixtures.md`, `tests/test_selo_e_entrega.py`, `tests/test_testes_tocados.py`. Contra bf475209, o patch próprio de `docs/hooks.md` e `tests/test_selo_e_entrega.py` é o mesmo.
- `bin/forge-testes:106,115,169`: `test_estado_ilegivel` segue em `FORGE_CHECK`, `REAPROVEITAM_O_LOTE` e no mapa de `hooks/`, agora ao lado do `test_pr_hook_rapido` da develop.
- `tests/test_testes_tocados.py:68`: contagem 86 → 87 (develop mais `test_estado_ilegivel`); `docs/hooks-fixtures.md:5`: 2485 fixtures, igual a `ls tests/hooks/*/*.json | wc -l`.
- `hooks/agentes.py`, os testes do item e as specs de mutante não mudaram no intervalo nem na develop desde bf475209: sem guarda mudada, AR-12 não se aplica.
- Prova rodada por mim: `python3 -m unittest tests.test_testes_tocados tests.test_estado_ilegivel`, 166 testes, OK (skipped=1). Sem PR aberto, não há CI a citar; a suíte inteira fica para o CI do PR.

## Revalidação (E2.492)
Delta lido: `forge-check parecer delta docs/reviews/v047-hook-estado-ilegivel.md`, intervalo `05d68fce..c108ed34` (junção da `origin/develop` 86ac0fcb), sem o que veio da base. Instância que não fez a entrega.
- Domínio: `bin/forge-testes`, `docs/hooks-fixtures.md`, `tests/test_selo_e_entrega.py`, `tests/test_testes_tocados.py`. O patch próprio contra a develop é o mesmo de antes: `test_estado_ilegivel` em `FORGE_CHECK`, `REAPROVEITAM_O_LOTE` e no mapa de `hooks/`; contagem 87 (86 da develop mais o item); índice com 2496 fixtures, igual a `ls tests/hooks/*/*.json | wc -l`; `lancar(limpar=)` e o teste do selo com estado ilegível.
- O que mais aparece no delta (`quem_importa`, `juncao_limpa`, `test_forge_mutante` no mapa da spec) veio da develop. `hooks/agentes.py`, os testes do item e as specs de mutante não mudaram: sem guarda mudada, AR-12 não se aplica. Sem linha nova em `achados-recorrentes.md`.
- Provas rodadas por mim: `python3 -m unittest tests.test_testes_tocados tests.test_estado_ilegivel`, 170 testes, OK (skipped=1); `python3 -m unittest tests.test_selo_e_entrega.Hook` (a classe do teste do item), 11 testes, OK. Sem PR aberto, não há CI a citar; a suíte inteira fica para o CI do PR.

## Revalidação (E2.704)
Delta lido: `forge-check parecer delta docs/reviews/v047-hook-estado-ilegivel.md`, intervalo `c108ed34..d2d82ffa` (junção da `origin/develop` 5b1aacd5, com o #621), sem o que veio da base. Instância que não fez a entrega.
- Domínio: `bin/forge-testes`, `docs/adr/0003-hooks-deterministicos-e-silenciosos.md`, `docs/hooks.md`, `docs/hooks-fixtures.md`, `tests/test_testes_tocados.py`. Contra 5b1aacd5, o patch próprio de `docs/adr/0003` (item 4) e de `docs/hooks.md` é o mesmo de antes; a emenda do SessionStart veio da develop.
- `bin/forge-testes:107,117,173`: `test_estado_ilegivel` em `FORGE_CHECK`, `REAPROVEITAM_O_LOTE` e no mapa de `hooks/`, ao lado de `test_hook_destino_opaco`, `test_conformidade_opaco`, `test_pre_push_patch` e `test_ambiente_hook` da develop; os cinco módulos existem em `tests/`. Junção com os dois lados, sem módulo perdido.
- `tests/test_testes_tocados.py:77`: contagem 88 → 89 (develop mais `test_estado_ilegivel`); `docs/hooks-fixtures.md:5`: 2814 fixtures, igual a `ls tests/hooks/*/*.json | wc -l`.
- `hooks/agentes.py`, `tests/test_estado_ilegivel.py`, `tests/test_selo_e_entrega.py`, as specs `v047-hook-estado-ilegivel*` e os fixtures `estado-ilegivel-*` não mudaram no intervalo: sem guarda mudada, AR-12 não se aplica. Sem linha nova em `achados-recorrentes.md`.
- Provas rodadas por mim: `tests/test_estado_ilegivel.py`, 9 testes, OK; `tests/test_indice_fixtures.py`, 7 testes, OK; `tests/test_testes_tocados.py`, 162 testes: 160 OK e 2 falhas de ambiente (`ExecucaoAfetados.test_afetados_rodam_em_paralelo_e_anotam_o_log` e `test_dirigido_roda_so_os_modulos_do_mapa_e_anota_o_log`, rodados com `env -i` sem `TMPDIR`: o `forge-partes-*` caiu dentro do repo temporário e a guarda de árvore mudada disparou); os dois, de novo com o `TMPDIR` do sandbox, OK. Sem PR aberto, não há CI a citar; a suíte inteira fica para o CI do PR.

## Revalidação (v0474 E1.6)
Delta lido: `forge-check parecer delta docs/reviews/v047-hook-estado-ilegivel.md`, intervalo `d2d82ffa..a99c1a9f` (junção da própria branch e o realinhamento dos mutantes), domínio código e testes: só `tests/mutantes/v047-hook-erro-libera-3.json` (M22) e `tests/mutantes/v047-hook-erro-libera-4.json` (M32). Instância que não fez a entrega.
- O `de` e o `para` de M22 e M32 passam a acompanhar `hooks/agentes.py` atual (a linha após o `return` agora é `pasta_ilegivel = False`; `atualizar_estado(` agora vem dentro de um `try:`). A guarda mutada é a mesma (`if raiz is None` → `if False`; `if recusa is None` → `is not None`), assim como os testes; nenhum mutante entra ou sai. Cada `de` aparece uma vez em `hooks/agentes.py`.
- CI do PR 630 no a99c1a9f (run 44092335854): suíte 3.12 e 3.14 (5/5 partes), catraca, passos, verificações longas e instalação verdes; só `bateria (pareceres)` reprovou, porque este parecer estava preso ao d2d82ffa (R-REVIEW, "commit: desatualizado"). Este commit resolve isso.
- Provas rodadas por mim: `bin/forge-mutante --conferir --base 5b1aacd5`: "o trecho de cada spec do diff está no lugar"; `bin/forge-mutante --processos 1` com M22 e M32: `M22 · morreu · hooks/agentes.py:947`, `M32 · morreu · hooks/agentes.py:961`. Sem guarda mudada no código: AR-12 não se aplica e não há linha nova em `achados-recorrentes.md`.

## Parecer
Aprovado no head a99c1a9f. Na revalidação anterior: Aprovado no head d2d82ffa. Na anterior a ela: Aprovado no head c108ed34. Na anterior a ela: Aprovado no head 05d68fce. Na revalidação anterior: Aprovado no head b09916f7. Na anterior a ela: Aprovado no head c3f86d7a. Do review anterior (bc129c11): Requisitos do plano conferidos no código e nos testes:
- R1: `ler_estado` (`hooks/agentes.py:271-294`) abre com `O_NOFOLLOW | O_NONBLOCK`, confere `S_ISREG` pelo `fstat`, lê até `LIMITE_DO_ESTADO + 1` (1 MiB), e lança `EstadoIlegivel` em JSON inválido ou vazio, raiz que não é objeto, `agentes` ou `lapides` que não é lista e `OSError`. Ausente segue `{"agentes": []}`; `{}` libera (fixture `estado-sem-chave-agentes-libera`). Fica em `agentes.py`, como o plano pede.
- R2: `recusar_ilegivel` (`:832-836`) recusa só no `PreToolUse`, disparo e retomada, com R-TETO numa linha sem conteúdo do arquivo; o erro vai ao `erros.log`. O R-BRIEF segue antes e independente (`errointerno-estado-corrompido-sem-brief-bloqueia`; selo em dia com estado ilegível recusa por R-TETO em `tests/test_selo_e_entrega.py`).
- R3: com `EstadoIlegivel`, nenhum evento regrava; `SubagentStart` e `SubagentStop` saem com 0 e o arquivo fica intacto (`contem` nos fixtures, inclusive nos de rc 2).
- R4: a exceção de `fixar_estado_do_clone` marca `pasta_ilegivel` e recusa depois do R-BRIEF; o `return False` legítimo segue liberando. Fixture renomeado para `errointerno-clone-sem-estado-explore-bloqueia`.
- R5: `.forge/config.json` não JSON ou com raiz lista recusa com "configuração ilegível" (fixtures e `test_config_ilegivel_no_clone_recusa_sem_gravar`); no `SubagentStop` sai com 0.
- R6: ADR 0003, item 4, e `docs/hooks.md` no mesmo branch; fragmento em `changelog.d/`.
- Casos de teste da tabela do plano presentes (link para `/dev/null` e para JSON válido, pasta, FIFO, teto, `PermissionError` por monkeypatch, AR-4). Guardas mudadas com um mutante por linha (15, em duas specs de até 8). `bin/forge-testes` põe `test_estado_ilegivel` no mapa de `hooks/` e em `REAPROVEITAM_O_LOTE`; a contagem do `forge-check` foi a 83.

Provas rodadas por mim: `tests.test_estado_ilegivel` e `tests.test_agentes_clone`, 26 testes, OK (25 s). `bin/forge-mutante --base 7fff73e4` nas duas specs: M1 a M15 morreram, nenhum sobrevivente; `--cobertura --base 7fff73e4` sem condição mudada fora das declaradas. Sem PR aberto, não há CI a citar; a suíte inteira fica para o CI do PR.
