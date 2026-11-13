---
tipo: revisao-seguranca
contrato: 1
pedido: melhorias-de-projeto-1311
branch: melhoria/mp1311-espera-longa
commit: b51d34bc0ae398f75f1a4fa571ab2abd3f459f80
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-13
---
# Review de segurança: mp1311-espera-longa

Head revisado: b51d34bc, revalidado por delta de af4bd16f (diff contra efe7c9e8: `skills/esperar-estado/SKILL.md`, teste e fragmento de changelog).

## Gatilhos
Nenhum gatilho direto da `R-SEGURANCA`: a entrega só muda texto de skill e um bloco de comando de leitura; não altera hook, guarda, permissão, segredo nem pipeline. Revisão feita a pedido, pelo risco de laço sem teto.

## Achados
- A1 (recomendado) skills/esperar-estado/SKILL.md:28 · laço sem teto fica preso se um check nunca sair de pendente (código 8); sem prazo máximo, o processo só acaba com o fim da sessão ou parada manual

## Sondas

## Detalhe dos achados
Conferências feitas (estáticas, mais o teste da skill):
- Fica preso para sempre? O laço sai em `fim=erro` (falha de `gh pr view`), em estado diferente de `OPEN` e em qualquer código de `gh pr checks` diferente de 8. Só persiste com PR aberto e check pendente, que é a própria espera pedida. Falha transitória de rede em `gh pr checks` dá código 1 e encerra, não gira. Roda só em segundo plano da sessão principal (regra 6); o subagente mantém o teto de 170 s (regra 4 e o bloco com `seq 1 5`). O segundo plano morre com a sessão, não sobra processo órfão.
- Escapa dos hooks? Rodei o bloco literal (com `run_in_background`) em `hooks/conformidade.py` e `hooks/parecer.py`: saída 0, sem recusa e sem contorno. O bloco só tem `gh pr view` e `gh pr checks` (leitura), `sleep` e `echo`; não há merge, push nem `gh api`. Nada ali esquiva um bloqueio: quem quiser mesclar continua passando pelos mesmos hooks.
- Custo e limite de API: duas chamadas a cada 30 s (cerca de 240 por hora), dentro do limite do `gh`, sem serviço pago (`R-CUSTO`).
- Teste: `python3 -m unittest tests.test_esperar_estado` com 13 testes, OK (inclui o laço longo que sai em `MERGED` após 13 leituras e a regra 6).

A1: recomendação, sem caminho de ataque. Correção mínima: acrescentar um teto largo (por exemplo `seq 1 480`, 4 horas) ou dizer na skill que se pára o segundo plano quando o CI passa do esperado. Esforço P. Dono: tech-lead (skill).

## Revalidação por delta (af4bd16f..b51d34bc)
O `forge-check parecer delta` mostrou só `skills/esperar-estado/SKILL.md` (texto enxugado). Conferido que nenhuma trava saiu: teto de 170 s e `fim=teto` com código 1; saída em `MERGED` e `CLOSED`; código 8 como único pendente e outro código encerra; `run_in_background` só na regra 6 (a regra 2 agora diz "salvo a regra 6"); "nunca encerre o turno com processo em segundo plano pendente"; trava `pesado` lida do arquivo, sem `kill -0`; os dois blocos de comando e o aviso sobre `$TMPDIR` e `$?` ao lado do envio, inalterados. Nenhum bloqueio novo; A1 segue recomendado, sem mudança. Teste `tests.test_esperar_estado`: 15 testes, OK.

## Riscos aceitos e ferramentas
Nenhum risco aceito. As ferramentas de segredo e de workflow não rodaram: a entrega não toca segredo nem workflow. Sem PR aberto para a branch (consulta ao `gh` devolveu lista vazia), então sem CI do PR; só o teste afetado.
