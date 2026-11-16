---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-specs-conferidas
commit: 0064a82ee0216c00f2281e29ea6695c224d73445
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: v047-specs-conferidas

Pedido v047, etapa E2.282, sobre a entrega E2.215 (classe AR-12). Base `e13aed85`, head revisado `0064a82e`. Revisão por instância que não fez a entrega.

## Gatilhos
`R-SEGURANCA`: a entrega mexe na ferramenta de mutação que mede os testes das guardas (`bin/forge-mutante`) e em specs que mutam controles do Forge (`hooks/conformidade.py`, `hooks/_comum.py`, `hooks/parecer.py`, `hooks/pesado.py`, `hooks/agentes.py`, `.githooks/pre-push`, o pre-push do modelo de projeto e o `ci.yml`). Retirar ou desalinhar um mutante de guarda enfraquece a prova de que a guarda é testada.

## Resumo
- `--conferir --todas` (`bin/forge-mutante:689`, `:969`) só lê objetos do git: `resolver` com `--end-of-options`, `ls-tree -z` no sha resolvido, `git show sha:arquivo`, spec limitada por `MAXIMO_DA_SPEC` e validada por `validar_spec`. Não executa teste nem código da spec; o cache em `texto_no_commit` (`:657`) é por sha resolvido e arquivo, imutável. Sonda de injeção de opção pelo `--rev` saiu 2 sem gravar arquivo.
- Os 47 mutantes retirados (incluindo as specs `lote-l10` e `lote-fechar2-2` inteiras e `lote-m8-hook:M4`, `M5`, `M11` do pre-push e `I57`, `I58`, `I169` do `hooks/agentes.py`): o `de` de cada um aparece 0 vez na fonte da base e do head. A guarda já tinha saído em entregas anteriores; a retirada não reduz a cobertura de nenhum controle vigente.
- As specs alinhadas das guardas (conformidade, comum, parecer, pesado, ci.yml, os dois pre-push) mantêm o mesmo sentido da guarda declarada: a troca nova nega a mesma condição na forma atual da linha.
- A catraca `ConferirTodas` (`tests/test_forge_mutante.py:1272`) chama a ferramenta com o interpretador isolado e cobra igualdade nos dois sentidos com a lista de pendentes: linha nova na lista sem desencontro real reprova, e spec nova fora do lugar reprova.

## Achados
- A1 (recomendado) hooks/conformidade.py:2813 · o mutante fix-037-uniao-seg:M5 (falha fechada da prova da suíte fora de projeto) sobrevive: o teste declarado não chega a esse ramo; cartão ao qa-engineer com um teste que alcance a recusa por erro interno com o alvo citando a prova (R-QA).
- A2 (recomendado) .githooks/pre-push:587 · o mutante lote-m8-hook:M9 (plano montado sem o isolamento do interpretador, classe AR-5) sobrevive: o teste do módulo falso não distingue; cartão ao qa-engineer para um teste que mate a troca (R-QA).
- A3 (recomendado) tests/fixtures/mutantes-pendentes.txt:13 · seguem na catraca, com o trecho repetido, 8 mutantes de guarda de segurança (lista no detalhe); enquanto ficam ali, a mutação dessas guardas não roda; dar contexto ao `de` com prazo (R-QA).

## Sondas

## Detalhe dos achados
**A1.** Evidência: `hooks/conformidade.py:2813`, spec `tests/mutantes/fix-037-uniao-seg.json:44`; o commit `df4e2bbc` registra a sobrevivência. Caminho: um refactor que desligue esse `if` (recusa da prova da suíte quando a decisão interna dá erro) passaria pela suíte, e um erro interno do hook com o alvo citando a prova deixaria de falhar fechado. Severidade: baixa (lacuna de teste preexistente, não vulnerabilidade; o defeito não existe hoje). Correção mínima: teste de comportamento que provoque a exceção dentro de `decidir` com o alvo citando a prova e espere a recusa da prova. Esforço P. Dono: `qa-engineer`.

**A2.** Evidência: `.githooks/pre-push:587`; o commit `2124eec7` registra a sobrevivência. Caminho: sem o isolamento, um módulo plantado em `bin/` da branch decidiria o plano de testes do envio (classe AR-5). Severidade: baixa (o pre-push é checagem local; o CI roda a bateria inteira e é o portão). Correção mínima: o teste do módulo falso no plano precisa reprovar quando o isolamento sai. Esforço P. Dono: `qa-engineer`.

**A3.** Evidência: `tests/fixtures/mutantes-pendentes.txt`. Lista completa dos mutantes de guarda de segurança que seguem pendentes: `lote-fc-seguranca-1:M5`, `s8-verde-protegido:M3`, `hk3-parecer-pasta-14:M103`, `hk3-parecer-pasta-14:M104`, `hk3-parecer-pasta-14:M105`, `hk3-parecer-pasta-15:M106`, `pesado-trava-fundo:M4`, `pn4-decisao-aprovacao:M2`. Caminho: não há ataque direto; a ferramenta recusa o `de` repetido (falha visível, não aprovação falsa), mas a guarda fica sem medida de mutação até o alinhamento. Severidade: informativa. Correção mínima: dar mais contexto ao `de` de cada um, sair da lista no mesmo commit. Esforço P. Dono: `tech-lead` (dono da E2.215) ou o `qa-engineer`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes do item rodados no clone: `ConferirTodas` e `Conferir` de `tests.test_forge_mutante`, 10 testes OK; `--conferir --todas --rev 0064a82e` saiu 1 com 44 desencontros, iguais às 44 linhas da lista de pendentes. A suíte inteira roda no CI do PR. Ferramentas: leitura estática e o git local; nenhuma varredura externa.
