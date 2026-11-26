---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-g2-1-publicar
commit: 939e4d22a8040dcf65b47201c97c6d7a17ed795e
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-26
---
# QA: v0481-g2-1-publicar (E6.33, PR #878, G2.1: forge-check parecer publicar; classe C), volta por delta

Parecer anterior: aprovado em dc6bc47e (E6.27). Head revisado 939e4d22 (`HEAD` = remoto). Delta lido: `git diff dc6bc47e..939e4d22`: só a develop trazida com o #885 (merge 939e4d22; conflito só em `docs/hooks-fixtures.md`, índice gerado, regenerado) mais os pareceres do commit anterior.

## Critério → teste → resultado (delta)
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A lógica do item não mudou: o patch contra a develop é igual ao aprovado | linhas `+/-` ordenadas, fora do índice e de `docs/qa`, `docs/reviews`, `docs/security`: `git diff 6cc4cd5a dc6bc47e` e `git diff 34ab6714 939e4d22` dão o mesmo md5 (a3e73501...) e os mesmos 27 arquivos | patch por base | igual |
| Nenhum teste se perdeu | `test_fixtures_do_publicar` (9 fixtures, mínimo 9) | `--raiz` antes do subcomando e depois do `--` | passou |
| Recusa com FIFO no perfil | `RecusaComFifoNoPerfil`, 7 testes | FIFO no perfil | passou |
| Git dos testes com o ambiente do ponto único | `tests/test_forge_pareceres.py`, 35 testes | sem configuração de manutenção do usuário | passou |
| Índice regenerado: 3592 = 3583 da develop + 9 `contrib-publicar` | `git diff 34ab6714 939e4d22 -- docs/hooks-fixtures.md`: só linhas das 9 fixtures da branch | n/a | conferido |

## Cenários e resultado real
- Só os módulos tocados: `test_hooks.py -k test_fixtures_do_publicar` 1 teste OK; `-k RecusaComFifoNoPerfil` 7 testes OK; `test_forge_pareceres.py` 35 testes OK. A suíte inteira ficou com o CI.
- Mutantes (`bin/forge-mutante --processos 2 tests/mutantes/v0481-g2-1-publicar-6.json`, `rev=939e4d22a804`): M31 a M37 `morreu` (hooks/conformidade.py:2646, 2649, 2649, 1391, 1393, 1392, 1389; as linhas andaram com o #885, o conteúdo é o mesmo). Sem sobrevivente.
- Vermelho antes do verde: sem teste novo no delta; o da A1 já foi visto vermelho no parecer dc6bc47e.

## CI do head exato
`gh pr checks 878`, runs 45732216497 e 45732216156 com `headSha` 939e4d22a8040dcf65b47201c97c6d7a17ed795e: `suíte (python 3.12 e 3.14, partes 1 a 5)`, `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, `teto de pulados` (2), `instalação (python 3.14)` e `árvore já provada na develop` verdes. `catraca`, `bateria (pareceres)` e `bateria` esperam o rótulo e os pareceres deste head, fora das partes que contam.

- ci: 939e4d22a8040dcf65b47201c97c6d7a17ed795e verde

## Parecer
Aprovado no head 939e4d22: a lógica não mudou (patch idêntico ao aprovado em dc6bc47e), nenhum teste se perdeu, mutantes todos mortos e CI verde nas partes que contam.
