---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-receita-alcance
commit: f56597cbefd9f17b22078b21773cacbbdddc735c
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0480-receita-alcance (PR #835, E146.4)

Escopo: diff `9d239dda..f56597cb` (6 arquivos, texto dos agentes de portão e da receita `skills/briefs-e-conferencia/envio-de-parecer.md`). Pergunta do brief: alguma restrição de pasta, de papel ou de envio saiu dos agentes de portão sem ir para a receita?

## Gatilhos
Gatilhos: texto de agente de portão sobre escrita e envio de parecer (controle do Forge, só texto; nenhum hook, guarda ou workflow tocado).

## Achados

## Sondas

## Detalhe dos achados
Conferência frase a frase do que saiu de cada agente e para onde foi (só aperta ou neutro):

- `agents/security-engineer.md:16`: neutro. Restrições de pasta (`docs/security/`, nunca `docs/security/aceites/`, nunca código) ficam no agente; só o ponteiro passa a caminho `${CLAUDE_PLUGIN_ROOT}` e o "atrás do remoto" volta explícito.
- `agents/tech-lead.md:18`: neutro. Saiu "Validade presa ao domínio: `R-REVIEW`"; segue em `docs/regras/R-REVIEW.md:17` e na receita (`envio-de-parecer.md:3`). Modelo e `forge-check docs` continuam no agente (linha 17).
- `agents/qa-engineer.md:18-20`: neutro. Saíram "`forge-check docs` valida" e "(até 300 caracteres)"; foram para `envio-de-parecer.md:7` (modelo, `forge-check docs`, achado até 300). O limite continua no `_modelo.md` e no `forge-check docs`, que barram.
- `agents/devops-engineer.md:17-18`: aperta. Saíram "Modelo em `docs/devops/_modelo.md`; `forge-check docs` valida", "com `git add <caminho>` explícito" e "Validade presa ao domínio"; os três estão na receita (`envio-de-parecer.md:5,7,9` e `:3`), e o devops passa a receber o "um passo por chamada" e o `git pull --rebase origin <branch>`, que antes não tinha.
- Receita (`envio-de-parecer.md:5-11`): a pasta de cada portão vira lista explícita e o `git add` explícito vale para as quatro; continuam a proibição de `git add .`/`-A`, de heredoc e de encadear ação crítica; nada afrouxa `R-VERIFY` (sem `--force`, sem `--no-verify`) nem `R-MAIN`.

Nenhuma restrição de pasta, de papel ou de envio se perdeu.

Fora do meu domínio (ao `tech-lead`, não bloqueia este parecer): o check `bateria (passos)` do head f56597cb falha em `changelog.d/v0480-receita-alcance.md:1`, tipo `Mudado` inválido (o `bin/forge-changelog:26` aceita `Adicionado`, `Alterado`, `Corrigido`); a suíte não chegou a rodar no CI. A correção toca só o fragmento, fora de `docs/security/` e dos agentes, e não invalida este parecer (`R-REVIEW`); o merge segue preso ao CI verde.

Testes dos arquivos tocados, locais no head: `python3 -m unittest tests.test_citacao tests.test_volta_por_delta tests.test_brief_tamanho` com 127 testes OK.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: leitura do diff, `grep`, testes estruturais citados; varredura de segredo não se aplica (diff só de texto, sem credencial).
