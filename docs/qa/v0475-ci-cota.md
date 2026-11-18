---
tipo: qa
contrato: 1
pedido: v0474
branch: melhoria/v0475-ci-cota
commit: e0ac850854ef8d5efc64507f04379864c893f803
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-17
---
# QA: v0475-ci-cota (E3.60, cobre E3.42)

Sem especificação de UX nem contrato de API: a obrigação é o item E3.42 (aviso de minutos do Actions acima de 80%, `R-CUSTO`) e o docstring de `bin/forge-cota-ci`. Diff conferido contra a base 2fa505d7: `bin/forge-cota-ci`, `tests/test_cota_ci.py`, `tests/mutantes/v0475-ci-cota.json`, duas skills (texto) e o fragmento de changelog. Só leitura por `gh api`, sem token novo e sem custo.

## Achados
- A1 (bloqueante) skills/ci-cd/SKILL.md:56 · o texto novo estoura o teto de caracteres: test_metricas_texto.test_nenhuma_metrica_passa_do_teto e test_orcamento_instrucao.test_nenhum_agente_passa_do_teto passam na base e falham no head (reproduzido em e0ac8508). Encurtar a skill.
- A2 (recomendado) tests/test_cota_ci.py:84 · test_opcao_desconhecida_sai_2 passa também na base (rc 2 de "arquivo não existe") e não confere stderr; assertir "uso:" em stderr para ele falhar sem a ferramenta.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E3.42 avisa acima de 80% (rc 1) | test_acima_de_80_avisa_com_rc_1 | logo acima do limite (85%) | passou |
| E3.42 não avisa abaixo | test_abaixo_do_limite_diz_ok | 50% | passou |
| limite estrito de 80% | test_exatamente_80_nao_avisa | exatamente 80% | passou |
| limite configurável | test_limite_configuravel | --limite 40 | passou |
| sem permissão: não verificável + comando | test_sem_permissao_diz_nao_verificavel_e_o_comando | HTTP 403 | passou |
| resposta sem campos / só um campo | test_resposta_sem_os_campos_nao_verifica, test_so_um_dos_campos_nao_verifica | vazio, parcial | passou |
| franquia 0 sem divisão | test_franquia_zero_nao_divide | zero | passou |
| booleano não é número | test_booleano_nao_vale_como_numero | tipo | passou |
| uso errado sai 2 | test_limite_invalido_sai_2, test_opcao_desconhecida_sai_2 | entrada inválida | passou (ver A2) |

## Cenários e resultado real
- Unitário local: `python3 -I -m unittest discover -s tests -p test_cota_ci.py` -> `Ran 11 tests ... OK`.
- Mutação (`bin/forge-mutante tests/mutantes/v0475-ci-cota.json`, rev=e0ac850854ef): M1 a M11 todos `morreu`, nenhum sobrevivente; os 11 mutantes cobrem as guardas do diff (limite, igualdade, padrão 80, tipos, franquia, rc de uso, endpoint, não verificável).
- Vermelho antes do verde: `forge-testes --vermelho 2fa505d7` não deu veredito, porque a fila R-TETO (carga alta, outros agentes) o manteve sem saída; não vale como vermelho. Substituto, cópia da base (`git archive 2fa505d7` + o teste novo, `unittest -I`): `Ran 11 tests ... FAILED (failures=10)`; só o teste de A2 passa na base. O autor deve colar o `--vermelho` oficial.
- CI: sem PR nem check-run `bateria` para o sha ainda; a suíte inteira fica para o CI do PR.
- Permissões e acessibilidade: não se aplicam (CLI de leitura, sem UI); o uso do token existente do `gh` não amplia escopo.
- Regressão (forge-testes --vermelho 2fa505d7, saída final): `regressão=2` (test_metricas_texto e test_orcamento_instrucao, H=falha B=ok), `prova (asserção)=10`, `sem veredito=1` (test_forge). Reproduzido à mão no checkout de e0ac8508: os dois falham por estouro de `skills/ci-cd/SKILL.md` e do total de caracteres do devops-engineer. Por isso o parecer é reprovado.
