---
tipo: qa
contrato: 1
pedido: lote-s1-scripts
branch: melhoria/lote-s1-scripts
commit: 8e22f173e103f04a77bab9152747f0d79473f9f0
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-24
---
# QA: lote-s1-scripts

Pedido LOTE-S1-SCRIPTS (E1 a E4; revisão LOTE-S1-SCRIPTS-REV, E3.1). Head testado `8e22f173e103f04a77bab9152747f0d79473f9f0`, base `3c66b881af31817ce5d2dde996c7ca56d54cb511`. Sem especificação de UX nem contrato de API: as obrigações são os itens E1 a E4 do pedido.

## Achados
- A1 (bloqueante) tests/mutantes/lote-s1-scripts.json:1 · o diff muda guardas em bin/ (chmod da pasta do log, link em changelog.d, versão de topo, teto do push --delete) e a branch não traz spec de mutantes; declarar um por linha de guarda (classe: guarda sem mutante)
- A2 (recomendado) bin/forge-fechar:178 · o mutante que remove `[ -O . ]` do subshell do chmod sobrevive; equivalente para usuário comum (chmod em pasta alheia já falha com EPERM) e a checagem de dono do caminho vem antes (linha 168); registrar a justificativa na spec do A1

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 modo da pasta do log vira 700, setuid e setgid saem | tests.test_fechar_log_check.FecharLogCheck.test_pasta_do_log_do_proprio_usuario_com_modo_diferente_de_700_vira_700_com_aviso (4755 e 6755 novos) | modos 755, 777, 500, 2755, 4755, 6755 | passou |
| E1 chmod age sobre a pasta já aberta, não sobre o caminho (TOCTOU) | ...FecharLogCheck.test_o_chmod_da_pasta_do_log_age_sobre_a_pasta_ja_aberta_e_nao_sobre_o_caminho | argumento do chmod é `.` | passou |
| E2 push --delete que trava é cortado pelo teto, 3 tentativas, remota dita viva, código 3 | tests.test_fechar_orfao.Teste.test_push_delete_que_trava_e_cortado_pelo_teto_e_a_remota_viva_e_dita | teto 1 s; remota segue no servidor | passou |
| E2 teto fora da faixa recusado; padrão 80 s (3x80 + pausas < 300 s) | ...Teste.test_teto_do_delete_fora_da_faixa_e_recusado_e_o_padrao_deixa_tres_tentativas_abaixo_de_300s | 0, 101, não numérico | passou (parte do padrão confere o texto-fonte, estrutural) |
| E3 changelog.d link: release não publica nem apaga .md externos | tests.test_changelog.Release.test_changelog_d_como_link_para_fora_da_raiz_nao_publica_nem_apaga_os_md_externos | pasta como link para fora | passou |
| E3 fragmento que é link para fora recusado, alvo fica | ...Release.test_fragmento_que_e_link_para_fora_da_raiz_e_recusado_e_o_alvo_fica | arquivo como link | passou |
| E3 `novo` com changelog.d link não grava fora | ...Release.test_novo_com_changelog_d_como_link_e_recusado_sem_gravar_fora | pasta como link | passou |
| E3 versão aninhada antes da de topo com manifesto já na versão alvo recusada | ...Release.test_versao_aninhada_antes_da_de_topo_com_o_manifesto_ja_na_versao_alvo_falha_sem_gravar_nada | topo = alvo, aninhado antes | passou |
| E4 aviso do perfil directory não sai como ✘ com validação passando | tests.test_forge.ValidarPluginAviso.test_aviso_do_perfil_directory_com_validacao_passando_nao_sai_como_x | rc 0 | passou |
| E4 falha real mantém ✘ e código | ...ValidarPluginAviso.test_validacao_que_falha_mantem_o_x_e_o_codigo | rc 1 | passou (guarda; passa também na base, por desenho) |

## Cenários e resultado real
- Suíte dirigida do lote (`python3 -m unittest tests.test_fechar tests.test_fechar_log_check tests.test_fechar_orfao tests.test_changelog tests.test_forge`, head): `Ran 577 tests in 164.650s · OK (skipped=1)`. O skip é `FragmentoTemONomeDaBranch` (worktree em HEAD solta, branch não é `melhoria/*`), preexistente e não adicionado pelo lote.
- Vermelho (`forge-testes --vermelho 3c66b881af31817ce5d2dde996c7ca56d54cb511 --prazo 900`, saída 0): abre com `vermelho: base=3c66b881af31 head=8e22f173e103`; `revertidos à base: bin/forge-changelog, bin/forge-fechar, changelog.d/lote-s1-scripts.md, scripts/validar-plugin.sh`; `contagem: não prova (passa na base)=1936; prova (asserção)=9; pulado=1`. Os 9 que provam são os 9 testes novos ou ampliados da tabela acima, todos `H=ok · B=falha`.
- Mão, forge-changelog em repositório de brinquedo em `$TMPDIR/qa-engineer-lote-s1-scripts/cl`: `release` e `novo` com `changelog.d` como link para pasta externa: `changelog.d: link simbólico ou fora da raiz do repositório; recusado.`, rc=1, `e.md` externo intacto, CHANGELOG sem mudança. Manifesto `{"extra": {"version": "9"}, "version": "0.2.0"}`: recusado, nada gravado. Manifesto aninhado antes com topo 0.1.0: recusado (a troca textual pegaria o campo errado). Manifesto com o aninhado depois do topo: passa, topo trocado, aninhado intacto (sem falso positivo).
- Mão, forge-fechar com `push --delete` que trava de verdade (pre-receive do remoto dormindo 30 s, `FORGE_FECHAR_TETO_DELETE=2`, fluxo completo sobre o harness de gh e forge-check falsos): `registro: apagando a branch remota melhoria/x (até 2s por tentativa, 3 tentativas)`, `limpeza: remota=pendente worktree=ok branch=ok`, aviso `a branch remota continua viva`, rc=3, 7,9 s no total, remota ainda no servidor.
- `scripts/validar-plugin.sh` real: `aviso do perfil directory (não reprova; a validação passou): 1 problem ...`, `✔ Validation passed`, rc=0. A linha `⚠ Found 1 plugin directory warning` do validador segue como veio.
- shellcheck (`-S warning`): `bin/forge-fechar` 1 ocorrência na base e 1 no head (a mesma, preexistente); `scripts/validar-plugin.sh` 0 e 0.
- Mutação (spec minha, fora da branch, em `$TMPDIR/qa-engineer-lote-s1-scripts/lote.json`, 8 mutantes, um por guarda mudada), `forge-mutante` rc=1:
  - `M1 · morreu · bin/forge-changelog:74` · `M2 · morreu · bin/forge-changelog:162` · `M3 · morreu · bin/forge-changelog:109` · `M4 · morreu · bin/forge-changelog:136`
  - `M5 · morreu · bin/forge-fechar:178` (tirar `u-s`) · `M6 · morreu · bin/forge-fechar:178` (chmod no caminho em vez de `.`) · `M7 · morreu · bin/forge-fechar:122` (sem `timeout`)
  - `M8 · sobreviveu · bin/forge-fechar:178` (sem `[ -O . ]`): ver A2.
- Não executado: acessibilidade e E2E de navegador (sem interface); PA-7 (`docs/engineering/achados-recorrentes.md`) está vazio ("nenhum ainda"), nada a conferir.

## Riscos
- `timeout` mata só o `git push`; um filho do pre-push que ignore o sinal pode sobreviver ao corte (não provado, não bloqueia).
- Sem o `timeout` no PATH, a limpeza roda sem teto (desenhado e documentado no código).
