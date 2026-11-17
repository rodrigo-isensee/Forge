---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-docs-pareceres
commit: 853e5f30085d70fc94d396c282ed43397ba1e49b
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-16
---
# QA: v047 docs-pareceres (E1.276, revalidação E1.317)

Intervalo `origin/develop..7d32017c`. Sem especificação de UX: as obrigações são as da etapa E1.252 do pedido v047 (o `pedido:` do parecer é id de `docs/pedidos/` ou `release-X.Y.Z`; `forge-check docs <arquivo>`; mensagem do bloco Achados vazio; modelo do review). Bug em `docs/qa/bugs/` não aberto: o defeito é um teste do repositório que cai no head.

## Revalidação por delta 7d32017c..b3bc317a (E1.317)
`forge-check parecer delta` lista no domínio `bin/forge-check`, `tests/mutantes/v047-docs-pareceres.json` e `tests/test_forge.py`. Aprovado: A1 e A2 do parecer anterior resolvidos, sem achado novo.
- A1 resolvido: `documentos_dados` passa `real.name` por `sem_controle` (`nome`); `python3 -m unittest tests.test_forge.SaidaSanitizada` · 8 testes, OK.
- A2 resolvido: o helper `docs` devolve veredito por asserção quando `cmd_docs` não recebe `arquivos`. Vermelho refeito à mão, porque `forge-testes --vermelho` com a suíte inteira estoura o prazo neste ambiente e `-k` não combina com ele: cópia do head com `bin/forge-check` e `_modelo.md` da base c5c3a449; classe nova, 11 testes, todos `FAIL` por asserção, nenhum `ERROR` (antes, 8 de 10 em TypeError). O teste novo `test_aviso_do_criterio_na_copia_de_fora_aponta_o_arquivo_dado` cai na base e passa no head (CA-3).
- Classe nova + SaidaSanitizada no head: 19 testes, OK. A suíte inteira roda só no CI do PR; sem PR ainda, sem check-run `bateria` do sha.
- Mutantes (`bin/forge-mutante tests/mutantes/v047-docs-pareceres.json tests/mutantes/v047-docs-pareceres-2.json --processos 3`), rc=0, M1..M13 `morreu` (M6, M8, M13 por erro do teste declarado sob o mutante). O delta mexe em duas linhas de guarda (408 e o aviso em 431); M8 cobre a primeira e o teste novo, a segunda.
- Remoto avançou só com pareceres de review e segurança; head local igual a c059048d antes deste commit.

## Revalidação por delta b3bc317a..b8451e77 (E2.515)
Só entraram merges da develop (head 853e5f30 e 86ac0fcb); `git diff 86ac0fcb..853e5f30` toca só pareceres, os dois JSON de mutantes, `tests/test_forge.py` (classe do autor) e o modelo do review: a parte do autor é a já revisada. `forge-check parecer delta` lista `bin/forge-check` e `tests/test_forge.py` pelo que veio da base. Aprovado, sem achado novo.
- `python3 -m unittest tests.test_forge.DocsPareceresPedidoECaminho tests.test_forge.SaidaSanitizada` · 19 testes, OK.
- `forge-check docs` rc=0.
- `bin/forge-mutante <2 specs> --base 853e5f30 --processos 3` · `fora do diff` M8..M13 (nada de guarda mudou no delta), rc=0.
- Suíte inteira: só no CI do PR; sem PR, sem check-run `bateria`.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CA-1 pedido inexistente ou nome da branch recusado, mensagem com o id | test_pedido_inexistente_e_nome_da_branch_sao_recusados_com_o_id_na_mensagem; sonda S1 | id fora de docs/pedidos, nome da branch inteiro e sem prefixo, `../`, `release-0.47` | passou |
| CA-2 pedido registrado, `release-X.Y.Z` e raiz de pedidos valem | test_pedido_registrado_release_e_branch_que_e_pedido_valem; test_pedido_da_raiz_de_pedidos_vale_e_sem_pasta_de_pedidos_nada_a_conferir | sem pasta de pedidos nada a conferir; `release-1.2.3x` recusado (sonda) | passou |
| CA-3 FC-DOCS-CAMINHO: só os arquivos dados, estrito, cópia fora da raiz com critério da pasta do tipo | test_copia_fora_da_raiz_...; test_dentro_da_raiz_a_pasta_errada...; test_arquivo_ausente_ou_que_nao_e_md_e_recusado; test_linha_de_comando_com_arquivo | ausente, não `.md`, diretório, tipo desconhecido, sem frontmatter | passou |
| CA-4 sem arquivos o pedido só se confere no delta | test_sem_arquivos_o_pedido_so_e_conferido_no_delta | delta vazio, delta com o arquivo, base ilegível | passou |
| CA-5 mensagem do bloco Achados vazio e aprovado sem o bloco | test_parecer_aprovado_sem_o_bloco_achados_passa; teste da cópia fora (mensagem nova) | "Nenhum." dentro do bloco | passou |
| CA-6 modelo do review diz o id e o parecer sem achados | test_modelo_do_review_diz_o_id_do_pedido_e_o_parecer_sem_achados | n/a | passou |
| Regressão da suíte | SaidaSanitizada (8 testes, `python3 -m unittest tests.test_forge.SaidaSanitizada`) | interpolação crua de caminho | FALHOU (A1) |

## Cenários e resultado real
- Classe nova: `python3 -m unittest tests.test_forge.DocsPareceresPedidoECaminho` · 10 testes, OK.
- Sondas com `--raiz-pedidos ~/.forge-contrib docs <copia>`: `pedido: v047` rc=0; `melhoria/v047-docs-pareceres` rc=1 "é o nome da branch"; `v047-docs-pareceres` rc=1 "é o nome da branch"; `release-1.2.3` rc=0; `release-1.2.3x` rc=1 "não está em docs/pedidos/".
- Vermelho (`forge-testes --vermelho origin/develop --modulos tests.test_forge --prazo 1500`), rc=2:
  `vermelho: base=c5c3a449d7c3 head=7d32017c69de módulos=test_forge (restrito por --modulos)`
  `revertidos à base: bin/forge-check, changelog.d/v047-docs-pareceres.md, templates/projeto/docs/reviews/_modelo.md`
  `tests.test_forge.DocsPareceresPedidoECaminho.test_linha_de_comando_com_arquivo · H=ok · B=falha · prova (asserção)`
  `tests.test_forge.DocsPareceresPedidoECaminho.test_modelo_do_review_diz_o_id_do_pedido_e_o_parecer_sem_achados · H=ok · B=falha · prova (asserção)`
  8 testes da classe nova: `H=ok · B=erro · sem veredito` (TypeError na base)
  `tests.test_forge.SaidaSanitizada.test_todo_valor_de_caminho_numa_fstring_passa_pelo_sanitizador · H=falha · B=ok · regressão`
  `contagem: não prova (passa na base)=609; prova (asserção)=2; regressão=1; sem veredito=8`
- Mutantes (`bin/forge-mutante tests/mutantes/v047-docs-pareceres.json tests/mutantes/v047-docs-pareceres-2.json --processos 3`), rc=0, 13 de 13 morreram (M1..M13; M6, M8, M13 por erro do teste declarado sob o mutante). `--cobertura --base c5c3a449` lista as 12 condições do diff como cobertas, nenhuma sem mutante.
- A suíte inteira roda só no CI do PR; sem PR ainda, não há check-run `bateria` do sha para citar. A1 indica que ela falhará.
