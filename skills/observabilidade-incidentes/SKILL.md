---
name: observabilidade-incidentes
description: Logs, métricas, alertas e roteiro de incidente do projeto. Mantida pelo devops-engineer; use ao desenhar ou revisar como o sistema avisa que está mal e como o time reage.
---

# Observabilidade e incidentes

Dono: o `devops-engineer`. Documente no projeto em `docs/devops/observabilidade.md`, sem dado pessoal nem segredo em log, métrica ou alerta.

## Logs
- Uma linha por evento, estruturada (campos nomeados), com nível, hora, identificador da requisição e resultado.
- Registre o que decide a investigação: entrada rejeitada, chamada externa que falhou, mudança de estado. Nunca senha, token, documento ou corpo inteiro de requisição.

## Métricas e alertas
- Comece por quatro sinais: taxa de erro, latência, tráfego e saturação (CPU, memória, disco, fila).
- Alerta só para o que pede ação humana agora; cada alerta tem o que significa, o impacto e o primeiro passo. Alerta ignorado duas vezes vira ajuste ou sai.
- Verificação de saúde simples (`/saude` ou equivalente) usada pelo ambiente e pelo deploy.

## Roteiro de incidente
1. **Detectar e declarar:** quem viu abre o registro com hora e sintoma.
2. **Conter:** reverter a última entrega (rollback, `ci-cd`) vem antes de achar a causa.
3. **Comunicar:** o Jarvis avisa a pessoa em linguagem simples: o que está afetado e quando volta.
4. **Corrigir e confirmar** pelo mesmo sinal que alertou.
5. **Registrar em até 2 dias** em `docs/retrospectivas/`: linha do tempo, causa, o que faltou para detectar antes e uma ação com responsável. Sem culpa de pessoa.

Segurança (vazamento, acesso indevido) entra também no `security-engineer`; custo novo de ferramenta de monitoramento passa pelo `R-CUSTO`.
