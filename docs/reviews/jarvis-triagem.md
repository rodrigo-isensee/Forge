---
tipo: review
contrato: 1
pedido: jarvis-triagem
branch: melhoria/jarvis-triagem
commit: ae15503
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Parecer de autor: triagem de cada pedido no Jarvis

- **Mudança:** seção "Triagem de cada pedido" antes de "Como conduzir um pedido" (faço eu x passo para `forge:<agente>`, aviso em uma linha, sem agente certo avisa e propõe caminho); "Comunicação com o usuário" exige citar o agente nas respostas que delegam.
- **Proteção:** dois invariantes novos em `agents/jarvis.md` no `tests/config.json`; só acrescenta, nada afrouxado.
- **Verificação:** 310 testes OK e `scripts/validar-plugin.sh` passa. Hooks intactos; CHANGELOG em `[Não publicado]`.
