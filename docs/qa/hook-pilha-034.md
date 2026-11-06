---
tipo: qa
contrato: 1
pedido: hook-pilha-034
branch: melhoria/hook-msg-segmento
commit: ed9c22a7ef1e43d0142183afcdada364b9df339e
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-06
---
# QA: hook-pilha-034 (E1.4, pilha de hooks inteira)

Base: develop d9b26bb. Código testado: ed9c22a, topo das 7 branches (revalidação do parecer aprovado dae76f8 sobre dde743b). Entre os dois, fora os pareceres, mudou só a fixture `tests/hooks/conformidade/hook-msg-segmento-atribuicao-mascarada-bloqueia.json` (volta do CI do PR #451). Os critérios são os do pedido (E1, E2 e E3); não há especificação de UX.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: `\` + quebra de linha no meio da palavra recusa nos dois hooks | fixtures `continuacao-linha-107` a `-111` e `-112` (parecer); sonda própria: `g$'\x68' repo de\⏎lete`, `g$'\x69't pu\⏎sh`, `$'\x67'it push origin ma\⏎in` | continuação no meio da palavra | passou, rc 2 |
| E1: `$'…'` decodificado até o primeiro NUL | fixtures `-098` a `-105`; sonda: `gh $'repo\0x' delete`, `$'gh\0' repo delete`, `$'g\x69t\0' push origin main` | NUL no começo, no meio e no fim | passou, rc 2 |
| E1: NUL legítimo segue liberado | fixture `-106`; sonda: `printf $'a\0b'`, `echo $'a\0b' && git status` | falso positivo | passou, rc 0 |
| E1: formas compostas até o ponto fixo; teto falha fechado | `test_formas_compostas_ate_o_ponto_fixo_e_teto_fecha`, mutantes M42, M44 e M45 | teto de rodadas | passou, mutantes mortos |
| E1: `bash -c`, `eval` e `sh -c` com `$'…'` | sonda própria nos dois hooks; fixtures `-38` a `-91` | aninhamento | passou, rc 2 |
| E1: casos legítimos liberados | sonda: `git status && \⏎git log`, `echo $'\x67\x68'`, `printf '%s' $"gh" repo view`, `echo `date``, `gh repo view`, `gh pr view 1` | falso positivo | passou, rc 0 |
| E2: R7 e R8 do rótulo afrouxa-regra recusam; outro rótulo libera | fixtures `rotulo-variavel-r7-*` (3) e `rotulo-variavel-r8-*` (4), em `test_fixtures_da_trilha_034` | `#` em expansão antes da crase; `$'…'` antes da crase; aspa escapada | passou |
| E2: `tests.test_hook_ansi_c` mata o M4 (`hooks/_comum.py:1894`) | `tests.test_hook_ansi_c` e mutante M4 | guarda da aspa escapada | passou, M4 morreu |
| E3: a reaplicação das branches não muda o comportamento | `test_fixtures` (todas as fixtures dos dois hooks) e a suíte do push | n/a | passou |

## Cenários e resultado real
Ambiente: worktree `/root/.forge-contrib/wt/hook-msg-segmento`, código ed9c22a (revisão do review a6953f9 sobre ele).

- **Suíte inteira (D-5), sem rodar de novo (R-TETO):**
suite: reusa
  `/tmp/push-pilha2.log`, do push de ed9c22a (00:18, `dae76f8..ed9c22a`): `Ran 968 tests`, `Ran 1654 tests`, `Ran 2622 tests in 1485.502s (2 processos)`, `processo 1: rc 0, 968 testes, 1485.3 s, 50 módulos`, `processo 2: rc 0, 1654 testes, 919.0 s, 42 módulos`, `OK (skipped=30)`, `push_rc=0 00:18:14`. Nenhuma linha de falha (FAIL, ERROR) no log. Pulos e avisos, copiados do log, inclusive os do meio das linhas de pontos:
  - `AVISO: job 'j' pulado por falta de suporte: condição sem suporte (token inesperado): __import__('os').system('touch /tmp/forge-suite-ybjee8_e/p1/tmpcppv4afu/executou')` (texto de teste, não executado aqui)
  - `AVISO: --confiar: o código do PR de fork de 'dona' vai rodar nesta máquina com o seu ambiente e com a credencial do gh em disco; ela fica exposta a esse código.`
  - `AVISO: j/lint pulado: actionlint ausente no PATH` (duas vezes, linhas 10 e 18 do log)
  - `catraca: a API do GitHub não respondeu por inteiro (KeyError); vale como sem rótulo.` e duas vezes `catraca: a API do GitHub não respondeu por inteiro (OSError); vale como sem rótulo.`
  - marcas de pulo `s` no meio das linhas de pontos do log, contadas por linha: linha 25: 1; linha 41: 25; linha 43: 4; total 30, igual a `OK (skipped=30)`.
  - `pre-push: outra suíte do Forge está rodando ou na fila antes desta (pid 1178827 ns 4026533819 desde 20:58:18); esperando a vez por até 21600 s (R-TETO).` e `suite-paralela: 2622 testes em 92 módulos, 2 processos (carga alta (load 13.4 de 12 núcleos, 14.5 GB disponíveis)).`
- **Fixture mudada em ed9c22a:** o comando passa do token falso antigo (40 caracteres alfanuméricos depois de `ghp_`) para um token falso com sufixo `_FAKE` repetido, com `git push origin main` depois; `descricao`, `entrada` e o esperado não mudaram. Prova o mesmo: o `TOKEN_DO_GITHUB` (`hooks/conformidade.py:42`) aceita `_` e mascara o valor (`GH_TOKEN=*** git push origin main`, conferido com a mesma expressão), e o padrão `ghp_[A-Za-z0-9]{20,}` de `scripts/verificar-contribuicao.sh:16` não casa mais. O `test_fixtures` do push de ed9c22a cobre a fixture e fechou `OK`; não rodei `tests.test_hooks` de novo.
Os itens abaixo (ansi_c, fixtures, sonda, mutantes, vermelho) são da rodada em dde743b; o código de hooks não mudou em ed9c22a (só a fixture acima), então valem.
- **`python3 -m unittest tests.test_hook_ansi_c`:** `OK`, rc 0.
- **Fixtures dos dois hooks:** `python3 -m unittest tests.test_hooks.Hooks.test_fixtures tests.test_hooks.Hooks.test_fixtures_da_trilha_034`: `Ran 2 tests in 470.101s`, `OK`.
- **Sonda própria** (montagem das fixtures, comando trocado): as recusas saem com rc 2 e as liberações com rc 0, como na tabela. No `parecer`, `g$'\x68' pr mer\⏎ge docs/x`, `bash -c $'gh pr m\x65rge 1'` e `eval $'…'` recusam; `$'gh\0' pr merge 1` recusa por R-CONTRIB; `gh pr view 1` e `echo $'a\0b' && gh pr view 1` liberam. Sem `$'…'`, `gh pr m\x65rge` é texto literal e libera, como no bash.
- **Mutantes:** `bin/forge-mutante tests/mutantes/hook-conformidade-034-*.json --processos 2` (rev 5edf63c32e03, 8 specs): 43 mutantes, 43 `morreu`, rc 0 (entre eles M3, M4, M43, M44, M45 e M46).
- **Lista de mutantes contra o diff:** `bin/forge-mutante --cobertura --base d9b26bb3e6b11e7d45c8b7ed81c7da7a8a325503` dá toda linha de guarda mudada em `hooks/` como `coberta`, sem nenhuma `não coberto`. As duas `isenta` (`hooks/_comum.py:360` e `:378`) têm motivo lido: a quebra que sobra é conferida pela forma juntada, e a forma repetida só repete o mesmo caminho.
- **Vermelho antes do verde:** `bin/forge-testes --vermelho d9b26bb3e6b11e7d45c8b7ed81c7da7a8a325503 --modulos test_hooks --prazo 1500`, rc 0. Abre com `vermelho: base=d9b26bb3e6b1 head=5edf63c32e03 módulos=test_hooks (restrito por --modulos)` e fecha com `contagem: não prova (passa na base)=67; prova (API ausente)=4; prova (asserção)=8; pulado=1`. Nenhum teste cai no HEAD. Provam, entre outros, `test_fixtures`, `test_fixtures_da_trilha_034`, `test_ansi_c_decodifica_como_o_bash`, `test_formas_compostas_ate_o_ponto_fixo_e_teto_fecha` e `test_marcador_critico_tambem_na_forma_juntada`. O pulado (`test_erro_interno_com_lista_de_permissao_falha_fechado`) fica pulado também na base, não vem da pilha. Em `test_hook_ansi_c` (`--modulos test_hook_ansi_c`, rc 1), os 9 testes passam na base: o módulo já existe lá, e o M4 é que prova o reforço dele.

## Conferência do PA-7
Li `docs/engineering/achados-recorrentes.md` (AR-1 a AR-11) de novo em ed9c22a; o delta é uma fixture, sem `bin/`, hook, `.githooks/` nem script novo, então AR-3 a AR-5 e AR-7 a AR-11 não se aplicam. A lista de mutantes cobre o diff (AR-1), o ramo de falha de guarda tem fixture que prova pela ação (AR-2), e a mascara do shell não esconde código nas sondas (AR-6). O review e a segurança já registraram os A1 e A2 (review) e o A1 (segurança) como recomendações anteriores à pilha, em cartão; não são regressão e não os reabro.

## Bugs
Nenhum aberto; sem arquivo em `docs/qa/bugs/`.

## Parecer
Aprovado. No código ed9c22a (código de hooks igual ao de dde743b; só a fixture mudou) os repros do E1 e do E2 recusam, os casos legítimos passam, a suíte inteira do push de ed9c22a passou (`suite: reusa`, `/tmp/push-pilha2.log`), os testes novos provam contra a base e os 43 mutantes morreram.
