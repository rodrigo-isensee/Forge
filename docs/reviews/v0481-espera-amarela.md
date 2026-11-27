---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-espera-amarela
commit: 517557abcd34a5605bac2c37b3d344acb953ed61
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-27
---
# Review: v0481 (E47.2, #948, espera amarela, 1.ª rodada completa)

Diff lido inteiro `319a968d..517557ab` (3 commits do E47.1), no clone de revisão `/root/.forge-contrib/wt/v0481-espera-amarela-tech-lead-2`, no head `517557ab`.

## CI e ferramentas (citadas, não refeitas)
- ci: 517557abcd34a5605bac2c37b3d344acb953ed61 verde
- `gh pr checks 948`, run `46072616070` (ci.yml) e `46077654097` (catraca.yml), head `517557ab`: suíte 3.12 (5/5), `bateria (passos)`, `bateria (python 3.14)`, `bateria (verificações longas)`, `instalação (python 3.14)`, `teto de pulados (python 3.12)` e `árvore já provada na develop` verdes. Vermelhos que esperam: `bateria (pareceres)` e `bateria` (R-REVIEW sem parecer, log do job) e `catraca` com `catraca (conferência)`, que é o antigo job `catraca` partido em dois: o passo de regras falha só por R-CONFORMIDADE sem o rótulo (script da base, sem o rc 3), e o passo do texto do PR (T1) está verde.
- Testes do diff, à mão: `python3 -m unittest` de `test_catraca.{EsperaNaoEVermelho,Workflows,PrazoTotalDaApi}`, `test_ci_local`, `test_forge_pronto.ProvaDoCi`, `test_modelos_projeto.TestPassoAPassoDaProtecao`, `test_pre_envio_brief.ChecksForaDaLinhaDoCi`, `test_suite_partes.FiacaoDoCI` · 134 testes, OK.
- Mutantes: `bin/forge-mutante --processos 1` nas duas specs do item · M1 a M12 morreram; M6 realinhado de `v047-ci-parecer-job.json` (`--ids M6`) morreu. `--cobertura --base 319a968d`: as guardas novas de `tests/catraca.py` (2137, 2272, 2280) cobertas por M1 a M4; os workflows a ferramenta não mede, e as linhas de guarda deles (ci.yml 618 a 620, catraca.yml 58 a 60 e 82) têm M5 a M11, com teste de comportamento que roda o fim do passo em subprocesso com `python3` e `gh` falsos.
- Teto (H1): 75 linhas de código (+75 -8 em `.github/workflows/`, `scripts/ci-local` e `tests/catraca.py`, comentários inclusos), abaixo de 150; um comportamento só.

## Leitura
1. Escopo: faz o que o E47.1 pede e a ordem do dono de 26/11 21:39: espera sai com 3, o agregador troca de nome e o check exigido fica pendente, ainda barrando a junção. A lista de checks exigidos não muda.
2. Nenhum caso de defeito cai no rc 3 do script. Modo pareceres: o rc 3 exige todas as violações com a marca, e a marca só entra quando todas as linhas do `cmd_pr` casam `LINHA_DE_ESPERA` (ausente, da branch ausente, `commit: desatualizado`). Reprovado, forjado (`commit não existe`), autoria, `ci:` e o `nao_aprovam` não casam e seguem no rc 1; qualquer linha nova do `cmd_pr` cai no vermelho por padrão (falha fechada). Modo regras: rc 3 só com o título `[afrouxa-regra`, sem custo, sem liberação e com os eventos da API lidos; `ErroDeGit` segue no rc 1.
3. Workflows: rc diferente de 3 sai com o próprio rc; API que falha e check exigido já verde no head ficam vermelhos. O `always()` no agregador da catraca.yml é necessário: sem ele a conferência vermelha pularia o agregador e `catraca` pulado contaria como verde; com `!cancelled()` o run cancelado também deixaria o pulo. O afrouxamento de asserção (`checks: read`, `always()`) vem no título com `[afrouxa-regra`; o script do modo pareceres roda sem o token (`env -u`). Segurança e devops dão o parecer próprio.
4. Os 4 testes realinhados (`test_forge_pronto`, `test_modelos_projeto`, `test_pre_envio_brief`, `test_suite_partes`) tiram só o sufixo `${{ needs.<id>.outputs.espera }}` no fim do nome, e o `test_suite_partes` ainda afirma que nenhum outro job se chama `bateria`. Os dois testes com valor esperado trocado que a catraca aponta (`test_gate_do_ci_nao_deixa_codigo_escapar_nem_forjar_o_verde`, `test_leitor_entende_matriz_e_needs_do_ci_real`) mudam pelo motivo do item e ficam mais estritos (o `always()` da catraca.yml só no agregador, sem `uses:` nem script).
5. Commits em Conventional Commits em português, com pedido e etapa; fragmento em `changelog.d/`.

## Achados
- A1 (recomendado) docs/protecao-de-branch.md:29 · "Defeito segue vermelho com o nome exato" falha na combinação: suíte vermelha e parecer ausente dão `bateria (espera parecer)` vermelho e `bateria` pendente (ci.yml:681); idem T1 vermelho e rótulo ausente (catraca.yml:70). Junção barrada; corrigir o texto ou pôr o sufixo só com os needs verdes.
- A2 (recomendado) .github/workflows/catraca.yml:8 · Com o `edited`, o run de título sem `[afrouxa-regra` deixa `catraca` vermelho no head; corrigido o título, o run novo espera com outro nome e o vermelho velho fica até o rótulo. É o mesmo limite do run cancelado, já documentado; vale citar este caso na linha 29 da proteção.

## Parecer
Aprovado no head `517557ab`. O script não leva defeito ao rc 3, os workflows falham fechados (rc, API, verde velho, conferência não verde), o teto de 150 linhas é respeitado, os 4 testes realinhados seguem estritos e os 12 mutantes do item mais o M6 realinhado morrem. A1 e A2 são recomendados: a junção nunca fica aberta e o vermelho aparece em outro nome. Viram cartão depois do merge.
