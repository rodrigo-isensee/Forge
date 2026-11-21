---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-merges
commit: 7bfe5cc8f5d288500c63894a8ff985576d958aa6
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: v0478 E62.22 (forge-check entrega: merges da develop e de pareceres aninhados, revalidação no head 7bfe5cc8)

Substitui o parecer reprovado do head 590d1954 (A1: redefinição de `vindos_da_base`). Delta lido por `forge-check parecer delta` (intervalo 590d1954..7bfe5cc8): bin/forge-check, changelog, specs de mutantes, test_forge_check_base_igual e test_selo_e_entrega.

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A1 anterior: não regredir o E7 (`vindos_da_base`) | tests/test_forge_check_base_igual.py | assinatura/nome | passou (14 OK; antes 4 falhas) |
| ENTREGA-MERGE-DA-DEVELOP (um só merge-base, 1.a linha de pais, arquivo presente, ls-remote por nome exato) | test_selo_e_entrega (162 testes) | merge cruzado, PR lateral, ausente nos dois lados, ref por cauda | passou |
| ENTREGA-MERGE-DE-PARECER-ANINHADO (conferido mais novo, mesmo no outro pai e no merge) | MergeDeParecerAninhado | rebaixamento, dois sem ordem | passou |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_forge_check_base_igual.py`: Ran 14 tests, OK (rc=0). Log e6222-baseigual.log.
- `python3 -I -m unittest discover -s tests -p test_selo_e_entrega.py`: Ran 162 tests, OK (rc=0). Log e6222-selo.log.
- Mutantes (uma chamada por spec, rev=7bfe5cc8f5d2, todos rc=0): v0479-entrega-merges.json D1 a D8 morreram; v0479-entrega-merges-2.json N1 a N8 morreram; v0479-entrega-merges-3.json D9 e R1 morreram. Também as specs editadas no delta: revisor-wt-e6a-3.json (15 mortos) e est-030-l1.json (8 mortos), rc=0. Logs e6222-mut1 a mut5.log.
- `forge-mutante --cobertura --base 8ee73d15` (rc=0): toda condição mudada (2516, 2525 a 2528, 2535, 2868 a 2880, 3290, 3291, 7390) tem mutante coberto; nenhuma sem mutante, nenhuma `só equivalente`; `spec editada` só em est-030-l1 e revisor-wt-e6a-3 (rodadas acima). Log e6222-cob.log.
- A1 anterior resolvido: o `vindos_da_base` do E7 está intacto; a nova função se chama `vindos_do_remoto_da_base`. Os achados A2 do review e A1 a A4 da segurança têm teste e mutante nomeados no delta (N4 a N8, D4, D8, D9, R1), todos mortos.
- Suíte completa: não rodei (CI do PR; ainda sem PR e sem check-run `bateria`).
- Vermelho antes do verde: não rodei `forge-testes --vermelho` neste head; a prova de que os testes novos dependem da guarda é cada mutante acima, que os faz cair.

## Parecer
Aprovado: o defeito A1 está corrigido e não há achado aberto no domínio do QA.
