---
tipo: revisao-seguranca
contrato: 1
pedido: v048
branch: melhoria/v048-dono-pesos
commit: ca3c07bb5c4eebe23e849d0031dd9822c5aed05f
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-28
---
# Review de segurança: v048 (#959, DONO-DA-GERACAO-DOS-TEMPOS, E6.8)

1ª rodada completa no head `ca3c07bb` contra a base `ae194fa9` (develop). Exceção de tamanho aceita pelo dono (decisão de 2026-11-28 11:19). Escopo lido: `scripts/pesos-do-ci.py`, `skills/trabalho-em-paralelo/ritmo-e-corte.md`, `tests/test_pesos_do_ci.py`, `tests/mutantes/v048-dono-pesos.json`, os 3 specs da v047 realinhados e o fragmento de changelog. Nenhum arquivo em `.github/` muda no diff.

## Gatilhos
Gatilhos: dado externo não confiável (API do GitHub) alimentando artefato versionado da suíte, CI (confiança em execução de PR).

## Achados

## Sondas

## Detalhe dos achados
Sem achado. O que foi conferido, com evidência:

- **Execução de fork ou de outro repositório não entra.** `scripts/pesos-do-ci.py:64-72` exige, na execução, `event=pull_request`, `path` do ci.yml, `repository` e `head_repository` iguais ao `--repo`, `completed/success`; e, no PR lido em `repos/<repo>/pulls/N`, `merged_at` string, base `develop`, `head.repo` igual ao `--repo` e `head.sha` não vazio igual ao `head_sha` da execução. Teste: `tests/test_pesos_do_ci.py` `DepoisDoF6.test_pr_nao_mesclado_de_fork_de_outra_base_ou_de_outro_sha_nao_entra`. Sondas locais (todas devolveram `{}`, controle válido devolveu os pesos): execução com `head_repository` de fork, execução de outro repositório, PR com `head.repo` nulo (fork apagado), `head.sha` vazio dos dois lados, `merged_at: true`, `pulls/N` devolvendo lista, execução `failure`, outro workflow, perna de push dentro de execução de PR.
- **Confiança equivalente à do push na develop.** Só conta a execução do último sha de um PR mesclado do próprio repositório: o código que gerou as anotações é o que passou por review e entrou na develop. O caso residual (execução nossa listando um número de PR de outro repositório) cai no `head.sha` igual e, mesmo se casasse, o código seria o mesmo já mesclado; sem caminho de ataque.
- **Perna amarrada ao tipo da execução.** `scripts/pesos-do-ci.py:86-92`: a perna de push só vale em execução de push e a de PR só em execução de PR. Teste: `test_perna_de_push_nao_vale_em_execucao_de_pr_e_a_de_pr_nao_vale_em_push`. Os filtros de anotação (alfabeto, plano, finito, teto de 900 s, conjunto completo de partes) seguem os da v047 e valem para as duas origens.
- **Entrada malformada falha fechada.** `scripts/pesos-do-ci.py:149-155`: execução que não é objeto, sem PR, com dois PRs ou número de outro tipo é descartada sem pedir `pulls/` (`test_execucao_de_pr_malformada_nao_quebra_nem_entra`). JSON ilegível da API cai em `scripts/pesos-do-ci.py:230-232`: rc 1, stdout vazio, stderr só com o nome do tipo da exceção (sonda local: `JSONDecodeError`, rc 1), sem eco de cabeçalho ou token. `--conferir` com arquivo que não é objeto sai 1 (`:223-228`, `test_conferir_com_pesos_que_nao_sao_objeto_sai_1`).
- **Teto de chamadas.** O laço de PR para em `2 * limite` execuções aceitas e lê no máximo uma página de 100 execuções; o pior caso é 100 leituras de `pulls/N` por geração, sem amplificação explorável.
- **CI, permissão e segredo.** Nenhum workflow muda; a geração continua manual, pelo tech-lead, na marca de versão (`skills/trabalho-em-paralelo/ritmo-e-corte.md:52`), com `python3 -I` e saída revisada em commit; sem token novo, sem escopo novo, sem escrita automática no repositório (`R-MAIN`, `R-CUSTO`).
- **Para a correção do A1 do code review** (achar o PR pelo sha da execução, p.ex. a lista de PRs do commit): muda o caminho de confiança e volta a esta segurança por delta. Essa rota pode devolver mais de um PR, inclusive de fork com o mesmo sha; a correção mantém, para o PR escolhido, todas as guardas de `scripts/pesos-do-ci.py:64-72` (mesclado, base `develop`, `head.repo` igual ao `--repo`, `head.sha` igual ao da execução), descarta a execução quando nenhum ou mais de um PR as cumpre, e o teste ganha a lista vazia na execução e um PR de fork no mesmo sha.

Suíte: `python3 -m unittest tests.test_pesos_do_ci` local, 24 testes OK; a suíte inteira fica com o CI do PR #959 no Revisar-sha (citado no relatório da etapa, não afirmado aqui).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática, a suíte do arquivo e sondas locais com a API injetada (sem rede). Faltaram no PATH, sem instalar (`R-CUSTO`): o varredor de segredos, o de workflows e o SAST da skill; lacuna sem efeito aqui, porque o diff não toca workflow nem traz credencial.
