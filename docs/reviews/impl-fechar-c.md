---
tipo: review
contrato: 1
pedido: impl-fechar-c
branch: melhoria/impl-fechar-c-c4
commit: 0ffbc737bc1227d11134b5214f85b56d85c021dd
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-31
---
# Review: impl-fechar-c (branch c4)

Etapa E1.2, revisor de outra instância (D-ETAPAS-INST = A). Diff lido: `234dbe0..c03922e` (2 commits: correção e fragmento).

## Item entregue
E4 do pedido, FECHAR-B-REC-REVIEW item 3, pela opção B' do modelo de ameaças (SEC-FECHARC-1): com o rótulo ausente, a execução da `catraca` vista vira candidata (`run_cand`); uma leitura do rótulo logo depois da leitura dos checks a promove a velha (`run_antes`) se o rótulo continua ausente, ou a descarta se ele já está lá. Leitura que falha conta como ausente (só atrasa, nunca libera). O texto de `docs/fechamento-integrador.md` (seção da Catraca do rótulo) passa a dizer a regra nova e o caso do `cancel` antes do rótulo.

Conferido o fluxo do caso AB-C4-1 à mão: a volta 1 promove o run 1; a volta 2 vê o run 2 e a leitura posterior o descarta; a volta 3, com o rótulo, trata o run 1 como velha pendente e o run 2 em `fail` para na hora. O merge continua exigindo tudo `pass` e o head preso; descartar candidata só leva à rede de 10 leituras ou ao prazo.

## M14 (R-REVIEW, agents/tech-lead.md:19)
Um comportamento (quando a execução vira velha). 133 linhas depois da volta do QA (`bin/forge-fechar` 15+3, `tests/test_fechar_corrida_rotulo.py` 111, dos quais 32 do delta; `tests/test_fechar_espera_catraca.py` 2+2), abaixo de 150. Sem `hooks/` nem `PROTEGIDOS`. Cumpre.

## Checklist
1. Nem mais nem menos. 2. Falha fechada mantida; nenhuma chamada que escreve (o teste C4-5 confere o texto do script). 3. Legível; o comentário da leitura nova explica as três saídas. 7. Quatro cenários (nova reprova, nova passa e mescla presa ao head, descartada sem velha nunca mescla, leitura que falha nunca mescla) mais o de texto. A mudança em `test_fechar_espera_catraca.py` (rótulo na 3ª leitura) só acompanha a leitura a mais por volta; os cenários dele seguem os mesmos e verdes. 9. Commits limpos.

Ferramentas: módulos `tests/test_fechar*.py` rodados na worktree, sem bytecode: `Ran 207 tests in 111.969s` / `OK (skipped=1)`. Shellcheck: não instalado aqui; fica com o CI, pendência registrada.

## Achados
- A1 (recomendado) bin/forge-fechar:691 · ler | grep -qx com pipefail: se o grep sai antes do fim da escrita, o SIGPIPE faz rótulo presente contar como ausente; é o lado fechado (só atrasa) e a mesma forma da leitura da linha 677; ler para uma variável antes do grep tira o caso.

## Revalidação (delta)
`forge-check delta --parecer` sobre o parecer anterior (`c03922e..0ffbc73`) listou dois arquivos, ambos lidos: `tests/test_fechar_corrida_rotulo.py:34-45` e `:84-103` (+32: o auxiliar `rotulo_lido`, que sequencia as leituras do rótulo, e os testes AB-C4-4 e AB-C4-7: falha só na leitura posterior com o rótulo presente depois, e rótulo retirado na espera sem a candidata descartada virar velha; ambos terminam com `sem_merge`, então a falha fechada fica provada) e `tests/mutantes/impl-fechar-c-c4.json:1-113` (spec de mutantes, só dado de teste, com os dois testes novos ligados aos mutantes C4-1 e seguintes). Nenhuma linha de `bin/` mudou. Já lido e mantido: o código de `bin/forge-fechar`, o texto de `docs/fechamento-integrador.md`, o fragmento e o resto dos testes.

## Parecer
Aprovado. A recomendação A1 não devolve.
