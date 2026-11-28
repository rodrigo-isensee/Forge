---
tipo: qa
contrato: 1
pedido: release-0.47.8
branch: melhoria/v0478-release-0478
commit: 3a621ba09372145609a045581aba0e79c85f6688
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: release 0.47.8 inteira (v0478, E27.4)

Head `3a621ba0` (marca da 0.47.8 sobre a develop em `2904a68a`). Cobre `git diff v0.47.6..3a621ba0` (84 arquivos, 0.47.7 e 0.47.8 juntas) e a junção dos itens, cada um já integrado com os próprios pareceres.

Itens, com QA, review e segurança `parecer: aprovado` em `docs/{qa,reviews,security}/`: forge-check defeitos (`v0477-forge-check-defeitos`, #667), textos de processo (`v0477-textos-processo`, #668), mutante pulado, índice do Forge, devops-lote (E6), cobertura-c1 (T1), fechar-mensagem, guardas-forge-check (E2.1). Develop-verde (E16) tem QA e review aprovados, sem parecer de segurança (só teste e peso; sem gatilho). Token-bot (E7) é só documentação e tem só review aprovado, sem teste a rodar.

Delta da marca: `git diff --name-only 2904a68a HEAD` lista só `.claude-plugin/plugin.json`, `dev/.claude-plugin/plugin.json`, `CHANGELOG.md` e os oito fragmentos removidos de `changelog.d/`; nenhum arquivo de `bin/`, `hooks/`, `.githooks/` nem `tests/catraca.py`. Mutação e vermelho antes do verde se aplicam aos itens (cada parecer os traz) e não a este head.

## Develop vermelha em 2904a68
O CI do push da develop em `2904a68a` (run 44396179688) falhou em "suíte (push na develop, python 3.12, parte 1/5)" e, por derivação, em "Partes e teto de pulados verdes". O log do job não ficou acessível a este QA (download bloqueado pelo sandbox; as anotações da API só trazem "Process completed with exit code 1"). Tentei reproduzir com `CI=true python3 scripts/suite-partes.py --parte 1/5` no head (959 testes, 42 módulos, carga 25 a 30 em 12 núcleos): a execução não terminou nos prazos e não deu veredito. Não reproduz, e o teste que falha não foi identificado aqui. O head desta release difere de `2904a68a` só em versão e changelog, então a falha, se for da suíte, vale para ele; a prova é o check-run `bateria` do CI do PR no mesmo sha, que decide o merge.

Prova da suíte: o check-run `bateria` do CI do PR no mesmo sha (a suíte local não vale, I5, e falha por ambiente do sandbox: /proc e gh).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Versão sobe contra a main | `python3 scripts/conferir-release.py --base origin/main`: base 0.47.7, release 0.47.8 | versão igual à da base | passou |
| Os dois manifestos batem com o CHANGELOG | `plugin.json` e `dev/.claude-plugin/plugin.json` em `"version": "0.47.8"`; uma entrada `## [0.47.8] - 2026-11-18` | manifesto sem par | passou |
| Entrada em português | leitura da `[0.47.8]`: Adicionado (E6.1, E6.6, índice, token), Alterado (T1), Corrigido (develop verde, fechar, forge-check, mutante) | item sem entrada | passou |
| `changelog.d/` sem pendentes | `bin/forge-changelog conferir-release`: ok | pasta só com README | passou |
| Os itens juntos, sem código após a marca | `git diff --name-only 2904a68a HEAD`: só versão, changelog e fragmentos | n/a | passou |
| Cada item com os pareceres aprovados | `parecer: aprovado` conferido nos arquivos acima | portão faltando | passou |
| Suíte no head | check-run `bateria` do CI do PR, mesmo sha | n/a | pendente do CI do PR (não é achado) |

## Provas
- `git rev-parse HEAD` = 3a621ba09372145609a045581aba0e79c85f6688
- `bin/forge-changelog conferir-release`: ok: changelog.d/ sem fragmentos pendentes
- `scripts/conferir-release.py --base origin/main`: versão base: 0.47.7 | versão da release: 0.47.8

## Notas
- Sem bugs abertos.
