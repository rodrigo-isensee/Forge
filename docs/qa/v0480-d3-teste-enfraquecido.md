---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0480-d3-teste-enfraquecido
commit: 23026d32d43b1139c5eac2bf3529a8bd2b47ff2b
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA por delta: v0481 (D3, catraca recusa teste afrouxado; PR #867), de 8daa1611 a 23026d32

Delta (`git diff 8daa1611..23026d32`): em tests/test_catraca.py:777, `assert 1` virou `assert self` em test_d. Nenhum outro arquivo de produção ou de teste mudou (os demais são pareceres).

## Delta contra o parecer anterior
- A1 anterior (D3B1 e D3B5 sobreviviam porque `assert 1` é asserção vazia): corrigido; `assert self` conta como asserção com nome, e os dois mutantes morrem.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| D3: asserção só de constantes não conta | test_assercao_so_de_constantes_nao_conta | assert True, assertTrue(1), vácuo renomeado | prova, passou |
| D3: na volta só barra o valor que a branch trocou | test_valor_que_a_base_trocou_e_entrou_por_merge_depois_da_aprovacao_nao_barra, test_volta_que_restaura_o_valor_da_base_barra_so_pela_perda_dura | merge da develop depois da aprovação | prova, passou |
| D3: acréscimo, ajudante e arquivo fora de tests/ passam | test_acrescimos_ajudante_e_arquivo_fora_de_tests_passam | a própria catraca fora da comparação; só `def test_*` | passou; agora mata D3B1 e D3B5 |
| Demais critérios | mesmos testes | n/a | inalterados, passam |

## Cenários e resultado real
Vermelho (`bin/forge-testes --vermelho aabc476c5dbad3b3efced688e578bb5c71c5f722 --modulos tests.test_catraca`), rc=0:

    contagem: não prova (passa na base)=387; prova (API ausente)=8; prova (asserção)=13

Mutação (`bin/forge-mutante --processos 4 --base 8daa161194a94fffbeba29e5a1a087aa0a9343fb` nas 9 specs tests/mutantes/v0480-d3-teste-enfraquecido.json e -2 a -9), rc=0:

    base=8daa161194a9 mb=8daa161194a9 rev=23026d32d43b
    D3B1 · morreu · tests/catraca.py:750
    D3B5 · morreu · tests/catraca.py:709
    (53 mutantes, 53 morreram; nenhum sobrevivente nem sem veredito)

Os de "(erro)" (D3C2, D3C4, D3E5, D3E8, D3F1, D3F7) seguem mortos pela regra do controle verde, como antes.

CI: a suíte inteira roda no CI do PR; não refeita aqui.
