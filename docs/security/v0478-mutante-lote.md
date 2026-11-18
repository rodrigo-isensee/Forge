---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-mutante-lote
commit: b11631b2e9e536b11b918c470f7e80c9147b83ec
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0478 mutante-lote (E17.3)

Gatilhos: controle (bin/forge-mutante, cuja `analisar` é a mesma que a catraca usa em MUTANTES-SPEC-HOOKS, tests/catraca.py:864).

Diff lido: `0c47762a..b11631b2` em bin/forge-mutante, tests/test_forge_mutante.py, tests/mutantes/*.json, skills/qa-testing/SKILL.md, changelog.d/v0478-mutante-lote.md. Suíte: não rodada localmente (brief E17.3); rodei só as sondas abaixo, contra cópias do módulo na base e no head.

## Achados
- A1 (bloqueante) bin/forge-mutante:596 · cruza(nova) só exige uma ocorrência do trecho dentro do nó: um trecho genérico (ex.: `.startswith(`) isenta toda condição nova do arquivo que o contém, e a catraca (tests/catraca.py:864) passa a aceitar guardas de controle sem mutante. Exigir que toda ocorrência caia em condição nova de mesmo texto.
- A2 (recomendado) tests/test_forge_mutante.py:1 · falta o caso ilegítimo do corpus: isenta de trecho genérico com duas condições novas de textos diferentes deve sair `sem mutante` nas duas (S1 vira teste).

## Sondas
- S1 · analisar("hooks/h.py") com 2 condições novas distintas `x.startswith('adm')` e `y.startswith('../') or y.startswith('/')`, isenta trecho `.startswith(` · espera: sem mutante nas 2 (como na base 0c47762a) · obtido: head b11631b2 dá `isenta` nas 2
- S2 · analisar com a forma proposta (A1) nos casos S1 e `x is None or y is None` repetida 2 vezes · espera: S1 sem mutante nas 2; repetida isenta nas 2 · obtido: S1 sem mutante nas 2; repetida isenta nas 2

## Detalhe dos achados
**A1.** Evidência: bin/forge-mutante:596-598 (`dados.find(trecho, ini)` e só o fim dentro do nó) chamado de bin/forge-mutante:645 com `nova=True`; a isenta da condição nova não consulta `usadas`, então uma isenta cobre um número ilimitado de condições. Antes, o trecho tinha de ser único no arquivo, o que impedia um trecho genérico de casar. Caminho de ataque: o autor de um PR que muda guardas de um hook ou do `bin/` (código de controle, classe C) declara uma isenta com motivo plausível e um trecho comum a várias guardas novas; a catraca do CI (MUTANTES-SPEC-HOOKS) só lista faltas e não imprime as isentas, então o PR fica verde com N guardas sem mutante, exatamente o que a regra existe para impedir (o autor escolhendo o que prova). A saída do `--cobertura` mostra uma linha `isenta` por condição, mas nenhum hook, pre-push nem CI a chama. Resposta à pergunta do autor: sim, uma guarda nova pode escapar de mutante por isso (S1). Severidade: média (afrouxa controle de integridade do processo; sem dado nem segredo). Correção mínima, que não afrouxa e mantém o caso legítimo do teste `test_isenta_vale_para_cada_condicao_nova_com_o_mesmo_trecho`: em bin/forge-mutante:645 passar `nova=[(c[3], c[4]) for c in mudadas if c[0] == texto]` (os nós das condições novas de mesmo texto) e, em `cruza`, com `nova`, aceitar só se o trecho ocorre ao menos uma vez dentro de [ini, fim] e **toda** ocorrência do trecho no arquivo cai inteira dentro de um desses nós. A isenta passa a valer para as cópias da mesma condição, nunca para condições de texto diferente nem para o trecho que aparece fora delas (cópia antiga fora do hunk ou comentário: falha fechada, o autor alonga o trecho). Protótipo conferido em S2. Esforço: P. Dono: tech-lead (autor do E17.1). Com essa forma, a mudança deixa de afrouxar e não precisa do OK do dono para isso; mantida a forma atual, só segue com `riscos-aceitos` aceito pelo dono (R-DECISAO).

**A2.** Corpus de ilegítimos: o teste novo prova só o caso legítimo (mesmo texto repetido). Correção: um teste com S1 (duas condições de textos diferentes, trecho comum) esperando rc 1 e `sem mutante` nas duas. Dono: tech-lead ou qa-engineer.

Sem achado nas demais partes: `--ids` (escolher, bin/forge-mutante:1044) recusa id vazio ou não declarado antes de rodar e imprime `só os ids:`, então a rodada parcial fica visível no parecer de QA; `isenta velha` sai rc 1 em vez de 2 (segue não zero); `isenta fora do diff` só ignora isenta da spec do merge-base que não cruza nada, e isenta que não cruza não libera condição alguma; `isentas_na_base` lê pelo git com caminho da própria spec e falha fechada (conjunto vazio).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff e sondas locais com a biblioteca padrão sobre cópias da base e do head; nenhuma varredura de segredo pertinente ao diff (só código de ferramenta e specs).
