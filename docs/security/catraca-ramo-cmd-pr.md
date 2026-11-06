---
tipo: revisao-seguranca
contrato: 1
pedido: catraca-ramo-cmd-pr
branch: melhoria/catraca-ramo-cmd-pr
commit: c0124465c1e425a8c799da5ba06dcb4a1b03bd36
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-04
---
# Review de segurança: versao-033 (CATRACA-RAMO-CMD-PR)

Mudança: a catraca (`tests/catraca.py`, modo pareceres) passa o `ramo` do PR a `pareceres_que_nao_aprovam` e ao `cmd_pr` do `bin/forge-check`, que só contam pareceres com `branch:` igual ao ramo; sem nenhum do tipo exigido, sai `sem parecer ... com branch:` (falha fechada). O `forge-check pr` manual (sem `ramo`) não muda.

## Gatilhos
R-SEGURANCA: a entrega mexe num controle do Forge (a catraca de pareceres do CI).

## Achados
- A1 (recomendado) bin/forge-check:484 · Pré-existente, não piora: o ramo do PR (head_ref) é escolhido pelo autor; num PR de fork com o nome de uma branch já mesclada, os pareceres dela na develop contam. Hoje só o commit_vale segura; vale exigir o repositório do head igual ao da base.

## Detalhe dos achados
Análise da pergunta "piora em relação à base?":

- **Parecer forjado com `branch:` do próprio ramo.** Já era possível antes: `pedidos_da_branch` (bin/forge-check:484) já filtrava por `branch == ramo`, e o `cmd_pr` escolhia o mais recente do pedido sem olhar a branch. Agora o conjunto de candidatos só encolhe (filtro a mais, nunca a menos). A defesa contra forja continua a mesma: autoria (local), `commit_vale` (bin/forge-check:459) e o review humano do PR. Não piora.
- **Melhora:** antes, um `aprovado` de outra branch do mesmo pedido, vencendo no desempate (data, caminho), cobria um `reprovado` da própria branch; agora não cobre (tests/test_catraca.py, `test_e11_reprovado_da_propria_branch_barra_com_aprovado_de_outra_vencendo`). O que deixa de barrar é só o `reprovado` de outra branch, que é sobre outro código (o defeito do #437).
- **Casar o parecer de outra branch pelo nome.** A comparação é igualdade exata de string (bin/forge-check:738, tests/catraca.py:1124), sem normalização de caixa, Unicode ou prefixo; o frontmatter só tira espaços das pontas (bin/forge-check:187), e o git não aceita espaço nem controle em nome de ref. Prefixo, maiúsculas, `/`, espaços e homóglifos não casam com outro nome. Só o nome idêntico casa: é o A1, pré-existente (o `pedidos_da_branch` já usava o mesmo critério), severidade baixa, mitigado pelo `commit_vale` (o `commit:` do parecer alheio tem de bater com o head fora de LIVRES) e pelo review humano do PR. Correção mínima (fora deste pedido): na etapa do workflow, recusar quando `github.event.pull_request.head.repo.full_name` difere de `github.repository`, ou passar isso à catraca. Esforço P. Dono: devops-engineer.
- **Injeção em `run:`.** O workflow não muda neste diff; `github.head_ref` entra por `env:` (`HEAD_REF`, .github/workflows/ci.yml:203) e é usado entre aspas, em `--ramo="$HEAD_REF"` (ci.yml:213): sem interpolação de expressão no script nem injeção de opção. O script e o `bin/forge-check` rodam da base (ci.yml:208-211; tests/catraca.py:1075), então o PR não troca o `cmd_pr` que o julga.
- **Promoções e homolog.** `PROMOCOES` (tests/catraca.py:1084) e o retorno antecipado seguem iguais; a entrada na homolog vinda de outra branch continua exigindo QA, agora o da própria branch (`test_e11_tipo_exigido_so_em_outra_branch_falha_fechado`). Ramo vazio (`HEAD_REF` ausente) filtra por `branch: ""` e falha fechada.

## Riscos aceitos e ferramentas
Sem riscos aceitos. Leitura do diff `origin/develop...c012446`; testes dos arquivos tocados: `python3 -m unittest -k e11 -k outra_branch tests.test_catraca` (6 testes, OK). Não rodados: suíte inteira (D-5, do QA), gitleaks, zizmor e actionlint (diff sem workflow nem segredo).
