---
tipo: qa
contrato: 1
pedido: fechar-master
branch: melhoria/fechar-master
commit: ac8e3de3ecf908d37d52416b79b015dbfb13803a
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-23
---
# QA: fechar-master

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: `--ref` main, master, develop, homolog recusado antes de qualquer ação, com e sem `--limpar` | `test_fechar_longas.test_branches_longas_fixas_sao_recusadas_com_e_sem_limpar`; sonda CT-01 | `master` (a lacuna do A1 do QA da LIMPEZA-REGRA); refs locais e remotas e chamadas ao gh/check inalteradas | passou |
| E1: `--ref` igual à branch de integração do `CLAUDE.md` recusado | `test_branch_de_integracao_do_claude_md_e_recusada`; sonda CT-02 | branch fora da lista fixa (`trunk`) | passou |
| Sem a linha no `CLAUDE.md`, só a lista fixa | `test_sem_a_linha_no_claude_md_branch_de_trabalho_segue_valida` | ausência da linha | passou |
| Branch de trabalho não é barrada pela linha | `test_claude_md_com_a_linha_nao_barra_a_branch_de_trabalho`; sonda CT-03, CT-04 | `melhoria/x` com a linha presente | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_fechar_longas tests.test_fechar`: 84 testes, OK.
- Sonda de ponta a ponta (repositório com remoto local, `HOME` em `$TMPDIR/qa-fecharmaster/`, script da branch, `gh` falso de `tests/test_fechar.py`; sonda em `$TMPDIR/qa-fecharmaster/sonda.py`):
  - CT-01: `--ref` main, master, develop e homolog, com e sem `--limpar` (8 casos): rc=1, "a branch da entrega não pode ser <ref> (R-FLUXO, R-VERIFY)", `branch -a`, `for-each-ref` e `ls-remote` idênticos, zero chamadas a gh/check.
  - CT-02: `--ref trunk` (linha "Branch de integração: `trunk`" no `CLAUDE.md`), com e sem `--limpar`: rc=1, mensagem própria, nada mudou.
  - CT-03: `melhoria/x` com PR mesclado + `--limpar`: rc=0, branch local e remota apagadas.
  - CT-04: `melhoria/x` no fluxo completo (squash): rc=0, branch apagada.
- Vermelho antes do verde: com `bin/forge-fechar` da base (139a3b4) e os testes do HEAD, `tests.test_fechar_longas` dá FAILED (failures=2: `test_branches_longas_fixas...` e `test_branch_de_integracao...`); os dois de branch de trabalho passam nos dois lados, como esperado. `forge-testes --vermelho 139a3b4` rodou os módulos mas estourou o meu prazo externo (rc=124, sem veredito); o vermelho vale pela execução manual acima, numa cópia em `$TMPDIR`.
- Mutação (o autor não declarou spec em `tests/mutantes/`; lista do QA, uma por guarda mudada: lista fixa, comparação, leitura do arquivo, padrão da linha, mensagem), `bin/forge-mutante`:
  ```
  M1 · morreu · bin/forge-fechar:56
  M2 · morreu · bin/forge-fechar:62
  M3 · morreu · bin/forge-fechar:59
  M4 · morreu · bin/forge-fechar:61
  M5 · morreu · bin/forge-fechar:62   (rc=0)
  ```
- Fora do escopo, só observação: o formato da linha da branch de integração (primeira palavra entre crases na primeira linha que cita "integração") segue no cartão INTEGRACAO-FORMATO.
