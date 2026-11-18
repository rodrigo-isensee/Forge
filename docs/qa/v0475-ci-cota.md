---
tipo: qa
contrato: 1
pedido: v0474
branch: melhoria/v0475-ci-cota
commit: 322798df5b7bd991ddf6a955c00a92363e13e1b3
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0475-ci-cota (E3.60, cobre E3.42)

Sem especificação de UX nem contrato de API: a obrigação é o item E3.42 (aviso de minutos do Actions acima de 80%, `R-CUSTO`) e o docstring de `bin/forge-cota-ci`. Diff conferido contra a base 2fa505d7: `bin/forge-cota-ci`, `tests/test_cota_ci.py`, `tests/mutantes/v0475-ci-cota.json`, duas skills (texto) e o fragmento de changelog. Só leitura por `gh api`, sem token novo e sem custo.

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

## Revalidação no head 19e7b93f (delta desde e0ac8508)
- Corrigido: o antigo A1 (teto de texto): `python3 -m unittest tests.test_metricas_texto` -> `Ran 2 tests ... OK`; `tests.test_orcamento_instrucao` -> `Ran 8 tests ... OK`. O antigo A2 (stderr "uso:") foi tratado no teste novo.
- `python3 -I tests/catraca.py --base origin/develop` -> rc 0 (sem guarda sem mutante).
- `tests.test_cota_ci` -> `Ran 26 tests ... OK`.
- `tests.test_ambiente_git` -> `Ran 20 tests ... FAILED (failures=1)` (A1; `test_cota_ci.py` não existe na base, a falha vem deste delta).
- Mutação, uma rodada por pedido (`--processos 3`): spec 1 rev=19e7b93fe4b5, M1 a M11 `morreu`; spec 2 rev=19e7b93fe4b5, M12 a M27 `morreu`; nenhum sobrevivente.
- Vermelho oficial (`forge-testes --vermelho`): não rerrodado (fila R-TETO ocupada); vale o substituto do parecer anterior e o autor cola o oficial.
- CI: sem check-run `bateria` consultado para este sha; a suíte inteira fica para o CI do PR.
- Parecer: reprovado por A1 (única razão).

## Revalidação no head 322798df (delta desde 19e7b93f)
- Delta (`forge-check parecer delta`): só `tests/test_cota_ci.py`; `git init` e `git remote add` passam `env=sem_manutencao()` (ponto único de `ambiente_git`).
- `python3 -m unittest tests.test_ambiente_git` -> `Ran 20 tests ... OK` (A1 corrigido).
- `python3 -m unittest tests.test_cota_ci` -> `Ran 26 tests ... OK`.
- `python3 -I tests/catraca.py --base origin/develop` -> rc 0 (sem guarda sem mutante).
- O delta não toca código de `bin/` nem a spec de mutantes; a mutação do head 19e7b93f (M1 a M27 `morreu`) segue valendo. Vermelho oficial e suíte inteira: CI do PR (check-run `bateria` do sha).
- Parecer: aprovado.
