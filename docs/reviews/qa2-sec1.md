---
tipo: review
contrato: 1
pedido: qa2-sec1
branch: melhoria/qa2-sec1
commit: 1093bc1036069b2d5757750b6ad374da75e7c64e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-20
---
# Code review: QA2-SEC1 (plano e testes de abuso durante a implementação)

Diff revisado: `bd204b8...1093bc1` (6 arquivos, 22 inserções, 6 remoções): `agents/qa-engineer.md`, `agents/security-engineer.md`, `skills/qa-testing/SKILL.md`, `skills/cyber-security/SKILL.md`, `tests/config.json`, `changelog.d/qa2-sec1.md`. Revisor: instância que não implementou o cartão (`R-REVIEW`, D-ETAPAS-INST).

Ferramentas: `python3 -m unittest discover -s tests` rodado duas vezes nesta revisão (uma por vez, `R-TETO`). A primeira terminou com `Ran 876 tests` e `FAILED (errors=7)`; a segunda, com a listagem filtrada por `^(ERROR|FAIL):`, não listou nenhum teste com erro ou falha. Os erros da primeira não se repetiram e não foram atribuídos ao diff (que só mexe em texto e em `tests/config.json`); o autor registrou 876 OK e `validar-plugin` OK. O QA (E1.3) roda a suíte de novo sobre o commit final.

## Contra o E1 (plano antecipado)
- O plano nasce da especificação durante a implementação, sem ler o código: `skills/qa-testing/SKILL.md:44`.
- Quando o código chega, a primeira tarefa é conferir o diff contra a lista de `CA-n`, completar as bordas, rodar vermelho antes do verde: `skills/qa-testing/SKILL.md:45`.
- O parecer sai só sobre o commit final e depois do review: `skills/qa-testing/SKILL.md:46`.
- Bom limite: pedido de correção sem especificação nova não tem plano antecipado (`:44`), o que evita plano sem base.

## Contra o E2 (SEC-1)
- Formato dos casos de abuso (entrada, caminho, resultado esperado), só com gatilho e "sem gatilho, não se aplica": `skills/cyber-security/SKILL.md:18`.
- O QA escreve os testes de abuso em arquivo seu, na mesma janela: `skills/qa-testing/SKILL.md:47`; o agente cita (`agents/qa-engineer.md:13`) e o `security-engineer` cita a skill (`agents/security-engineer.md:18`), mantendo o parecer de segurança sobre o commit final. SEC-2 não entrou.

## Texto único
- A regra mora na seção "Plano antecipado" da skill `qa-testing`; o formato dos casos de abuso mora na skill `cyber-security`. Os agentes citam as seções. A frase do `agents/qa-engineer.md:13` é um resumo de uma linha com a citação da seção, no padrão dos demais passos do agente; ver recomendação R1.
- Regras citadas pelo ID (`R-REVIEW`, `R-QA`, `R-SEGURANCA`), sem trecho de regra entre aspas (AntiDuplicacao).

## Portões não afrouxados
- `docs/regras/R-REVIEW.md` e `docs/regras/R-QA.md` não foram tocados. O texto novo reforça a ordem: o veredito do QA continua depois do review e sobre o commit final; só a escrita do plano e dos testes antecipados sai do caminho crítico. ARQ-1 (QA em paralelo com review) não entrou, conforme a decisão do dono.
- Nenhum controle mudou (hook, CI, `forge-check`), o que confirma a suposição de "sem gatilho de segurança" do pedido.

## Invariantes
- `tests/config.json`: só acréscimos (6 trechos novos: 2 em `agents/qa-engineer.md`, 3 em `skills/qa-testing/SKILL.md`, 1 em `skills/cyber-security/SKILL.md`); nenhum trecho existente saiu nem mudou. A chave `skills/cyber-security/SKILL.md` é nova e única no objeto (sem chave duplicada que sobrescreveria outra). Cada trecho novo bate com o texto da branch.

## Neutralidade e changelog
- R-NEUTRO: nada de projeto, stack ou nome específico no texto novo.
- Fragmento `changelog.d/qa2-sec1.md` presente, seção "Alterado", sem tocar `CHANGELOG.md` nem a versão.
- `agents/jarvis.md` fora, como o pedido manda; o passo 4 dele ("prepara os testes desde a especificação") segue coerente com o texto novo.
- Critério de reversão e "Por que o existente não basta": não se aplicam (ajuste de prática em texto, sem mecanismo novo).

## Commits
- `8862c1c docs(qa): ...` (texto) e `1093bc1 test(invariantes): ...` (proteção e fragmento): Conventional Commits em português, divisão coerente.

## Achados

## Detalhe dos achados
- R1 (recomendado) agents/qa-engineer.md:13 · o passo 2 repete em uma frase o conteúdo da seção "Plano antecipado" (nasce da especificação, sem ler o código, parecer no commit final depois do review). Está dentro do padrão de resumo com citação e um dos trechos virou invariante; se a seção mudar, o resumo precisa acompanhar. Sem bloquear: numa próxima volta, reduzir a frase à citação da seção.
