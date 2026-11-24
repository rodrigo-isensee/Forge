---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0480-d3-teste-enfraquecido
commit: 8daa161194a94fffbeba29e5a1a087aa0a9343fb
parecer: reprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA por delta: v0481 (D3, catraca recusa teste afrouxado; PR #867), de e7a71a8e a 8daa1611

## Achados
- A1 (bloqueante) tests/test_catraca.py:777 · o delta fez D3B1 e D3B5 (spec -2) sobreviverem: `assert 1` em test_d agora é asserção vazia (_vacua) e não conta; trocar por asserção com nome, ex. `assert self`, e reprovar o mutante.

## Delta contra o parecer anterior
- A1 anterior (vermelho rc 2, erro na base por regra_testes_afrouxados): corrigido; o teste ganhou asserção de raiz e a base falha por asserção.
- Regressão nova: mutantes que morriam em e7a71a8e passam a sobreviver em 8daa1611 (provado nos dois commits, abaixo).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| D3: asserção só de constantes não conta | test_assercao_so_de_constantes_nao_conta | assert True, assertTrue(1), vácuo renomeado | prova, passou |
| D3: na volta só barra o valor que a branch trocou | test_valor_que_a_base_trocou_e_entrou_por_merge_depois_da_aprovacao_nao_barra, test_volta_que_restaura_o_valor_da_base_barra_so_pela_perda_dura | merge da develop depois da aprovação | prova, passou |
| D3: acréscimo, ajudante e arquivo fora de tests/ passam | test_acrescimos_ajudante_e_arquivo_fora_de_tests_passam | a própria catraca fora da comparação; só `def test_*` | passa, mas não mata D3B1 e D3B5 (A1) |
| Demais critérios do parecer anterior | mesmos testes | n/a | inalterados, passam |

## Cenários e resultado real
Vermelho (`bin/forge-testes --vermelho aabc476c5dbad3b3efced688e578bb5c71c5f722 --modulos tests.test_catraca`):

    contagem: não prova (passa na base)=387; prova (API ausente)=8; prova (asserção)=13
    rc=0

Sem veredito não há mais: o A1 anterior sumiu (de 17 provas para 21).

Mutação (`bin/forge-mutante --processos 4 --base e7a71a8e2f87ef83fc7cb3708396ac05e87ba65d` nas 9 specs de tests/mutantes/v0480-d3-teste-enfraquecido-*.json; "apoio de teste no diff: todos os mutantes entram"), rc=1:

    base=e7a71a8e2f87 mb=e7a71a8e2f87 rev=8daa161194a9
    D3B1 · sobreviveu · tests/catraca.py:750
    D3B5 · sobreviveu · tests/catraca.py:709

Os demais morreram (D3C2, D3C4, D3E5, D3E8, D3F1 e D3F7 por erro do teste declarado, aceito pela regra do controle verde); os das specs -8 e -9 (D3H1 a D3H7) morreram. Prova de regressão: a spec -2 sozinha em e7a71a8e (cópia limpa) dá D3B1 e D3B5 `morreu`; em 8daa1611 dá `sobreviveu`.

CI: a suíte inteira roda no CI do PR; não refeita aqui.
