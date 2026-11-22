---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-ae3-1-controle
commit: 98882c4903c31dd2e074783dec70b31882046244
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-22
---
# QA: v0478 (AE3.1, E108.4)

## Achados
- A1 (bloqueante) bin/forge_controle.py:21 · SEGREDO diferencia maiúscula: docs/chave.PEM (e .KEY, id_RSA) passa e é commitado (reproduzido: salvar devolveu salvo e o commit contém docs/chave.PEM). Quebra a recusa de segredo do desenho (R-SEGURANCA); usar re.IGNORECASE e testar.

## Critério → teste → resultado
Critérios tirados do contrato do módulo (docstring, AE3.1).
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| só a lista positiva entra, mensagem fixa, sem add -A | Salvar.test_so_os_caminhos_da_lista... | caminho fora da lista (preparado.txt) | passou |
| sem mudança, sem commit | Salvar.test_sem_mudanca_nao_faz_commit | vazio | passou |
| nunca push | Salvar.test_nunca_faz_push | n/a | passou |
| GIT_* herdado ignorado | Salvar.test_git_dir_herdado... | ambiente | passou |
| recusa link, pasta-link, repositório aninhado, sem commit parcial | Recusas.test_link_*, test_pasta_que_e_link, test_repositorio_aninhado | tipo de arquivo | passou |
| recusa segredo | Recusas.test_nome_de_segredo (só `.env`) | nome em minúsculas apenas | passou, mas a sonda com `.PEM` falhou (A1) |
| teto de bytes | Recusas.test_arquivo_acima_do_teto / no_teto | máximo e máximo+1 | passou |
| hook ativo / core.hooksPath: nao-verificavel | Ambiente.test_hook_*, test_hooks_path_* | hook, .sample, sem pasta | passou |
| subpasta não é raiz; trava concorrente: ocupado | Ambiente.test_subpasta, test_segundo_salvar | permissão/concorrência | passou |
| falha de git em cada passo | Falhas.* (7) | falha de chamada | passou |

## Cenários e resultado real
- Provas: `python3 -I -m unittest discover -s tests -p test_forge_controle.py`: Ran 25 tests, OK. Sem suíte local; a bateria é a do CI do PR.
- Mutantes: as 4 specs (CTL1 a CTL25) rodaram: todos morreram, rc 0 (CTL1 e CTL24 por erro do teste declarado, aceito). `--cobertura --base b0895f6c`: todas as condições do diff cobertas; `não coberto: tests/pesos-d4.json` (dados, sem guarda).
- Vermelho antes do verde: módulo e testes novos (a base não tem forge_controle); o vermelho vem da carga da base, sem teste herdado.
- Sonda manual (repositório temporário): nome com acento e espaço salva; `.PEM` maiúsculo salva (A1).
- Bug: sem arquivo em docs/qa/bugs; o A1 acima cobre (severidade alta).
