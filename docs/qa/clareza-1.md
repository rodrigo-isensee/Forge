---
tipo: qa
contrato: 1
pedido: clareza-1
branch: melhoria/clareza-pacote-1
commit: 6b3eca09da5005b02f9cf5775b38aeeb14b09f67
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-16
---
# QA - clareza-1 (pacote 1 de clareza: C-1, C-2, C-3, C-7, C-9, C-8, S-19)

Sem UX nem API. Revalidação proporcional (segunda rodada). Código testado: 6b3eca0 (implementação 4a83650; voltas do autor 4088593, 8e5b5e2 e, para os bugs B1 a B4 do parecer anterior, 8e130be -> 4e045d7, 720ae37, 75e8ac3 e 6b3eca0) sobre a base b16d20f. O HEAD da branch (05217fa) só acrescenta pareceres (review e segurança, ambos `parecer: aprovado`, `commit: 6b3eca0`) sobre o código testado. Não escrevi o diff. Não rodei mutação nem vermelho-antes-do-verde: o diff é de texto, e os testes novos do autor conferem presença de trechos; a verificação de leitura é o exploratório abaixo. O parecer anterior (commit 8e5b5e2, 2 médios e 2 baixos abertos) fica substituído por este.

## Obrigação -> teste -> resultado
| ID | Obrigação | Teste (comando real) | Fronteira protegida | Resultado |
|---|---|---|---|---|
| PQ-1a | Suíte verde, execução 1 | `python3 -m unittest discover -s tests -q` | n/a | 770 testes, OK, 120,4 s |
| PQ-1b | Suíte verde, execução 2 | idem | n/a | 770 testes, OK, 120,1 s; a falha intermitente do pre-push vista no review não se repetiu em nenhuma das duas |
| PQ-2 | Plugin válido | `scripts/validar-plugin.sh` | n/a | "Validation passed" |
| PQ-3 | Review e segurança aprovados no commit 6b3eca0 | `forge-check pr clareza-1 --ref HEAD --base origin/develop` | portão R-REVIEW e R-SEGURANCA | antes deste arquivo o único achado era o parecer de QA desatualizado (`agents/agile-coach.md mudou depois do parecer`), esperado; review e segurança sem achado |
| B1 | R-DECISAO e jarvis.md dizem o mesmo sobre item novo sob ordem ampla | leitura cruzada de `R-DECISAO.md:28` e `jarvis.md:108` | item novo reversível sob "pode fazer" | Fechado. Os dois dizem que item novo ou irreversível volta como pergunta; o jarvis.md acrescenta "sem passar pelo teste de bloqueante" e o teste de bloqueante fica para dúvidas de entendimento. Invariante `sem passar pelo teste de bloqueante` em `tests/config.json` |
| B2 | `técnico` explícito como decisão do time | `R-DECISAO.md:29` | `técnico` sob ordem ampla | Fechado para `técnico`: "Item `técnico` não depende de ordem... executa sem ordem do usuário", com invariante. Ver observação O4 sobre `suposição` e `no-protótipo` |
| B3 | `PERGUNTA: nenhuma` conta zero no agile-coach | `agents/agile-coach.md:14` | tag zero | Fechado: "`PERGUNTA: nenhuma` conta zero, pois a linha não é uma pergunta", com invariante |
| B4 | Exemplo da modo-iniciante sem "decidam vocês" em opção de custo | `skills/modo-iniciante/SKILL.md:39-45` | exemplo vs item 6 | Fechado: a opção B virou "aviso impresso na caixa" (sem custo por mensagem); nenhuma opção do exemplo é de custo, então a saída "decidam vocês" é coerente com o item 6 |
| EX-b | C-3: pergunta de exemplo traz todos os elementos (repetido) | montada pela seção "Como perguntar" (itens 1 a 6) | elementos obrigatórios | Contexto, exemplo, opções com efeito, "Afrouxa o processo?", custo com faixa e média, recomendação com base, "Faltam 2" e "decidam vocês" presentes. Só a observação O3 permanece |
| EX-d | C-7 e C-9 coerentes entre R-DECISAO, jarvis.md e modo-iniciante (repetido) | leitura cruzada de `R-DECISAO.md:26-29`, `jarvis.md:108`, `modo-iniciante:37` | exceções (custo, acesso, exceção a regra, irreversível) | As quatro exceções iguais nos três; sem contradição restante |
| EX-e | C-8 e S-19: o agile-coach lê as tags do modelo, inclusive o zero (repetido) | `agile-coach.md:14` contra "Tags de registro" do modelo (`_modelo.md:21-28, 48-49`) | tag zero e seção ausente | Lê as cinco tags; zero e "não medido" batem com o modelo. A contagem de linhas `PERGUNTA:` sem `nenhuma` dá o número certo |

## Bugs
Nenhum aberto. B1 a B4 do parecer anterior estão corrigidos (tabela acima). Sem arquivo em `docs/qa/bugs/` (nenhum defeito aberto).

## Observações (sem bug)
- O1: item aninhado em `## Escopo` sem regra de marca. O2: a forma do zero das outras tags (`NAO-ENTENDI:`, `ESCOPO+:`, `DEVOLVIDA:`) é só "ou a tag equivalente". O3: "Faltam N perguntas." não diz o que dizer quando N = 0, e a opção C do exemplo traz "sem diferença" em vez de faixa e média (permitido por "ou não medido").
- O4: sob ordem ampla, `suposição` e `no-protótipo` "ficam fora" (a ordem não os confirma), mas o texto não diz se o time executa a suposição já registrada ou se espera. Hoje o `jarvis.md` manda fazer só `confirmado` ou `delegado`; a leitura mais provável é que a suposição registrada segue o fluxo normal. Sem efeito de segurança; sugestão de esclarecer numa frase, a critério do autor.
- A saída das suítes traz `ResourceWarning: unclosed file` (stderr), sem falha; não comparei com a base.

## Resultado da execução
2026-10-16, WSL2, python 3.10, worktree ~/.forge-contrib/wt/clareza-1: 770 testes x 2, todos OK; validação do plugin OK; B1 a B4 confirmados fechados; exploratório (b), (d) e (e) repetido. Sem bug aberto, por isso sem `aceite_usuario`.
