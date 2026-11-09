# Como o Jarvis recebe quem abre um projeto pela primeira vez?

Propósito: desenho curto do ONBOARDING-1 na 0.44.0, fundido com a fase E do produto, na versão mínima. Substitui, para esta versão, o desenho de 17/10 (`docs/onboarding-1/arquitetura.md` do forge-contrib), que dependia da BP-1 e da BP-2 antigas. Público: Jarvis, `tech-lead`, `ux-designer`, `qa-engineer`. Revisão: 2026-12-08.

Estado: proposta, implementada na branch `melhoria/v10-onboarding`.

## 1. Princípio
O Jarvis facilita para quem não sabe como funciona o desenvolvimento de software; o time faz o resto e aprende com os erros. Na primeira abertura, a pessoa só responde o que é produto. O técnico (stack, comando de pronto, ambiente, dependências) o time decide e registra como suposição (`R-DECISAO`).

## 2. O que muda
| Antes | Agora |
|---|---|
| Roteiro só para projeto novo (`forge novo-projeto`) | Mesmo roteiro para novo e adotado: o estado (`.forge/novo-projeto.json` ou pasta com código) diz qual; no adotado, o Jarvis lê o projeto antes e propõe o objetivo |
| 6 perguntas: perfil, objetivo, quem usa, stack, regras invioláveis, comando de pronto | 3 perguntas de produto: objetivo, quem usa, o que não pode quebrar. Perfil sai das boas-vindas ("se já programa, diga"); stack e pronto o time escolhe |
| Ciclo explicado só no pedido guiado | Antes da configuração, uma mensagem: o que o time faz e os três momentos em que a pessoa é chamada (protótipo; produto, prioridade, custo, acesso ou exceção; juntar na `main`) |
| Passo "ambiente novo" com Docker e medidas | Uma frase: ambiente é do time; `sudo` e segredo, a pessoa no terminal dela |

A entrada continua a de hoje: `agents/jarvis.md` manda à skill `forge:novo-projeto` sem `.forge/versao`. Nenhum hook, script ou agente novo; nenhuma linha nova no `jarvis.md`.

## 3. Orçamento de instrução
Corte em vez de acréscimo: a skill `novo-projeto` cai de 6.720 para cerca de 5.200 caracteres; a `modo-iniciante` ganha só a frase que a liga à primeira abertura, paga com corte na mesma skill. O `jarvis.md` não muda (`tests/test_orcamento_instrucao.py`, `docs/regras/orcamento.json`).

## 4. Fora desta versão
`forge` no PATH (L44), `scripts/jarvis` em pasta sem Forge (L45), `bin/forge-adotar` (L46), skill `adotar-projeto` (L47) e README para quem chega (L48): seguem no backlog da fase E.

## 5. Teste que prova
`tests/test_novo_projeto.py`: o roteiro tem só as três perguntas de produto, cobre projeto adotado, explica quando a pessoa é chamada, não pergunta stack nem comando de pronto e continua sem pedir segredo.

## 6. Afrouxa? Gatilho de segurança?
Não afrouxa: as proteções (`R-MAIN`, nada sem "sim", nunca segredo no chat) ficam literais. Sem gatilho: só texto de skill.
