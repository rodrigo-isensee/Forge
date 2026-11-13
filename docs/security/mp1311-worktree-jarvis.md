---
tipo: revisao-seguranca
contrato: 1
pedido: melhorias-de-projeto-1311
branch: melhoria/mp1311-worktree-jarvis
commit: c61435e6efaa446b3c73bb4504ea6e1cf60ca06c
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-13
---
# Review de segurança: mp1311-worktree-jarvis (por delta até c61435e6)

## Gatilhos
Toca texto de agente e de skill (regras do Jarvis e do brief); a `R-SEGURANCA` pede o portão pelo corte de redação em texto guardado. Sem código de produção, hook ou workflow.

## Achados
- A1 (recomendado) agents/jarvis.md:40 · a linha "crie a worktree" não diz que o clone local é a saída; ela só está na skill. Aceitável pela divisão (herdado do parecer anterior, não bloqueia).

## Sondas

## Detalhe dos achados
O A1 bloqueante do parecer anterior (b94e026e), skills/briefs-e-conferencia/SKILL.md:12, está resolvido: o delta b94e026e..c61435e6 em código/texto toca só essa skill e restaura a frase literal "Leia a skill `checagem-do-brief` para o que a ferramenta não sabe (estado do remoto, credencial, efeito fora da worktree)". O resto do delta são pareceres de review e QA. O clone local segue com `origin` no GitHub e branch da `origin/develop`, sem `--force` nem token no texto.

## Riscos aceitos e ferramentas
Nenhum. Rodados no head: tests.test_modelos_projeto e tests.test_jarvis_nucleo (37 OK), mais test_pesos_teto, test_skills_v0442 e test_invariante_gatilho. Sem PR aberto: sem CI; a suíte inteira não foi rodada. gitleaks e demais não aplicáveis (só texto).
