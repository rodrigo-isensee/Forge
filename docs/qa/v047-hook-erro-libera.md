---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-hook-erro-libera
commit: 9e3f57c66510ceff571fd59e3153b145b8d58e6b
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 2
bugs_baixos: 0
data: 2026-11-13
---
# QA: v047-hook-erro-libera

Pedido v047, etapa E3.18: parecer de QA do head `9e3f57c6` (base `c5aa70e1`), HOOK-ERRO-LIBERA (erro interno e prazo vencido deixam de liberar a escrita protegida). Os critérios são as condições C1 a C8 e os casos E1 a E8 do modelo de ameaças da E3.6 (`/root/.forge-contrib/docs/security/v047-v2-ameacas.md`, seção 1). Sem PR e sem CI do head: a suíte inteira não rodou aqui (carga ~15 em 12 núcleos); rodei os testes do pedido, o vermelho do módulo novo, os 33 mutantes e sondas próprias. Os pareceres de review e de segurança no mesmo head não foram usados como prova, só conferi a reprodução dos dois bloqueantes da segurança.

## Achados
- A1 (bloqueante) hooks/conformidade.py:2824 · `ESCRITORES` não lista `checkout`, `restore`, `apply`, `am` do git: com erro forçado, `git restore --source=x docs/pedidos/v1.md` e `git checkout origin/x -- docs/pedidos/v1.md` dão rc 0 (a guarda normal dá rc 2). Reproduzido (R-CONFORMIDADE, C2). Sem mutante nesta linha.
- A2 (bloqueante) hooks/conformidade.py:2872 · Troca de base fora do texto: com erro forçado, `cd docs && cp x pedidos/v1.md` e `git -C docs checkout x -- pedidos/v1.md` dão rc 0 (a guarda normal dá rc 2, o controle `cp x docs/pedidos/v1.md` dá rc 2). Reproduzido (R-CONFORMIDADE, C2, C3).
- A3 (recomendado) tests/mutantes/v047-hook-erro-libera.json:1 · Nenhum mutante tira um verbo de `ESCRITORES` (`:2824-2825`): a lista que decide o marcador não tem prova de mutação; some um mutante por verbo do git que entrar na correção de A1.
- A4 (recomendado) agents/tech-lead.md:21 · M14: 432 linhas contáveis contra a orientação de 150 (M14 não é trava); o corpo do PR precisa de `teto: excedido, 432 linhas, <motivo>`, e o pedido mistura quatro classes (C1, C2 a C5, C6, C7) em `hooks/`.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| C1 (`~` de usuário inexistente não lança) | E1, E2: fixtures `errointerno-til-de-usuario-inexistente-bloqueia`, `errointerno-cp-pelo-home-bloqueia`; `test_nenhum_expanduser_de_path_nos_hooks` | `~zz` inexistente | passou |
| C2 (erro interno em escrita protegida recusa) | `test_cada_entrada_da_politica_com_erro_forcado_recusa` (48 entradas), `test_fixtures_do_pedido` (25), `test_politica_ilegivel_ou_sem_caminhos_marca_tudo` | política vazia ou ilegível; cada entrada; legítimos que liberam (`git status`, `ls ~zz`, `cp x build/y`) | passou na forma literal; falha em A1 e A2 (sonda própria) |
| C3 (alvo opaco `$`, crase, `<(` marca) | `errointerno-alvo-opaco-bloqueia` | alvo montado em tempo de execução | passou |
| C4 (Write, Edit, MultiEdit, NotebookEdit) | `errointerno-write-na-raiz-bloqueia`, `-em-briefs-`, `-fora-da-raiz-libera` | dentro da raiz, `..`, fora da raiz (libera) | passou |
| C5 (prazo vencido recusa) | `test_fixtures_do_prazo` (4), `test_marcador_que_responde_decide`, `test_erro_do_marcador_marca` | prazo em `docs/pedidos`, `.github`, oráculo; sem escrita libera | passou |
| C6 (`-s -E` no lançador dos hooks) | `test_usercustomize_e_pythonpath_nao_desligam_os_hooks`, `test_catraca_compara_o_script_sem_as_opcoes_do_interpretador` | `usercustomize` que sai com 0 | passou |
| C7 (estado do `agentes` não leva o R-BRIEF) | `test_fixtures_do_agentes` (8 `errointerno-*` do `agentes`) | `agentes.json` corrompido sem brief; clone sem estado | passou |
| C8 (alcance dito nas ADRs e docs) | leitura do diff (ADR 0003, 0009, `docs/hooks.md`) | n/a | conferido, sem teste |

Unitário: `tests.test_hook_erro_libera` com 11 testes, 25 fixtures `errointerno-*` (mínimo afirmado em `minimo(..., 25)`, `:44`; contei 25 arquivos).

## Cenários e resultado real
**Teste do pedido, no head:** `python3 -m unittest tests.test_hook_erro_libera` → `Ran 11 tests ... OK`.

**Vermelho antes do verde** (`R-QA`): `bin/forge-testes --vermelho c5aa70e1 --modulos test_hook_erro_libera`, rc 0. Abre com `vermelho: base=c5aa70e11859 head=9e3f57c66510`; os 11 testes passam no HEAD (`H=ok`) e caem na base: 7 por asserção e 4 por API ausente; `contagem: prova (API ausente)=4; prova (asserção)=7`. Uma 1ª rodada na suíte inteira não deu veredito (saída cortada por pipe) e uma 2ª com `test_hooks` estourou o prazo de 580 s com a máquina carregada (rc 124, sem veredito, não conta como vermelho); `test_hooks` ficou sem rodada vermelha aqui.

**Mutação** (`bin/forge-mutante --processos 2` sobre as 5 specs `tests/mutantes/v047-hook-erro-libera{,-2,-3,-4,-5}.json`): 33 mutantes, 33 `morreu`, rc 0; cinco mortes (M3, M4, M15, M20, M23) vieram por erro do teste declarado sob o mutante, que passa sem ele (morte válida pela regra do `forge-mutante`). `forge-mutante --cobertura --base c5aa70e1`: toda condição Python mudada tem mutante declarado, duas isentas com motivo (`conformidade.py:2376`, `tests/apoio_volta_unica.py:810`), `hooks/hooks.json` como `não coberto` (os mutantes M29 e M30 o cobrem à mão). A linha de guarda `ESCRITORES` (`conformidade.py:2824`, uma atribuição, não condição) não tem mutante: A3.

**Sondas próprias** (fixture temporário fora da árvore, `forcar: Guarda.bash/erro`, esperado rc 2, lançador dos testes):
- controle `cp x docs/pedidos/v1.md`: rc 2 (recusa, como deve).
- `git restore --source=x docs/pedidos/v1.md`: rc 0 (liberou).
- `git checkout origin/x -- docs/pedidos/v1.md`: rc 0 (liberou).
- `cd docs && cp x pedidos/v1.md`: rc 0 (liberou).
- `git -C docs checkout x -- pedidos/v1.md`: rc 0 (liberou).
O mesmo conjunto fora do erro forçado (guarda normal) recusa, conforme a segurança; reproduzi só o lado do erro forçado.

**Teto M14** (`agents/tech-lead.md:21`): `git diff --numstat --no-renames` sobre `bin/ hooks/ scripts/ .github/ .githooks/ tests/*.py tests/config.json`, base `c5aa70e1` a `9e3f57c6` = 432 linhas (hooks 182, tests 250), fora corpus, fixtures, mutantes e `.md`. Julgamento: a orientação é de 150 e não trava; o comportamento é um (falha fechada com erro ou prazo), com corpus próprio de 25 fixtures e 33 mutantes, o que atenua. Pesa contra: tocar `agentes.py` (C7) e o lançador (C6) além do `conformidade.py` é mais de uma classe em `hooks/`. Não bloqueia por si (A4, recomendado); o corpo do PR declara o teto.

**Suíte e CI:** sem PR, não há check-run `bateria` do head; a suíte inteira fica para o CI do PR.

**Acessibilidade e E2E:** n/a (hooks de linha de comando, sem interface).
