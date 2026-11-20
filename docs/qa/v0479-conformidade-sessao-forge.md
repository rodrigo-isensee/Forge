---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-sessao-forge
commit: fe8607dfc22953432cf43dbf4ea4fbf2158292d2
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0479-conformidade-sessao-forge (E51.5)

Diff 0f6034ea..fe8607df: `hooks/conformidade.py` (travas na `GuardaDaProva`), `hooks/vigia.py` (clone do Forge como projeto), 13 fixtures `e51-*` (11 em `conformidade`, 2 em `vigia`), classe `HookSessaoDoForge`, spec de 7 mutantes. Pedido de controle. Suíte inteira: só no CI do PR, não rodada aqui. O remoto avançou só com pareceres de review e segurança (código segue em fe8607df); trazido por merge.

## Critério → teste → resultado
| Critério (obrigação) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Na sessão do Forge (wt/* e clone) as travas valem para todo papel: R-MAIN, R-VERIFY, push para integração, tag v* | `HookSessaoDoForge.test_travas_do_conformidade` (11 fixtures) | papel sem lista, wt/* e clone; mínimo 11 | passou no head; 8 recusas caem na base |
| O resto da linha segue livre (ADR 0009, seção 6) | mesmo teste: `escrita-dev-libera`, `push-branch-tech-lead-libera`, `tag-lista-libera` | push de branch de trabalho, `git tag -l`, escrita | passou |
| O `vigia` grava `violacoes.jsonl` na sessão do Forge | `HookSessaoDoForge.test_vigia_registra` (2 fixtures) | mínimo 2; contorno e arquivo em vigor | passou; erra na base |
| Alvo opaco com ação crítica (variável no push) | caso de abuso do QA, sem teste no branch | `B=develop; git push origin $B`, `F=--force; git push $F origin melhoria/x` | FALHA: saída 0, esperado 2 (A1) |

## Provas
Classe no head: `python3 -I -m unittest discover -s tests -p test_hooks.py -k HookSessaoDoForge`: 2 testes, OK.

Mutantes (`bin/forge-mutante tests/mutantes/v0479-conformidade-sessao-forge.json`, saída 0, 19 s):
```
forge-mutante: pedido=v0479-conformidade-sessao-forge rev=fe8607dfc229 spec=81bf549b656c5bb636c72c71853311c40e07d096a3029a23bf97fa537fbb8548
M1 · morreu · hooks/conformidade.py:3762
M2 · morreu · hooks/conformidade.py:3784
M3 · morreu · hooks/conformidade.py:3784
M4 · morreu · hooks/conformidade.py:3784
M5 · morreu · hooks/conformidade.py:3784
M6 · morreu · hooks/conformidade.py:3915
M7 · morreu · hooks/vigia.py:509 · (erro) o teste declarado deu erro sob o mutante e passa sem ele
```
Cobertura (`--cobertura --base 0f6034ea`): linhas 3762 (M1) e 3784 (M2-M5) cobertas; nenhuma condição mudada sem mutante. Os mutantes passam, mas a spec não inclui o alvo opaco (A1): o conjunto morto não cobre o defeito.

Vermelho: `bin/forge-testes --vermelho 0f6034ea5aaaab5f0aab8acb593523497cdc3b6f --modulos test_hooks --prazo 1500` deu rc=2, sem veredito (módulo inteiro: H 1153 s, B estourou 1500 s; `-k` não combina com `--vermelho`):
```
vermelho: base=0f6034ea5aaa head=fe8607dfc229 módulos=test_hooks (restrito por --modulos)
revertidos à base: changelog.d/v0479-conformidade-sessao-forge.md, docs/hooks.md, hooks/conformidade.py, hooks/vigia.py
test_hooks · sem veredito (prazo, sinal ou executor sem registro em B)
```
Vermelho manual, só a classe (cópia do head com `hooks/conformidade.py` e `hooks/vigia.py` da base): `FAILED (failures=8, errors=2)`; caem os 8 `bloqueia` de conformidade (clone-push-force, wt-commit-no-verify, wt-pr-merge-admin, wt-push-develop, wt-push-force, wt-push-main, wt-push-tag, wt-tag-tech-lead) e erram as 2 de vigia; os 3 `libera` passam, como devem. Não substitui o veredito da ferramenta.

Abuso (cópia do head com 2 fixtures extras, esperado 2): `B=develop; git push origin $B` e `F=--force; git push $F origin melhoria/x`, como `forge:tech-lead` em `wt/x`, saem 0. Confirma o A3 do review e o A1 da segurança.

## Achados
- A1 (bloqueante) hooks/conformidade.py:3784 · `trava_da_sessao_do_forge` não reconhece a recusa "ação crítica: o hook não modela" (alvo opaco): `B=develop; git push origin $B` e `F=--force; git push $F origin melhoria/x` saem 0 em wt/*; no projeto recusam. Incluir essa recusa no predicado.
- A2 (bloqueante) tests/mutantes/v0479-conformidade-sessao-forge.json:1 · sem fixture nem mutante do alvo opaco com ação crítica; ao corrigir o A1, somar fixture `e51-*` e mutante que a mate.
- A3 (recomendado) bin/forge-testes:1 · `--vermelho` não combina com `-k` e o módulo `test_hooks` passa de 1500 s só na base: sem veredito para pedido que mexe numa classe. Cartão: aceitar `--vermelho` com `-k` ou classe.
