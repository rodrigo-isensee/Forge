---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-bp14-retro
commit: 1df3df9ae7715dcf602b6cf7bff8159ecdbc0bf0
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-23
---
# Review de segurança: v0478 (E145.8, revalidação por delta do PR #833, BP14 retro)

Revalidação por delta. A rodada anterior (E145.4, commit `dbc33e5a`, reprovado com A1 e A2) fica no git. Delta lido por `forge-check parecer delta`: `dbc33e5a..1df3df9a`, um commit (E145.5), 3 arquivos: `docs/retrospectivas/_modelo.md`, `templates/projeto/docs/retrospectivas/_modelo.md`, `skills/kanban-metricas/SKILL.md`. Também relido `bin/forge-check:6069-6090` (o portão da retro, controle do Forge que o modelo alimenta); ele não mudou no delta.

Gatilhos: modelo de projeto copiado pelo `bin/forge-init` (`templates/projeto/`), portão `forge-check retro --pendentes` que lê as seções desse modelo.

## Só aperta ou neutro, por escrito
- `templates/projeto/docs/retrospectivas/_modelo.md:9`: **neutro**. A tabela pedido × não entregue saiu do corpo e virou texto dentro do comentário de uma linha da seção 1; o portão ignora a linha que começa por `<!--`, então a seção 1 copiada sem preencher volta a não ter corpo (S1). Era o afrouxamento de A1; agora o modelo fica como na base quanto ao portão.
- `docs/retrospectivas/_modelo.md:9`: **neutro**. Mesma linha; os dois modelos são idênticos byte a byte (`diff` sem saída; S2).
- `skills/kanban-metricas/SKILL.md:7-8,32`: **neutro**. Sai a frase de procedência ("Trechos movidos inteiros...") e o item 1 da retro fica mais curto; não toca regra com ID, invariante (`tests/config.json` não cita a frase), permissão nem portão. `tests.test_jarvis_nucleo`, `tests.test_reval_delta` e os testes de `kanban`/`teto`/`skill` de `tests.test_forge` passam no head.

## Achados anteriores
- A1 (bloqueante, E145.4): **corrigido** em `templates/projeto/docs/retrospectivas/_modelo.md:9`; prova S1.
- A2 (bloqueante, E145.4): **corrigido** em `docs/retrospectivas/_modelo.md:9`; prova S2.

## Sondas
- S1 · modelo de templates/projeto com Cobre: v0.1.0, v0.2.0, seções 2 a 5 com texto e a 1 como no modelo, em forge-check retro --pendentes · espera: secao sem corpo: dados do pedido; nao cobre · obtido: código 1, pendentes=2, esse aviso
- S2 · python3 -m unittest tests.test_retro_pendentes tests.test_medidas_m14b no head 1df3df9a · espera: OK · obtido: Ran 93 tests, OK

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum.
Ferramentas: `forge-check parecer delta`, leitura do diff e de `bin/forge-check:6069-6090`; S1 como subclasse de `RetroPendentes` no rascunho da sessão, fora do repositório; testes dos arquivos tocados (S2 e os citados acima). A suíte inteira não rodou (o brief pede sem suíte local); vale o CI do PR #833.
