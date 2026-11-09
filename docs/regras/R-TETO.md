---
id: R-TETO
titulo: Teto de recursos da máquina
verificada_por: hooks `agentes` e `pesado`; revisão
---
# R-TETO: Teto de recursos da máquina

Propósito: texto único desta regra; os outros arquivos citam o ID. Público: todo o time.

Revisar em: 2027-01-07
Medida: 121 linhas FLAKY e 7 falhas de envio por carga (estudo 0.43.1)

Teto de recursos da máquina (obrigatório), calculado na hora pela máquina (decisão do dono de 2026-11-06).
- **teto de agentes adaptativo** (somando todos os pedidos): o único limite é a memória livre; dispara enquanto a memória disponível passa do piso (`piso_memoria_gb` em `.forge/config.json`, padrão 2 GB). Não há trava por load nem número fixo de agentes. O hook `agentes` aplica a conta (ADR 0003); `.forge/config.json` pode fixar ou limitar o teto.
- O teto nunca relaxa as regras abaixo; agentes extras vão para trabalho leve (discovery, documentação, revisão), não para tarefa pesada.
- **tarefas pesadas uma de cada vez**, nunca em paralelo: testes E2E, testes de banco, build de produção, `docker compose up` de pilha completa, carga para teste de performance. A suíte inteira segue serial, uma por vez na máquina; a do merge roda no CI (`R-QA`), e o envio local roda só os testes afetados.
- Containers e servidores parados ao fim da etapa.
