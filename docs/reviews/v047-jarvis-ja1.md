---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-jarvis-ja1
commit: 3af10697072d98ce2cd78b6a8723acba350459ce
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047 (E2.189, lote JA1 da E2.180)

Diff revisado: `4138445e...85e46f8a` (4 commits, 68+/1-; código e teste 61 linhas, dentro do teto M14). Parecer completo (não havia parecer anterior). Escopo: cartões RESPOSTA-A-TODA-MENSAGEM-DO-DONO e ETAPA-SO-APOS-CONFERIR-DEVELOP (brief `v047-tech-lead-319`).

Ferramentas citadas, sem refazer: o item não tem PR nem CI (integração do Jarvis); a suíte completa fica no CI do PR. Rodei só os testes do item na raiz do clone: `python3 -m unittest tests.test_jarvis_nucleo tests.evals.test_erros_por_papel` → `Ran 37 tests ... OK (expected failures=2)`.

## Achados
- A1 (recomendado) skills/falar-com-o-dono/SKILL.md:22 · A regra de abrir etapa só após conferir a develop é do fluxo do pedido, não da fala com o dono; o brief E2.180 pedia texto em fluxo-do-pedido e falar-com-o-dono. Sugestão: mover ou apontar a regra em skills/fluxo-do-pedido/SKILL.md (R-REVIEW).
- A2 (recomendado) tests/evals/test_regressao_forma.py:63 · O conferir() usado pelo eval novo roda forge-check com o os.environ herdado (GIT_* inclusive) e Python sem -I; quando a trava nascer e o forge-check ler a develop, um GIT_DIR de hook aponta para outro repo (AR-4). Sugestão: filtrar GIT_* e usar -I no rodar().

## Sondas

## Parecer
Aprovado. O texto das duas regras está na skill que o Jarvis cita (`agents/jarvis.md` já aponta para `skills/falar-com-o-dono/SKILL.md`; núcleo no teto, sem ponteiro novo, como o brief permitia) e a `description` passa a disparar a skill a cada mensagem do dono. Os testes de texto em `tests/test_jarvis_nucleo.py` prendem as frases-chave por linha inteira da regra. O eval `EtapaJaResolvidaNaDevelop` tem controle (etapa sem commit na develop passa, rc 0) e o caso `@expectedFailure` falha por asserção, não por erro: sonda local com o corpo do teste sem o decorador deu `rc 0`, `resultado: aprovado` no `forge-check brief` (a trava não existe ainda, como o docstring diz). O `develop_com` limpa `GIT_*` e isola `HOME` e a config do sistema (AR-4 conferido no código novo). Sem guarda de código mudada: nenhum mutante devido (classe N). Commits um por cartão, Conventional Commits em português, fragmento `changelog.d/v047-jarvis-ja1.md` presente. Itens do Entregar da E2.180 conferidos contra os commits: os dois cartões têm commit e teste; o texto em `fluxo-do-pedido` ficou de fora (A1, recomendado: o brief dava "eval ou trava, ou texto"). A2 é de um apoio anterior ao diff e só pesa quando o `@expectedFailure` sair; a classe já está em AR-4 (contagem atualizada neste commit).

## Revalidação
- E2.228 (head 3af10697): delta lido com `forge-check parecer delta`, intervalo `85e46f8a..3af10697`; no domínio só `docs/engineering/achados-recorrentes.md` (AR-4, vezes 2→3, linha do meu próprio commit 476260dc). O resto do intervalo é o parecer de QA (9777258e) e o merge do remoto (3af10697), fora do domínio. Sem código nem teste mudado: achados e parecer mantidos, aprovado no head 3af10697.
