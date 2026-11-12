---
tipo: revisao-seguranca
contrato: 1
pedido: v046
branch: melhoria/v046-textos-jarvis
commit: be5bb7ee32898578994ab389c8b257cf54ba7034
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-12
---
# Review de segurança: v046 (textos do Jarvis, E21.3)

Diff revisado: `origin/develop...be5bb7ee` (base a1318e88), 4 arquivos, 18 linhas a mais e 16 a menos, só texto: `agents/jarvis.md`, `docs/regras/README.md` (parágrafo `R-WIP`), `skills/trabalho-em-paralelo/SKILL.md` e o fragmento `changelog.d/v046-textos-jarvis.md`. Classe C.

## Gatilhos
Texto de regra e do Jarvis que governa travas da fábrica (`R-WIP`, `R-TETO`, `R-DECISAO`, `R-MAIN`, `R-CONFORMIDADE`). Nenhum código, hook, workflow ou ferramenta mudou; as travas que barram de fato (hooks, `forge-check`, CI) ficam como estão.

Conferência das travas no texto novo:
- `R-TETO` e piso de memória: `docs/regras/README.md:29` mantém "respeitando o `R-TETO` inteiro" (teto de agentes, worktree por instância com disco livre, pesado um por vez, extras só em trabalho leve, fila espera sem folga); a skill (`skills/trabalho-em-paralelo/SKILL.md:9`) mantém "enquanto couber no teto" e `agents/jarvis.md:49` "dentro de `R-TETO`". A espera por "memória" (SKILL.md:19) obedece ao piso, não o contorna. `tests.test_orcamento_instrucao`: 8 testes, OK (jarvis.md 7958 bytes).
- Uma escrita por branch e série por arquivo: o texto novo exige "branch própria e nenhum arquivo em comum com outro em voo" e "um por vez" no arquivo comum, no merge na `develop`, no `KANBAN.md`, no pipeline e no mesmo módulo, ADR, modelo de ameaças ou tela (README.md:29); aperta, não afrouxa. `R-REVIEW` (autor não revisa o próprio cartão) segue no mesmo parágrafo.
- "Portão usa o CI do PR em vez da suíte local quando ele cobre": coincide com o que os papéis de portão já dizem (a suíte inteira roda só no CI do PR) e com a bateria obrigatória do CI para o merge; não remove nenhuma prova exigida por ferramenta.
- `R-DECISAO` e "andar sozinho": `agents/jarvis.md:49` restringe o que vai à pessoa a "decisão, rótulo, merge na `main` e comando em arquivo travado", e o bloco "Com a pessoa" (recibo antes de acionar o time, perguntar só o que é dela, `R-DECISAO`) fica intacto. "Andar sozinho" cobre só esperar e preencher vagas; não dá ao Jarvis decisão de produto, escopo, custo ou risco.
- `R-MAIN`: o merge na `main` continua da pessoa (jarvis.md:49 e "A pessoa valida e faz o merge na `main`" no bloco "Com a pessoa"); `## Limites` do Jarvis intacto.
- `R-CONFORMIDADE`: "comando em arquivo travado" vai à pessoa, ou seja, o bloqueio vira pedido e não contorno; a frase da skill sobre edição recusada em `agents/**` ("relata e para, sem contornar por script") permanece.
- Frases tiradas do jarvis.md para caber no orçamento ("O time de agentes faz todo o resto...", "como Jarvis", "honesto", "sozinhas", o parêntese dos lotes): nenhuma era trava; o lote por arquivo e o de até 3 tópicos seguem na skill (SKILL.md:15-16), e a honestidade do relato segue garantida por `R-PROVA`.

## Achados
- A1 (recomendado) skills/trabalho-em-paralelo/SKILL.md:19 · a forma literal 'until <condição>; do sleep 60; done' não traz o prazo; quem copiar o trecho deixa uma espera sem fim em segundo plano; escrever o prazo na própria forma (ex.: timeout <segundos> envolvendo o laço)
- A2 (recomendado) skills/trabalho-em-paralelo/SKILL.md:19 · a pausa por limite de uso perdeu 'nada novo é disparado' e vem logo após 'encha as vagas'; o 'só conferências e integradores' ainda restringe, mas dizer que na pausa não se enchem vagas evita a leitura oposta

## Sondas

## Detalhe dos achados
- A1: evidência SKILL.md:19. Caminho: sem atacante; risco operacional (processo em segundo plano que não termina, presa de vaga e de memória da máquina, contra o espírito de `R-TETO`). Severidade: baixa. Correção mínima: na forma literal, envolver o laço num limite de tempo e dizer o que fazer quando o prazo vence. Esforço P. Dono: tech-lead (autor do texto).
- A2: evidência SKILL.md:19 (texto anterior: "na pausa só seguem conferências e integradores; nada novo é disparado"). Caminho: sem atacante; leitura ambígua pode levar a disparos durante a pausa por limite de uso. Severidade: informativa. Correção mínima: "Pausa por limite de uso (Q1): nada novo, só conferências e integradores". Esforço P. Dono: tech-lead.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Diff lido por `git diff --word-diff` numa worktree destacada no head revisado; rodado só `tests.test_orcamento_instrucao` (`R-TETO`), 8 testes OK. Varreduras de segredos e de workflow não se aplicam (só texto, sem workflow tocado).
