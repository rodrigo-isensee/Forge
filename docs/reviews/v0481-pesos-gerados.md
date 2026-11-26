---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-pesos-gerados
commit: cb924113ca811f1c5172f7aad569e2b22b7a4595
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 E19.3, PESOS-GERADOS (#909), 1.ª rodada completa

Diff lido: `git diff 8ae4d6c6..cb924113` (merge-base com a `develop`), 8 arquivos, +121/-129; código de produção 50 linhas em `bin/forge-testes` e `scripts/suite-paralela.py` (H1 dentro do teto, um comportamento).

- ci: cb924113ca811f1c5172f7aad569e2b22b7a4595 verde

Leitura do `gh pr checks 909` no head: suíte 10/10 (3.12 e 3.14, partes 1 a 5), bateria (passos), bateria (verificações longas), instalação e árvore já provada verdes. Vermelhos que esperam outra coisa: `bateria (pareceres)` (espera os pareceres) e `catraca` (log do run 45825156644: R-CONFORMIDADE pede o rótulo `afrouxa-regra` do dono e R-QA aponta as guardas apagadas do A1).

## Achados
- A1 (bloqueante) tests/mutantes/v0481-pesos-gerados.json:1 · R-QA: a catraca do CI (run 45825156644) barra "guarda de bin/forge-testes mudada sem mutante declarado: apagada :967(base) e :965(base)". Guarda apagada não tem mutante: declare as duas em `isentas` com motivo, para o rótulo do dono cobrir só o afrouxamento real (R-CONFORMIDADE).
- A2 (recomendado) docs/engineering/v0479-pv-b3-pre-push.md:52 · os casos 2 (módulo novo sem peso, rc 1) e 3 (pesos ilegíveis, saída 2) do roteiro do pre-push deixam de valer com a E19.1; marque-os como superados pela E19.1 ou atualize o resultado esperado.
- A3 (recomendado) tests/test_forge.py:7297 · o nome `test_pr_nao_aumenta_os_modulos_sem_peso` contradiz a regra nova (o PR pode aumentar os sem peso); renomear dispara a catraca, então troque na próxima marca ou explique no docstring do teste.

## Sondas

## Parecer
Reprovado só pelo A1, que se corrige com duas entradas `isentas` na spec, sem mexer em código. O resto está correto e simples.

**Faz o que a ordem pede (E19, ordem do dono 26/11 09:40).** O PR comum não edita mais `tests/pesos-d4.json`: `--regerar` tira os pesos da lista `DERIVADOS` e, se um gerador os escrever, sai 2 (subTest novo em `test_escrita_fora_da_lista_fechada_sai_2`, morto pelo PG3). `--registros` não reprova o módulo novo sem peso, e `PesosDaSuite` só barra o módulo da base que perde o peso. A divisão usa a mediana para o módulo sem peso (`repartir`, `scripts/suite-paralela.py:153`, sem mudança) e a marca regera os pesos com `scripts/pesos-do-ci.py` (`skills/trabalho-em-paralelo/ritmo-e-corte.md:51`). O teste `test_dois_prs_paralelos_com_modulo_novo_se_juntam_sem_conflito` prova a trava que sai: duas branches da mesma base se juntam sem conflito.

**Afrouxamento de PR-VERDE C1.** O efeito é o que a ordem pede: "sem edição à mão em cada PR" implica aceitar o módulo novo sem peso. A catraca exige o rótulo `afrouxa-regra` do dono (R-CONFORMIDADE: asserções de 17845 para 17843, testes renomeados). O aceite é do dono, pelo Jarvis; este parecer não o substitui.

**Saída das guardas R4 a R7 da spec v0478-pv-b1-registros.** A saída é justa. O código que elas mutavam saiu inteiro (`modulos_sem_peso`, o `isinstance`, o `or sem_peso` e os dois `except` com `ValueError`), e a `de` de cada uma não existe mais no head. Atenção: saiu também o R6, não só R4, R5 e R7 como diz o brief. O R6 era justo sair: o `except (RuntimeError, OSError, ValueError)` deixou de existir, e PG1 (registros) e PG4 (regerar) cobrem agora as guardas novas de git ilegível. A spec antiga segue válida com R1, R2, R3 e R8, todos mortos.

**Pesos corrompidos: algum lugar ainda dá sem veredito?** Não; nenhum lugar dá mais saída 2. O comportamento falha fechado no CI, mas a classificação muda. Sonda `/root/.forge-contrib/wt/_tl265-v0481-sonda.sh`, que grava `{` e depois `[]` em `tests/pesos-d4.json`:
- `PesosDaSuite` fica vermelho nos dois casos (`{`: erro de JSON; `[]`: falha, porque todo módulo da base com peso "perde" o peso). Com isso o CI reprova e o `--registros` sai 1, com `registro desatualizado: pesos da suíte`, e não 2.
- `--regerar` não lê mais os pesos. Se um gerador os escreve, sai 2.
- `scripts/suite-paralela.py` `ler_pesos` devolve `{}` em silêncio e a divisão usa 1.0 para todos. Esse comportamento é anterior ao PR e fora do diff.
Aceito: o arquivo corrompido nunca dá verde, e o texto de ajuda (`2 = sem veredito (git)`) diz exatamente isso.

**Legibilidade e testes.** Nada morto em `bin/forge-testes`: `json` e `MODULO_DE_TESTE` seguem em uso. O `MEDIDOR_FALSO` continua no brinquedo e serve de sentinela: se o medidor voltasse a rodar, gravaria `test_novo: 0.5` e `test_modulo_novo_sem_peso_nao_e_medido` falharia. Os testes de comportamento cobrem o ramo de falha de cada guarda nova, em subprocesso com ambiente limpo e `-I`. O fragmento `changelog.d/v0481-pesos-gerados.md` está presente.

**Verificação à mão (só o que o diff toca).**
- `python3 -m unittest tests.test_testes_tocados.Registros tests.test_testes_tocados.Regerar tests.test_forge.PesosDaSuite tests.test_suite_paralela`: 102 testes, OK.
- `bin/forge-mutante tests/mutantes/v0481-pesos-gerados.json`: PG1 a PG4 mortos, rc=0.
- `bin/forge-mutante tests/mutantes/v0478-pv-b1-registros.json`: R1, R2, R3 e R8 mortos, rc=0.
- `bin/forge-mutante --cobertura --base 8ae4d6c6`: as duas linhas `apagada` do A1.
