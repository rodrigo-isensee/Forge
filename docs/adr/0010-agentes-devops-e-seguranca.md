# 0010 - Agentes `devops-engineer` e `security-engineer`

Estado: proposta. Data: 2026-10-14.
Propósito: registrar a decisão de dar ao time um dono para "como entrega e roda" e outro para a postura de segurança. Público: quem mantém o Forge. Revisão: 2026-10-14.

## Contexto
Pipeline, contêiner e infraestrutura não tinham dono: o `tech-lead` revisava o código e o `software-architect` acumulava a segurança como apêndice do desenho, de modo que o review de segurança concorria com a arquitetura e só acontecia quando alguém lembrava. Pedido do dono (2026-10-13), com propostas de discovery em `~/.forge-contrib/propostas/` e decisões do dono: devops P1 = (a), P2 = (b), P3 = (b); segurança P1 = A, P2 = A, P3 = A.

## Decisão
1. **`forge:devops-engineer`** (`sonnet`; `Read, Grep, Glob, Bash, Write, Edit`; skills `ci-cd` e `cyber-security`): dono de workflows, contêineres, IaC, ambientes, mecânica de release e rollback, e do tempo e do custo do CI. Dá o parecer em `docs/devops/<pedido>.md` (`tipo: revisao-devops`) sobre toda mudança em `.github/`, `Dockerfile*`, `compose*` e IaC, em rodada única com o code review (`R-REVIEW`). O hook `parecer` e o `forge-check pr` o exigem pelo diff.
2. **`forge:security-engineer`** (`opus`; `Read, Grep, Glob, Bash, Write`; skill `cyber-security`): dono da postura, do modelo de ameaças e do review de segurança, defensivo e estático, só com ferramentas gratuitas já instaladas (não instala nada). Parecer em `docs/security/<pedido>.md` (`tipo: revisao-seguranca`, `parecer: aprovado|reprovado|riscos-aceitos`).
3. **Regra nova `R-SEGURANCA`** (ADR 0002): o parecer de segurança é **portão quando há gatilho**. A lista de gatilhos está na regra; o diff revela os casos óbvios e os demais o plano técnico marca em `gatilhos_seguranca`. `riscos-aceitos` só vale com o arquivo de aceite do usuário em `docs/security/aceites/<pedido>.md`, que nenhum agente grava (hook `conformidade`).
4. **Hook `conformidade`**: papel `devops` (escreve em `.github/` no Forge, em `melhoria/*`, sem merge nem PR) e papel `seguranca` (sem merge, PR nem instalação de pacote); `docs/devops/` e `docs/security/` só dos seus papéis; a autoria dos dois pareceres é registrada e conferida (ADR 0009, 6.4).
5. **Fronteiras:** o `software-architect` decide topologia, provedor e ferramenta de IaC e perde a seção "Segurança" (aciona o `security-engineer`); o `tech-lead` mantém quais checks são exigidos para mesclar, o nível SemVer, o `CHANGELOG` e a release; o `qa-engineer` não declara "seguro". Divergência vira ADR com as duas posições.
6. **Neutralidade (ADR 0001):** núcleo neutro; a skill `ci-cd` traz princípios e GitHub Actions como padrão da fábrica; o que depende de linguagem vai para `stacks/<stack>/` (`pronto.md`, seção "CI"; `seguranca.md`, seção "SAST da stack").
7. **Restrições:** `R-CUSTO` (sem runner pago, sem recurso pago, sem instalar ferramenta); o token do bot não tem o escopo `workflow`, então o devops prepara a mudança e o dono a envia; proteção de branch, rulesets e `environments` continuam do dono (`R-CONFORMIDADE`). Proteger por hook os arquivos de infra **nos projetos** e o devops assumir a mecânica de release do Forge ficaram para depois (P2 = (b), P3 = (b)).

Verificado por hook: quem escreve cada parecer e cada pasta, merge, PR e instalação por papel, a exigência dos pareceres pelo diff. Só orientação: gatilhos que o diff não mostra (se o plano não os marca), a qualidade do parecer, o limiar das varreduras, o uso de ferramenta.

## Alternativas
- **Manter a segurança no arquiteto e o pipeline no `tech-lead`:** nenhum custo novo, mas o review de segurança continua opcional e o pipeline sem dono; rejeitada pelo dono.
- **Um agente só para as duas áreas:** menos agentes, porém mistura "como entrega" (mecânico, `sonnet`) com review de segurança (principal, `opus`) e quebra a separação de deveres: quem escreve o pipeline não deve ser o único a revisá-lo.
- **Parecer de segurança consultivo (B) ou portão em todo pedido (C):** o consultivo não impede nada; o portão universal custa `opus` e tempo em pedido sem risco. Escolhido: portão só com gatilho.
- **Parecer de devops como seção do parecer do `tech-lead` (b) ou só orientação (c):** não deixa rastro verificável por hook; escolhido o parecer próprio (a).
- **Agente de segurança instala e roda varreduras (C):** custo e superfície de ataque; escolhido rodar no CI do projeto e, local, só com a ferramenta já presente.

## Consequências
- Mais dois agentes e uma regra; toda entrega que toca gatilho passa por mais um parecer, em paralelo ao code review.
- A mudança em `.github/` do próprio Forge ganha um revisor especializado, mas continua exigindo o rótulo `afrouxa-regra` do dono.
- O diff é uma aproximação: gatilho semântico (autenticação, LGPD, webhook) depende de o arquiteto marcá-lo em `gatilhos_seguranca`.
- `docs/security/` deixa de ser gravável pelo arquiteto; documentos livres lá (postura, ameaças) não precisam de frontmatter.

## Critério de reversão
Reavaliar na terceira release depois do merge: se mais de 30% dos pareceres de segurança saírem "aprovado" sem achado, ou se os pareceres exigidos por gatilho atrasarem a entrega em mais de uma rodada de review, estreitar a lista de gatilhos (voltar a consultivo nos que não geraram achado). Se o devops e o `tech-lead` divergirem em mais de dois PRs por release, voltar o parecer de devops para seção do parecer do `tech-lead` (alternativa b).
