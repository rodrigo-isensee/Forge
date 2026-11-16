---
tipo: revisao-seguranca
contrato: 1
pedido: v047-develop-verde-594
branch: melhoria/v047-develop-verde-594
commit: 3932b52db16af1e0d21fdbc2a122a8ce01b77635
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: v047-develop-verde-594

Etapa E2.449 do pedido v047. Parecer completo (não havia parecer anterior) sobre o diff `58dfa2ab..3932b52d`: conserto da develop depois do #594 (PR 603), com o mapa do `bin/forge-testes`, dois módulos de teste e sete specs de mutantes.

## Gatilhos
Gatilhos: controle do Forge (bin/forge-testes decide o plano de testes do envio e do CI dirigido)

## Achados
- A1 (recomendado) tests/mutantes/z075-uma-delegacao-por-branch.json:1 · `forge-mutante --conferir --todas` segue com rc=1 por 31 trechos ambíguos (aparecem 2 ou mais vezes na fonte), todos já na base 58dfa2ab; fora do escopo deste item, sem caminho de ataque, mas a guarda AR-12 só vale verde. Dono: qa-engineer.

## Sondas

## Detalhe dos achados
**Mapa do `bin/forge-testes` (bin/forge-testes:318-320).** A spec nova ou alterada em `tests/mutantes/` passa a levar também ao `test_forge_mutante`. A mudança só acrescenta módulo ao plano dirigido e preserva a falha fechada: spec ilegível, sem `testes` ou com teste fora do padrão (`modulos_da_spec` devolve `None`, bin/forge-testes:360-369) segue na suíte completa, e não no `test_forge_mutante` sozinho. O mutante T8 (tests/mutantes/v047-specs-conferidas.json) prova esse ramo e morreu. Nenhum caminho de ataque: quem controla o diff já controla a spec, e o plano só cresce.

**Testes.** `tests/test_forge_mutante.py:1220-1234` troca o nome do atributo do ambiente para `self.env` (ponto único); o ambiente segue montado à mão por `sem_manutencao`, sem herdar o do CI (AR-4 conferido). `tests/test_testes_tocados.py:247-273` só ajusta o brinquedo e a expectativa ao mapa novo.

**Specs de mutantes (AR-12).** Os sete trechos que estavam fora do lugar na base (M34, M2, M3, M4, RP-M1, I96, I97) não aparecem mais no `--conferir --todas` do head. M2 (link do changelog.d) e M3 (pasta que é link no forge_dono) são guardas de segurança: foram realinhados com a mesma mutação, só com contexto a mais para ficarem únicos, sem afrouxar. I96 e I97 foram retirados porque a função `pesos_por_modulo` saiu de `scripts/suite-partes.py` no #576 (0 ocorrências no head); não há guarda órfã.

**A1.** Recomendação sem caminho de ataque: as 31 ambiguidades restantes já estavam na base e não pertencem a este item; ficam como cartão para o realinhamento seguinte.

## Riscos aceitos e ferramentas
Sem riscos aceitos. Rodado no clone, no head 3932b52d: `python3 -m unittest tests.test_testes_tocados tests.test_forge_mutante.ConferirTodas` (165 testes, OK, 1 pulado); `forge-mutante` das specs v047-specs-conferidas (T8 morreu), v0441-s2-fala (M3 morreu), lote-s1-scripts (M2 morreu; M8 sobrevive por desenho, equivalente declarado na própria spec, fora do diff) e lote-fc-seguranca-3 (todos morreram); `forge-mutante --conferir --todas` no head e na base, comparados. A suíte inteira é do CI do PR. Sem varredura de segredos nem de dependências: o diff não toca dependência, workflow nem credencial.
