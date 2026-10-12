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

3. **Regras de validade:** QA `aprovado` exige `bugs_criticos: 0` e `bugs_altos: 0`; bugs médios ou baixos abertos exigem `aceite_usuario: sim` (portão de QA); o `commit` do parecer vale para o `HEAD` da branch se o diff entre os dois só tocar pareceres e quadro (`docs/reviews/`, `docs/qa/`, `KANBAN.md`, `docs/kanban/`). Qualquer outra mudança depois do parecer pede novo parecer.
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
