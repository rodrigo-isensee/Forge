---
tipo: qa
contrato: 1
pedido: registro-pareceres-0.27.0
branch: melhoria/registro-pareceres-0.27.0
commit: 960f680644fa82482c419e42af4061fef9153f07
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-21
---
# QA: registro-pareceres-0.27.0

Escopo testado: o código entregue em `960f680` (E1 e E2 do pedido, já revisado em `641f6f1`, que só acrescenta `docs/reviews/registro-pareceres-0.27.0.md`). Não há UX nem API nesta entrega. O QA é de registro: confere que os pareceres da release 0.27.0 entram na develop idênticos ao estado aprovado e que a entrega não altera o restante do repositório.

Ambiente: worktree `~/.forge-contrib/wt/registro-pareceres-0.27.0` sincronizada com `origin/melhoria/registro-pareceres-0.27.0` (ff-only); base `341837724182e9012a4fb5a4746d55e24f5ac269`. Sem rede e sem custo (R-CUSTO). Os avisos de rede negada pelo sandbox (`api.anthropic.com`, `http-intake.logs.us5.datadoghq.com`) apareceram durante a suíte e a validação; nenhum teste falhou por causa deles. A origem ainda não foi confirmada (cartão SUITE-REDE-ANTHROPIC, já aberto pelo review).

## Critério -> teste -> resultado
| Obrigação | Teste (comando real) | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: os três pareceres são byte a byte o estado `4727325` | `git diff 4727325 HEAD -- docs/reviews/release-0.27.0.md docs/security/release-0.27.0.md docs/devops/release-0.27.0.md` e `sha256sum` contra `git show 4727325:<caminho>` | identidade do conteúdo (nenhuma reescrita) | diff vazio (0 bytes); os três sha256 batem (`88e19a13...`, `2fde3068...`, `6be043e3...`) |
| E1: escopo do PR só com os pareceres, o fragmento e o parecer de review | `git diff --name-status 341837724182e9012a4fb5a4746d55e24f5ac269 HEAD` | nenhum arquivo de código, teste, `CHANGELOG.md` ou `plugin.json` tocado | 5 arquivos `A`: `changelog.d/registro-pareceres-0.27.0.md`, os três pareceres e `docs/reviews/registro-pareceres-0.27.0.md` |
| E2: o fragmento é aceito pelo `forge-changelog` | cópia do HEAD (`git archive`) em `$TMPDIR/cl-copy`, `python3 bin/forge-changelog release 0.99.0 2026-10-21` | tipo fora de `Adicionado\|Alterado\|Corrigido`; fragmento sem linhas | rc=0, `5 fragmento(s) juntado(s) e apagado(s)`; a linha "registra na develop os pareceres ... da release 0.27.0" entrou no bloco. A versão 0.27.0 já existe no `CHANGELOG.md` da cópia, por isso o teste usou 0.99.0 só na cópia |
| E2: conferência do PR contra a base | `python3 bin/forge-changelog conferir --base 341837724182e9012a4fb5a4746d55e24f5ac269` (na worktree, só leitura) | fragmento novo presente; versão do PR igual à da base | rc=0, `ok: 1 fragmento(s) novo(s) em changelog.d/` |
| R-QA: suíte completa | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q` | regra da fábrica quebrada por qualquer teste | `Ran 1204 tests in 324.537s` / `OK` (rc=0) |
| R-QA: validação do plugin | `scripts/validar-plugin.sh` | manifesto e estrutura do plugin | rc=0, `Validation passed` (duas vezes: plugin e cópia). Avisos do diretório de plugins, sem relação com esta entrega: `README_MISSING` e `ICON_MISSING`, que não bloqueiam o `--strict` local |
| R-NEUTRO: nada de projeto nos pareceres | a suíte inclui `Neutralidade.test_sem_termos_de_projeto` | termos proibidos em agentes, skills, docs e modelos | dentro do `OK` da suíte completa |
| Conferência da ADR 0004 | `./bin/forge-check docs` na worktree | frontmatter dos pareceres e do parecer de QA | rc=0, sem saída |

## Cenários e resultado real
- Caminho feliz: os três pareceres idênticos ao `4727325`, fragmento aceito, suíte e validação verdes. Passou.
- Borda: versão já publicada no `CHANGELOG.md` (0.27.0) recusa a publicação do fragmento. Comportamento correto do `forge-changelog`; a entrega não tenta publicar a 0.27.0 de novo, por isso não é defeito. Passou.
- Erro: nenhum arquivo de código alterado, então nenhum teste precisou ser visto falhando. Não se aplica.
- Permissão: não se aplica (sem fluxo de acesso nesta entrega).
- Acessibilidade: não se aplica (sem tela).

## Vermelho antes do verde
Não se aplica: a entrega não traz teste novo nem correção de código. Os pareceres são documentos; o que se prova é a identidade com `4727325`.

## Mutação
Não se aplica: nenhum arquivo de código ou de teste foi alterado nesta entrega.

## Instáveis
Nenhum teste falhou nem mudou de resultado. A suíte rodou uma vez, verde.

## Bugs
Nenhum bug aberto. Nenhum arquivo em `docs/qa/bugs/` foi criado.

## Achados
