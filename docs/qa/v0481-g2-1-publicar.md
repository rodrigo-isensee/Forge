---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-g2-1-publicar
commit: dc6bc47efb98f0f017510992325e629f64e29214
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: v0481-g2-1-publicar (E6.27, PR #878, G2.1: forge-check parecer publicar; classe C), 3ª volta por delta

Base 6cc4cd5a, head dc6bc47e; delta lido: `git diff 841c14dc..dc6bc47e` (E6.25: `ultima_raiz` para no `--`, M37, git do teste com o ambiente do ponto único, linha no índice, develop trazida). Cópia pelo `forge-copia clone` em `/root/.forge-contrib/wt/v0481-g2-1-publicar-qa-engineer`, no head do remoto (`HEAD` = `ls-remote` = dc6bc47e). Parecer anterior (841c14dc): reprovado por A1 (regressão do `--`, sonda S4).

## Critério → teste → resultado (delta)
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A1 do QA 841c14dc / E6.22 / E6.24: `--raiz=` depois do `--` não conta (é o arquivo do argparse) e a primeira `--raiz` no Forge barra | fixture `contrib-publicar-raiz-depois-do-separador-no-forge-bloqueia` em `test_fixtures_do_publicar` (lado 2); mínimo subiu a 9 | `--raiz` antes do subcomando no Forge, outra depois do `--` | passou |
| Nada que barrava deixa de barrar | as 8 fixtures anteriores, mesmo teste (lotes 0 e 2) | `--raiz` única e duas `--raiz` sem `--` | passou |
| M37 (condição do `--`) | `bin/forge-mutante` M37 | só a condição, comentário igual | morreu |
| Ambiente do ponto único no git do teste (`sem_manutencao`) | `tests/test_forge_pareceres.py`, 35 testes | git dos testes sem configuração de manutenção do usuário | passou |
| Recusa sem prazo vencido e `perfil_iniciante` (veio da develop, #886; fora do domínio deste PR) | `RecusaComFifoNoPerfil`, 7 testes | FIFO no perfil | passou |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_hooks.py -k test_fixtures_do_publicar`: 1 teste (9 fixtures), OK. `-k RecusaComFifoNoPerfil`: 7 testes, OK. `test_forge_pareceres.py`: 35 testes, OK. Só os módulos tocados; a suíte inteira ficou com o CI.
- Vermelho: a nova fixture contra o `hooks/conformidade.py` de 841c14dc (cópia em `$TMPDIR`, resto no head): `Ran 1 test ... FAILED (failures=1)`, `AssertionError: 0 != 2` (o hook liberava). Com o hook do head, passa.
- Mutantes (`bin/forge-mutante --processos 2 tests/mutantes/v0481-g2-1-publicar-6.json`, `rev=dc6bc47efb98`): `M31 · morreu · hooks/conformidade.py:2604`, `M32 · morreu · :2607`, `M33 · morreu · :2607`, `M34 · morreu · :1390`, `M35 · morreu · :1392`, `M36 · morreu · :1391`, `M37 · morreu · :1388`. Sem sobrevivente. A linha de guarda nova do delta (o `if a == "--"`) tem o M37; as demais mudanças de código do delta vêm da develop (#886).
- A1 do parecer anterior: fechado, sem enfraquecer teste: o mínimo de fixtures subiu (8 para 9) e nenhuma fixture saiu nem virou `skip`.

## CI do head exato
`gh pr checks 878`, runs do `dc6bc47efb98f0f017510992325e629f64e29214` (`headSha` conferido nos dois): `suíte (python 3.12 e 3.14, partes 1 a 5)`, `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, `teto de pulados`, `instalação (python 3.14)` e `árvore já provada na develop` verdes.
Vermelhos por causa conhecida, fora das partes que contam:
- `catraca`: não é o `XDG_CACHE_HOME`; o log diz `R-CONFORMIDADE: mudança em bin/forge-check` e `hooks/conformidade.py`: espera o rótulo `afrouxa-regra` do dono no PR.
- `bateria (pareceres)`: `R-REVIEW`/`R-SEGURANCA` (último parecer não aprovado) e `R-QA` (o parecer anterior, 841c14dc, reprovado); espera os pareceres aprovados deste head. `bateria` falha só por consequência dele (`PARECERES: failure`, os outros quatro `success`).

- ci: dc6bc47efb98f0f017510992325e629f64e29214 verde

## Achados
Nenhum bloqueante. O A2 e o A3 do parecer anterior (cartões: pré-requisito do G2.2 e M9.2 sem o hook `autoria`) seguem como cartão, fora do delta, sem segurar o item.

## Parecer
Aprovado no head dc6bc47e: A1 fechado (fixture vermelha na base e verde no head, M37 morto), sem teste enfraquecido; CI verde nas partes que contam, com `catraca` e `bateria (pareceres)` à espera do rótulo e dos pareceres.
