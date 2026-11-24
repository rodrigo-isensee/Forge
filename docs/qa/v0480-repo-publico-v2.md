---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-repo-publico-v2
commit: 85f870f554dd9e67093a5b7a1f0c0ad8b89530fe
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0478 (E148.4, repositório público v2, PR #837)

Base 20630351, head 85f870f5 (código testado). Mudança em `hooks/conformidade.py` (trava de visibilidade no `gh repo create/new`, no `gh api` REST e no GraphQL; marcador do prazo por busca linear, E148.1), 86 fixtures `CONFORMIDADE-REPO-CREATE-PUBLICO` (62 de bloqueio, 24 de liberação), `tests/test_hooks.py::test_fixtures_do_repo_publico` e 8 specs de mutantes. Sem especificação de UX nem contrato de API: as obrigações são `R-CONFORMIDADE` (CONFORMIDADE-REPO-CREATE-PUBLICO) e o prazo de decisão do hook.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Criar repositório só com visibilidade privada explícita (`gh repo create/new`, `gh api` REST e GraphQL) | `Hooks.test_fixtures_do_repo_publico` (86 fixtures, os dois lados: código 0 e 2) | sem visibilidade, `--public` em toda forma, valor ilegível, campo colado, `--input`, variável GraphQL | passou |
| Leitura do `gh api` com variável, crase ou `\` + quebra segue livre (E148.1) | fixtures `trava-gh-leitura-*-libera`, `trava-gh-marcador-linear-libera` | lado liberado | passou |
| Decisão antes do prazo com 40 KB de string aberta e 8 KB de `gh repo ` repetido | mesmo teste, `medir_o_hook` com meio `PRAZO_DA_DECISAO_S` | custo de CPU do hook abaixo de metade do prazo | passou |
| Guardas mudadas têm mutante | 59 mutantes RP1 a RP60 (incl. RP57 a RP60 do marcador) | uma por linha de guarda | todos morreram |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_hooks.py -k test_fixtures_do_repo_publico` no head: 1 teste, OK, 13 s (inclui o orçamento de CPU do hook). Sem suíte local; a inteira roda no CI do PR (`R-QA`).
- A contagem de 86 fixtures confere (`grep -l`): 62 com `codigo` 2, 24 com `codigo` 0; o teste exige no mínimo 83 e os dois lados.

## Vermelho antes do verde
`bin/forge-testes --vermelho 20630351… --modulos test_hooks` saiu 2: o módulo inteiro estoura o prazo de 600 s por cópia (`test_hooks H 600.0 s, B 600.0 s`), sem veredito; não vale como vermelho. Refeito à mão numa cópia em `$TMPDIR` (head com `hooks/conformidade.py` trocado pelo da base):
```
python3 -I -m unittest discover -s tests -p test_hooks.py -k test_fixtures_do_repo_publico
AssertionError: 0 != 2 :
Ran 1 test in 9.078s
FAILED (failures=59)
```
Na base, 59 fixtures de bloqueio falham (a base libera); no head, o mesmo teste passa.

## Mutação (specs do autor, 8 arquivos, 59 mutantes)
`bin/forge-mutante tests/mutantes/v0480-repo-publico-fix*.json --processos 3`:
```
forge-mutante: pedido=v0480-repo-publico-fix rev=85f870f554dd spec=… (8 specs)
59 linhas "RPn · morreu · hooks/conformidade.py:<linha>", nenhuma sobrevivente, nenhum "sem veredito"
rc=0
```
RP57 a RP60 (marcador de E148.1: `if any(map(visibilidade_do_gh…` desligado, `any(all(…` anulado, `create|new` e `graphql|repos` trocados) morreram. Conferência da lista contra o diff: cada função nova (`api_publica`, `campos_da_api`, `privado_rest`, `graphql_publica`, ramo `repo create/new`, marcador) tem mutante.
A primeira rodada com `--processos 4` estourou os 590 s do meu `timeout`; refeita com `--processos 3` sem limite.

## Observações
- O teste de tempo mede CPU do hook nas duas fixtures de peso; passou no head com a máquina carregada (load médio 8 a 14).
