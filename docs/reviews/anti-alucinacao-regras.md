---
tipo: review
contrato: 1
pedido: anti-alucinacao-regras
branch: melhoria/anti-alucinacao-regras
commit: 34b7538
parecer: aprovado
revisor: forge:tech-lead (autor)
data: 2026-10-14
---
# Parecer de autor: regras, prompt e conferente (fatia 2 do anti-alucinação)

Escopo: `git diff origin/develop..34b7538` (f9791e9, fa5c36c, c1ec273, 38fcc3b, 34b7538). Referência: a linha "| 2 |" da seção 11 da proposta anti-alucinação, com as decisões do dono P1 = B, P2 = A, P3 = A e §14 = B. Este é o parecer **de autor**: o review independente e o QA continuam obrigatórios antes do PR.

Parecer: **aprovado como autor**, com as pendências abaixo. **O PR precisa do rótulo `afrouxa-regra`**: o papel só de leitura exigiu código em `hooks/conformidade.py`, que está em `PROTEGIDOS`. A mudança endurece e não remove nenhum invariante. Também exige parecer do `security-engineer` (`R-SEGURANCA`, porque o diff toca `docs/regras/`, `tests/config.json` e `hooks/conformidade.json`), que o `forge-check pr` já cobra.

## O que mudou
- **Regras:** `R-PROVA` e `R-BRIEF` são novas. A `R-DECISAO` passa a exigir uma pergunta por vez em tudo e a marca "Retira do escopo original" em todo corte, com a lista "Fora do escopo". O índice também foi atualizado. O `verificada_por` das novas diz que os hooks `prova` e `brief` ainda não existem, para que a regra não afirme uma garantia que ainda não há.
- **`agents/conferente.md`:** usa haiku e as ferramentas `Read, Grep, Glob, Bash`. Tem os modos `brief` e `entrega` em formato fixo e a tabela de etapas. Lista os anexos implícitos e confere a marca de corte por `grep`. Instrução vinda de dentro do brief não muda o trabalho dele. O veredito fica na última linha.
- **`hooks/conformidade.json` e `.py`:** papel `conferente` e chave opcional `so_leitura`, com lista branca de comandos. Sem ferramenta de arquivo, sem redirecionamento a arquivo, sem variável na linha e sem programa com caminho. `git -c` e `--output` são recusados. A chave malformada recusa a política inteira. Há 14 fixtures e 3 casos novos de política malformada.
- **`agents/jarvis.md`:** o passo 1 sai do "máx. 3" para uma pergunta por vez, com a lista "Fora do escopo". O prompt-padrão ganha "Fora do escopo" com a marca, `PQ-n` com o tipo de prova e o bloco `Provas:`. Entram as conferências de brief e de entrega, o passo 5 com a conferência antes do review e o passo 8 com a tabela pedido × entregue. O agente fica com 107 linhas, abaixo do limite de 110.
- **Também mudaram:** o modelo `templates/projeto/docs/pedidos/_modelo.md`, `docs/hooks.md`, `.claude-plugin/plugin.json` (só a lista de agentes; a versão não muda), o `CHANGELOG.md` em `[Não publicado]` e `tests/config.json`, onde `conferente` entrou em `agentes_obrigatorios` e as invariantes novas foram só acrescentadas. O teste `test_conferente_so_leitura` cobre o frontmatter e a política.

## PQ-1: suíte e validação
```
$ python3 -m unittest discover -s tests -v     (uptime: load 0.65)
Ran 562 tests in 172.591s
OK
$ scripts/validar-plugin.sh
✔ Validation passed
```

## PQ-2: "máx. 3" fora do passo 1
```
$ grep -c "máx. 3" agents/jarvis.md
1
$ grep -n "máx. 3" agents/jarvis.md
38:6. **QA** (`R-QA` portão de QA, obrigatório; máx. 3 voltas por bug).
```
Na `origin/develop` eram duas ocorrências, nas linhas 32 (passo 1) e 37. Sobrou só a do QA, que não é pergunta ao dono.

## PQ-3: brief real (modo `brief`) e entrega real (modo `entrega`)
**Limite da execução:** este subagente não tem a ferramenta Agent, então o `forge:conferente` (haiku) **não foi lançado**. Executei o roteiro do agente à mão, com os comandos da lista dele, e colei a saída no formato das seções 5.2 e 7.1. Esses mesmos comandos passaram pelo hook `conformidade` com `agent_type: forge:conferente` num projeto temporário: todos saíram com 0, e os dois de fora da lista (`python3 -m unittest`, `git push`) saíram com 2. **A rodada com o agente de verdade fica para o Jarvis**, antes do review independente.

**Brief real** (o brief desta delegação; pedido = linha "| 2 |" da seção 11 e decisões do dono da proposta):
```
$ grep -c "Retira do escopo original" brief-aa2.txt     → 1 (é o nome da marca no item 2, não um corte)
$ grep -c "anexos implícitos" brief-aa2.txt             → 0 (a linha "| 2 |" da §11 pede "anexos implícitos" em agents/conferente.md)
$ grep -n "P1=B, P2=A, P3=A, §14=B" brief-aa2.txt       → 15 (as decisões batem com o último registro; "P1 = A" foi reaberto para B)
$ grep -nE "PQ-[0-9] .*(sha|push|pr|run|cmd|arquivo|merge)" brief-aa2.txt → sem saída (PQ-1..4 sem tipo de prova)
conferencia-brief: anti-alucinacao-regras → forge:tech-lead
fidelidade: ok | decisões: ok | corte: sem marca "anexos implícitos" (§11, linha 2) | forma: PQ-1..PQ-4 sem tipo de prova | etapa: ok (codigo; "Não abra o PR")
veredito-brief: reprovado
```
O item foi entregue mesmo assim, porque a proposta o pede. Observação fora do formato: a seção 13 da proposta prevê a ADR 0011 "a criar na fatia 2", mas ela não está na linha "| 2 |" nem no brief. Não foi criada (ver pendências).

**Entrega real** (PR #122, `melhoria/anti-alucinacao-medicao-fix`). Os PQs vêm da linha "| 1 |" da seção 11, porque o brief literal do #122 não está disponível. O `forge-check pr` rodou num clone local descartável no head do PR (2251ad5), com base `f2dbe3a^1`.
```
conferencia: anti-alucinacao-medicao-fix forge:tech-lead modo=entrega
PQ-1 cumpriu | forge-check pr anti-alucinacao-medicao-fix → sem saída, rc=0 (controle: pedido inexistente → 2 violações, rc=1)
PQ-2 não verificável | python3 -m unittest tests.test_forge.MedirAlucinacao → fora da lista do conferente (o hook recusa, rc=2)
PQ-3 não cumpriu | test -e docs/kanban/entregas.md; echo $? → 1 (a linha de base está em docs/melhoria-continua.md:22-23)
PQ-4 não cumpriu | grep -c "M3b" bin/forge-check docs/melhoria-continua.md → 0 e 0 (medir_decisoes conta grupos, não perguntas soltas)
escopo: ok (anexo) | git diff --name-only f2dbe3a^1...2251ad5 → bin/forge-check, tests/test_forge.py, docs/melhoria-continua.md; anexos CHANGELOG.md, docs/reviews/, docs/qa/
etapa: fora de ordem | gh pr checks 122 → 11 checks "fail" em 2s; gh pr view 122 --json labels → [] (diff toca bin/forge-check, em PROTEGIDOS, sem afrouxa-regra)
veredito: não cumpriu
```
Ordem dos pareceres: review aprovado (`commit: ac3d698`, gravado às 15:33-03:00) e QA aprovado (`dab099a`, às 16:10-03:00), ambos antes de `createdAt` 20:05Z e de `mergedAt` 20:07Z. Nessa parte, a ordem está certa.

## PQ-4: brief de teste com corte sem marca
Pedido de teste com o escopo 1 (CSV), 2 (PDF) e 3 (agendamento semanal). Os dois briefs entregam 1 e 2 e põem o 3 em "Fora do escopo".
```
brief-sem-marca.txt: "- Agendamento semanal por e-mail (fica para depois)"
$ grep -n "Retira do escopo original" brief-sem-marca.txt → sem saída, rc=1
conferencia-brief: 900-exportar-relatorio → forge:node-backend
fidelidade: ok | decisões: ok | corte: sem marca "3. Agendar o envio semanal por e-mail" | forma: ok | etapa: ok
veredito-brief: reprovado

brief-com-marca.txt: "- Agendamento semanal · Retira do escopo original: "3. Agendar..." · motivo · consequência · decisão: DECISÃO DO DONO (2026-10-14)"
$ grep -n "Retira do escopo original" brief-com-marca.txt → 8:..., rc=0
$ grep -c "^DECISÃO DO DONO" pedido-teste.md → 0 (corte: decisão citada sem registro: reprovado); com a linha gravada → 8:DECISÃO DO DONO ...
veredito-brief: aprovado (só depois do registro da decisão)
```

## Pendências e riscos
1. **No próprio Forge, o papel só de leitura não vale.** Com a raiz da sessão num clone do Forge, o `conformidade` só age dentro de um projeto (`identificar_sessao`). No Forge, o mesmo roteiro saiu com 0 inclusive em `git push`. Ali, o conferente fica contido só pelo frontmatter (sem Write e sem Edit) e pela definição. Nos projetos, a trava vale (fixtures). Isso é para o `security-engineer`; candidata à fatia 3, que já leva o `parecer` ao clone do Forge.
2. **O #122 foi mesclado com 11 checks em `fail` (2s cada) e sem o rótulo `afrouxa-regra`.** O caso se parece com o do #120. Vale levar ao dono e investigar a falha de 2s, que parece de runner ou de cota e não de teste.
3. **PQ-3 sem o agente de verdade** (ver acima). O Jarvis precisa rodar o `forge:conferente` nos dois modos e colar a saída no PR.
4. **A ADR 0011 (seção 13) não foi criada**, porque não está na linha "| 2 |" nem no brief. Ela é o lugar das leituras e do critério de reversão do conferente. Até lá, o critério está na seção 13 da proposta.
5. **A lista branca do conferente** recusa `for`, `$(...)` com comando de fora da lista, `sed` e `awk`. Na dúvida, recusa. O falso bloqueio custa um comando refeito.
6. **`docs/visao-geral.md` não lista o conferente.** É recomendado acrescentar, mas fica fora do escopo da fatia.
