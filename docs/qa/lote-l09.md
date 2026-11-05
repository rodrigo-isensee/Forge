---
tipo: qa
contrato: 1
pedido: versao-034
branch: melhoria/lote-l09
commit: 8c889ce5e9d57f4657a86c6608444ac0ae596f74
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

## Revalidação (head d4d1ca7)
- O `commit:` passou a ser a6eee8b, o teste do QA na lote-l09 (o 61e72dd da qa-l09 foi reaplicado por cherry-pick, mesmo conteúdo). Depois vieram o merge do L08 e d4d1ca7 (o teste no mapa do bin/forge-testes), sem mudar código nem teste.
- `-p test_qa_lote_l09.py`: 3 OK sobre d4d1ca7.
- O `commit:` aponta para d4d1ca7: a linha do mapa do forge-testes entrou depois do teste; o código de produção não mudou (o teste a6eee8b é ancestral).

## Revalidação (pareceres só da própria branch, 083a959 do L08)
O código novo veio do L08 por merge; o QA trouxe também o teste do L08 (QaPareceresDaBranch) por merge, e o `commit:` é o head 0e3067b, que o contém. Cenário de ponta a ponta (branch com parecer próprio aprovado e alheio desatualizado passa; sem o próprio reprova) passa nesta branch. `-p test_qa_lote_l08.py` e `-p test_qa_lote_l09.py`: 27 testes OK. Nota: a spec tests/mutantes/lote-l08-e7b.json, herdada do L08, está velha (bug L08-3, no L08); não é defeito do L09.

## Revalidação 0.34
Junção da develop no L09 (E3 do pedido versao-034), código testado em 8c889ce5e9d57f4657a86c6608444ac0ae596f74. A árvore estava em 213851d, que só difere de 8c889ce em docs/reviews e docs/security (sem código nem teste).
- Suíte inteira (`.githooks/pre-push --suite`, `FORGE_TRAVA_ESPERA=14400`, uma tarefa pesada por vez, R-TETO): `Ran 2616 tests in 1919.772s (2 processos)`, `OK (skipped=30)`, rc=0. Nenhuma falha de ambiente do pid namespace apareceu, então não houve o que provar igual na origin/develop. Log: `$TMPDIR/qa-lote-l09-suite.log` (TMPDIR vazio na sessão; o arquivo ficou no scratchpad da sessão, qa-lote-l09-suite.log).
- `scripts/validar-plugin.sh`: rc=0, "Validation passed".
- O delta 0e3067b..8c889ce traz o L08 (bin/forge-check, tests/apoio_conferida.py, specs de mutantes do L08); nada do E15. Os testes do E15 (test_qa_lote_l09.py) passam dentro da suíte.
- Bugs: nenhum. Parecer: aprovado.
