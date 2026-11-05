---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/lote-textos-033
commit: 0349217471b8d9ccd4be4f1e3d11a700e055fb57
parecer: aprovado
escopo: completo
revisor: forge:qa-engineer
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-03
---
# QA: lote de textos L02 da 0.33 (E13, E17, E20)

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E13: o autor envia a branch de trabalho; o PR é do integrador (FLUXO-6 = A) | leitura do diff em `agents/jarvis.md` (passo 5) e grep de "sem push" em `agents/`, `skills/`, `stacks/` (nenhuma sobra) | push sem `-u`, conferindo a branch; PR fora do autor | passou |
| E17: pasta literal de logs por pedido no modelo de brief | leitura do diff em `skills/briefs-e-conferencia/SKILL.md` | `$TMPDIR/<papel>-<pedido>/`, nunca nome genérico | passou |
| E20: sessão de projeto não roda a suíte do Forge, o CI do PR roda (Q6, leitura 2) | leitura do diff em `skills/contribuir-com-o-forge/SKILL.md` (seção 5); grep de `unittest discover` em `agents/` e `skills/` | "três verdes" virou "duas verdes e os testes tocados"; só a menção de proibição resta | passou |

## Execução
- Suíte inteira sobre afe1248 (`.githooks/pre-push --suite`): `Ran 2489 tests in 856.814s (4 processos)`, `OK (skipped=28)`, rc=0.
- `scripts/validar-plugin.sh`: `Validation passed`.
- `bin/forge-check docs`: rc=0.
- Contradição: nenhuma frase de `agents/` ou `skills/` manda o autor ficar sem push nem manda a sessão de projeto rodar a suíte inteira; `agents/qa-engineer.md` e as regras D-5 tratam do QA do Forge, não da sessão de projeto.
- Só texto: nenhum teste novo nem mutante (sem código de controle); vermelho antes do verde não se aplica.
- PA-7 (`docs/engineering/achados-recorrentes.md`): conferido, nenhuma classe se aplica a texto sem teste.
