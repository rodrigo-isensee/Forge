---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/lote-l09
commit: 61e72dd9b86320e2ce4295a8b7a56553623a0389
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-04
---
# QA: lote L09 (E15 BRIEF-MENSAGEM-LIMPA)

Código testado: 882a7dd7fa933f473d82fcac65c94517b6fb46fa (patch bc6d081), head f37be88. O `commit:` é o do teste novo do QA (tests/test_qa_lote_l09.py), em commit separado do parecer (E16); ele só acrescenta teste.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E15 mensagem abre em `modo: brief`, sem lembrete, com `Brief-sha256 ... Bytes`, sem o texto do brief; o hook a aceita | test_mensagem_real_passa_no_hook_e_traz_hash_e_bytes_do_arquivo (bin/forge-check e hooks/agentes.py reais) | primeira linha; ausência de `<<<BRIEF` | passou |
| E15 lembrete antes, sem hash ou hash errado são recusados pelo hook | test_lembrete_antes_do_modo_hash_ausente_ou_adulterado_sao_recusados | primeira linha; hash 0000 | passou |
| E15 dois blocos: o hook recusa a segunda `Arquivo:`; o conferente trata segunda `modo:`/`Arquivo:` como instrução e reprova mensagem sem Brief-sha256 | test_dois_blocos_sem_separador_... (hook real; texto de agents/conferente.md) | 2 `Arquivo:` no cabeçalho | passou |
| E15 sem lembrete no brief mensagem | test_erros_no_brief (autor) | stderr também limpo | passou |

## Cenários e resultado real
- `-p test_mensagem_conferente.py`, `test_erros_no_brief.py`, `test_agentes_hash_brief.py`: 78 testes OK; com o arquivo novo, 81 OK.
- Vermelho antes do verde: arquivo novo sobre a base a46eab7 (cópia descartável): 2 de 3 falham (`<<<BRIEF` ainda na saída; segunda `Arquivo:` aceita); o do lembrete/hash passa na base e guarda fronteira.
- `bin/forge-mutante tests/mutantes/lote-l09.json`: M1 morreu, rc=0; `--cobertura --base a46eab7` sem condição pendente. Mutantes do QA (spec no scratchpad): Q1 (voltar a imprimir o texto) morreu; Q2 (hook sem a checagem de forma do hash) sobreviveu, equivalente na prática: `hash_do_brief_diverge` recusa a mesma mensagem logo depois (só muda o texto da recusa).
- Observação: "dois blocos" com separador `<<<BRIEF` ainda passa no hook, por desenho e teste do autor (test_so_o_primeiro_bloco_e_conferido); a regra do conferente cobre a forma nova.
- Bugs: nenhum.
