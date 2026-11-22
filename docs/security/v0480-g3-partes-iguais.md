---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-g3-partes-iguais
commit: 790f114d38117b7da7232f9b7b94f98c945d03aa
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-22
---
# Review de segurança: v0478 (E102.10, revalidação das fatias de test_fixtures e do T1)

Revalidação por delta do parecer em 4c0b3842 (commit 7b62627b). Head 790f114d.

## Gatilhos
Gatilhos: teste de controle dos hooks de conformidade (cobertura das fixtures e do T1 de HOOK-COMENTARIO-SHLEX, ADR 0013).

## Delta lido
`forge-check parecer delta`, intervalo 4c0b3842..790f114d: no domínio só `tests/test_hooks.py` (+12/-2); fora, `changelog.d/v0480-g3-partes-iguais.md`. Sem mudança em `hooks/`, `bin/`, `scripts/`, `.githooks/` nem `.github/`.

## Achados anteriores
- A1 (recomendado): corrigido. `corpus_da_fatia(k)` (`tests/test_hooks.py:2682-2685`) é o único corte; `verificar_t1_da_fatia` (`:2715`) e `test_t1_as_fatias_cobrem_todo_o_corpus` (`:2696`) o chamam.
- A2 (recomendado): corrigido. `test_fatias_travadas_aos_metodos` (`:2687-2691`) compara a contagem de métodos `test_fixtures_fatia_*` e `test_t1_fatia_*` com as constantes. O prefixo não pega `test_fixtures_as_fatias_cobrem_todas` nem `test_t1_as_fatias_...`. Sondas S1 e S2: as duas mutações ficam vermelhas.

## Sondas
- S1 · `FATIAS_DO_T1=5` em memória e rodar `test_fatias_travadas_aos_metodos` · espera: falha · obtido: `AssertionError: 4 != 5`
- S2 · `del Hooks.test_fixtures_fatia_4` e rodar o mesmo teste · espera: falha · obtido: `AssertionError: 3 != 4`

## O que foi conferido
- A trava conta métodos e não confere qual `k` cada método passa. Hoje os 8 métodos passam 0 a 3 sem repetição (`:755-765`, `:2670-2680`). Repetir um `k` seria erro de edição visível no diff, sem caminho de ataque. Não é achado.
- Execução local: `test_fatias_travadas_aos_metodos` e `test_t1_as_fatias_cobrem_todo_o_corpus` passaram (2 testes, 7,2 s). As fatias e a suíte inteira ficam para o CI do PR. Não há run de CI neste head (sem PR, como diz o brief).

## Riscos aceitos e ferramentas
Sem risco aceito. Revisão estática do delta, mais sondas de mutação em memória. Não houve varredura de segredo nem de dependência porque o delta não tem credencial nem dependência.
