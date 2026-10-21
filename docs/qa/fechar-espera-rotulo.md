---
tipo: qa
contrato: 1
pedido: fechar-espera-rotulo
branch: melhoria/fechar-espera-rotulo
commit: 9930be95b0ee3ab10c6bb1c4c7d971f1d6d41471
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-21
---
# QA - `bin/forge-fechar --esperar-rotulo` (E1.4)

Links: `docs/reviews/fechar-espera-rotulo.md`, `docs/security/fechar-espera-rotulo.md`. Não há UX nem API; as obrigações são E1 e E2 do pedido e `R-FLUXO`. Código testado: 9930be95 (os pareceres de review 0f48aad e de segurança 249d447 só acrescentam documentos). Offline, sem rede (`R-CUSTO`); sondas e cópias só em `$TMPDIR`.

## Resultados
| ID | Obrigação / cenário | Fronteira protegida | Resultado |
|---|---|---|---|
| CT-01 | Rótulo aparece na leitura N com a Catraca vermelha: mescla preso ao head (`--match-head-commit`), sem `--add-label` nem `pr edit` | rótulo ausente nas N-1 primeiras leituras | Passou (teste do autor e sonda S5: rótulo e verde já presentes, mescla preso) |
| CT-02 | Prazo esgotado sem rótulo (`--espera 0`): para com a mensagem do passo 5 de hoje, sem merge | prazo zero | Passou (teste do autor e sonda S6: rótulo só na leitura 999) |
| CT-03 | Head do PR muda durante a espera: para, sem merge | head diferente do conferido | Passou (teste do autor); mutante sem a conferência do head morreu |
| CT-04 | Outro check vermelho (`bateria`) ou desconhecido (`cancel`): para na hora | check que não é a Catraca | Passou (teste do autor; sonda S3 com `cancel`) |
| CT-05 | Sem a opção: comportamento de hoje (para no passo 5) | opção ausente | Passou (teste do autor) |
| CT-06 | Catraca vermelha com rótulo já aplicado: tolera 10 leituras e para no passo 4 | limite da tolerância | Passou (sonda S1: 11 chamadas de `pr checks`, rc 1, sem merge) |
| CT-07 | PR sem pedido de rótulo e Catraca verde, com a opção: mescla na primeira leitura | caminho sem espera | Passou (sonda S4: 1 leitura de checks) |
| CT-08 | Por leitura: o script nunca aplica rótulo nem mescla sem a Catraca verde | n/a | Passou: `grep -E 'add-label\|pr edit\|gh api\|--admin' bin/forge-fechar` sem ocorrência; o único `break` do laço de checks exige nenhum estado pendente; a Catraca vermelha mascarada só alimenta a espera |

## Execução
- Suíte completa (`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q`): 1201 testes, 1 falha em `tests/test_hooks.py::test_rotulo_so_dono_gh_pendurado_decide_antes_do_timeout_do_hook` (9,90 s contra limite de 9 s), teste sensível a tempo sob a carga da suíte inteira; arquivo fora do diff. Reexecutado sozinho: `tests.test_hooks` 34 OK; `tests.test_fechar` 54 OK. É provavelmente o "FA" intermitente citado no pedido (E1.1). Reportado, não pulado.
- `scripts/validar-plugin.sh`: Validation passed.
- Vermelho antes do verde: com o `bin/forge-fechar` de `10c838f` (develop) e os testes novos, 6 falham (`mescla_quando_o_rotulo_aparece_na_leitura_n`, `prazo_esgotado_para_como_sem_a_opcao`, `prazo_esgotado_com_catraca_vermelha_nao_mescla`, `head_que_muda_durante_a_espera_para`, `outro_check_vermelho_para_sem_esperar`, `catraca_vermelha_com_rotulo_aplicado_para_apos_a_tolerancia`: a opção desconhecida aborta); o sétimo (`sem_a_opcao`) descreve o comportamento de hoje e passa, como esperado.
- Mutação no diff (cópia em `$TMPDIR`, `sed`): sem a conferência do head; mascarar a Catraca vermelha sempre (sem a tolerância); mascarar qualquer check vermelho; tirar a mensagem de rótulo ao esgotar o prazo. Os 4 mutantes foram mortos por `tests.test_fechar`.

## Achados

## Recomendações (não bloqueiam; dono: tech-lead)
- Review 1 (`bin/forge-fechar:192-196`, `:218`): Catraca vermelha por outro motivo vira pendente até `--espera`, e a mensagem final fala do rótulo sem a saída dos checks. Confirmado pela sonda S2 (PR sem pedido de rótulo, Catraca vermelha, `--espera 0`: "o PR pede o rótulo afrouxa-regra", que não é verdade). Imprimir `$saida` antes do `die`.
- Review 2 (`:194`): o 10 é número mágico; nomear a constante ou derivar de tempo.
- Review 3 (`:223`): o passo 4 reimprime a cada volta (60 linhas em 30 min); imprimir uma vez.
- Review 4 (teste da tolerância): contar as chamadas de `pr checks` e afirmar o limite; a sonda S1 já mediu 11 (tolerância de 10 mais a leitura inicial).
- Segurança R1 (`:182`): head vazio da leitura (`|| true`) pula a conferência; tratar vazio como erro. O merge segue preso a `--match-head-commit`.
- Segurança R2 (`:194`): mascarar a Catraca só quando o passo 5 detecta o pedido do rótulo (mesma causa da Review 1).
- Segurança R3: o mascaramento depende do nome do job `catraca` (`.github/workflows/catraca.yml:19`); comentar o acoplamento no workflow.
- QA: o teste de hooks sensível a tempo (`tests/test_hooks.py`, limite de 9 s) falha sob carga; dono do teste: tech-lead, folga maior ou medida em chamadas.
