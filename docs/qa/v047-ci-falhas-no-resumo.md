---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-ci-falhas-no-resumo
commit: 2cafdfd9002dbf27c078beaec74858d76b382323
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-16
---
# QA: v047 · ci-falhas-no-resumo (E2.270, parecer E2.289)

Parecer completo (não havia parecer anterior) no head 82623453, base 5e74c70e. Sem especificação de UX nem contrato de API: as obrigações vêm do item E2.270 (o CI escreve no resumo e em anotações o nome e o local dos testes que falharam) e de `R-CUSTO` (sem custo), `R-SEGURANCA` (registro de teste é texto não confiável). Escopo: `scripts/falhas-no-resumo.py`, os 6 passos novos do `ci.yml`, os testes `tests/test_falhas_no_resumo.py`, `tests/test_ci_local.py`, `tests/test_suite_partes.py` e a spec de mutantes. A suíte inteira roda no CI do PR; cito o check-run `bateria` do mesmo sha como prova da suíte, não rodei a suíte inteira local.

## Achados
- A3 (recomendado) tests/mutantes/v047-ci-falhas-no-resumo-2.json:1 · G1 e G2 sem veredito de morte em /proc real: aqui G1 "sobreviveu" (teste novo sem `exigir`, passa vazio) e o teste do G2 é pulado. Rode as 2 specs onde /proc é do namespace, junto do A4 do review.
- A1 (recomendado) scripts/falhas-no-resumo.py:156 · 10 condições Python mudadas sem mutante declarado em `--cobertura` (linhas 156, 160, 162, 171, 178, 179, 180, 189, 199, 209). Não é pedido de controle, não bloqueia; o autor pode declarar ou isentar.
- A2 (recomendado) tests/test_suite_partes.py:383 · `(linha,) = [...]` (também em :372) dá ValueError, não asserção, na base: o `forge-testes --vermelho` marca "sem veredito" (rc=2) em 2 testes do Brinquedo5. Pôr `assertEqual(len(...), 1)` antes do desempacotamento.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E2.270-a falha e erro com teste, módulo, linha e erro | `Execucao.test_falha_escreve_no_resumo_anota_e_sai_com_zero`, `Leitor` (subteste, setUpClass) | subteste, setUpClass | passou (vermelho na base) |
| E2.270-b verde traz só a contagem | `Execucao.test_verde_so_a_linha_da_contagem` | zero falhas | passou (vermelho na base) |
| E2.270-c tetos de tabela e anotações | `Leitor.test_tetos_da_tabela_e_das_anotacoes` | máximo, logo acima do teto | passou; F4 e F5 morrem |
| E2.270-d registro ausente ou argumento errado não reprova | `Execucao.test_registro_ausente_ou_argumento_errado_nao_reprova` | ausente, uso inválido | passou; F9 e F10 morrem |
| E2.270-e registro não vira comando, tabela nem segredo | `Leitor.test_texto_do_registro_nao_vira_comando_nem_tabela_nem_segredo` | `::`, quebra de linha, `\|`, `<`, segredo | passou; F1, F2, F3, F6, F7 morrem |
| E2.270-f caminho fora do repositório ou com `..` | `Leitor.test_quadro_fora_do_repositorio_ou_com_ponto_ponto_fica_sem_arquivo` | `..`, fora da raiz | passou; F8 morre |
| E2.270-g local é o quadro dos testes, erro é a exceção, bloco repetido conta um | três testes de `Leitor` | quadro posterior do repositório, diff da mensagem | passou; F11, F12, F13 morrem |
| E2.270-h fiação: leitor depois da suíte em cada job, pipefail mantém o rc, permissões iguais | `Fiacao.*`, `test_ci_local`, `test_suite_partes.FiacaoDoCI` | `-I`, `!cancelled()`, `permissions` | passou; F14 morre |

## Cenários e resultado real
- `python3 -m unittest tests.test_falhas_no_resumo tests.test_ci_local tests.test_suite_partes` na raiz do clone: `Ran 119 tests in 104.512s`, `OK`.
- Sonda manual: registro com linha `::stop-commands::x` depois do erro e rótulo simples: sai uma anotação `::error file=tests/test_ci_local.py,line=3::m.C.test_x: AssertionError: a`, a linha injetada não vira comando, resumo em tabela correta, rc=0.
- Fiação conferida no diff: os 4 jobs que rodam a suíte têm `set -o pipefail` e `| tee`, e o passo do leitor com `if: ${{ !cancelled() }}` (partes: também `provada != 'true'`), `python3 -I`, sem mudança em `permissions` e sem rede. Sem custo (`R-CUSTO`). O texto de registro impresso pelo próprio passo da suíte já era assim antes (não é novo).

## Vermelho antes do verde (`forge-testes --vermelho`, restrito aos 3 módulos tocados por `--modulos`; a rodada sem restrição passa dos 550 s)
```
vermelho: base=5e74c70e01fa head=826234539425 módulos=test_falhas_no_resumo,test_ci_local,test_suite_partes (restrito por --modulos)
revertidos à base: .github/workflows/ci.yml, changelog.d/v047-ci-falhas-no-resumo.md, scripts/falhas-no-resumo.py
mantidos no HEAD: tests/mutantes/v047-ci-falhas-no-resumo.json, tests/test_ci_local.py, tests/test_falhas_no_resumo.py, tests/test_suite_partes.py
contagem: não prova (passa na base)=98; prova (API ausente)=13; prova (asserção)=8
rc=0
```
Nenhum teste cai no HEAD (todos `H=ok`). Os testes mudados `test_rapida_e_bateria_rodam_a_suite_pelo_script_dividido` e `test_a_suite_inteira_so_roda_nas_partes_e_na_rapida` provam por asserção.

## Mutação no diff (`bin/forge-mutante tests/mutantes/v047-ci-falhas-no-resumo.json`)
```
forge-mutante: pedido=v047-ci-falhas-no-resumo rev=826234539425 spec=ee3dde3dfc68311ac0f2471490bd10133681af66bd5f3f4613b137e324002658
F1 a F14 · morreu (14 de 14; nenhum sobrevivente, nenhum sem veredito)
```
`--cobertura --base 5e74c70e` lista 10 condições sem mutante (A1, recomendado: o item não é de controle).

## Segurança e abuso
Sem gatilho de segurança declarado no brief. O abuso evidente (injeção de comando de workflow e de Markdown pelo registro) tem teste e mutantes (F1 a F3, F6, F7).

## Achados recorrentes (PA-7)
Conferi AR-5 (python sem `-I` em caminho que decide): o leitor é chamado com `-I` nos 4 passos (F14 guarda o do 3.14). AR-12 (spec de mutante desatualizada): os 14 mutantes aplicam no head. Sem classe nova.

## Revalidação por delta no head 0f4a5413 (E2.511)
`forge-check parecer delta` deu o intervalo `82623453..0f4a5413`, sem o que veio da develop. Quase todo o delta repete o CI-RAPIDO do #576 (`ci.yml`, `scripts/suite-partes.py`, `scripts/pesos-do-ci.py`, 7 specs `v047-ci-rapido-*`); o novo é o leitor de falhas nas 4 matrizes, a guarda dos 4 agregadores na catraca (`test_catraca`: `always()` só no if dos agregadores, sem `uses:`, só `needs.*.result`) e as specs realinhadas (`v0432-integracao-6/7`, `v046-ci-lote-e1`). `forge-check parecer delta` não lista `scripts/falhas-no-resumo.py` nem `tests/test_falhas_no_resumo.py`: o domínio do parecer anterior não mudou.

Rodado local só nos arquivos tocados (sem `-I`, sem suíte completa; a suíte inteira é o check-run `bateria` do PR, que ainda não existe para este sha, sem PR aberto):
- `python3 -m unittest tests.test_ci_local tests.test_ci_rapido_guardas tests.test_falhas_no_resumo tests.test_pesos_do_ci tests.test_suite_partes tests.test_catraca`: `Ran 534 tests in 290.808s`, `OK`.
- `python3 -m unittest tests.test_forge.RodarUmModuloComIsolamento tests.test_forge.PrePushSoOsAfetados`: `Ran 6 tests`, `OK`.

### Mutantes (`bin/forge-mutante`, `--processos 4`)
`--conferir --base 86ac0fcb`: `conferidas: o trecho de cada spec do diff está no lugar` (AR-12). Spec do item (pedido próprio, rodada à parte): `v047-ci-falhas-no-resumo.json`, `rev=0f4a541379ec`, 14 morreu, rc=0. As 7 specs `v047-ci-rapido-1..7` (pedido v047), `rev=0f4a541379ec`, rc=0:
```
87 morreu · M20 · equivalente · scripts/pesos-do-ci.py:85 (declarado, não rodou) · 88 mutantes · nenhum sobrevivente, nenhum sem veredito
```
`--cobertura --base 86ac0fcb`: as condições de `suite-partes.py` e `pesos-do-ci.py` saem `coberta ... declarado, não provado`; `ci.yml` sai `não coberto` (YAML); as 3 specs editadas saem `spec editada`; as condições sem mutante são só as de `scripts/falhas-no-resumo.py` (A1, já recomendado, o item não é de controle).

### Vermelho antes do verde (`forge-testes --vermelho 86ac0fcb --modulos` nos 6 módulos tocados, `--prazo 500`)
```
vermelho: base=86ac0fcb9495 head=0f4a541379ec módulos=test_catraca,test_ci_rapido_guardas,test_pesos_do_ci,test_suite_partes,test_falhas_no_resumo,test_ci_local (restrito por --modulos)
contagem: não prova (passa na base)=440; prova (API ausente)=67; prova (asserção)=25; sem veredito=2
rc=2
```
Nenhum teste cai no HEAD (todos `H=ok`). Os 2 sem veredito são `Brinquedo5.test_parte_que_nao_divide_anota_o_erro_da_guarda` e `...test_parte_vermelha_anota_o_teste_que_caiu_e_a_verde_nao` (H=ok, B=erro): na base não há linha `::error`, e o desempacotamento `(linha,) = [...]` levanta ValueError em vez de falhar por asserção; o `forge-testes` não conta erro do módulo como vermelho. A causa é a ausência do recurso na base, confirmada na leitura do teste, e as 3 outras provas do `Brinquedo5` (`H=ok, B=falha`) cobrem o mesmo comportamento; vira A2 (recomendado), sem bloquear.

### Segurança, fronteiras e recorrentes
Sem gatilho de segurança. A guarda dos agregadores protege a fronteira `always()` sem checkout nem código da branch (cancelado ou pulado reprova). PA-7 conferido: AR-5 (`-I` no leitor, F14 morreu), AR-12 (specs aplicam no head), AR-1 (lista de mutantes: 1 por guarda mudada de `suite-partes.py` e `pesos-do-ci.py`, sem condição sem mutante fora do A1). Sem classe nova.

Parecer: aprovado, sem bug crítico, alto, médio ou baixo; A1 e A2 recomendados.

## Revalidação por delta no head 2cafdfd9 (E2.608)
`forge-check parecer delta` deu `0f4a5413..2cafdfd9`, sem o que veio da develop. No domínio: o conserto do kill do grupo em `templates/projeto/.githooks/pre-push` (fallback `kill -0 -- "-$etapa"` quando o `ps` não devolve o pgid), o teste novo `GrupoDaEtapa.test_ps_sem_resposta_com_o_grupo_criado_ainda_encerra_o_filho` (ps falso vazio), os mutantes G1 e G2 (`v047-ci-falhas-no-resumo-2.json`), o texto de comentário em `ci.yml`, `test_catraca.py` e a spec `v047-ci-rapido-3.json` (M25 e M26 acompanham o comentário), e `tests/test_forge.py` (classe `DocsPareceresPedidoECaminho`, vinda do item de pareceres). Linha de guarda mudada no diff: uma (a `[ -n "$pg" ] || {...}`), e os dois mutantes a cobrem (a condição `kill -0` e o corpo).

Rodado local, sem `-I`: `python3 -m unittest tests.test_prepush_so_docs`: `Ran 63 tests in 87.697s`, `OK (skipped=9)`; os 9 pulos são do sandbox (`/proc` de outro namespace de pid, `chown` fora do namespace), 6 deles em `GrupoDaEtapa`/`LimiteDaEtapa`, incluindo o teste do G2. O teste novo não foi pulado: rodou e passou, mas passa vazio aqui, porque `vivos()` lê `/proc` e vê outro namespace (A4 do review, de acordo).

```
forge-mutante --base 0f4a541379ec tests/mutantes/v047-ci-falhas-no-resumo-2.json
base=0f4a541379ec862622d23c1e330293bb7b78bb79 mb=0f4a541379ec862622d23c1e330293bb7b78bb79 rev=2cafdfd9002dbf27c078beaec74858d76b382323
forge-mutante: pedido=v047-ci-falhas-no-resumo rev=2cafdfd9002d spec=3bb5974762768a5325f1b42e77a7130c1178365923c04c7f7e614f226d967626
G1 · sobreviveu · templates/projeto/.githooks/pre-push:157
G2 · controle vermelho · templates/projeto/.githooks/pre-push
```
Isto é do ambiente, não prova de teste fraco, e não vale como "morreu": o veredito local é sem veredito. Para saber se o teste do G1 distingue, usei uma sonda minha, fora do repositório: reusei `GrupoDaEtapa` trocando `vivos()` por `kill -0` (que não depende de `/proc`) e `exigir` por nulo, rodando o teste novo numa cópia do head. Sem mutante: `OK`. Com o G1 aplicado (`de` trocado por `:`): `FAILED (failures=1)` em `test_ps_sem_resposta_com_o_grupo_criado_ainda_encerra_o_filho`, `assertTrue(ate(lambda: filho not in vivos(), 30))`, ou seja, o filho sobrevive sem o fallback. O G2 não pude sondar: o teste dele depende de `ps` e `/proc/<pid>/stat` no laço de vigia (`vigia`), sem substituto simples; fica sem veredito aqui (A3).

CI no mesmo sha (`run 44015249975`, PR do branch): as 10 partes da suíte (3.12 e 3.14, 1 a 5) e as verificações, passos, árvore, instalação e pulados deram success; `Catraca` (run 44015249948) success. O job `bateria (pareceres)` e, por ele, o agregador `bateria` falharam por `R-REVIEW`: os pareceres `docs/devops/` e `docs/security/` do item estão desatualizados em relação ao `ci.yml` mudado (comentário). Isso é dos pareceres desses donos, não do QA, e não é bug de produto. A suíte inteira do sha está provada nas partes; o `.verde` local não é citado (I5).

Vermelho antes do verde do teste novo: `forge-testes --vermelho 0f4a5413` não foi rodado (rodada passa de 550 s e o `/proc` do sandbox não prova de qualquer jeito). A prova vermelha do teste novo é a sonda acima: falha com o G1 (a base do conserto) e passa sem ele.

PA-7: AR-5 (python sem `-I`): nenhum caminho novo que decide; os testes sem `-I` seguem o brief. AR-12 (spec desatualizada): `v047-ci-rapido-3.json` M25 e M26 foram realinhados ao comentário do `ci.yml`; o `--conferir` das specs de mutantes não foi repetido, mas a suíte `FiacaoDoCI` (verde nas partes do CI) e a spec batem com o diff lido. AR-1 (um mutante por linha de guarda): cumprido (G1, G2). Classe nova: nenhuma.

Parecer: aprovado, sem bug crítico, alto, médio ou baixo; A1 e A2 do parecer anterior seguem recomendados, A3 novo recomendado.
