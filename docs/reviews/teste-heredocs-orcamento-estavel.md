---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/teste-heredocs-orcamento-estavel
commit: 09e0f132b78bef588c7d6a6b0e931e057a6065fe
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-04
---
# Review: versao-033 (E23 TESTE-HEREDOCS-ORCAMENTO-ESTAVEL)

## Achados
- A1 (recomendado) tests/test_hooks.py:646 · O teto de razão 6 (k=3) pega o quadrático puro (razão 9) mas não o parcial: o mutante "soma relendo" sobrevive (1,7/0,6 s). Aceito, o teto absoluto de metade do prazo segue; registre no docstring.
- A2 (recomendado) tests/test_hooks.py:946 · O controle recusa por outra regra (stderr R-), caminho um pouco diferente do caso grande; a razão mede também essa diferença. Folga de 2x sobre as medidas (2,6 a 3,0) cobre; reavalie se a razão subir.
- A3 (recomendado) tests/test_hooks.py:572 · O lançador reimplementa o `__main__` de hooks/conformidade.py:1995; se o hook mudar a chamada, o teste roda outra (A1 do QA, f989858). Depois: ler o prazo da linha de `_comum` ou trocar o global e seguir por `runpy`.

## Parecer
Aprovado. Diff lido por inteiro (4 módulos de teste, só testes, sem hooks/ nem PROTEGIDOS); changelog.d presente.

- Regressão quadrática: a razão de CPU entre o caso e um controle k vezes menor, medida na mesma execução, com teto (k+k²)/2 = 6, não depende da carga. O quadrático puro dá 9 e reprova; o autor provou a morte em e23-mutante.sh (rc=0). O mutante sutil que sobrevive é lacuna aceitável: o custo extra é de fator constante, não explode, e o teto absoluto de limite/2 e o vigia de prazo seguem de rede.
- Estabilidade: CPU de filhos (resource) exclui a espera da fila; razão de duas medidas de 0,5 a 0,7 s varia pouco sob carga; folga de 2x sobre 2,6 a 3,0. Falso vermelho é improvável. Falso verde só na faixa sutil (A1). Sem `resource` cai na parede (Windows), como antes.
- Vigia de prazo: prova o corte pelo sono do passo lento (alarme de 3 s) mais a CPU; sem parede. Passa também quando o alarme vence antes do passo lento (sono None), coerente.
- Teto por PR: 192 linhas contadas (numstat: 14+8, 6+2, 86+53, 17+6), acima de 150, com linha `teto: excedido, 192 linhas` no corpo. Aceito: um comportamento só (estabilidade dos testes de tempo), a refatoração de test_hooks (helper custo_do_caso e _formas_de_heredocs) não se divide sem deixar a base com dois estilos de medida; sem hooks/ nem PROTEGIDOS, então a exceção vale.
- Falso de git/gh: não há no diff. Teste de ausência: não há.

Provas: módulos curtos rodados no head a97ea35, load 3 a 6: test_hooks_volta_propriedades 9 testes OK (102 s), test_fechar_orfao 18 OK, test_fechar_corrida_rotulo 7 OK. test_hooks (17 min) não rodado por mim, fica para o QA (suíte inteira, D-5).

## Revalidação (09e0f13, volta por delta)

`bin/forge-check delta --parecer docs/reviews/teste-heredocs-orcamento-estavel.md` (rc=0): intervalo a97ea35..09e0f13, delta só em tests/test_hooks.py +9 -1, linhas 570 e 572-579 (o `LANCADOR`). Li só essas linhas e, para conferir, o `__main__` de hooks/conformidade.py:1994-1995, o uso de `PRAZO_DA_LINHA_S` em hooks/conformidade.py:721 e o `LANCADOR_MEDIDO` de tests/test_hooks_volta_propriedades.py:30. O resto do diff fica como "já lido" na rodada de a97ea35.

- Sem vazamento para produção: a troca vive só na string `LANCADOR` de tests/test_hooks.py; o hooks.json roda hooks/conformidade.py direto, e o hook não foi tocado (`PRAZO_DA_LINHA_S = 3.0` segue). No próprio lançador, `producao=True` cai no `runpy` de antes, com o prazo de 3 s; o `LANCADOR_MEDIDO` (vigia de parede, sempre `producao=True`) ainda acha o texto do `runpy` que substitui, então a medida dele não se perde.
- A injeção pega: `bash()` lê o global do módulo em cada linha (conformidade.py:721), e o lançador o troca antes de chamar `executar`, no mesmo módulo importado.
- O teste segue provando o orçamento de CPU: as asserções (razão linear k=3 e CPU < limite/2) não mudaram; alargar a parede da linha só tira o falso vermelho da fila da máquina (bug e23-01), e o teto de conferências e de caracteres segue. O prazo de 3 s de produção continua provado nos testes `producao=True`.
- Prova: `python3 -I -m unittest discover -s tests -p test_hooks.py -k test_muitos_heredocs_recusam_dentro_do_orcamento` no head 09e0f13, uma vez: 1 teste OK em 80,8 s; CPU das formas HEREDOC-DONOS 1,16 a 2,38 s contra limite 5,0 s. test_hooks inteiro não rodado (D-5, o QA já aprovou o delta em f989858).
- Teto por PR: 202 linhas, ainda um comportamento só, sem hooks/ nem PROTEGIDOS; exceção segue aceita, mas a linha do corpo do PR diz 192: corrija para `teto: excedido, 202 linhas, <motivo>` antes do fechamento (numstat: 14+8, 6+2, 95+54, 17+6).

Parecer mantido: aprovado em 09e0f13.
