---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-adotar-vermelho
commit: 3f526e8b98a26e7e35d2b6ee5706e98dae687841
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0478 adotar o teste vermelho de outro item (E21.4)

Escopo: `tests/test_teste_vermelho_alheio.py`, as invariantes novas em `tests/config.json` e os textos apontados (`teste-vermelho-alheio.md`, `autor-ate-o-merge.md`, `engineering-practices`, `qa-testing`, `agents/qa-engineer.md`). Sem suíte local; a bateria é o check-run `bateria` do PR.

## Achados
- A1 (recomendado) tests/test_teste_vermelho_alheio.py:55 · `test_invariante_reprova_o_texto_sem_a_condicao` só afirma que algum invariante deixa de casar; não prova que é o da condição 2. Conferir que o faltante cita "proibido apagar" tornaria o teste específico.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Condição 1 (PR próprio e pequeno, prioridade, parecer do QA, nunca misturado, PR parado espera) | `test_as_duas_condicoes_do_dono_estao_no_texto` | cada um dos 5 trechos | passa; mutante M3 morre |
| Condição 2 (proibido apagar/pular/afrouxar, QA explica, mutantes morrem) | idem | cada um dos 4 trechos | passa; M1 e M2 morrem |
| Autor, tech-lead e QA leem o apontamento | `test_texto_lido_pelo_autor_tech_lead_e_qa_aponta_o_detalhe` | 3 arquivos | passa |
| "Vira cartão" sai da dívida pré-existente | `test_qa_nao_manda_mais_o_vermelho_para_cartao` | linha da skill | passa; M4 morre |
| Invariantes protegem as condições, com regra e porque | `test_invariantes_protegem_as_duas_condicoes` | mínimo 8 trechos (hoje 8), motivo `R-QA` | passa; M5 morre |
| Ramo de falha: texto sem a condição 2 reprova invariante | `test_invariante_reprova_o_texto_sem_a_condicao` | texto sem a condição | passa (ver A1) |

## Provas
- Testes do módulo: `python3 -I -m unittest discover -s tests -p test_teste_vermelho_alheio.py` → `Ran 5 tests ... OK`. Invariantes e modelos: `test_forge.py -k nvarian` → 2 OK; `test_modelos_projeto.py` → 20 OK.
- Vermelho: `forge-testes --vermelho <base>` não devolveu saída no prazo (sem veredito, não vale como vermelho). Feito à mão numa cópia em `$TMPDIR` com `agents`, `skills` e `tests/config.json` da base 0c47762a e o teste novo: `Ran`, 3 FAIL e 2 ERROR (arquivo `teste-vermelho-alheio.md` ausente; "0 not greater than or equal to 8"; "'vira cartão' unexpectedly found"; `teste-vermelho-alheio.md` não encontrado em `autor-ate-o-merge.md`). Os 5 testes caem na base.
- Mutação manual no texto e na config (cópia descartável), um por condição:
  - M1 tira a linha "É proibido apagar": 2 falhas (texto e invariantes), morto.
  - M2 tira a linha "Os mutantes daquele trecho": 4 falhas, morto.
  - M3 troca "Nunca se mistura ao PR parado": 2 falhas, morto.
  - M4 tira "o time adota o conserto" da skill: 1 falha, morto.
  - M5 remove um invariante da config: 1 falha, morto.
  - 5 de 5 mortos.
- Merge: o remoto avançou só com pareceres (review e segurança); trazido por merge, sem conflito.
