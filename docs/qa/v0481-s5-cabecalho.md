---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-s5-cabecalho
commit: e216aa71cd0e5e720ce00da880a6e4adfd8464fd
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-26
---
# QA: v0481 S5 (cabeçalho do parecer em `frente`), PR #917, 1ª rodada

## Achados
- A1 (bloqueante) bin/forge_autorizacao.py:232 · R-QA: a catraca do CI falha e `forge-mutante --cobertura` confirma: a guarda `texto.startswith('---\n')` (base:230) saiu como "apagada" sem mutante que a cubra; M1 só cobre a condição nova. Declare mutante para ela ou a isenção da spec.
- A2 (recomendado) tests/test_autorizacao.py:374 · `FIXA ={` perdeu o espaço antes do `{` no diff, sem relação com S5; restaurar `FIXA = {`.
- A3 (recomendado) bin/forge_autorizacao.py:232 · O topo exige `---` exato, o `ler_frontmatter` aceita `---` com espaços (`.strip()`); falha fechada (vazio), mas `frente` e o validador divergem: alinhar ou registrar a diferença.

## Critério → teste → resultado
Sem especificação de UX: as obrigações são as do brief (S5, E25.1).

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| S5a: linha começando com `---` (ou `---` dentro de valor) não fecha o cabeçalho | `Frente.test_tracos_dentro_de_um_valor_ou_no_comeco_de_outra_linha_nao_fecham`; `ItemPresoAoCommit.test_linha_que_comeca_com_tracos_no_cabecalho_nao_recusa_o_parecer_e_o_corpo_nao_aprova` | `---x`, `----`, `a --- b` | passou; falha na base |
| S5b: sem fecho, vazio (o corpo não vale) | `Frente.test_sem_fecho_ou_sem_tracos_no_topo_e_vazio` | sem fecho, sem `---` no topo, ` ---` no topo, texto vazio | passou; falha na base |
| S5c: fecho como o `ler_frontmatter` (`strip() == ---`) | `Frente.test_fecho_com_espaco_vale_e_o_corpo_nao_entra` | fecho com tab e espaço | passou; falha na base |
| Corpo não sobrescreve o reprovado | caso 2 do teste de integração acima (`parecer: reprovado` no cabeçalho, `aprovado` no corpo) | fecho ` ---` | passou |

A decisão do time de aceitar o `strip` no fecho (igual ao validador da ADR 0004, em vez da comparação exata do brief) confere: `bin/forge-check:258-267` fecha com `linha.strip() == "---"`; o fecho de `frente` é igual. Só o topo diverge (A3).

## Cenários e resultado real
- Diff lido contra a base `3c833f3f` (merge-base): 4 arquivos (`bin/forge_autorizacao.py`, teste, spec de mutantes, fragmento do changelog); escopo bate com E25.1.
- Módulo tocado, local: `python3 -m unittest tests.test_autorizacao` · 25 testes, OK.
- Vermelho antes do verde: `bin/forge-testes --vermelho 3c833f3f1ba1e9770b8e5b10e7a1b0ed588d161f --modulos test_autorizacao` · `vermelho: base=3c833f3f1ba1 head=e216aa71cd0e módulos=test_autorizacao`; `prova (asserção)=4` (as 3 de `Frente` e o de integração, H=ok, B=falha), `não prova (passa na base)=21` (herdados), rc 0.
- Mutantes: `bin/forge-mutante tests/mutantes/v0481-s5-cabecalho.json` · pedido=v0481-s5-cabecalho rev=e216aa71cd0e; M1 morreu (L232), M2 morreu (L235), M3 morreu (L237), M4 morreu (L236, `(erro)`: o teste declarado dá erro sob o mutante e passa sem ele). Nenhum sobrevivente.
- Cobertura: `bin/forge-mutante --cobertura --base 3c833f3f1ba1e9770b8e5b10e7a1b0ed588d161f` · L232 M1, L235 M2, L236 M4 `coberta`; `apagada · bin/forge_autorizacao.py:230(base) · texto.startswith('---\n')` (A1).
- CI no head exato (`gh pr checks 917`), lido nos logs:
  - `catraca` falha: a mesma linha `R-QA: guarda de bin/forge_autorizacao.py mudada sem mutante declarado: apagada ... texto.startswith('---\n')` (A1).
  - `bateria (passos)` falha: infraestrutura, o download do actionlint saiu com `curl` 56 e `actionlint`/`zizmor` deram 127 (falta de binário); não vem do diff.
  - `bateria (pareceres)` falha: espera o parecer de review do PR (R-REVIEW); some quando houver parecer aprovado.
  - `bateria` e `bateria (python 3.14)` falham por consequência: as partes da suíte ficaram `skipped` porque os passos falharam.
  - `instalação (python 3.14)` e `árvore já provada na develop` passam.
  - Sem `- ci: <sha> verde`: as partes da suíte não rodaram no head (a falha de infraestrutura pede rerun com o motivo do log acima); a evidência local é o módulo tocado e os mutantes.
