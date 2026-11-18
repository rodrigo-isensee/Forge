---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v0475-ci-sem-reenvio
commit: 6cbb20bc801d3b0014ce62f97cdc8b20221edfd4
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v0474 E3.43 (CI sem reenvio, `R-CUSTO`), etapa E3.107

Escopo: diff `2fa505d7..6cbb20bc`, só texto (tech-lead, devops-engineer, qa-engineer, 3 agentes de stack, skills `trabalho-em-paralelo` e `briefs-e-conferencia`, fragmento de changelog) e `tests/test_textos_ci_custo.py`. Pergunta do brief: o corte de frases para caber nos tetos removeu alguma regra de segurança dos agentes?

## Gatilhos
Gatilhos: nenhum (texto de processo; não toca hook, `.githooks/`, workflow, segredo nem controle).

## Achados
- A1 (recomendado) agents/devops-engineer.md:16 · O corte tirou "Configura e tria o Dependabot; o dev da stack corrige o código que o bump quebrar": o item 5 segue com o título "Tempo e dependências" sem dono da triagem no agente; a prática sobrevive na skill ci-cd:57-61, que o devops carrega. Repor a frase.

## Sondas

## Detalhe dos achados
**A1.** Evidência: `git show 2fa505d7:agents/devops-engineer.md` linha 16 tinha a frase; no head 6cbb20bc a linha 16 só traz a medição do CI e a linha **CI pago**. Caminho de ataque: nenhum direto; o risco é de cadeia de suprimentos por omissão (alerta de dependência vulnerável sem dono explícito fica sem triagem). Mitigado porque o `devops-engineer` carrega `skills: ci-cd, cyber-security` e a `ci-cd` (linhas 57-61) mantém a triagem, a separação mecânico × correção do dev da stack e as proibições (sem auto-merge, sem `registries` com credencial em claro, sem `insecure-external-code-execution`). Severidade: baixa. Correção mínima: repor no item 5 do `devops-engineer` "Configura e tria o Dependabot; o dev da stack corrige o código que o bump quebrar" (ou cortar outra frase de apoio, se o teto apertar). Esforço: P. Dono: tech-lead (autor da branch).

**O que conferi e ficou de pé:**
- IDs de regra citados nos 3 agentes de base, antes e depois: devops `R-REVIEW`, `R-SEGURANCA` (mantidos, mais `R-CUSTO`); qa `R-REVIEW`, `R-SEGURANCA` (mantidos); tech-lead `R-FLUXO`, `R-REVIEW` (mantidos, mais `R-CUSTO`); a seção "Regras que você guarda" do tech-lead não mudou.
- Linhas de segurança intactas: parecer de devops com `R-SEGURANCA` quando há gatilho e "mesmo de outro agente" (devops:17); casos de abuso do modelo de ameaças e o oráculo do QA sem gatilho (qa:13); `R-SEGURANCA` do parecer do security-engineer citado pelo tech-lead (tech-lead:49). As referências cortadas (seção "Plano antecipado", seção "Teste-oráculo do portão", `@expectedFailure`, `--dry-run`, exemplos do conferente) existem nas skills que os agentes carregam (`skills/qa-testing/SKILL.md:43,50-54`) ou não são controle de segurança.
- Invariantes de `tests/config.json`: as 531 expressões casam em base e head (busca por regex em `git show <ref>:<arquivo>`), nenhuma sumiu; "Lote por arquivo" mudou para `ritmo-e-corte.md` e o rótulo segue na skill.
- A regra nova não afrouxa portão: rerun só com falha de infraestrutura no log e teste vermelho volta ao autor, coerente com `skills/ci-cd/SKILL.md:45` (reexecutar o mesmo sha por causa externa, nunca marcar aprovado).

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Suíte inteira: só no CI do PR (check-run `bateria` do mesmo sha); a branch ainda não tem PR nem run, então este parecer vale condicionado a esse CI verde no merge (`R-FLUXO`). Rodado aqui: `tests.test_textos_ci_custo` (5 OK), `tests.test_orcamento_instrucao` e `tests.test_metricas_texto` (10 OK). Sem varredura de segredo: diff só de texto, sem credencial; `gitleaks` não usado.
