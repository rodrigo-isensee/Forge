---
tipo: review
contrato: 1
pedido: k2-e-processo
branch: melhoria/processo-pronto-develop-instancias
commit: 61b438259a4719084fb2f745b8409e8d3a7d6875
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-15
---
# Code review: processo (definição de pronto, develop antes do review, instâncias por gargalo)

Escopo: E2 do pedido `k2-e-processo`, diff `bad3edd...61b4382` (5 commits): `agents/jarvis.md`, `agents/tech-lead.md`, `docs/regras/R-FLUXO.md`, `docs/regras/R-WIP.md`, `skills/engineering-practices/SKILL.md`, `tests/config.json`, `changelog.d/processo-pronto-develop-instancias.md`. Revisor independente; não escrevi a branch.

Conferido sem rodar a suíte completa (o autor a rodou; a segurança lê a mesma worktree em paralelo):
- `git diff --numstat bad3edd..HEAD -- tests/config.json` → `7	0`: só acréscimos, nenhum invariante existente afrouxado.
- Os 7 padrões novos casam com o texto da branch (script de regex sobre `invariantes` de `tests/config.json`, todas as entradas: nenhuma falha).
- `origin/develop` = `bad3edd` = base: a branch já está atualizada com a integração.
- Fragmento `changelog.d/processo-pronto-develop-instancias.md`: nome = branch sem prefixo, seção `### Alterado` (tipo válido de `bin/forge-changelog`), `CHANGELOG.md` intocado.
- Neutralidade (`R-NEUTRO`): nenhum nome de projeto, linguagem ou ferramenta de stack; os exemplos de documentação (README, guias, ADR, comentários de contrato) são genéricos.
- Commits: Conventional Commits em português, um por item, trailers presentes.

## O que está bom
- (a) Definição de pronto nos dois lugares pedidos: item 5 do prompt-padrão do Jarvis ("rodado da raiz do repositório", "documentação afetada pela mudança atualizada na mesma entrega") e seção nova `## Definição de pronto` na skill, sem nome de ferramenta.
- (c) `R-WIP` ganha "Gargalo ganha ajuda" subordinado a `R-TETO`, com quem sobe (Jarvis), quando dispensa (fila acabou) e o que fazer sem folga (a fila espera); "Trabalho em paralelo" do Jarvis repete em uma linha, citando `R-TETO`. Coerente com a decisão do dono ("respeitando o limite de hardware").
- Escolha de `R-FLUXO` para (b), e não `R-REVIEW`: concordo. O assunto é quando a branch recebe a integração (fluxo de branches); `R-REVIEW` trata do portão. O texto conversa com `R-QA` (revalidação incremental do que o conserto toca) e com o hook `parecer` da 0.15.0 (#141: parecer só se invalida por arquivo da própria entrega).

## Achados

### Bloqueia
1. `docs/regras/R-FLUXO.md:21` com `agents/tech-lead.md:25` · problema: a regra de (b) entrou só na seção `## No projeto` de `R-FLUXO`, mas o `tech-lead.md` a põe em "No repositório Forge" e cita `R-FLUXO` como fonte. Pelo texto único (ADR 0002), no Forge a regra não existe: a seção `## No Forge` não diz nada sobre atualizar a branch antes do review, e o pedido E2 é justamente sobre o processo da fábrica (a E3.4 deste mesmo pedido integra a `develop`). Ao contrário, nos projetos o `tech-lead` só chega à regra pelo ID, porque a linha dele está na seção do Forge. · sugestão: tirar a regra da seção do projeto e pô-la onde valha para os dois contextos (por exemplo, uma seção `## No Forge e no projeto` ou uma linha em `## No Forge` com "a `develop`" e a de `## No projeto` com "a branch de integração do projeto"); no `tech-lead.md`, levar a linha para fora de "No repositório Forge" (por exemplo, para a responsabilidade 4, "Decisões de commit", ou para "Regras que você guarda"), mantendo o trecho protegido `**uma vez, antes do review**`. Ajustar o invariante de `R-FLUXO` se o texto mudar (só acréscimo ou mesma frase). · severidade: bloqueia.

### Recomendado
2. `docs/regras/R-WIP.md:11` · problema: "dentro do limite de hardware e do teto de agentes de `R-TETO`" nomeia só o teto de agentes; `R-TETO` também limita a **2 worktrees** além do diretório principal e manda **tarefas pesadas uma por vez** (e agentes extras para trabalho leve). Instância nova de um gargalo pesado (ex.: QA rodando E2E) não pode rodar em paralelo, e cada instância exige worktree, que tem teto próprio. Lido isolado, o texto convida a ultrapassar os dois. · sugestão: "dentro de `R-TETO` (teto de agentes, limite de worktrees, tarefas pesadas uma por vez)". · severidade: recomendado.
3. `tests/config.json` (bloco `docs/regras/R-WIP.md` e `docs/regras/R-FLUXO.md`) · problema: os invariantes novos protegem só os títulos em negrito; a parte que é a regra de fato não está protegida: em `R-WIP`, o limite ("dentro do limite de hardware"/`R-TETO`); em `R-FLUXO`, "Depois do QA só se atualiza se houver conflito real". Apagar a cláusula de limite manteria a suíte verde. · sugestão: acrescentar esses dois trechos aos invariantes (só acréscimo). · severidade: recomendado.
4. `skills/engineering-practices/SKILL.md:30` · problema: "volta ao autor antes do review, sem gastar rodada" não diz qual rodada nem quem confere; pode ser lido contra `R-QA` ("No máximo 3 voltas por bug") e `docs/economia-de-tokens.md` regra 1 ("Uma rodada por entrega"). · sugestão: "sem contar como rodada de review (`docs/economia-de-tokens.md`, regra 1) nem como volta de `R-QA`; quem confere é o Jarvis (prova `PQ-n` do brief)". · severidade: recomendado.

### Informativo
5. `R-WIP` já limita Code review e QA a 2 cartões por coluna: instâncias extras de revisor ou de QA não passam disso. Coerente (puxar, não empurrar), só não está dito; não pede mudança.
6. Pareceres de segurança e de devops: a entrega não toca pipeline, contêiner nem IaC (sem parecer de devops). O parecer de segurança (`docs/security/processo-pronto-develop-instancias.md`, ainda não versionado na worktree) é do `security-engineer` e não foi refeito aqui.

## Veredito
**Reprovado** pelo achado 1 (coerência da regra com a fonte única). Correção de texto pequena, do autor. Os recomendados 2 a 4 entram na mesma volta. Depois da correção, a conferência se limita aos arquivos tocados por ela, sem refazer este review inteiro.
