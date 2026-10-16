---
tipo: qa
contrato: 1
pedido: clareza-1
branch: melhoria/clareza-pacote-1
commit: 8e5b5e25bd34917141dc80940a1aa62f8fb6bd11
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 2
bugs_baixos: 2
aceite_usuario: sim
data: 2026-10-16
---
# QA - clareza-1 (pacote 1 de clareza: C-1, C-2, C-3, C-7, C-9, C-8, S-19)

Sem UX nem API. Código testado: 8e5b5e2 (implementação 4a83650 e volta do autor 4088593 e 8e5b5e2) sobre a base b16d20f. O HEAD da branch (a17f0ce) só acrescenta pareceres (review e segurança, ambos `parecer: aprovado`, `commit: 8e5b5e2`). Não escrevi o diff. Não rodei mutação nem vermelho-antes-do-verde: o diff é de texto, e os testes novos do autor conferem presença de trechos (o exploratório abaixo é a verificação de leitura). Os achados abaixo voltam ao autor (`forge:tech-lead`); nenhum arquivo além deste foi tocado.

## Obrigação -> teste -> resultado
| ID | Obrigação | Teste (comando real) | Fronteira protegida | Resultado |
|---|---|---|---|---|
| PQ-1a | Suíte verde, execução 1 | `python3 -m unittest discover -s tests -q` | n/a | 770 testes, OK, 120,5 s |
| PQ-1b | Suíte verde, execução 2 | idem | n/a | 770 testes, OK, 118,9 s; a falha intermitente do pre-push vista no review não se repetiu em nenhuma das duas |
| PQ-2 | Plugin válido | `scripts/validar-plugin.sh` | n/a | "Validation passed" |
| PQ-3 | Review e segurança aprovados no commit 8e5b5e2 | `forge-check pr clareza-1 --ref HEAD --base origin/develop` | portão R-REVIEW e R-SEGURANCA | único achado: "sem parecer para o pedido clareza-1 (R-QA)", esperado antes deste arquivo |
| EX-a | C-1: preencher o modelo com marcas, "Clareza" e tags sem ambiguidade | leitura do modelo; pedido de exemplo preenchido em dois itens de cada seção | marca em Escopo, Fora do escopo e Critério de pronto | Preenche. Só duas dúvidas menores: item aninhado em Escopo não diz se leva marca (baixa, observação O1) e `PERGUNTA: nenhuma (ou a tag equivalente)` não dá a forma do zero de `NAO-ENTENDI:`, `ESCOPO+:`, `DEVOLVIDA:` (O2) |
| EX-b | C-3: pergunta de exemplo traz todos os elementos | montada pela seção "Como perguntar" (itens 1 a 6) | elementos obrigatórios | Contexto, exemplo, opções com efeito, "Afrouxa o processo?", custo com faixa e média, recomendação com base, "Faltam N" e "decidam vocês" aparecem. Achados B4 e O3 |
| EX-c | C-2: recibo vale para todo pedido | `agents/jarvis.md:33` ("em todo pedido"); sem a exceção "salvo leitura" que o review reprovou | recibo sem exceção | Vale para todo pedido registrado. Nada de C-5 no texto |
| EX-d | C-7 e C-9: "tanto faz" e ordem ampla coerentes com a R-DECISAO e o jarvis.md | leitura cruzada de `R-DECISAO.md:26-28`, `jarvis.md:108`, `modo-iniciante:37` | exceções (custo, acesso, exceção a regra, irreversível) | Exceções iguais nos três. Contradições: B1 e B2 |
| EX-e | C-8 e S-19: o agile-coach lê as tags do modelo, inclusive o zero | leitura de `agile-coach.md:14` contra "Tags de registro" do modelo | tag zero (`PERGUNTA: nenhuma`) | Lê as cinco tags e o caso "seção ausente = não medido". O zero em forma de tag não está no agile-coach: B3 |
| EX-f | Nada de C-4, C-5 ou C-6 | `git diff b16d20f...8e5b5e2 -- bin hooks .github` e busca por portão de 90%, atalho fechado, `forge-check pedido clareza` | fora do escopo | 0 arquivos em bin, hooks e .github; as menções a C-4/C-5/C-6 estão só nos pareceres, nenhuma no texto de produção |
| EX-g | Texto neutro e custo de eficiência no changelog | `changelog.d/clareza-pacote-1.md` | R-NEUTRO, decisão do dono sobre custo | Traz "Afrouxa o processo? Não" e eficiência de 1 a 3 min por pedido, média 2 |

## Bugs
Sem arquivo em `docs/qa/bugs/` por restrição do brief (só este arquivo). Todos para o `forge:tech-lead` (autor do texto).

- **B2 (média): a ordem ampla deixa sem cobertura os itens `técnico`, `suposição` e `no-protótipo`.**
  - Passos: 1. Pedido com Critério de pronto `PQ-1 ... · técnico` e uma suposição. 2. O usuário diz "pode fazer". 3. Ler `jarvis.md:108` ("faça apenas o que já está `confirmado` ou `delegado`") e `R-DECISAO.md:28` ("só cobrem itens já marcados `confirmado` ou `delegado`").
  - Esperado: "pode fazer" executa o pedido todo, incluindo o que o time decide (`técnico`) e o que está como suposição registrada.
  - Obtido: lido ao pé da letra, só dois dos cinco marcadores têm ordem; um agente que segue o texto pararia nos PQ `técnico` (todos os PQ do modelo levam essa marca) ou os trataria como "novo". Ambíguo; falta dizer que `técnico`, `suposição` e `no-protótipo` seguem o fluxo normal.
- **B3 (média): o zero em forma de tag fica contado como uma pergunta.**
  - Passos: 1. Pedido com `## Registro de clareza` contendo `PERGUNTA: nenhuma`. 2. Seguir `agile-coach.md:14` ("perguntas (`PERGUNTA:`)"). 3. Contar as linhas que começam com `PERGUNTA:`.
  - Esperado: 0 perguntas (o modelo diz que `PERGUNTA: nenhuma` registra zero).
  - Obtido: o agile-coach não conhece a forma `nenhuma`; a contagem direta dá 1. O modelo e o agile-coach divergem. Basta uma frase no `agile-coach.md` ("`PERGUNTA: nenhuma` conta zero") e um teste que a exija.
- **B1 (baixa): R-DECISAO e jarvis.md divergem sobre item novo sob ordem ampla.** `R-DECISAO.md:28` diz que item novo "volta ao usuário como pergunta"; `jarvis.md:108` diz que só vira pergunta se passar no teste de bloqueante, senão vira suposição (o ato irreversível volta sempre). O jarvis.md reconcilia; quem lê só a regra (fonte única) chega à conclusão oposta para o item novo reversível. Alinhar a frase da regra ao teste de bloqueante.
- **B4 (baixa): o exemplo oferece "decidam vocês" numa pergunta com opção que custa dinheiro.** `modo-iniciante/SKILL.md:44` fecha com `Se preferir, diga "decidam vocês"` e a opção B é "cada mensagem custa dinheiro". O item 6 diz que a saída não se oferece em pergunta de custo. O exemplo é a parte mais copiada; trocar o exemplo por um sem opção de custo ou tirar a saída dele.

## Observações (sem bug)
- O1: item aninhado em `## Escopo` sem regra de marca. O2: forma do zero das outras tags só implícita. O3: "Faltam N perguntas." não diz o que dizer na última pergunta (N = 0), e a opção C do exemplo traz "sem diferença" em vez de faixa e média (permitido por "ou não medido", mas é o único item do exemplo sem a média).
- A saída das suítes traz `ResourceWarning: unclosed file` (stderr), sem falha; não comparei com a base.

## Resultado da execução
2026-10-16, WSL2, python 3.10, worktree ~/.forge-contrib/wt/clareza-1: 770 testes x 2, todos OK; validação do plugin OK; exploratório EX-a a EX-g feito. Sem bug crítico nem alto; 2 médios e 2 baixos abertos, por isso `aceite_usuario: sim` (o dono decide se o pacote segue com eles ou volta ao autor).
