---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-retros
commit: 9b2109ef447889d8338bf962cf6faa20bf76e6bf
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 · retrospectivas atrasadas (0.47.12 a 0.47.14 e três pedidos), etapa E116.4

Diff `8773be38..9b2109ef`: seis retros em `docs/retrospectivas/` e o fragmento `changelog.d/v0480-retros.md`; só documentação, sem código, sem guarda nem mutante.

## Ferramentas (citadas, não refeitas)
- `forge-check docs` (0.47.15 instalado) no head: sai 0.
- `forge-check retro --pendentes --agora 2026-11-23T15:00:00-03:00`: v0.47.12, v0.47.13 e v0.47.14 saíram da lista; nenhum `aviso:` (as duas retros de pedido sem tag própria usam `Tags:` e não reivindicam versão).
- Neutralidade (`R-NEUTRO`): `python3 -m unittest -k Neutralidade tests.test_forge`, 6 testes OK.

## Leitura
- Modelo: as seis seguem as cinco seções do `_modelo.md`, com marca `medido`/`estimado`/`não medido` e a fonte em cada linha de dado.
- `R-DECISAO`: nenhuma regra nova em texto; a causa recorrente vai a cartão (JARVIS-CONFERE-ESTADO-ANTES) e a proposta do PR-VERDE fica com métrica e critério de reversão para o tech-lead. Os cartões citados existem no `KANBAN.md`.
- Conferidos contra a fonte: etapas do 1311 (99, `grep -cE`), `Melhoria vista:` por janela (1, 2, 0), datas das tags v0.47.11 a v0.47.14.
- A contagem de ERRO-JARVIS, marcada `medido`, não bate com a fonte (A1).

## Achados
- A1 (bloqueante) docs/retrospectivas/2026-11-23-0.47.13.md:17 · ERRO-JARVIS contado só na forma `ERRO-JARVIS:` e perde `ERRO-JARVIS 20:4x:`: são 8/5/12 entradas, não 5/1/9 (S1); o "Um ERRO-JARVIS" (0.47.13:32), os 15 (anti-erro:17) e o "5 de 15" (0.47.14:37) mudam junto.

## Sondas
- S1 · entradas ERRO-JARVIS nas linhas datadas de `docs/pedidos/v0478.md` por janela de tag, fora citações ("no brief)") · espera: 5, 1, 9 · obtido: 8 (1694..1946), 5 (2006, 2083, 2397, 2548, 2635), 12 (3042..3468)
