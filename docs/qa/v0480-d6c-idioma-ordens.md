---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0480-d6c-idioma-ordens
commit: 66c9f9a1869ca39537b97be3a3e70c73456ec93b
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA (revalidação por delta): idioma das mensagens ao dono na linha fixa das ordens (v0481 E1.3, PR #866)

Delta `0c7e8f0c..318ec8a7` (head da branch). O merge da develop (66c9f9a1) trouxe a base a27eab7e (vigia de agentes e pesado, E172.3): `hooks/_comum.py`, `hooks/agentes.py`, `hooks/pesado.py`, 6 fixtures novas, `tests/test_hooks.py`, mutantes da base e `docs/hooks-fixtures.md`. Nada disso é do #866; o código do pedido (`hooks/ordens.py`, mutantes M1 a M8, fixtures de idioma) não mudou desde 0c7e8f0c, e o parecer E174.14 (aprovado) vale para ele.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Índice de fixtures soma os dois lados do merge | `test_indice_fixtures` e regeneração por `scripts/indice-fixtures.py` | corpus de 3579 `.json` | passou |
| `tests/test_hooks.py` vindo da base não derruba o pedido | `OrdensEmVigor` e `test_vigia_prazo_trava_sem_marcador_recusa_e_fora_da_sessao_vigiada_libera` | hook sem marcador crítico | passou |
| Critérios anteriores (A1 aninhado, idioma, FIFO, teto) | `OrdensEmVigor` inteiro | JSON profundo, lista de códigos | passou |

## Provas
- Índice: o diff `0c7e8f0c..318ec8a7` em `docs/hooks-fixtures.md` vai de 3573 para 3579 fixtures (`agentes` 130 para 133, `pesado` 27 para 30, mais as linhas `vigia-*`), e a contagem de `.json` em `tests/hooks` é 3579: bate. Rodei `scripts/indice-fixtures.py` na árvore e não houve diferença com o arquivo commitado; as linhas de `ordens` do #866 seguem no índice. O índice só soma os dois lados.
- `python3 -I -m unittest discover -s tests -p test_indice_fixtures.py`: 7 testes, OK.
- `python3 -I -m unittest discover -s tests -p test_hooks.py -k OrdensEmVigor`: 23 testes, OK.
- `forge-check parecer delta`: domínio = `docs/hooks-fixtures.md` e `tests/test_hooks.py`, sem o que veio da base; ambos conferidos acima (o trecho de `test_hooks.py` é do vigia, E172.3, coberto pelo parecer da base `v0480-vigia-agentes-pesado`).
- Mutantes e vermelho: sem rerrodar; o código e os testes do pedido não mudaram desde o parecer E174.14.
- CI: a suíte inteira não rodou aqui; o check-run `bateria` do PR #866 no sha final segue obrigatório para o merge.
