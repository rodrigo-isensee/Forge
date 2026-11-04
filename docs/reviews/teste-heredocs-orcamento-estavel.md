---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/teste-heredocs-orcamento-estavel
commit: a97ea358e0bde9f726e6eb1f41f0849e7fdaa23e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-04
---
# Review: versao-033 (E23 TESTE-HEREDOCS-ORCAMENTO-ESTAVEL)

## Achados
- A1 (recomendado) tests/test_hooks.py:646 · O teto de razão 6 (k=3) pega o quadrático puro (razão 9) mas não o parcial: o mutante "soma relendo" sobrevive (1,7/0,6 s). Aceito, o teto absoluto de metade do prazo segue; registre no docstring.
- A2 (recomendado) tests/test_hooks.py:946 · O controle recusa por outra regra (stderr R-), caminho um pouco diferente do caso grande; a razão mede também essa diferença. Folga de 2x sobre as medidas (2,6 a 3,0) cobre; reavalie se a razão subir.

## Parecer
Aprovado. Diff lido por inteiro (4 módulos de teste, só testes, sem hooks/ nem PROTEGIDOS); changelog.d presente.

- Regressão quadrática: a razão de CPU entre o caso e um controle k vezes menor, medida na mesma execução, com teto (k+k²)/2 = 6, não depende da carga. O quadrático puro dá 9 e reprova; o autor provou a morte em e23-mutante.sh (rc=0). O mutante sutil que sobrevive é lacuna aceitável: o custo extra é de fator constante, não explode, e o teto absoluto de limite/2 e o vigia de prazo seguem de rede.
- Estabilidade: CPU de filhos (resource) exclui a espera da fila; razão de duas medidas de 0,5 a 0,7 s varia pouco sob carga; folga de 2x sobre 2,6 a 3,0. Falso vermelho é improvável. Falso verde só na faixa sutil (A1). Sem `resource` cai na parede (Windows), como antes.
- Vigia de prazo: prova o corte pelo sono do passo lento (alarme de 3 s) mais a CPU; sem parede. Passa também quando o alarme vence antes do passo lento (sono None), coerente.
- Teto por PR: 192 linhas contadas (numstat: 14+8, 6+2, 86+53, 17+6), acima de 150, com linha `teto: excedido, 192 linhas` no corpo. Aceito: um comportamento só (estabilidade dos testes de tempo), a refatoração de test_hooks (helper custo_do_caso e _formas_de_heredocs) não se divide sem deixar a base com dois estilos de medida; sem hooks/ nem PROTEGIDOS, então a exceção vale.
- Falso de git/gh: não há no diff. Teste de ausência: não há.

Provas: módulos curtos rodados no head a97ea35, load 3 a 6: test_hooks_volta_propriedades 9 testes OK (102 s), test_fechar_orfao 18 OK, test_fechar_corrida_rotulo 7 OK. test_hooks (17 min) não rodado por mim, fica para o QA (suíte inteira, D-5).
