---
tipo: review
contrato: 1
pedido: v046
branch: melhoria/forge-pesado-m12
commit: cdfafd25f1f6dcbeb7d22caabdb58b68f53f6773
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-11
---
# Review: v046 · E14.2 · forge-pesado (M12)

## Achados
- A1 (recomendado) bin/forge-pesado:12 · o docstring diz "sem escrever", mas `Hook.run()` cria `.forge/run/` e o `.gitignore` se faltarem; dizer "não grava estado do hook" ou aceitar a criação.
- A2 (recomendado) bin/forge-pesado:38 · o `except OSError: continue` de `esperando` (senha ilegível) não tem teste nem mutante; um teste com pasta de nome numérico em `pesado.fila/` cobre o ramo.
- A3 (recomendado) bin/forge-pesado:55 · com pid morto e fila vazia o hook libera (`ocupada` exige pid vivo), mas `esperar` espera até o teto; a divergência é escolha declarada (`esperar-estado`, regra 5), então registre no `--help` que a espera é conservadora.

## Sondas

## Parecer
Aprovado, sem bloqueante.

Lido: `bin/forge-pesado` (113 linhas), `tests/test_forge_pesado.py` (15 testes), 2 specs de mutantes (16), fragmento de changelog. Nenhum arquivo de `hooks/` mudou. O comando só lê `pesado.json` e a fila, importa `_comum.ler_json`, `Hook.run`, `pesado.pid_vivo` e `pesado.TRAVA_S` em vez de copiar a regra, e usa a mesma validade do hook (`min(expira_s, TRAVA_S)`). Saída escapada com `json.dumps` e comando cortado em 80 caracteres, com teste de caractere de controle. A fila ignora link simbólico, só testa `flock` compartilhado sem apagar a senha morta e não bloqueia (`LOCK_NB`). JSON ilegível, fora de projeto, teto fora da faixa (`nan`, `inf`, 0, 541) e passo inválido saem 2, cada um com teste de comportamento. O teto de 540 s é o da skill `esperar-estado`. Os testes rodam subprocesso com ambiente limpo e `python -I`; o pid "morto" usa valor acima do `pid_max`, sem depender do sistema.

Guardas: as 16 linhas de guarda do diff têm um mutante cada (`v046-forge-pesado.json` e `-2.json`, dentro do limite de 8 por spec); todos morreram. Os mutantes cobrem o ramo de falha por teste de comportamento, não por texto da fonte.

Tamanho: 269 linhas de código e teste (113 + 156), acima das 150; um comportamento só (ler o estado e esperar a vez), comando novo sem mudança em outro módulo, então o teto excedido se justifica. O PR (quando houver) traz `teto: excedido, 269 linhas, <motivo>`.

Itens do Entregar (E14.2): comando novo, só leitura do estado do hook, `_comum.Hook.run`, teste em módulo novo, sem mudar `hooks/`: todos com commit; sem `pendente:`. Sem lente de segurança própria aqui (`R-SEGURANCA` é do security-engineer); nada de segredo, injeção ou escrita fora do estado.

Revisor sem escrita na branch (Z10): o parecer fica em `/workspaces/.forge-contrib/docs/reviews/` e vai à branch por quem integrar.
