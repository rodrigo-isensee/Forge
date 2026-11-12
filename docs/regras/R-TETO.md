---
id: R-TETO
titulo: Teto de recursos da máquina
verificada_por: hooks `agentes` e `pesado`; revisão
---
# R-TETO: Teto de recursos da máquina

Propósito: texto único desta regra; os outros arquivos citam o ID. Público: todo o time.

Revisar em: 2027-01-07
Medida: 121 linhas FLAKY e 7 falhas de envio por carga (estudo 0.43.1)

Teto de recursos da máquina (obrigatório), calculado na hora (decisão do dono de 2026-11-06).
- **teto de agentes adaptativo** (somando todos os pedidos): o único limite é a memória livre; dispara enquanto ela passa do piso (`piso_memoria_gb` em `.forge/config.json`, padrão 2 GB). Sem trava por load nem número fixo. O hook `agentes` aplica a conta (ADR 0003); o arquivo pode fixar ou limitar o teto.
- O teto nunca relaxa as regras abaixo; agente extra faz trabalho leve (discovery, docs, revisão).
- **tarefas pesadas uma de cada vez**, nunca em paralelo: testes E2E e de banco, build de produção, `docker compose up`, teste de carga. A suíte inteira roda uma por vez. A do merge roda no CI (`R-QA`); o envio local não roda teste. Exceção (dono, 2026-11-10): `suite-partes.py --duas-partes` junta as 2 partes só com load1 < nproc e memória sobre o piso. Reverter se passar de 21 FLAKY em 7 dias.
- Containers e servidores parados ao fim da etapa.
