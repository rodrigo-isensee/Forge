---
tipo: qa
contrato: 1
pedido: anti-alucinacao-medicao-fix
branch: melhoria/anti-alucinacao-medicao-fix
commit: dab099a
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 2
bugs_baixos: 2
aceite_usuario: sim
data: 2026-10-14
---
# QA - correção da medição anti-alucinação (`forge-check transcricao lastro` / `decisoes`, corrige o #120)

Links: `docs/reviews/anti-alucinacao-medicao-fix.md`, `docs/melhoria-continua.md` (M1, M3). Não há UX nem API; as obrigações são os bloqueantes 1 a 3 do parecer do #120 e a linha de base do M1. Offline, só disco local (`R-CUSTO`).

## Resultados
| ID | Obrigação / cenário | Fronteira protegida | Resultado |
|---|---|---|---|
| CT-01 | `lastro` sobre as transcrições do Forge (282 .jsonl): números vs. linha de base | n/a | Passou com ressalva: total 845 afirmações, 118 sem lastro, 14,0% (277 relatórios); sessão s2: 831/113, 13,6%. Doc registra 113/832 (13,6%) e a re-review 114/833 (13,7%). A diferença é crescimento da sessão em curso (o corpus não é congelado). Ordem de grandeza e 13,6% da sessão estável batem |
| CT-02 | `decisoes` na mesma pasta | n/a | Passou: respostas=441, com_grupo=28, violacoes=0 (re-review: 438/28/0; +3 respostas da sessão corrente) |
| CT-03 | Saída anonimizada (stdout) | caminho pessoal, projeto, texto | Passou no stdout: só `sessao sN` e contagens; grep por usuário, nomes de projeto e `/home`: 0. Falhou na frase do anúncio (stderr), ver AA1-04 |
| CT-04 | Pasta vazia | vazio | Saída 1, "nenhum arquivo .jsonl" (lastro e decisoes) |
| CT-05 | Caminho inexistente | inexistente | Saída 1, "caminho inexistente" |
| CT-06 | .jsonl vazio | vazio | Saída 0, zeros, `taxa=n/a` (sem divisão por zero) |
| CT-07 | JSONL corrompido (JSON truncado, texto, array, string) e bytes binários | corrompido | Saída 0, aviso "4 linhas ignoradas (malformadas)" / "1 linhas", sem traceback |
| CT-08 | `--help` (raiz, `transcricao`, `lastro`, `decisoes`) | n/a | Saída 0, uso correto |
| CT-09 | Achado 1 da re-review (JSON aninhado) | objeto aninhado | Reproduzido: AA1-01, média |
| CT-10 | Achado 2 ("200 OK") | contexto de testes | Reproduzido: AA1-02, média |
| CT-11 | Achado 3 (fetch de `upstream/`) | remoto != origin | Reproduzido: AA1-03, baixa |
| CT-12 | `python3 -m unittest discover -s tests` | n/a | Passou: 561 testes, OK (654 s) |
| CT-13 | `scripts/validar-plugin.sh` | n/a | Passou: `Validation passed` (a validação tenta api.anthropic.com e o sandbox nega; não afeta o resultado) |

## Severidade dos 3 achados da re-review
Todos contam a mais (inflam M1), nenhum esconde afirmação falsa: 1 e 2 média (métrica errada, contorno simples), 3 baixa. Mais um achado novo, AA1-04 (baixa). Nenhum bloqueia. Pedem cartão próprio antes de cobrar a meta de -80% do M1.

## Vermelho antes do verde e mutação
Não reexecutei o vermelho dos 5 testes novos de `MedirAlucinacao`; a re-review registra que falhariam na versão anterior. Mutação: sem ferramenta gratuita na stack do Forge; não executada.

## Bugs
`docs/qa/bugs/AA1-01-mescla-com-json-aninhado-fica-sem-lastro.md`, `AA1-02-http-200-ok-conta-como-testes-ok.md`, `AA1-03-fetch-de-outro-remoto-prova-push.md`, `AA1-04-aviso-de-stderr-imprime-caminho-pessoal.md`.

## Veredito
Aprovado em dab099a. Zero críticos e altos; 2 médios e 2 baixos abertos exigem aceite do dono (`aceite_usuario: sim`).
