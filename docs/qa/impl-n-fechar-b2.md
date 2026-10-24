---
tipo: qa
contrato: 1
pedido: impl-n-fechar-b2
branch: melhoria/impl-n-fechar-b2
commit: f62766c87ab10b0a0bb650b072a12364311f433b
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-23
---
# QA: impl-n-fechar-b2 (RET-FECHAR-B2, lote N-FECHAR-b refeito)

Commit testado: `4b0c0b9` (HEAD `145fce0` da branch mais o merge `0a974e9`, que só traz `docs/security/`). Base `af79bef`. Sem especificação de UX nem contrato de API (script de integração); as obrigações são B1 a B5, R2 do lote a e RET-FECHAR-B2-V1 (A1, A2), conforme `changelog.d/impl-n-fechar-b2.md` e os pareceres de review e segurança.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| B1 parada do passo 4 diz se o rótulo ajuda | `test_fechar_aviso_rotulo` | nome do check com caracteres de controle | passou |
| B2 espera do rótulo vale para a execução velha da Catraca | `test_fechar_espera_catraca` (inclui `test_a2_*`: execução nova em `skipping` ou outra conclusão para) | execução nova fora de pass/pending/queued/in_progress | passou |
| B3 leituras do PR por número; MERGED preso ao head, base e commit de merge | `test_fechar_pr_numero` | número só de dígitos (1 a 9), URL única, PR de fork | passou |
| B4 comando para ler o log do check na parada | `test_fechar_log_check` | TMPDIR com aspa, só o número da execução no comando | passou |
| B5 parecer, remoto e merge presos ao mesmo sha | `test_fechar_sha_conferido`, `test_fechar` (`--ref` pelo sha) | sha relido diferente do remoto | passou |
| R2 `tmp2b` e `dorme_pid` nascem vazios | `test_fechar_vars_vazias` | valor herdado do ambiente | passou |
| V1-A1 segundo PR do mesmo head não é mesclado | `test_segundo_pr_do_mesmo_head_para_antes_do_ready_e_do_merge`, `test_mesmo_numero_pelo_nome_segue_para_o_merge` | dois PRs abertos do mesmo head | passou |
| V1-A2 texto do documento sem garantia falsa | revisão de `docs/fechamento-integrador.md:16` | n/a | passou |
| R-VERIFY nenhuma asserção removida | diff de `tests/test_fechar.py` | n/a | passou |

## Cenários e resultado real
- Suíte completa (`python3 -m unittest discover -s tests`, worktree `qa-impl-n-fechar-b2`): `Ran 1640 tests in 372.922s`, `FAILED (failures=4, skipped=1)`. As 4 falhas são exatamente as conhecidas do ambiente, que o PR #288 corrige: `test_shellcheck_no_hook` (SC2329 em `.githooks/pre-push:243`), `test_erro_interno_com_lista_de_permissao_falha_fechado` e as fixtures `conformidade/contrib-falha-fechada-pela-raiz-cwd-home-bloqueia` e `-cwd-wt-bloqueia`. Nenhuma é de `test_fechar*`; nenhuma falha nova.
- Os 7 módulos `test_fechar*` à parte: `Ran 126 tests in 37.509s`, `OK`.
- Vermelho antes do verde: cópia em `$TMPDIR` com os testes novos e o `bin/forge-fechar` de `af79bef` (sem a implementação): `Ran 46 tests`, `FAILED (failures=37)`. Os 9 que passam sem a implementação guardam comportamento que já existia (caminho normal e entradas sem efeito na base). Com a implementação, os 46 passam.
- Mutação: o Forge não tem ferramenta de mutação para shell (`R-CUSTO`); a sonda manual do A1 está no review (`bin/forge-fechar` de `aba4857` com os testes de `7f3b9ba`: FAIL) e o vermelho acima cumpre o papel para B1 a B5 e R2.
- `scripts/validar-plugin.sh`: `Validation passed`. `shellcheck bin/forge-fechar`: 3 avisos (SC2034, SC2015, SC2086, linhas 450, 467 e 474), os mesmos da `develop`, nenhum novo.
- Sem E2E de navegador nem acessibilidade (sem interface). Não houve chamada real ao GitHub: os testes usam `gh` falso.

## Bugs abertos
Nenhum. Recomendações não bloqueantes já registradas no review (A3: mensagem da linha 669; `--dry-run` nas linhas 480 e 484; `cancel` antes do rótulo no documento) seguem com o tech-lead.

## Revalidação por delta (REVAL-288, E3.3)
Depois do review por delta aprovado, pela decisão "C" do dono (2026-10-23). Delta desde `4b0c0b9` (commit do parecer anterior) até `f62766c`: a entrada da `develop` (`7423c44`, PR #288, FIX-SUITE-LOCAL: `.githooks/pre-push`, `tests/test_hooks.py`, `tests/apoio_pathlib_312/`, duas fixtures `contrib-falha-fechada-pela-raiz-cwd-*`, documentos `suite-local-verde`) e pareceres em `docs/` (a segurança só teve o `pedido:` alinhado). Nenhum código da entrega mudou. Comando: `bin/forge-testes`, que escolheu a suíte completa (`bin/forge-fechar` sem mapa): 1640 testes, 898 s, `OK`, rc 0. As falhas conhecidas do ambiente somem, como previsto. Comportamento já aprovado (B1 a B5, R2 e as recomendações do review): igual, sem regressão. Veredito: aprovado, sem achado novo.
