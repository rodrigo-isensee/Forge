---
tipo: qa
contrato: 1
pedido: versao-034
branch: melhoria/lote-l10
commit: 8f22ad36940371ce59a4819a3a976b4d3e4bb0d4
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-06
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

## Revalidação (pareceres só da própria branch, 083a959 do L08)
O código novo veio do L08 por merge; o QA trouxe também o teste do L08 (QaPareceresDaBranch) por merge, e o `commit:` é o head 83a28d7, que o contém. Cenário de ponta a ponta (branch com parecer próprio aprovado e alheio desatualizado passa; sem o próprio reprova) passa nesta branch. `-p test_qa_lote_l08.py` e `-p test_qa_lote_l09.py` e `-p test_qa_lote_l10.py`: 28 testes OK. Nota: a spec tests/mutantes/lote-l08-e7b.json, herdada do L08, está velha (bug L08-3, no L08); não é defeito do L10.

## Revalidação 0.34
Head 8f22ad36940371ce59a4819a3a976b4d3e4bb0d4 (junções do L09 e da develop em 0e47e06 e do changelog do L08 em 8f22ad3); o `commit:` passou a ser esse head, sem teste novo do QA nesta rodada. Review revalidado no mesmo head em docs/reviews/lote-l10.md (1a451c4).

suite: reusa (a execução do push de 8f22ad3, /tmp/push-l10.log, 62 linhas; não rodei nada de novo, R-QA, R-TETO)

Resumo final copiado do log (linhas 49 a 55):
- `processo 1: rc 0, 962 testes, 1418.7 s, 51 módulos`
- `processo 2: rc 0, 1657 testes, 889.7 s, 43 módulos`
- `Ran 2619 tests in 1418.972s (2 processos)`
- `OK (skipped=30)`
- `push_rc=0 02:19:20` (linha 62)

Falhas: nenhuma linha de FAIL ou ERROR no log. Pulos: 30 (`skipped=30`, linha 55), sem lista por teste no log. Avisos e aviso de rede, literais, com o número da linha:
- linha 5: `AVISO: job 'j' pulado por falta de suporte: condição sem suporte (token inesperado): __import__('os').system('touch /tmp/forge-suite-vgcwdivh/p1/tmpeszu1two/executou')` (caso de teste de recusa de condição; o log não mostra execução)
- linha 9: `AVISO: --confiar: o código do PR de fork de 'dona' vai rodar nesta máquina com o seu ambiente e com a credencial do gh em disco; ela fica exposta a esse código.`
- linha 10: `AVISO: j/lint pulado: actionlint ausente no PATH`
- linha 18: `AVISO: j/lint pulado: actionlint ausente no PATH`
- linha 46: `catraca: a API do GitHub não respondeu por inteiro (KeyError); vale como sem rótulo.`
- linhas 47 e 48: `catraca: a API do GitHub não respondeu por inteiro (OSError); vale como sem rótulo.`

O que mudou desde 83a28d7 e se tem teste (por leitura do diff):
- Código de produção: só `bin/forge-check` (`pr_da_cli` ganhou `conferir`; `pareceres_da_integracao` passa `conferir=False`), vindo do L08 (3625656) por merge; coberto por tests/test_conf_escopo.py (mais 9 linhas) e pela spec tests/mutantes/lote-l08-escopo.json (nova). O código do L10 (E14) não mudou; seus testes (test_volta_por_delta, test_qa_lote_l10) rodam na suíte do push.
- Testes e apoio: tests/apoio_conferida.py, tests/sem_claude_ancestral.py, test_atualizar, test_estado_da_branch, test_sugerir e as specs de mutantes do L08 (e7, e7b); são testes, entram na execução do push.
- Versões, CHANGELOG e fragmentos de changelog, pareceres e docs de outros itens: sem lógica a testar.
- Nenhum bug novo; 0 abertos. A spec velha do L08 (bug L08-3) segue sendo do L08.

Parecer: aprovado.
