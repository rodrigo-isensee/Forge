---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-f4-vigia-fluxo
commit: 8d755e503e51f53e37af2befea60ba7622b26dc8
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-27
---
# Review: v0481 (E34.2, F4 do estudo de atrito, PR #931)

1ª rodada completa no `8d755e50` (base da comparação: `2bdf1a2e`, a develop mesclada no head). Diff: `hooks/vigia.py` (+118/-10, 99 linhas de código contando docstrings: dentro do H1), testes em `tests/test_hook_vigia_f4.py`, uma fixture de silêncio, 30 mutantes novos em 4 specs, M3 e M8 da spec `v0480-vigia-time-parado` realinhados e o fragmento do changelog.

## Achados
- A1 (bloqueante) hooks/vigia.py:662 · ADR 0003 item 7 (e item 2) exige o aviso de time parado sem rede e determinístico; o F4 chama `gh pr list` no Stop do Jarvis (1,4 a 1,8 s medidos, prazo 5 s; meta de 300 ms em docs/hooks.md:77). Mudar o item 7 pede emenda da ADR e o rótulo afrouxa-regra (ADR 0003:92); o PR diz nenhuma
- A2 (bloqueante) hooks/vigia.py:731 · o reason sai do texto fixo do item 7 da ADR 0003 (regex de tests/test_hooks.py:872) e não tem teto: 79 caracteres com 1 PR e 1353 com 50 (S1), contra os ~200 do item 7. Sugestão: formato novo na emenda do A1, regex do test_hooks.py e um teto de itens no texto
- A3 (bloqueante) hooks/vigia.py:717 · a catraca do 8d755e50 reprova por R-QA: a guarda apagada `agentes_rodando(hook, raiz) != 0` (hooks/vigia.py:618 da base) fica sem mutante que a cubra (`forge-mutante --cobertura --base 2bdf1a2e` sai 1, `apagada`); declare-a ou isente-a com motivo na spec do pedido
- A4 (bloqueante) docs/hooks.md:86 · a seção do time parado e o item 7 da ADR 0003 seguem com zero agentes vigentes e só cartões; o F4 conta PR e agente preso com agente rodando, e a documentação afetada não veio na entrega (definição de pronto)
- A5 (recomendado) hooks/vigia.py:638 · o check de status de commit (StatusContext) traz o nome em `context`, não em `name`: reprovado ou pendente, entra como None e manda o PR ao autor; hoje o CI só usa check-runs, mas o F1 leva o parecer ao status do commit
- A6 (recomendado) hooks/vigia.py:665 · `subprocess.TimeoutExpired` do gh cai no `calado` e vai ao erros.log a cada Stop, o que o comentário da linha 668 quer evitar para o rc diferente de 0; trate o prazo vencido como o rc 1

## Sondas
- S1 · python3 sonda_f4.py <cópia> (aviso_time_parado com 1 e 50 PRs à espera de parecer, gh e teto falsos, regex de tests/test_hooks.py:872) · espera: reason no formato do item 7 da ADR 0003, até ~200 caracteres · obtido: contrato=False com 79 caracteres (1 PR) e 1353 caracteres (50 PRs)
- S2 · bin/forge-mutante --cobertura --base 2bdf1a2e93848891987b1536ae6039c6269b576f · espera: rc 0, toda guarda mudada coberta · obtido: rc 1, `apagada · hooks/vigia.py:618(base) · agentes_rodando(hook, raiz) != 0`

## Verificações
- CI do PR no `8d755e503e51f53e37af2befea60ba7622b26dc8` (`gh pr checks 931`): suíte 1/5 a 5/5, verificações longas, passos, python 3.14, instalação, teto de pulados e árvore já provada verdes; `catraca` vermelha por defeito (A3); `bateria` e `bateria (pareceres)` esperam os pareceres. Não aprova sem a catraca verde.
- Testes afetados, à mão: `python3 -m unittest tests.test_hook_vigia_f4 tests.test_vigia_parado`, 50 testes OK.
- Mutantes: `bin/forge-mutante` nas 4 specs `v0481-f4-vigia-fluxo*.json` (M1 a M30) e na `v0480-vigia-time-parado.json`, todos mortos, rc 0.
- Lógica de `papel_do_pr`: ordem dos ramos correta (main, conflito, check fora dos portões, pendente, parecer ausente, afrouxa-regra sem rótulo, catraca ou bateria), conferida contra os checks reais do #931 (os três portões reprovados, nenhum pendente, cai em `review/QA/segurança`). `prs_parados` respeita o teto do R-TETO e a branch ocupada; `instancias_presas` lê só o transcript do agente pelo id validado; cada parte cala sozinha.

## Parecer
Reprovado. A lógica nova está correta e testada, com um mutante por guarda, mas o F4 muda o contrato do item 7 da ADR 0003 (rede no hook, texto do reason fora do formato fixo e sem teto) sem emenda nem rótulo (A1, A2), deixa a guarda apagada sem cobertura na catraca (A3) e não atualiza docs/hooks.md nem a ADR (A4). A1 e A2 tocam uma decisão de arquitetura: a emenda da ADR 0003 é do `software-architect` com o tech-lead, e o rótulo `afrouxa-regra` é do dono; o autor ajusta o código ao texto que a emenda fixar. A5 e A6 viram cartão depois do merge.
