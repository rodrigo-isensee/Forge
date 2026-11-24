---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-vigia-agentes-pesado
commit: 25c60be778696f894a488b8a266d5874db63ef9b
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 E172.35 (PR #859, revalidação por delta no head 25c60be7; item E172.3)

Revalidação pelo delta (`forge-check parecer delta`, intervalo `e54654c9..25c60be7`). No domínio do review: `tests/mutantes/v0455-prazo.json`, `tests/mutantes/v0480-vigia-trava-critica.json`, `tests/test_hooks_volta_propriedades.py`; o resto do delta são os pareceres do QA, da segurança e o meu anterior. Código de `hooks/` sem mudança desde o parecer reprovado em e54654c9.

## Achados
- A3 (recomendado) hooks/pesado.py:450 · mantido do parecer anterior: alarme de 290 s entre o gravar_a_vez e a saída do hook deixa a trava gravada sem PostToolUse que a solte; vira cartão depois do merge.
- A4 (recomendado) docs/hooks.md:1 · mantido do parecer anterior: a seção do vigia ainda o descreve só no conformidade e no parecer; vira cartão depois do merge.

## Sondas
- S1 · python3 -m unittest tests.test_forge_mutante.ConferirTodas.test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes (env -i, head 25c60be7) · espera: OK · obtido: OK
- S2 · python3 -m unittest tests.test_ambiente_git.LeituraEstatica.test_nenhum_modulo_roda_git_sem_o_ponto_unico (env -i, head 25c60be7) · espera: OK · obtido: OK

## Parecer
Aprovado. A1 resolvido: P11 (`hooks/_comum.py:2900`) e M1 a M4 (`hooks/_comum.py:2861` e `:2863`) apontam a fonte atual; M3 agora muta a guarda nova (`critico is None and evento != "PreToolUse"`), um mutante por linha de guarda. A2 resolvido: o `git init` do `VigiaAgentesPesado` monta o env com `sem_manutencao`.

Rodado aqui no head 25c60be7: S1, S2 e `tests.test_hooks_volta_propriedades.VigiaAgentesPesado` (5 testes OK em 28,5 s); `bin/forge-mutante --processos 1` em `v0480-vigia-trava-critica.json --ids M1,M2,M3,M4` (4 de 4 mortos; M2 e M4 por erro do teste declarado) e em `v0455-prazo.json --ids P11` (morto).

CI do head 25c60be7 (run 45440138432): as 10 partes da suíte nas duas versões de Python, `instalação`, `teto de pulados`, `bateria (passos)` e `bateria (verificações longas)` verdes; `bateria`, `bateria (pareceres)` e `catraca` vermelhos aguardam os pareceres neste head.
