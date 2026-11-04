---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/tempo-b1
commit: b250b178dab0a1200945ac6bf8c120da1270a55b
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-04
---
# Parecer de QA - TEMPO-B1 (E6, L07)
Base 2c4cbf46b1e9f7f166e6504e27f13013ead1751f; código b250b178dab0a1200945ac6bf8c120da1270a55b; head testado 58e3f67d547ff6c21a43a09516a53ac12fd4c74a (só pareceres depois do código). Review (fb754b1) e segurança (58e3f67) aprovados.

## Escopo
A mensagem ao `forge:conferente` leva só o cabeçalho, com `Arquivo:` e `Brief-sha256:`, sem o texto do brief (D06 = A). Obrigações: `forge-check brief mensagem` (brief e entrega) imprime só o cabeçalho; o hook `hooks/agentes.py` libera a forma curta e a antiga e recusa o resto como antes (R-BRIEF).

## Tabela obrigação -> teste -> resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Forma curta com hash certo libera (brief e entrega) | sonda ponta a ponta + `test_mensagem_curta_com_hash_certo_libera_nos_dois_modos` | caminho relativo e absoluto | passa |
| Hash errado, maiúsculo, arquivo ausente, fora de `docs/briefs/`, `..`, sem `modo:`, sem hash, sem `Arquivo:`, duas `Arquivo:`, vazia: recusa | sonda + `test_mensagem_curta_recusa_...` | hash, caminho, forma | passa (rc 2) |
| Mensagem antiga com texto integral segue liberando | sonda ("antiga integral", "antiga entrega") + testes do módulo | compatibilidade | passa |
| `brief mensagem` imprime só o cabeçalho | `test_saida_so_com_cabecalho_hash_e_bytes`, `test_entrega_traz_tudo_do_arquivo_...` + execução real | 4 linhas (brief), sem `<<<BRIEF`/`BRIEF>>>` | passa |
| Nada recusado na base passa a liberar, salvo a forma curta | sonda diferencial base x head, 15 entradas | tabela abaixo | passa |

## Execução real
- Suíte inteira em 58e3f67 (`.githooks/pre-push --suite`, depois de `--status`): `Ran 2491 tests in 839.813s (4 processos)`, `OK (skipped=28)`, rc=0. Os 28 skips já vêm da base; não adicionei nenhum.
- `scripts/validar-plugin.sh`: `Validation passed`, rc=0. `bin/forge-check docs`: rc=0.
- Sonda do hook com `hooks/agentes.py` da worktree e da base 2c4cbf4 (registro de agentes limpo a cada chamada, para o R-TETO não contaminar), entradas em `$TMPDIR/qa-engineer-tempo-b1/probe.py`:
  - curta brief / entrega / caminho absoluto: head 0, base 0
  - hash errado, hash maiúsculo, arquivo ausente, fora de briefs, `..`, sem modo, sem hash, sem Arquivo, duas Arquivo, vazia: head 2, base 2
  - antiga integral (brief e entrega): head 0, base 0
  - Resultado idêntico nos dois: o hook decide igual; só o texto da recusa mudou. A forma curta já liberava na base.
- Saídas reais de `forge-check brief mensagem` (brief: 4 linhas; entrega: 11 linhas), sem delimitador; o hash impresso (41f3f9de...) é o do arquivo; ambas liberam no hook.
- Vermelho: `forge-testes --vermelho 2c4cbf4 --modulos test_agentes_hash_brief,test_mensagem_conferente`: `vermelho: base=2c4cbf46b1e9 head=58e3f67d547f`, `contagem: não prova (passa na base)=34; prova (asserção)=1`, rc=0. Prova: `test_entrega_traz_tudo_do_arquivo_e_o_desde_da_ultima_conferida` (base falha, head passa). Os testes de hook da forma curta passam na base por desenho (a base já a aceitava), e a sonda diferencial acima cobre isso. `test_forge.py` ficou de fora do vermelho por custo (a rodada inteira estourou 580 s); a saída só com cabeçalho está provada pela execução real.
- Mutação: nenhuma guarda mudou no diff (`forge-mutante --cobertura --base 2c4cbf4` não lista condição; as linhas mudadas são o texto de `bloquear` e a escrita da saída); sem mutante a declarar.
- Fixtures e acessibilidade: não se aplicam (sem tela).

## Achados
(nenhum)

## Registrados nos outros pareceres
Os recomendados do review (A1, A2) e da segurança (A1, A2, A3) seguem para o E15; sem achado novo de QA.

## Parecer
Aprovado: comportamento igual ao da base para toda entrada recusada, forma curta liberada, saída do `forge-check` só com cabeçalho.
