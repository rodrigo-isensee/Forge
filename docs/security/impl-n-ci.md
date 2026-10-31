---
tipo: revisao-seguranca
contrato: 1
pedido: impl-n-ci
branch: melhoria/impl-n-ci-c2
commit: 40472ddba9cf8d420f42b8518f2d6f81c147ec14
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-31
---
# Review de segurança: IMPL-N-CI, branch c2 (E1.3, rodada 1)

Diff lido: `234dbe0..40472dd`. Revisão estática e local, em paralelo ao code review, contra o modelo de ameaças `docs/security/ameacas/n-ci.md` (C-6 a C-12, AB-1 a AB-7).

**O que a branch entrega:** a primeira metade do E2 do pedido (item 55 d), a medida no resumo do passo do CI e no título do `::group::`: as unidades mais lentas, a soma, a maior unidade, o desequilíbrio e os módulos sem peso. A proteção do veredito (C-6 a C-8) ficou para a c3, pela divisão decidida pelo Jarvis em 2026-10-30 15:39.

**M14 (`agents/tech-lead.md:19`):** cumpre. Contam `scripts/suite-paralela.py` 44 e `tests/test_suite_paralela.py` 73, total 117 linhas, abaixo de 150, sem exceção de teto. Ficam fora `changelog.d/` e os pareceres. A branch não toca `hooks/` nem caminho de `PROTEGIDOS`. Comportamento, um só: a medida no resumo e no título do grupo, que o pedido trata como um item.

## Gatilhos
Controles do Forge (`R-SEGURANCA`): `scripts/suite-paralela.py` decide o veredito do portão no pre-push e no CI.

## Achados
- A1 (recomendado) scripts/suite-paralela.py:515 · O resumo sai antes do veredito e só o `OSError` é contido. C-6, C-7 e C-10 chegam na c3, e o AB-2 in-process (tests/test_suite_paralela.py:254) suja o resumo real. Condição: a c3 entra na develop antes da promoção para a homolog.

## Detalhe dos achados
**O que foi conferido.**
- *O veredito não depende do código novo.* `montar_resumo` (`scripts/suite-paralela.py:420`) só é chamado dentro de `publicar_no_ci` e só quando `GITHUB_STEP_SUMMARY` existe. No pre-push (sem a variável) nada do código novo roda. `ler_pesos` passa a ser lido uma vez (`:478`) e o mesmo dicionário vai para `repartir` e para o resumo: a divisão continua função da árvore (C-12, AB-7, `test_divisao_nao_depende_da_execucao_anterior`). O resumo não é lido de volta, não alimenta o carimbo K6 nem a gravação de pesos.
- *C-8 (relatório ausente ou malformado).* O cálculo tolera `None`, `duracoes` que não é dicionário, chave fora das unidades, valor não numérico, `NaN` (cai no `v >= 0`) e `Infinity` (vira `inf` no texto). A divisão por `n` usa `n ≥ 1`, porque sem módulo o script sai antes, e `media or 1` evita a divisão por zero. Exercitei `montar_resumo` com esses relatórios e com durações zeradas, numa cópia em `$TMPDIR`: nenhuma exceção e nenhum `::` no texto.
- *C-9, AB-4 (só nomes e números).* As unidades do resumo são filtradas por `k in nomes`, e `nomes` sai de `partes`, que vem de `modulos()` (só identificadores). O título do grupo (`:395`) leva os mesmos nomes, e um identificador não carrega `::` nem quebra de linha. A saída dos testes não entra no resumo. `test_resumo_so_leva_nomes_e_numeros` faz um teste imprimir `::error::`, `::stop-commands::`, `/etc/passwd` e uma cadeia com cara de token, e confere que nada disso chega ao resumo. As linhas `processo i: ...`, que já existiam, continuam com os mesmos campos.
- *C-11, AB-6 (tamanho).* `LIMITE_LENTAS, LIMITE_SEM_PESO = 10, 20` (`:59`), com "e mais N" (`lista_curta`). Coberto por `test_resumo_limita_as_unidades_sem_peso` (27 módulos: 20 nomes e "e mais 10"; 10 lentas).
- *Sem a variável, nada é escrito.* `test_sem_github_step_summary_nada_e_escrito`.
- *Segredos, rede, custo (`R-CUSTO`).* O diff não traz rede, segredo nem dependência nova, nem muda workflow. O resumo de um repositório público é público, e o texto novo só tem nomes de módulo e números.

**A1 em prosa.** Evidência: `scripts/suite-paralela.py:515` (`publicar_no_ci` antes do cálculo do veredito, `:516`-`:520`); `:452` (só `OSError`); `tests/test_suite_paralela.py:254` (`orquestrar()` no próprio processo, sem tirar `GITHUB_STEP_SUMMARY` e `GITHUB_ACTIONS`). Caminho: não há fuga do portão. Uma exceção fora do `OSError` derruba o script com código ≠ 0, que falha fechado, mas esconde os erros da guarda, que só são impressos depois. A exercitação acima não achou entrada que provoque a exceção. Sem o C-7, o resumo de uma execução reprovada traz números de orçamento sem dizer que reprovou, e o C-10 deixa o brinquedo do AB-2 escrever um bloco no resumo real do CI. Os dois afetam só a integridade de um artefato informativo (A3 do modelo), lido no checkpoint. Severidade: baixa. Correção mínima: a c3 já planejada (C-6 a C-8, e o teste `test_orquestrar_no_processo_nao_escreve_no_resumo_real` para o C-10, já visto em `origin/melhoria/impl-n-ci-c3`). Só não é bloqueante porque a develop não é a release. Se a c3 não entrar antes da promoção da develop para a homolog, o C-6 e o C-7 viram requisito não cumprido do lote. Esforço: P (já feito na c3). Dono: tech-lead.

**Evidência própria em 40472dd (árvore limpa):** `python3 -m unittest -k resumo -k grupo_do_ci -k divisao_nao_depende tests.test_suite_paralela`: `Ran 7 tests in 33.384s`, `OK`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do diff e do modelo de ameaças, os testes acima e a exercitação de `montar_resumo` com relatórios malformados. Ausentes no PATH, nada instalado (`R-CUSTO`): `gitleaks`, `zizmor`, `actionlint`, `semgrep`, `osv-scanner`, `trivy`. O diff não muda workflow, dependência nem shell.
