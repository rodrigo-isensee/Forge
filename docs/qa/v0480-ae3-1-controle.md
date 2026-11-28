---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-ae3-1-controle
commit: 40244cc20339c7438a9a20ec66e8b92ccfc405d1
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-22
---
# QA: v0478 (AE3.1, E108.4)

## Critério → teste → resultado
Critérios tirados do contrato do módulo (docstring, AE3.1).
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| só a lista positiva entra, mensagem fixa, sem add -A | Salvar.test_so_os_caminhos_da_lista... | caminho fora da lista (preparado.txt) | passou |
| sem mudança, sem commit | Salvar.test_sem_mudanca_nao_faz_commit | vazio | passou |
| nunca push | Salvar.test_nunca_faz_push | n/a | passou |
| GIT_* herdado ignorado | Salvar.test_git_dir_herdado... | ambiente | passou |
| recusa link, pasta-link, repositório aninhado, sem commit parcial | Recusas.test_link_*, test_pasta_que_e_link, test_repositorio_aninhado | tipo de arquivo | passou |
| recusa segredo | Recusas.test_nome_de_segredo, test_segredo_em_maiusculas, test_cada_nome_de_segredo | qualquer caixa | passou (revalidado: `.PEM`, `.KEY`, `id_RSA`, `.ENV`, `.NETRC` recusados em qualquer caixa) |
| teto de bytes | Recusas.test_arquivo_acima_do_teto / no_teto | máximo e máximo+1 | passou |
| hook ativo / core.hooksPath: nao-verificavel | Ambiente.test_hook_*, test_hooks_path_* | hook, .sample, sem pasta | passou |
| subpasta não é raiz; trava concorrente: ocupado | Ambiente.test_subpasta, test_segundo_salvar | permissão/concorrência | passou |
| falha de git em cada passo | Falhas.* (7) | falha de chamada | passou |

## Cenários e resultado real
- Provas: `python3 -I -m unittest discover -s tests -p test_forge_controle.py`: Ran 25 tests, OK. Sem suíte local; a bateria é a do CI do PR.
- Mutantes: as 4 specs (CTL1 a CTL25) rodaram: todos morreram, rc 0 (CTL1 e CTL24 por erro do teste declarado, aceito). `--cobertura --base b0895f6c`: todas as condições do diff cobertas; `não coberto: tests/pesos-d4.json` (dados, sem guarda).
- Vermelho antes do verde: módulo e testes novos (a base não tem forge_controle); o vermelho vem da carga da base, sem teste herdado.

## Revalidação (head 59ad2edc, delta desde 98882c49)
- A1 do parecer anterior: corrigido (SEGREDO com `re.IGNORECASE`, mais `.p8/.kdbx/.jks/.keystore`, `.netrc`, `credentials*`, `secrets*`); teste de maiúsculas cobre. Fechado.
- Provas: `python3 -I -m unittest discover -s tests -p test_forge_controle.py`: Ran 41 tests, OK, rc 0.
- Mutantes: `bin/forge-mutante tests/mutantes/v0478-ae3-controle-5.json tests/mutantes/v0478-ae3-controle-6.json --base 98882c49...`, linha `base=98882c4903c31dd2e074783dec70b31882046244`: CTL26 a CTL35 morreram, rc 0.
- Config que roda comando (fsmonitor, filtros, gpg, include) e trava por link: cobertas pelos testes novos e pelos mutantes.

## Revalidação (head ba201c86, delta desde 59ad2edc)
- Delta no domínio: uma linha em `docs/indice-forge.md` (entrada de `forge_controle.py`) e `tests/pesos-d4.json` (peso de teste, dado); o resto veio da develop. Sem código de guarda mudado, sem mutante novo.
- Provas: `python3 -I -m unittest discover -s tests -p test_indice_forge.py`: Ran 19 tests, OK, rc 0. Sem suíte local; a bateria é a do CI do PR.

## Revalidação (head 40244cc2, delta desde ba201c86)
Delta do domínio (`forge-check parecer delta`): `bin/forge_controle.py` (só a docstring perdeu o caminho do doc) e `tests/test_forge_controle.py` (isolamento da config de sistema e teste novo).
- `test_forge_controle`: 42 testes, OK. `test_reval_delta`: 10 testes, OK (TMPDIR próprio).
- `test_config_de_sistema_com_filter_lfs_so_nao_vaza_com_o_isolamento`: 1 teste, OK. Com a config de sistema falsa (`filter.lfs`) e o isolamento desligado, `salvar` sai `nao-verificavel` sem commit; com o isolamento ligado, sai `salvo`. O teste cobre os dois lados, então o isolamento que cai derruba a suíte.
- Sem achado.
