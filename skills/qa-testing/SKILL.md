---
name: qa-testing
description: Padrões de QA do projeto - plano de testes, pirâmide de testes, E2E, acessibilidade, formato de relatório de bug e critérios de severidade. Use ao planejar, escrever ou executar testes e ao reportar defeitos.
---

# QA

## Pirâmide de testes
| Nível | Quem escreve | Onde |
|---|---|---|
| Unitário | agentes de desenvolvimento da stack | junto do código |
| Integração de API | agente de back-end | conforme a stack |
| Componente | agente de front-end | conforme a stack |
| E2E | `qa-engineer` | conforme a stack |
| Acessibilidade | `qa-engineer` | conforme a stack |

Ferramentas, pastas e comandos: `${CLAUDE_PLUGIN_ROOT}/stacks/<stack>/pronto.md` (a stack vem do `CLAUDE.md` do projeto).

Os E2E cobrem os fluxos críticos; o restante fica nos níveis mais baixos.

## Plano de testes (`docs/qa/<feature>.md`)
```markdown
# Plano de testes - <feature>
Links: especificação de UX, contrato da API, plano técnico.

## Escopo
O que está e o que não está coberto.

## Cenários
| ID | Cenário | Tipo | Prioridade | Automatizado |
|---|---|---|---|---|
| CT-01 | Login com credenciais válidas | E2E | Alta | sim |

## Dados de teste
Usuários, permissões e fixtures necessários.

## Resultado da execução
Data, ambiente, aprovados/falhos, links para bugs.
```

Para cada critério de aceite da especificação, pelo menos um cenário. A tabela critério → teste → resultado do parecer traz a coluna "fronteira protegida" (o limite que o teste guarda: vazio, máximo, permissão; `n/a` se não houver). Sempre incluir: entradas inválidas, limites (vazio, máximo, caracteres especiais), usuário sem permissão, falha da API e navegação só por teclado.

## Plano antecipado (o plano sai do caminho crítico)
- **Durante a implementação:** o QA escreve `docs/qa/<feature>.md` a partir da especificação (`CA-n`, fronteiras, dados), sem ler o código do autor, o que preserva a independência. Pedido de correção sem especificação nova não tem plano antecipado.
- **Quando o código chega:** a primeira tarefa é conferir o diff contra a lista de `CA-n` (escopo que mudou invalida o plano), completar as bordas que o código revelar, rodar vermelho antes do verde e executar.
- **Parecer:** só sobre o commit final e depois do review; `R-REVIEW` e `R-QA` ficam intactos, e só a escrita do plano e dos testes antecipados sai do caminho crítico.
- **Casos de abuso:** com gatilho de segurança (`R-SEGURANCA`), o QA transforma os casos de abuso do modelo de ameaças em testes, em arquivo seu, na mesma janela; o formato dos casos está na skill `cyber-security`.

## E2E
- Seletores por papel e texto acessível; `data-testid` só em último caso.
- Nada de espera fixa; use as esperas automáticas da ferramenta.
- Cada teste cria e limpa os próprios dados, sem depender de ordem.
- Navegador padrão no desenvolvimento; os demais no CI.

## Acessibilidade
- Verificação automática em todas as telas dos fluxos principais, com as tags WCAG 2.2 AA.
- Zero violações críticas ou sérias para aprovar.

## Teste nasce de obrigação, e para quando ela está coberta
- **Obrigação → teste:** todo teste responde a uma obrigação nomeada: critério de aceite (`CA-n`), regra (`R-<ID>`) ou suposição registrada. Teste nascido da estrutura do código ("cobrir esta função") não entra. Cada teste diz o que precisa quebrar para ele falhar.
- **Regra de parada:** uma amostra por classe de equivalência mais cada fronteira (vazio, mínimo, máximo, logo fora do limite). Para quando toda obrigação tem evidência e nada é redundante.
- **Teste redundante não entra:** no máximo um teste por comportamento distinto; o segundo que falha pelo mesmo motivo é apagado ou fundido. Cobertura se diz por obrigação, não em percentual.
- **Guarda contra suíte vazia:** teste que percorre pasta, glob ou lista afirma um mínimo de itens (N de hoje menos margem pequena); pasta renomeada derruba o teste em vez de passar sem ler nada.

## Vermelho antes do verde
Todo teste novo de correção ou de regra (`R-QA`) precisa ser visto falhando sem a implementação.
- **No Forge:** `forge-testes --vermelho <base>`, rodado pelo autor e de novo pelo QA, com a saída colada no parecer (ela abre com `vermelho: base=… head=…` e lista o que voltou à base). Ele roda em cópias em `$TMPDIR` e exige a árvore limpa; nunca mexe na árvore do autor. O veredito é por teste: saída 0 = ao menos um teste prova e nenhum cai no HEAD; 1 = nenhum prova ou algum cai; 2 = sem veredito (prazo, sinal, erro do próprio módulo de teste), que volta ao autor e nunca vale como vermelho. A falha de carga ou de preparação (módulo ou classe) da base só prova teste que a base não tinha; o que já existia sai "não prova (herdada da base)", então um `import` novo num módulo existente, sem teste novo, sai 1.
- **"Dívida pré-existente"** é só etiqueta: o teste que cai no HEAD continua bloqueando e vira cartão.
- **Projeto:** a forma da stack (`${CLAUDE_PLUGIN_ROOT}/stacks/<stack>/pronto.md`): rodar o teste novo contra o código anterior, numa cópia; `git stash` na árvore do autor só como recuo.

O parecer de QA registra o comando e a falha observada; teste que nunca falhou não prova nada.

## Mutação no código alterado
Quando a stack tiver ferramenta gratuita (`${CLAUDE_PLUGIN_ROOT}/stacks/<stack>/pronto.md`), rode mutação só nos arquivos alterados pelo diff, nunca no projeto inteiro. A meta de pontuação é do projeto, em `docs/engineering/praticas.md`; mutante sobrevivente vira teste novo ou justificativa no parecer. Cobertura de linhas não é meta.

## Simulação de merge (a base certa)
Para saber como a entrega fica sobre a base de integração, simule o merge fora da árvore de trabalho:
1. Use um clone ou uma worktree **com as refs remotas** e rode `git fetch origin <base>`.
2. Faça `git merge --no-ff refs/remotes/origin/<base>` na cópia descartável.
3. Rode a checagem **contra essa base** (a mesma da validação), nunca contra a base local.

Nunca use um clone sem as refs remotas (por exemplo `git clone --no-tags --single-branch` de outra ref, ou clone local sem `origin/<base>`): a checagem compara com a base errada e sai com rc 0. Confira que `git rev-parse refs/remotes/origin/<base>` responde antes de confiar no resultado.

## Mutantes declarados nos pedidos de controle
No Forge, o que decide por regra de código (`bin/`, `hooks/`, `.githooks/`, `tests/catraca.py`) tem a prova de mutação feita à mão e declarada: `bin/forge-mutante tests/mutantes/<pedido>.json` lê a spec (3 a 16 mutantes: arquivo, trecho `de`, trecho `para`, testes que devem cair; o mutante equivalente se declara no campo `equivalente`, com a justificativa, e sai na linha `equivalente: <id> · <justificativa>`, sem rodar) e roda cada um numa cópia descartável. Pedido com mais de 16 mutantes divide em `tests/mutantes/<pedido>-<n>.json` (mesmo `pedido`, id único no conjunto) e passa todas as specs numa só rodada: `bin/forge-mutante tests/mutantes/<pedido>-1.json tests/mutantes/<pedido>-2.json`.
- Pedido de controle: o autor declara os mutantes, **um por linha de guarda mudada no diff**. Nos demais, o QA escreve a lista e pode somar até 16.
- O QA confere a lista contra o diff antes de rodar: linha de guarda mudada sem mutante é achado bloqueante do QA, porque a saída 0 só prova o que a lista cobre (o autor, sozinho, escolheria mutantes que o teste dele já mata).
- `forge-mutante --cobertura --base <Base-sha>` é a checagem do autor antes do push: lista a condição Python mudada sem mutante declarado (cobertura é "declarado, não provado"; shell e outros tipos saem como `não coberto: <arquivo>`, uma vez por arquivo; `isentas` na spec, até 8, com `trecho` e `motivo`, saem como `isenta · arq:L · motivo` para o review e o QA lerem). A rodada de mutantes segue sendo a evidência do QA, e nenhum hook, pre-push nem CI chama a checagem.
- O QA roda `forge-mutante` e cola a saída no parecer. Saída 0 é o inverso do usual: todos os mutantes morreram. Prazo estourado ou erro de carga é "sem veredito", nunca "morreu".
- Mutante sobrevivente é achado bloqueante do QA até virar teste ou justificativa de mutante equivalente aceita pelo QA.

Bug ou falha de plano cuja classe se repete (já está em `docs/engineering/achados-recorrentes.md` ou volta neste pedido): o `qa-engineer` grava a linha `AR-<n>` nesse arquivo, no formato dele (só classe, ID da regra, contagem e `arquivo:linha`), no mesmo PR do parecer.

## Relatório de bug (`docs/qa/bugs/<id>-<titulo>.md`)
```markdown
# <id> - <título curto>
- Severidade: crítica | alta | média | baixa
- Responsável sugerido: agente de desenvolvimento da stack
- Ambiente: branch/commit, navegador

## Passos para reproduzir
1. ...

## Resultado esperado
## Resultado obtido
## Evidência
Log, screenshot ou trace da ferramenta de E2E.
```

## Severidade
- **Crítica:** perda de dados, falha de segurança, fluxo principal bloqueado sem contorno.
- **Alta:** funcionalidade importante quebrada, com contorno difícil.
- **Média:** funcionalidade secundária quebrada ou contorno simples.
- **Baixa:** cosmético, texto, alinhamento.

## Critério de pronto
Todos os cenários de prioridade alta passando, nenhum bug crítico ou alto aberto e zero violações de acessibilidade críticas ou sérias.
