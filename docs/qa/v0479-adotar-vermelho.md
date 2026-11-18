---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-adotar-vermelho
commit: 60782c174474ecc203b5a01defcb7a58a038785c
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0478 adotar o teste vermelho de outro item (E21.7, revalidação)

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

## Revalidação E21.7 (head 60782c17, delta de 3f526e8)
Delta pelo `forge-check parecer delta`: `teste-vermelho-alheio.md`, `tests/config.json` (+4 invariantes: critério herdado da base, formas proibidas, aviso ao tech-lead, linha bloqueante) e `tests/test_teste_vermelho_alheio.py` (+3 testes). O A1 acima segue recomendado, não bloqueia.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Vermelho é alheio só se já cai na base (A1 da segurança) | `test_criterio_de_alheio_e_so_herdado_da_base` | texto antigo "ou cai em código que o diff não toca" | passa; morre com o critério antigo |
| Formas proibidas, autor e tech-lead são invariantes (A2) | `test_cada_trecho_tirado_do_texto_reprova_um_invariante` | 3 trechos | passa; morre sem as formas proibidas |
| Config e texto não se afastam | `test_texto_inteiro_casa_todos_os_invariantes` | invariantes da skill | passa; morre nos 4 mutantes novos |

## Provas da revalidação
- `python3 -I -m unittest discover -s tests -p test_teste_vermelho_alheio.py` → `Ran 8 tests ... OK`.
- Vermelho à mão (o `forge-testes --vermelho` estourou 120 s: sem veredito, não vale): cópia de 60782c17 com a skill de 3f526e8 → `FAILED (failures=2)` (critério herdado da base; texto casa invariantes).
- Mutação manual na skill (cópia em `$TMPDIR`), um por invariante novo: volta o critério antigo, 2 falhas, morto; tira as formas proibidas, 2 falhas, morto; tira "avisa o `tech-lead`", 1 falha, morto; tira a linha do achado bloqueante, 1 falha, morto. 4 de 4 mortos.
- Merge: o remoto avançou só com o parecer de segurança (915f67a7); trazido por merge, sem conflito. Suíte inteira: check-run `bateria` do PR.
