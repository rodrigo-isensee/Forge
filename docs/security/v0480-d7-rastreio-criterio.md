---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-d7-rastreio-criterio
commit: 3ed7a573dc9999ff05f8cc9c485603286c72fc59
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0478 (E174.32, PR #868, D7), revalidação

Volta por delta. Lido: `forge-check parecer delta` de `64c4dd9b..3ed7a573` (no domínio: `bin/forge-check` em `provas_por_criterio` e `cmd_criterios`, `skills/produto-criterios/SKILL.md`, `skills/produto-criterios/rastreio.md`; fora: `tests/test_criterios.py` e mutantes, lidos para a S1). Já lido na rodada 1: o resto do diff `aabc476c..64c4dd9b`.

Gatilhos: controle do Forge que lê registro de pedido e brief (forge-check), integridade do selo do brief.

**Só aperta ou neutro:** só aperta. O delta troca a leitura crua do brief por `briefs_selados` (confere o sha256) e move texto da skill para `rastreio.md`, sem retirar exigência; nenhuma guarda, hook, regra ou invariante foi afrouxada.

## Achados
- A1 (bloqueante) bin/forge-check:8188 · corrigido: provas_por_criterio só lê brief de briefs_selados (sha256 do selo confere); S1 de novo dá rc 1 e 0 entregues; teste com o sha real e o caso de brief alterado (tests.test_criterios, 8 OK).
- A2 (bloqueante) bin/forge-check:7987 · etapas_conferidas lê Cobre: e Branch: do brief cru, sem o sha256 do selo: editar o brief Y depois do selo para o Cobre: da etapa X torna X conferida e o PQ de X sai entregue sem entrega conferida dela. Quebra rastreio.md:15. explorável: S2

## Sondas
- S1 · python3 -I sonda_d7.py bin/forge-check (brief selado com o sha256 real, depois `cobre: C-1` vira `cobre: C-1, C-2`) · espera: rc 1, 0 entregues · obtido: rc 1, 0 entregues, 2 não entregues
- S2 · python3 -I sonda_d7.py bin/forge-check (selo de Y Cobre: E2.1, conferida do head, selo de X Cobre: E1.1 com cobre: C-1; Y editado para Cobre: E1.1) · espera: C-1 não entregue · obtido: C-1 entregue (p1-x.md PQ-1)

## Detalhe dos achados
**A2.** Evidência: `bin/forge-check:7987` lê `(raiz_pedido / m.group(1)).read_text(...)` e ignora `m.group(2)` (o sha256); `provas_por_criterio` (`bin/forge-check:8187`) usa esse conjunto como `conferidas`. Antes da edição de Y, a S2 dá C-1 não entregue. Caminho: o mesmo de A1 (quem escreve `docs/briefs/`, o Jarvis auditado pela tabela): o brief Y de uma etapa já conferida é editado depois do selo para levar o `Cobre:` (e, se preciso, a `Branch:`) de uma etapa nunca conferida; o brief selado e intacto dessa etapa passa a provar o critério. A rodada 1 devia ter pego (mesma família de A1: leitura do brief sem o selo); registro como falha minha de varredura. Severidade: média (como A1). Correção mínima: em `etapas_conferidas`, pular o brief cujo `hashlib.sha256(bytes).hexdigest()` difere de `m.group(2)` (só aperta também os outros consumidores, `bin/forge-check:8246` e `:9641`), ou calcular as conferidas de `provas_por_criterio` só dos `briefs_selados`; teste com o cenário da S2. Esforço: P. Dono: o autor da E174.2.

## Riscos aceitos e ferramentas
Nenhum risco aceito. CI do head 3ed7a573 no momento da leitura: `bateria (pareceres)` e `catraca` vermelhos, suíte pendente; não diagnosticado aqui. Rodados: `python3 -m unittest tests.test_criterios` (8 OK), S1 e S2. Sem ferramenta externa de varredura (diff só de Python da biblioteca padrão e texto).
