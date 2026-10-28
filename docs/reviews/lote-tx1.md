---
tipo: review
contrato: 1
pedido: lote-tx1
branch: melhoria/lote-tx1
commit: 426bbd46d4f3e1a34c4fe6da2306f54510e7ee6c
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-27
---
# Review: lote-tx1

## Achados
- A1 (recomendado) docs/engineering/achados-recorrentes.md:12 · o arquivo diz que só o tech-lead e o security-engineer escrevem linhas AR-n; o novo texto de skills/qa-testing/SKILL.md:91 manda o qa-engineer escrever: alinhar a frase (e a linha 5) na próxima mudança
- A2 (recomendado) skills/engineering-practices/SKILL.md:51 · cita `head_do_pr` (nome de função do Forge) numa skill que vai a todos os projetos; trocar por exemplo genérico

## Parecer
Aprovado, revisado 363ceee..426bbd4 (6 textos, 7 commits, um por cartão mais o changelog).
- E1 item 12 do checklist: cumpre o cartão (nome exato, não prefixo); não contradiz as demais regras do checklist.
- E2 cyber-security passo 4 e jarvis (brief de volta, preenchimento dos PREENCHER): cumpre; compatível com R-SEGURANCA.
- E3 jarvis: logs e sondas em `$TMPDIR` com o pedido no nome (`push-<pedido>.log`): cumpre.
- E4 jarvis: retomada confere `git branch --show-current` ou traz `HEAD:refs/heads/<branch>`: cumpre, coerente com o push do R-FLUXO.
- E5 review e QA gravam AR-n no mesmo PR do parecer, no formato do arquivo; ver A1 (recomendado, não devolve).
- E6 README:22 "público" confere com `gh repo view` (PUBLIC); a linha 19 trata do repositório do projeto novo, outro assunto, correta.
- R-NEUTRO: nada de projeto específico; sem regra com ID afrouxada; fragmento `changelog.d/lote-tx1.md` presente; só texto, 10 linhas, abaixo do teto M14.
- Segurança: sem controle novo, sem gatilho; devops e segurança não se aplicam. Não rodei a suíte (só texto; o pre-push do autor registrou 742 OK).
