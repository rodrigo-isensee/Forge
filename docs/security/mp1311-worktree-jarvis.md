---
tipo: revisao-seguranca
contrato: 1
pedido: melhorias-de-projeto-1311
branch: melhoria/mp1311-worktree-jarvis
commit: b94e026e78bc59ad93b242eac87feff073f98bfa
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-13
---
# Review de segurança: mp1311-worktree-jarvis

## Gatilhos
Toca texto de agente e de skill (regras do Jarvis e do brief); a `R-SEGURANCA` pede o portão pelo corte de redação em texto guardado. Sem código de produção, hook ou workflow.

## Achados
- A1 (bloqueante) skills/briefs-e-conferencia/SKILL.md:12 · o corte trocou "Leia a skill `checagem-do-brief` para o que a ferramenta não sabe" por "Skill `checagem-do-brief`: ..."; tests/test_modelos_projeto.py:113 (ChecagemDoBrief) falha no head e passa na base efe7c9e8.
- A2 (recomendado) agents/jarvis.md:40 · a linha "crie a worktree" não diz que o clone local é a saída; ela só está na skill. Aceitável pela divisão, mas o brief de delegação depende de o Jarvis ler a skill.

## Sondas

## Detalhe dos achados
A1: evidência acima. Caminho: o corte de redação enfraqueceu o imperativo que manda ler a skill de checagem do brief, regra guardada por teste; sem ele o Jarvis pode delegar sem checar estado do remoto, credencial e efeito fora da worktree. Severidade média. Correção mínima: restaurar a frase literal "Leia a skill `checagem-do-brief` para o que a ferramenta não sabe" e cortar outro trecho para caber no teto. Esforço P. Dono: tech-lead.

Conferência dos cortes: as invariantes de `tests/config.json` para `agents/jarvis.md` e `skills/briefs-e-conferencia/SKILL.md` seguem todas presentes (conferido por regex); o que sumiu em jarvis.md foi só "(padrão `node-react`)" (sem invariante, e remove nome de stack do núcleo, ADR 0001) e "gerado,"; na skill, o corte de "Nunca parta de ... molde copiado" mantém "Nunca parta de outro brief". Nenhuma regra com ID foi perdida. O clone local manda `origin` no GitHub e branch da `origin/develop`, sem `--force` nem token no texto.

## Riscos aceitos e ferramentas
Nenhum. Rodados: tests.test_jarvis_nucleo (20 OK), tests.test_modelos_projeto (1 falha, A1; base OK), e 13 módulos de teste que citam os dois arquivos (OK). Sem PR aberto: sem CI; a suíte inteira não foi rodada. gitleaks e demais não aplicáveis (só texto).
