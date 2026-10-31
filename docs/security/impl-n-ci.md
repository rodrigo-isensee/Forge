---
tipo: revisao-seguranca
contrato: 1
pedido: impl-n-ci
branch: melhoria/impl-n-ci-c3
commit: 44617ead4fee4eab8193b8e07cda121e45f5cf2b
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-31
---
# Review de segurança: IMPL-N-CI, branch c3 (E1.3)

Diff lido: `c162bcb..44617ea`, ou seja o que a c3 acrescenta à develop depois que a c2 entrou pelo PR #408 (`git merge-base --is-ancestor c162bcb 44617ea` confirmado). A revisão é estática e local, em paralelo ao code review, contra o modelo de ameaças `docs/security/ameacas/n-ci.md` (C-6 a C-12, AB-1 a AB-5).

**O que a branch entrega:** a segunda metade do item E2 do pedido (item 55 d): o veredito da suíte protegido do resumo do CI (C-6 a C-8), e o teste que roda o orquestrador no próprio processo passa a não escrever no resumo real (C-10). Com isso fica cumprida a condição do parecer de segurança da c2 (A1 daquela rodada: C-6 e C-7 na c3, antes da promoção da 0.31).

**M14 (`agents/tech-lead.md:19`):** cumpre. Pelo `git diff --numstat --no-renames c162bcb...44617ea`, contam `scripts/suite-paralela.py` (28+13) e `tests/test_suite_paralela.py` (80+15), 136 linhas no total, abaixo de 150 e sem exceção de teto. Ficam fora `changelog.d/impl-n-ci-c3.md` e os pareceres. A branch não toca `hooks/` nem caminho de `PROTEGIDOS`. O PR carrega um comportamento só: o resumo não esconde nem muda o veredito.

## Gatilhos
Controles do Forge (`R-SEGURANCA`): `scripts/suite-paralela.py` decide o veredito do portão no pre-push e no CI.

## Achados
- A1 (recomendado) scripts/suite-paralela.py:536 · Nenhum teste fixa a ordem do C-6 (o resumo depois do veredito e dos erros da guarda). O mutante que troca as linhas 535 e 536 passa nos 11 testes de resumo. Sem efeito no portão hoje, porque o except amplo contém o erro.

## Detalhe dos achados
**O que foi conferido.**
- *C-6 (o veredito não depende do resumo).* O código de saída e a linha do veredito saem do ramo da guarda (`:527`-`:534`), e os erros da guarda são impressos antes. `print(veredito)` (`:535`) vem antes de `publicar_no_ci` (`:536`). Em `publicar_no_ci`, `montar_resumo` passou para dentro do `try`, e o `except Exception` (`:461`) imprime no stderr só o nome do tipo da exceção, sem mensagem nem dado. Os manipuladores de sinal já foram restaurados antes (`:504`-`:505`), então um `Interrompido` não pode ser engolido ali. `fechar_verde` (`:540`) conserva a ordem anterior: pesos só com `FORGE_SUITE_MEDIR=1` e carimbo K6 só com o veredito verde e a árvore igual. Nada lê o resumo (C-12). No pre-push, sem `GITHUB_STEP_SUMMARY`, o código novo não roda.
- *C-7.* A primeira linha traz o veredito (`:424`). Com `FAILED`, o resumo para em "execução reprovada: não vale para o orçamento" (`:432`-`:434`), sem a medida. O veredito vem do próprio script (só contagens), nunca da saída dos testes, e por isso o C-9 continua valendo.
- *C-8.* Relatório `None` ou malformado continua tolerado, e o módulo sem duração é listado com teto (`LIMITE_SEM_DURACAO`, `:59`; `:429`-`:431`). Os nomes saem de `partes`, só identificadores.
- *C-10.* `orquestrar_no_processo` (`tests/test_suite_paralela.py:169`) tira `GITHUB_STEP_SUMMARY` e `GITHUB_ACTIONS`, restaura o ambiente e descarrega os `test_*` do brinquedo. O AB-5 (`:320`) prova isso com um sentinela.
- *Casos de abuso:* AB-1 `:291`, AB-2 `:300` (pasta no lugar do arquivo e `montar_resumo` forçado a lançar, nas suítes verde e vermelha), AB-3 `:279`, AB-5 `:320`.
- *Mutantes que rodei numa cópia em `$TMPDIR`:* `except OSError` no lugar de `except Exception` reprova `test_resumo_nao_muda_o_veredito` (errors=1). `if False:` no lugar do ramo `FAILED` reprova `test_resumo_comeca_pelo_veredito` (failures=1). A troca de `:535` com `:536` sobrevive (A1).
- *Segredos, rede, custo (`R-CUSTO`).* O diff não traz rede, segredo nem dependência nova, e não muda workflow.

**A1 em prosa.** Evidência: `scripts/suite-paralela.py:535`-`:536`. Os testes de `:279`-`:320` conferem o código de saída, a última linha do stdout e o stderr, mas não a ordem entre a escrita do resumo e o veredito. Caminho: não há, hoje. O `except Exception` contém qualquer erro do resumo, e "resumo indisponível" vai para o stderr. Uma regressão futura que estreite o `except` e ponha o resumo antes do veredito, porém, voltaria a sumir com os erros da guarda (ameaça (b) do modelo) e só o AB-2 a pegaria pelo `except`. Severidade: informativa. Correção mínima: no AB-1 ou no AB-2, conferir que o arquivo de resumo é escrito depois da linha do veredito, por exemplo comparando a ordem num log comum. Esforço: P. Dono: tech-lead.

**Evidência própria em 44617ea (clone limpo em `$TMPDIR`):** `python3 -m unittest -k resumo -k orquestrar_no_processo -k guarda_reprova -k grupo_do_ci tests.test_suite_paralela` deu `Ran 11 tests in 11.278s`, `OK`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do diff e do modelo de ameaças, os testes acima e três mutantes. Não estão no PATH, e nada foi instalado (`R-CUSTO`): `gitleaks`, `zizmor`, `actionlint`, `semgrep`, `osv-scanner`, `trivy`. O diff não muda workflow, dependência nem shell.
