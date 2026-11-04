---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/lote-l10
commit: f25db720f6c418c78c2b9e0624a893bb9538e337
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-04
---
# QA: lote L10 (E14 VOLTA-ETAPA-NOVA)

Código testado: effbe5b1b16cedb1c84698afcf4921c053692c48, head 018abcb. O `commit:` é o do teste novo do QA (tests/test_qa_lote_l10.py, 32 linhas, commit separado do parecer, E16). Segurança do L10 aprovada em ea27a6a (informada pelo coordenador).

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| C-1 só acréscimo no fim; linha anterior editada, com espaço a mais ou acréscimo no meio reprova | test_volta_acrescenta_so_a_etapa_aberta_depois_do_brief_anterior (autor; gerar e conferir reais) | espaço a mais (T-1); meio | passou |
| C-2 forma do gerador e texto de ## Etapas; etapa repetida | idem | texto C em vez de B; duas vezes | passou |
| C-3/T-3 prova só do Histórico, depois do brief anterior | idem (antes, sem prova, sem brief, fora da forma) e test_so_o_brief_anterior_exato... (QA: brief -10 não vale como -1; "abertura prevista" e "abertas" não valem) | prefixo de nome; palavra a mais | passou |
| C-4 etapa da volta ou já no Entregar do anterior | idem | Cobre:; E1.1 | passou |
| C-5 gerador e conferência com a mesma função | idem (gerado passa na conferência, rc 0) | n/a | passou |
| T-2 Objetivo e Relatório byte a byte | idem | uma palavra mudada | passou |

## Cenários e resultado real
- `-p test_volta_por_delta.py`: 68 OK; arquivo novo do QA: 1 OK.
- `bin/forge-mutante tests/mutantes/lote-l10.json`: M1 a M12 mortos, rc=0. `--cobertura --base f37be88` listou 4 condições sem mutante (1864, 1866, 1978, 1979); somei Q3 a Q6 do QA (spec no scratchpad) e Q1/Q2 (nome do brief, forma da linha): 6 de 6 mortos.
- Vermelho antes do verde: o teste novo do QA não roda na base (usa o fixture E14, que a base não tem), então a prova é por mutação (Q1 e Q2 caem só com o teste novo; os demais, com o do autor).
- Cenário de abuso fora do plano do autor: `aberta-nao` entra (bug L10-1, baixa). A data da linha não é comparada, só a ordem no Histórico (é o que C-3 pede).
- Bug: docs/qa/bugs/L10-1-abertura-aceita-sufixo.md.

## Revalidação (delta 08aa2a4 e 59bec42, head fd7b144)
- O `commit:` passou a ser o do teste do QA que acrescenta o caso `aberta-nao` (fd7b144), sobre a correção 08aa2a4 (código testado).
- L10-1 fechado: `ETAPA_ABERTA` termina em `aberta\s*$` (bin/forge-check:1832). `aberta-nao`, `abertura prevista` e `abertas` não valem como prova; o caso novo do QA passa e antes da correção falhava (observado sobre effbe5b).
- `test_volta_por_delta` + `test_qa_lote_l10`: 69 OK.
- `bin/forge-mutante tests/mutantes/lote-l10.json`: M1 a M13 mortos, rc=0 (M13 guarda a âncora do fim da linha).
- Bugs abertos: 0 (docs/qa/bugs/L10-1-abertura-aceita-sufixo.md fechado).

## Revalidação (head f25db72)
- Depois do parecer anterior vieram os merges do L09 e f25db72 (o teste do QA no mapa do bin/forge-testes), sem mudar código nem o teste; o `commit:` segue fd7b144, que é ancestral do head.
- `-p test_qa_lote_l10.py`: 1 OK sobre f25db72.
- O `commit:` aponta para f25db72: a linha do mapa do forge-testes entrou depois do teste; o código de produção não mudou (o teste fd7b144 é ancestral).
