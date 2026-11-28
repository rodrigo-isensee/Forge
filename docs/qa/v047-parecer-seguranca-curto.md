---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-parecer-seguranca-curto
commit: c2138efd8de14c9412bc8f6e6bced8187a8b5283
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-16
---
# QA: v047 (parecer de segurança curto, E2.276, conferido em E2.280)

Escopo `5e74c70e...02fe845d`: texto em `agents/security-engineer.md` e nos dois modelos `docs/security/_modelo.md` (original e do template), fragmento de changelog e `tests/test_achado_teto_doc.py`. Sem código de controle (`bin/`, `hooks/`, `.githooks/`, `tests/catraca.py`): `forge-mutante` n/a. Não havia parecer de QA anterior: completo. O pedido não traz `CA-n`; as obrigações são as três regras decididas em E2.276 (mitigação pelo ID, gatilhos em uma linha, volta sem recopiar) e `R-SEGURANCA`/`R-REVIEW` citadas no texto.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Mitigação citada pelo ID, sem recopiar (agente e dois modelos) | `ParecerCurto.test_agente_e_modelos_trazem_as_tres_regras_do_parecer_curto` | frase nos 3 arquivos | passou |
| Volta não recopia a rodada anterior (3 arquivos) | mesmo teste (subTest por frase) | frase nos 3 arquivos | passou |
| Gatilhos em uma linha, formato `Gatilhos: ` | `ParecerCurto.test_gatilhos_do_modelo_em_uma_linha` | seção com 0 quebras de linha | passou |
| Modelo do projeto igual ao da fábrica | `ParecerCurto.test_os_dois_modelos_seguem_iguais` | igualdade byte a byte | passou |
| Compactação não tira regra do agente (invariantes, `R-SEGURANCA`, `R-REVIEW`) | `AchadoTetoDoc` (já existente) e `test_forge` | IDs na âncora | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_achado_teto_doc` no head: `Ran 4 tests`, OK.
- `python3 -m unittest tests.test_clareza tests.test_modelos_projeto`: `Ran 26 tests`, OK.
- `forge-check docs`: rc=0.
- Diff lido: a frase de gatilhos no modelo e a do agente concordam (`Gatilhos: ...`); sem limite numérico alterado, sem texto de stack. O parecer de segurança do pedido pode seguir o formato novo sem conflito com o teto de 300 caracteres por achado.
- Suíte inteira: no CI do PR (check-run `bateria` do mesmo sha); sem PR ainda, não citada.

## Vermelho antes do verde
`bin/forge-testes --vermelho 5e74c70e` estourou o prazo de 400 s sem veredito (rc 143 do `timeout`): é "sem veredito", não vale como vermelho. Substituto: cópia em `$TMPDIR` com o head e os 3 arquivos de texto trazidos da base `5e74c70e`: `Ran 4 tests ... FAILED (failures=14)`, caem os testes novos (as 4 frases nos 3 arquivos, os dois modelos iguais e a seção de gatilhos); no head, 4 OK. O autor deve rodar o `--vermelho` oficial no CI/PQ dele.

## Achados recorrentes (PA-7)
Conferidos AR-1 a AR-14: nenhum se aplica (sem código, hook, mutante, comando ou limite numérico alterado). AR-9 (limite antigo no texto): o texto novo não altera limite; o teste prova a frase nova presente. Nenhuma linha nova.

## Revalidação por delta (head c2138efd, E2.379)
`forge-check parecer delta` lista só `agents/security-engineer.md` (enxugado para caber no teto; sem mudança de regra: IDs `R-SEGURANCA`, `R-REVIEW`, `R-CUSTO`, `R-CONFORMIDADE` etc. mantidos, 8 linhas com ID; 6803 bytes). Frases do parecer curto e a regra de achado de 300 caracteres seguem no texto. Rodados no head: `tests.test_achado_teto_doc` (4 OK), `tests.test_orcamento_instrucao` (8 OK), `tests.test_pesos_teto` (2 OK), `tests.test_clareza` (9 OK), `tests.test_modelos_projeto` (17 OK); `forge-check docs` rc=0. Sem achados novos; o restante do intervalo veio da base (develop). Vermelho antes do verde: sem teste novo no delta (só texto), n/a. Suíte inteira: CI do PR.

## Mesclagem
`origin/melhoria/v047-parecer-seguranca-curto` já contido no clone ("Already up to date"); o head testado é ancestral do commit do parecer.
