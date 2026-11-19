---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-meta85-forge-check
commit: a281e4a5565d8675b1047c997d727c9a5ab1231c
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-19
---
# QA: v0478 META85 em `bin/forge-check` (E34.5)

Head testado `6853e0ee` (o brief); o clone avançou por fast-forward até `f84d9f28` só com os pareceres de review e segurança.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Cartão 1: entrega exige `--mutantes` e `--pronto` | `test_meta85_entrega` (12 testes): sem logs, log ausente, vazio, outro head, rc=1, acima do teto, linhas vazias nas pontas, só o pronto faltando, fora da etapa codigo, sem código, forma nova recusa as opções | log vazio, ausente, maior que 8 MiB, head divergente | passou (12/12); vermelho: 10 provam, 2 de não cobrança passam na base por natureza |
| Cartão 2: `parecer delta` com `revalida:` | `test_meta85_revalida` (4 testes): barrou, aprovado com domínio intacto, aprovado com domínio mudado, review aprovado com código mudado | domínio mudado × intacto | passou (4/4); 4/4 provam |
| Cartão 3: `classe` barra mais de 10 arquivos | `test_meta85_item_arquivos` (6 testes): 10 passa, 11 recusa, `--json`, acompanhantes não contam, módulo do portão em `tests/` conta, base ilegível | 10 × 11, base ilegível | passou (6/6); 4 provam, 1 dá erro na base (A1), 1 não prova (10 arquivos passa também na base) |

## Provas
- Vermelho: `bin/forge-testes --vermelho eca1d21b --modulos test_meta85_entrega,test_meta85_revalida,test_meta85_item_arquivos` (sem `--modulos` a suíte estoura o prazo do sandbox):
  `contagem: não prova (passa na base)=4; prova (asserção)=17; sem veredito=1` · `tests.test_meta85_item_arquivos.ItemAteDezArquivos.test_testes_mutantes_changelog_e_pareceres_nao_contam · H=ok · B=erro · sem veredito` · rc=2.
- Mutantes M1 a M21 (`bin/forge-mutante` nas 4 specs, `--processos 4`): M1 a M21 `morreu`, nenhum sobrevivente, rc=0, `rev=6853e0ee2ac9`. `--cobertura --base eca1d21b`: todas as condições do diff `coberta`, nada sem mutante.
- Testes que o CI pega: `tests.test_forge.AntiDuplicacao` OK (2); `test_testes_tocados` OK (162, 1 pulado pelo sandbox, sem `/proc`); `forge-testes --texto` (inclui `test_metricas_texto`, `test_orcamento_instrucao`) rc=0, 217 OK.
- Suíte inteira não rodada local; vale o check-run `bateria` do mesmo sha no CI do PR.

## Cenários e resultado real
Caminho feliz, bordas (10/11 arquivos, log vazio, teto de 8 MiB, base ilegível) e erros cobertos acima. Sem permissões nem acessibilidade (CLI). Médio A1 vira cartão se o autor não corrigir antes do reenvio; o código de produção está certo (mutantes e testes verdes).

## Revalidação no head 99f474bb
Delta (`forge-check parecer delta`): `bin/forge-check`, mutantes -3, -5, -6, `test_meta85_item_arquivos` e `test_meta85_revalida`. O A1 (KeyError na linha 50) está resolvido: o teste usa `.get` e agora prova.
- Vermelho: `bin/forge-testes --vermelho eca1d21b --modulos test_meta85_entrega,test_meta85_item_arquivos,test_meta85_revalida`: `contagem: não prova (passa na base)=4; prova (asserção)=21`, nenhum erro, rc=0.
- Mutantes M22 a M32 (specs -5 e -6, `--base 6853e0ee`, `rev=99f474bbcb86`): todos `morreu`, nenhum sobrevivente.
- Testes novos de `riscos-aceitos` (`test_meta85_revalida`, com e sem aceite do usuário): provam na base (falham lá) e passam no head. Módulos rodados local: entrega 12 OK, item_arquivos 6 OK, revalida 7 OK.
- O remoto avançou um commit só de parecer de segurança (`c357c6c7`), trazido por fast-forward.
- Suíte inteira não rodada local; vale o check-run `bateria` do mesmo sha no CI do PR.

## Revalidação no head 06abb4fa
Delta (`forge-check parecer delta`, intervalo `99f474bb..06abb4fa`): `bin/forge-check` (`base_sem_flag_do_pr`, fonte única do `pr_da_cli` e do `revalida:`), mutantes -7 e `test_meta85_revalida`. O `parecer delta` agora revalida pela mesma base do `pr` sem `--base`.
- Vermelho: `forge-testes --vermelho 9afb847f --modulos test_meta85_revalida`: `contagem: não prova (passa na base)=8; prova (asserção)=2` (`test_base_que_ja_contem_o_head_revalida_como_o_pr`, `test_fora_da_branch_de_trabalho_revalida_pelo_diff_literal`), nenhum cai no HEAD, rc=0. O 3º teste novo da rodada (`test_branch_de_trabalho_pelo_sha_...`) passa na base por construção (a simulação já era a do `pr`); a proteção dele é o mutante M36.
- Mutantes M33 a M36 (spec -7, `--base 99f474bb`, `rev=06abb4fa3387`): todos `morreu` (M33 `:3585`, M34 `:1542`, M35 `:1541`, M36 `:1570`), nenhum sobrevivente.
- Módulo rodado local: `test_meta85_revalida` 10 OK.
- Sem achado bloqueante. Suíte inteira não rodada local; vale o check-run `bateria` do mesmo sha no CI do PR.

## Revalidação no head a281e4a5
Delta (`forge-check parecer delta`, intervalo `06abb4fa..a281e4a5`, sem o que veio da base): `bin/forge-testes`, `skills/briefs-e-conferencia/autor-ate-o-merge.md`, `tests/test_testes_tocados.py`; a junção com a develop resolveu os conflitos nesses três arquivos. No `bin/forge-testes`: progresso no stderr do `--vermelho` (teto e uma linha por módulo, módulos do diff primeiro) e os módulos `test_hooks_parecer_repo` e `test_hooks_parecer_matriz` na lista FORGE_CHECK.
- Módulos rodados local (`python3 -I -m unittest discover -s tests -p <módulo>.py`): `test_testes_tocados` 164 OK (1 pulado pelo sandbox), `test_meta85_entrega` 12 OK, `test_meta85_revalida` 10 OK, `test_meta85_item_arquivos` 6 OK.
- Vermelho com a lista de módulos: `forge-testes --vermelho 5ae868eb87e5 --modulos test_meta85_entrega`, rc=0: `vermelho: base=5ae868eb87e5 head=a281e4a5565d módulos=test_meta85_entrega (restrito por --modulos)` · `contagem: não prova (passa na base)=2; prova (asserção)=10`. O `--modulos` restringiu a um módulo e o progresso saiu no stderr (`[1/1] test_meta85_entrega H 7.5 s, B 6.3 s; 16 s no total`).
- Sem achado bloqueante. Suíte inteira não rodada local; vale o check-run `bateria` do mesmo sha no CI do PR.
