---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-h5-prova-local
commit: c046a44b34066447d9f595b9d31e3679ba2b9fba
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-17
---
# QA: v047-h5-prova-local

## Achados

## Critério → teste → resultado
Obrigação: H5 (E2.642/E2.648 da v047), `forge-mutante --base` roda dos `testes` de cada mutante só os dos módulos do plano do `forge-testes --listar`; sem plano dirigido ou sem teste nos módulos, rodam inteiros.
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| H5: teste fora dos módulos do diff não roda e sai a linha | `LimiteDosModulos.test_teste_fora_dos_modulos_do_diff_nao_roda` | teste vermelho fora do plano não derruba | passou |
| H5: sem plano dirigido (suíte completa) roda inteiros | `LimiteDosModulos.test_sem_plano_dirigido_roda_os_testes_declarados_inteiros` | plano ausente | passou |
| H5: sem teste nos módulos, ou com todos, fica como está | `LimiteDosModulos.test_mutante_sem_teste_nos_modulos_ou_com_todos_fica_como_esta` | conjunto vazio, todos, módulo.Classe | passou |
| H5: listar que falha ou estoura prazo não limita | `LimiteDosModulos.test_listar_que_falha_ou_estoura_o_prazo_nao_limita` | OSError, prazo | passou |

## Cenários e resultado real
- Testes tocados (`python3 -I -m unittest discover -s tests -p test_forge_mutante.py -k LimiteDosModulos`, TMPDIR no ambiente): Ran 4 tests, OK. Suíte inteira: só no CI do PR, não rodada aqui.
- Vermelho antes do verde (`forge-testes --vermelho 73a0ab81`): `vermelho: base=73a0ab8179b3 head=c046a44b3406`; revertidos à base: bin/forge-mutante, changelog.d/v047-h5-prova-local.md; nenhum teste cai no HEAD.
  - test_listar_que_falha_ou_estoura_o_prazo_nao_limita · H=ok · B=erro · prova (API ausente)
  - test_mutante_sem_teste_nos_modulos_ou_com_todos_fica_como_esta · H=ok · B=erro · prova (API ausente)
  - test_teste_fora_dos_modulos_do_diff_nao_roda · H=ok · B=falha · prova (asserção)
  - contagem: não prova (passa na base)=847; prova (API ausente)=2; prova (asserção)=1. O 4.º teste (sem plano dirigido) é guarda de regressão e passa na base, como esperado.
- Mutantes (`bin/forge-mutante tests/mutantes/v047-h5-prova-local.json`), todos mortos (rc 0):
  - M1 · morreu · bin/forge-mutante:1050; M2 · morreu · :1051; M3 · morreu · :1051; M4 · morreu · :1034 · (erro) o teste declarado deu erro sob o mutante e passa sem ele; M5 · morreu · :1038.
- Cobertura (`forge-mutante --cobertura --base 73a0ab81`): condições 1038, 1050 e 1051 cobertas (declarado, não provado); nenhuma condição mudada sem mutante.
- Diff conferido: só `bin/forge-mutante`, teste, spec e fragmento; sem escopo fora do H5.
