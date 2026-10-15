# 0004 - Contrato verificável entre agentes

Estado: vigente. Data: 2026-10-12.
Propósito: tornar checáveis por programa os documentos que os agentes passam uns aos outros. Público: quem mantém o Forge e os agentes. Revisão: 2026-10-12.

## Contexto
Reviews, pareceres de QA, planos técnicos e cartões são texto livre. O portão de QA e o hook de parecer (ADR 0003) precisam saber, sem ler prosa, se há um parecer aprovado para o commit certo. Hoje isso depende de interpretação do modelo, que varia.

## Decisão
1. **Frontmatter restrito** no topo de cada documento de contrato: só pares `chave: valor` numa linha, listas em `[a, b]`, sem aninhamento, o que permite um parser curto sem biblioteca de YAML. Todo frontmatter tem `tipo` e `contrato` (versão do formato, começa em `1`).
2. **Campos mínimos:**

| Documento | Onde | Campos obrigatórios |
|---|---|---|
| Review | `docs/reviews/<pedido>.md` | `tipo: review`, `pedido`, `branch`, `commit`, `parecer: aprovado\|reprovado`, `revisor`, `data` |
| QA | `docs/qa/<pedido>.md` | `tipo: qa`, `pedido`, `branch`, `commit`, `parecer: aprovado\|reprovado`, `escopo: completo\|incremental`, `bugs_criticos`, `bugs_altos`, `bugs_medios`, `bugs_baixos`, `data` |
| Plano técnico | `docs/architecture/features/<feature>.md` | `tipo: plano-tecnico`, `pedido`, `estado: proposta\|vigente`, `ux`, `adrs`, `agentes` |
| Cartões | `KANBAN.md` | Sem frontmatter: o contrato é a tabela (colunas fixas do modelo, `ID` único, `Responsável` = `forge:<agente>` ou `usuário`) e o WIP declarado no título de cada coluna |

3. **Regras de validade:** QA `aprovado` exige `bugs_criticos: 0` e `bugs_altos: 0`; bugs médios ou baixos abertos exigem `aceite_usuario: sim` (portão de QA); o `commit` do parecer vale para o `HEAD` da branch se o diff entre os dois só tocar pareceres e quadro (`docs/reviews/`, `docs/qa/`, `KANBAN.md`, `docs/kanban/`). Com a base informada (`forge-check pr --base`, usado pela catraca), vale também se o diff efetivo do `HEAD` sobre o merge-base com a base, fora desses caminhos, for o patch do `commit` aplicado sobre a base nova (emendado em 2026-10-15, ver abaixo): mesclar a base depois do parecer não o invalida. Qualquer outra mudança depois do parecer pede novo parecer.
   - **Emenda de 2026-10-15 (afrouxa a comparação; vem com o rótulo `afrouxa-regra`):** "idêntico" passa a ser "o `HEAD` é o patch do parecer aplicado sobre a base nova". `git merge-tree --write-tree --merge-base=<merge-base do parecer> <merge-base do HEAD> <commit do parecer>` simula o merge, e a árvore resultante é comparada, arquivo a arquivo e fora dos caminhos livres, com a do `HEAD`: igual vale; diferente pede novo parecer e a mensagem cita o arquivo (nome vindo de saída `-z`). Assim, o deslocamento de linhas e o contexto vindos da base não contam, mas qualquer linha da branch a mais, a menos, em outro lugar (inclusive a mesma linha mudada de posição ou a remoção de uma cópia repetida) ou vinda da resolução de um merge, conta. Arquivo em conflito no merge simulado não tem árvore a comparar, porque a resolução é manual: pede novo parecer (falha fechada, `R-SEGURANCA`), com uma única exceção, o `CHANGELOG.md` da raiz, onde vale a comparação `-U0`: as mesmas linhas adicionadas e removidas pela branch, na mesma ordem, sem número de `@@`, e qualquer dúvida (binário, arquivo ausente, erro do git) pede novo parecer. **Risco residual:** vale só para o `CHANGELOG.md`, que é texto e não executa: a posição da entrada da branch não é conferida (é o que permite pôr a entrada do changelog antes ou depois da da base). Em todo arquivo executável a posição é conferida (volta 3, decisão do time para fechar o risco da volta 2). Quebra de linha é só o `\n` do git (nada de `splitlines`, que também quebra em `\r`, `\x0c`, `\x1c`, `\u2028`). Motivo: em 2026-10-15 a comparação estrita invalidou pareceres de `melhoria/teste-abertura-feita` e `melhoria/ci-ubuntu-26` só porque o merge da `develop` deslocou linhas e mexeu no `CHANGELOG.md`, sem mudar nada da branch, e a mensagem apontava o primeiro arquivo alterado (vindo da base), não o que divergia. O objetivo do item não muda: qualquer mudança de conteúdo ou posição da branch pede novo parecer. Desenho escolhido sobre o `-U0` puro e sobre a âncora de contexto (review e segurança da volta 1, achados do `-U0` sem posição): o merge simulado é o próprio critério do git, não tem falso positivo por vizinhança e fecha a linha movida. Reversão: voltar à comparação estrita (`git diff` entre o commit e o `HEAD`, sem a base) em `arquivos_divergentes`.
4. **Validador `bin/forge-check`**, em Python só com biblioteca padrão, no PATH enquanto o plugin está ativo. Subcomandos `docs`, `kanban` e `pr <pedido>`. Sai com 0 quando o documento é válido; senão, sai com 1 e imprime uma linha por violação (`arquivo: campo: problema (R-ID)`). Usado pelos hooks, pelo comando "pronto" do projeto e, se o projeto quiser, pelo CI dele.
5. **Agentes e skills** mostram o frontmatter esperado no seu modelo de documento (`tech-lead` para review, `qa-engineer` para QA, `software-architect` para plano técnico), citando esta ADR.

## Alternativas consideradas
| Opção | Prós | Contras |
|---|---|---|
| YAML completo com biblioteca externa | Formato rico | Dependência a instalar em toda máquina; superfície de cadeia de suprimentos |
| Arquivos JSON separados (`*.parecer.json`) | Parsing trivial | Dois arquivos por parecer que se desencontram; pior para leitura humana |
| Cartões como arquivos com frontmatter | Contrato uniforme | Desmonta o `KANBAN.md` de leitura única que o usuário já usa |
| Interpretação pelo modelo (hoje) | Zero código | Não determinístico; o hook de parecer fica impossível |

## Consequências
- Mais fácil: o portão de QA vira verificável; o `agile-coach` tira métricas do frontmatter sem ler prosa.
- Mais difícil: documentos antigos dos projetos não têm frontmatter. A migração (ADR 0005) adiciona um frontmatter mínimo ou marca o documento como anterior ao contrato (`contrato: 0`, ignorado pelo validador).
- Mudar campo obrigatório é quebra de formato: sobe `contrato`, exige migração e versão major (ADR 0005).
- Risco: o agente preencher `parecer: aprovado` sem ter testado. O frontmatter não prova o conteúdo; o review do `tech-lead` e a validação do usuário continuam sendo o controle.
