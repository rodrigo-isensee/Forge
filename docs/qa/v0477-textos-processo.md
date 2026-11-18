---
tipo: qa
contrato: 1
pedido: v0477
branch: melhoria/v0477-textos-processo
commit: 447a4c8da0973a8fd04121d8a32032948e0a8570
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0477 (textos H8 e SIEG-G6)

Diff contra a base 038249c5: `agents/tech-lead.md`, `skills/trabalho-em-paralelo/ritmo-e-corte.md`, `docs/regras/R-LIMITES.md` (uma palavra em R-CUSTO) e o fragmento de changelog. Só texto; nenhum código, hook nem teste mudou. Sem teste novo, então sem vermelho antes do verde nem mutação (sem regra de código no diff). A seção H8 já existe em `skills/engineering-practices/tamanho-por-item.md` (linha 20), e o ponteiro do `tech-lead.md` aponta para ela.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| H8: o item pequeno tem caminho curto citado no tech-lead | `tests.test_orcamento_instrucao`, `tests.test_jarvis_nucleo`, `tests.test_metricas_texto`; leitura do ponteiro | orçamento de instrução do agente | passou (8, 43 e 2 testes) |
| SIEG-G6: cada item deixa a suíte verde sozinho no corte e na integração | `tests.test_sobreposicao_quadro` (61), leitura de `ritmo-e-corte.md` | n/a | passou |
| Regras com ID e invariantes preservadas (R-LIMITES mexida) | `tests.test_forge.RegrasInviolaveis` | texto de `R-CUSTO` na fonte | passou (3 testes) |
| Guarda sem mutante (R-QA) | `python3 -I tests/catraca.py --base origin/develop` | n/a | rc=0 |

## Cenários e resultado real
Módulos rodados no head 447a4c8d com TMPDIR próprio, sem suíte inteira (ela é do `bateria` do CI).

- `tests.test_metricas_texto`: Ran 2, OK.
- `tests.test_orcamento_instrucao`: Ran 8, OK.
- `tests.test_jarvis_nucleo`: Ran 43, OK.
- `tests.test_sobreposicao_quadro`: Ran 61, OK.
- `tests.test_forge.RegrasInviolaveis`: Ran 3, OK.

Falha citada pelo autor, `tests.test_forge.ForgeCheck.test_raiz_depois_do_subcomando_e_git_isolado`: reproduzida no head e também numa cópia limpa da base 038249c5 (`git archive`, sem `.git`), com a mesma asserção (stderr traz `pr: PR de "melhoria/x" não lido (gh pr view: ... not a git repository ...)`, esperado vazio). O diff não toca `bin/`, `hooks/` nem `tests/`, então não vem deste pedido. Causa provável: ambiente, porque o teste usa o `gh` real (2.45.0) do PATH com `GIT_DIR` inexistente; não provei a causa. Como defeito da develop, não está provado: o último run de CI da develop (44261590105) está `failure`, sem eu ter lido qual teste. Não bloqueia este pedido; fica como pergunta ao tech-lead conferir no `bateria` do PR.

## Observações
Nenhum bug aberto.
