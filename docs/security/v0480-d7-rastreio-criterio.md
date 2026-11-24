---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-d7-rastreio-criterio
commit: 64c4dd9ba9c4b3484431167e1b7a42adc7b80ec5
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0478 (E174.18, PR #868, D7)

Primeira rodada; sem parecer anterior na branch. Diff lido: `aabc476c...64c4dd9b` (bin/forge-check, bin/forge-testes, skills/produto-criterios/SKILL.md, tests/test_criterios.py, mutantes, pesos, changelog).

## Gatilhos
Gatilhos: controle do Forge que lê registro de pedido e brief (forge-check), integridade do selo do brief.

**Só aperta ou neutro:** só aperta. O subcomando `criterios` é novo, só leitura e sem rede; nenhuma guarda, hook, regra ou invariante existente foi afrouxada; a skill ganha uma exigência (id `C-n` e `cobre:`). A saída passa por `sem_controle` e `caminho_impresso`; o pedido passa por `caminho_do_pedido` (travessia barrada); o caminho do brief é preso a `docs/briefs/<nome>` pelo `BRIEF_SELADO`. O defeito abaixo é uma promessa nova não cumprida (o selo), não o afrouxamento de um controle existente.

## Achados
- A1 (bloqueante) bin/forge-check:8192 · provas_por_criterio lê o brief cru sem conferir o sha256 do selo; brief editado após o selo com `cobre: C-n` faz o critério sair entregue (rc 0). Use briefs_selados (confere o hash) e teste com selo errado saindo não entregue (o teste usa selo 'a'*64 e passa).

## Sondas
- S1 · python3 -I sonda_selo.py bin/forge-check (brief selado com o sha256 real, depois `cobre: C-1` vira `cobre: C-1, C-2`) · espera: rc 1, 1 entregues, 1 não entregues · obtido: rc 0, 2 entregues, 0 não entregues

## Detalhe dos achados
**A1.** Evidência: `bin/forge-check:8192` (`(raiz_pedido / m.group(1)).read_text(...)`), sem comparar com o grupo 2 do `BRIEF_SELADO` (o sha256); `tests/test_criterios.py:59` sela com `'a' * 64` e o teste espera `entregue`, ou seja, o teste fixa o comportamento sem selo. A skill (`skills/produto-criterios/SKILL.md:16`) e o changelog prometem "brief selado". Caminho: quem escreve `docs/briefs/` (o Jarvis, justamente quem a tabela pedido × entregue audita, ou uma edição tardia por engano) acrescenta `cobre: C-n` a um PQ depois do selo e da `entrega conferida`; a tabela mostra ao dono critério entregue sem prova selada, e rc 0. Severidade: média (controle anti-alucinação contornável pelo agente auditado; sem gate automático consumindo o rc hoje). Correção mínima: em `provas_por_criterio`, iterar `briefs_selados(raiz, caminho, pedido_txt)` (que já confere `hashlib.sha256(dados) == sha` e resolve em `docs/briefs/` por `dentro_da_raiz`) em vez de ler o arquivo cru; ajustar o `setUp` do teste para selar com o sha256 real e acrescentar o caso "brief alterado depois do selo não prova". Esforço: P. Dono: o autor da E174.2.

## Riscos aceitos e ferramentas
Nenhum risco aceito. CI do head 64c4dd9b: vermelho (bateria, bateria pareceres, bateria 3.14, suíte parte 1/5 em 3.12 e 3.14); não diagnosticado aqui (o log do job não abre neste sandbox). Rodados: `python3 -m unittest tests.test_criterios` (7 OK) e a sonda S1. Ferramentas externas de varredura não usadas (diff só de código da biblioteca padrão e texto).
