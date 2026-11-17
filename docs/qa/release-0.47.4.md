---
tipo: qa
contrato: 1
pedido: release-0.47.4
branch: melhoria/v0474-release-0474
commit: f198cfbd8261eb15acee8adbb95709484f524097
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-17
---
# QA: release 0.47.4 contra a main (v0474, E4.8)

Head `2539b54f` (PR 640). Base: parecer `docs/qa/v0474-release-0474.md` (aprovado no `f198cfbd`); desde então a branch só soma pareceres de segurança e de review (docs) e merges da própria branch. Suíte inteira: check-run `bateria` do mesmo sha no PR; a suíte local completa não foi rodada.

Nota (E4.12): `commit:` aponta para o Revisar-sha `f198cfbd` (commit da versão); o `2539b54f` só tem parecer (AQ-5). O conteúdo revisado é o mesmo.

Sem achados (o bloco `## Achados` fica de fora).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Versão sobe contra a main | `python3 scripts/conferir-release.py --base origin/main`: base 0.47.3, release 0.47.4 | versão igual à da main | passou |
| `changelog.d/` sem pendentes | `bin/forge-changelog conferir-release` | pasta só com README | passou |
| Testes do changelog e da release | `python3 -m unittest tests.test_changelog tests.test_conferir_release` | n/a | passou (106, OK) |
| Plugin válido | `scripts/validar-plugin.sh` (sem -I): marketplace, plugin e dev | n/a | passou |

## Notas
- Os `deny api.anthropic.com` do `validar-plugin.sh` são do sandbox, não da validação.
- Vermelho antes do verde e mutação: não se aplicam; a marca não traz teste novo nem regra de código.
- Cartão do mutante pulado (G1 e G2 do spec `v047-ci-falhas-no-resumo-2`, teste pulado por /proc do sandbox): pulado por ordem do caller; segue como cartão médio a abrir pelo Jarvis, sem bloquear a versão. Não conta como bug aberto desta release.
- Sem bugs abertos.
