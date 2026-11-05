---
tipo: qa
contrato: 1
pedido: versao-035
branch: melhoria/brief-forma-aceita
commit: 4f2ef7ed87f238ba07b694c8d6ef1ce8f8b92219
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-05
---
# QA: versao-035, E7 BRIEF-FORMA-ACEITA

Etapa E2.6. Testado o commit 4f2ef7e (o HEAD da branch, 807426e, só soma o parecer de review). Sem gatilho de segurança (desenho, E7). Review aprovado sobre o mesmo commit.

suite: reusa · execução verde do pre-push sobre a mesma árvore 4f2ef7e (R-QA; decisão do dono de 2026-11-05 14:59): `Ran 2619 tests in 1661.449s (2 processos)`, `OK (skipped=30)`, `push_rc=0`, log /tmp/push-e7.log. Não rodei a suíte de novo (R-TETO).

## Achados
- A1 (recomendado) bin/forge-check:4567 · o comentário de FORMAS_DE_COMMIT diz heredoc só como <<'EOF' exato, mas o hook também aceita <<EOF sem aspas (mutante M5 sobreviveu, equivalente); só <<$'EOF' é recusado. Ajustar o texto; a oferta segue correta

## Critério → teste → resultado
Obrigação do E7 (pedido, Escopo): o brief gerado traz as formas de commit e merge que os hooks aceitam.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E7: brief de código traz cada forma de commit | FormasNoBrief.test_brief_de_codigo_traz_a_secao_com_cada_forma | tipo código; sem merge no brief de código | passou |
| E7: cada forma de commit passa no hook `conformidade` | FormasPassamNoHook.test_cada_forma_de_commit_passa_no_hook_conformidade_como_tech_lead | oferta não envelhece em relação ao hook | passou |
| E7: o teste do hook distingue aceita de recusada | FormasPassamNoHook.test_o_teste_distingue_aceita_de_recusada | recusa de `--no-verify` (R-VERIFY) | passou |
| E7: forma do merge vem do PQ de merge, uma vez | FormasNoBrief.test_etapa_de_merge_traz_a_linha_do_merge_uma_vez | etapa de merge: 1 ocorrência | passou |
| E7: brief de review não traz a seção | FormasNoBrief.test_brief_de_review_nao_traz_a_secao | tipo review | passou |
| E7: a seção não cai no Pronto quando (review A1) | FormasNoBrief.test_brief_gerado_e_preenchido_passa_na_forma_com_a_secao | forma ok com a seção presente | passou |
| mapa do forge-testes cobre o módulo novo | test_testes_tocados.Mapa.test_forge_check_roda_os_modulos_dele (40) | contagem de módulos | passou |

## Cenários e resultado real
Testes dos arquivos tocados (de `tests/`): `python3 -m unittest test_brief_forma_aceita test_testes_tocados`: `Ran 92 tests in 28.644s`, `OK`.

Vermelho antes do verde: `forge-testes --vermelho d9b26bb3e6b11e7d45c8b7ed81c7da7a8a325503 --modulos test_brief_forma_aceita`, rc 0:
```
vermelho: base=d9b26bb3e6b1 head=807426e5961a módulos=test_brief_forma_aceita (restrito por --modulos)
revertidos à base: bin/forge-check, bin/forge-testes, changelog.d/brief-forma-aceita.md, docs/reviews/brief-forma-aceita.md
contagem: não prova (passa na base)=2; prova (API ausente)=1; prova (asserção)=3
```
Os dois que passam na base são guardas negativas (review sem a seção; hook recusa `--no-verify`), que protegem fronteira e não regra nova; os três de comportamento novo e o de hook caem na base.

Mutantes (spec fora do repositório, lista minha, uma por linha de guarda do diff em `bin/forge-check`: 4554, 5967 e a forma heredoc de 4569), `bin/forge-mutante`:
```
M1 · morreu · bin/forge-check:4554   (seção fora do cabeçalho)
M2 · morreu · bin/forge-check:5967   (brief de código sem a seção)
M3 · morreu · bin/forge-check:5967   (etapa de merge sem a seção)
M4 · morreu · bin/forge-check:5967   (review com a seção)
M5 · sobreviveu · bin/forge-check:4569   (<<EOF sem aspas)
M6 · morreu · bin/forge-check:4569   (<<$'EOF')
```
M5 é equivalente: o hook aceita `<<EOF`, então a oferta continua válida (A1, recomendado). Mutante com cobertura de forma recusada (M6) morre.

Prazo e acessibilidade: não se aplicam (sem UI). Nenhum bug aberto.
