---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-heredocs-orcamento
commit: ec8997a6bfb365a9061316ea7905d12e8d5279a7
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-14
---
# Review: v047-heredocs-orcamento (TESTE-HEREDOCS-ORCAMENTO-ESTAVEL)

Etapa E1.211 do pedido v047 (instância revisora, não a autora). Diff lido inteiro: `origin/develop..ec8997a6` (base `f4b0c2ae`, igual ao merge-base), um commit. Classe C: só código de apoio dos testes; `hooks/` não muda.

## O que a branch entrega
- `tests/apoio_volta_unica.py:50-59`: `menor_custo(medir, limite, vezes=3)`, a menor de até 3 medidas, parando na primeira abaixo do limite (estrito, como o `assertLess`).
- `tests/test_hooks.py:986-999`: `medir_o_hook`, a medida única do hook real (CPU dos filhos por `RUSAGE_CHILDREN`, prazo da linha largo, montagem fora da janela, pasta nova a cada medida; parede sem `resource`). O teste do orçamento de heredocs passa a usá-la no lugar do bloco que repetia a mesma montagem.
- `test_linha_adversaria_de_crases_e_pastas_recusa_dentro_do_orcamento` (`:1109-1144`) troca o relógio pela CPU do hook, com o mesmo limite (metade do timeout do `hooks.json`); a parede vai à mensagem. A garantia de parede em produção segue com o vigia de 3 s, testado à parte (`test_t_vigia_*`), a mesma decisão já registrada na docstring do teste de heredocs.
- `test_comando_logico_*` e `test_tirar_heredocs_em_tempo_linear` envolvem a medida em `menor_custo`; limites 1,0 s e 3,0 s iguais.
- Nenhum limite muda (conferido linha a linha no diff). A afirmação "a carga só soma" vale para CPU de processo (contenda de cache e troca de contexto não tiram custo); um custo do código acima do orçamento passa dele nas três medidas, e o teste `test_regressao_passa_do_limite_nas_tres_e_para_na_terceira` fixa isso.

## M14
`git diff --numstat --no-renames origin/develop...HEAD`: `tests/apoio_volta_unica.py` 13+1, `tests/test_hooks.py` 55+43, `tests/test_medida_cpu.py` 33+1; total 146 linhas que contam (fora o fragmento `changelog.d/` e a spec `tests/mutantes/`). Abaixo de 150, um comportamento só. Cumpre.

## Guardas e mutantes
Linhas de guarda mudadas: `apoio_volta_unica.py:55` (`range(vezes - 1)`), `:56` (`if melhor[0] < limite`), `:58` (`min`). Spec `tests/mutantes/v047-heredocs-orcamento.json`, M1 a M4, um por linha (o `:56` com dois, quebra e limite estrito). Cada um tem teste de comportamento em `tests/test_medida_cpu.py` (`MenorCustoDasMedidas`), com medidas falsas, sem ler a fonte nem rodar subprocesso.

## Ferramentas (citadas, não refeitas)
- `bin/forge-mutante --processos 1 tests/mutantes/v047-heredocs-orcamento.json` (rev `ec8997a6bfb3`): M1, M2, M3, M4 `morreu`.
- `bin/forge-mutante --cobertura --base f4b0c2ae`: `coberta · tests/apoio_volta_unica.py:56 · M1, M2`; rc=0, sem condição descoberta.
- `python3 -m unittest tests.test_medida_cpu.MenorCustoDasMedidas`: `Ran 3 tests` `OK`.
- `python3 -m unittest` dos três testes de orçamento tocados que cabem no teto (`test_comando_logico_le_os_limites_uma_vez_por_texto`, `test_tirar_heredocs_em_tempo_linear`, `test_linha_adversaria_de_crases_e_pastas_recusa_dentro_do_orcamento`): `Ran 3 tests in 23.791s` `OK`.
- Suíte inteira: só no CI do PR, que ainda não existe (o brief pede sem PR); o teste de heredocs longo (`test_muitos_heredocs_*`) fica para ele.

## Leitura (checklist da skill)
1. Faz o que o cartão pede (orçamento estável sob carga, limites iguais), nem mais. 2. Classe C, sem `hooks/`; R-NEUTRO sem termo novo. 3. `medir_o_hook` tira a duplicação da montagem. 7. Os três ramos do `menor_custo` têm teste. 11. Não há teste de ausência novo. 12. Sem falso de `git`/`gh`.

## Achados
- A1 (recomendado) tests/apoio_volta_unica.py:58 · `min(melhor, medir())` compara a tupla inteira: com custo empatado cai nos demais campos (no `tirar_heredocs`, listas de corpos), que podem não ser comparáveis; `min(..., key=lambda m: m[0])` deixa o critério só no custo.
- A2 (recomendado) tests/test_hooks.py:3290 · o comentário do fim ainda diz que o apoio define "as duas funções" antes do import; agora são três (`menor_custo`), como o próprio apoio já corrigiu na linha 25.

## Sondas

## Parecer
Aprovado no head `ec8997a6`. A troca de relógio por CPU e o menor de três medidas deixam o orçamento estável sob carga sem afrouxar limite, e um custo de código acima do orçamento continua reprovando nas três medidas. A1 e A2 são recomendados e não devolvem (R-REVIEW).

## Revalidação
E1.219: delta lido por `forge-check parecer delta` em `ec8997a6..596e9946`: nenhum arquivo do domínio mudou. Só o campo `pedido:` do frontmatter foi corrigido para `v047`; veredito e `commit:` iguais.
