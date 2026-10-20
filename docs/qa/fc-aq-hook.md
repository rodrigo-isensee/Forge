---
tipo: qa
contrato: 1
pedido: fc-aq-hook
branch: melhoria/fc-aq-hook
commit: f058327f0dbed7dcc9e7eec11140eac02e6b358d
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-20
---
# QA: fc-aq-hook

Código testado: f058327 (HEAD do remoto 77e06a7 só acrescenta pareceres). Sem plano antecipado (pedido de política sem especificação de UX); os critérios são E1 a E3 e PQ-1/PQ-2 do pedido.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 aq grava em propostas/ e arquitetura/ do clone | `test_aq_grava_so_nas_duas_pastas_do_clone_de_contribuicao` (subtestes propostas, arquitetura) + extra: subpasta `arquitetura/sub/x.md` | permissão concedida só às duas pastas | passou |
| E2 recusa em pedidos/, KANBAN.md, outra pasta de docs, fora do clone | mesmo teste (pedidos, quadro, outra pasta de docs, fora do clone) | permissão negada fora da lista | passou |
| E2 travessia `..` | mesmo teste (travessia) | caminho que sai da pasta liberada | passou |
| E2 link simbólico para fora | mesmo teste (link para fora) + extra: `~/.forge-contrib` inteiro como link para fora | alvo real fora do clone | passou |
| Maiúsculas trocadas (brief) | extra: `DOCS/Propostas`, `.Forge-Contrib` | caixa do caminho | recusado (código 2), passou |
| Outros papéis sem mudança | extra: tech-lead, backend-dev, qa-engineer gravando nas duas pastas: resultado idêntico com o json da develop e o da branch (a lista `escrita_permitida` só restringe quem tem entrada, o aq; ganho de permissão do aq não vaza) | permissão por papel | passou |
| E3 ADR 0009 e changelog.d | suíte (testes estruturais, `test_aq_tem_papel_e_lista_de_escrita_no_hook`) | n/a | passou |
| PQ-2 suíte e validação do plugin | comandos abaixo | n/a | passou |

## Cenários e resultado real
- Suíte `python3 -m unittest discover -s tests -q` na worktree: Ran 952 tests in 307.665s, OK.
- `scripts/validar-plugin.sh`: Validation passed (os avisos de rede negada no sandbox são do ambiente, sem efeito).
- Vermelho antes do verde: cópia limpa do commit com `hooks/conformidade.json` de 50997b7 (develop) em `$TMPDIR/cp`, `python3 -m unittest tests.test_hooks.Hooks.test_aq_grava_so_nas_duas_pastas_do_clone_de_contribuicao`: FAILED (failures=2), subtestes propostas e arquitetura (`2 != 0 : R-CONFORMIDADE: o papel aq escreve só em docs/propostas/, docs/arquitetura/`). Com o json da branch: passa.
- Casos extras (script em `$TMPDIR/extra.py`, HOME descartável, fora do repositório, não commitado): todos como o esperado no json da branch; com o json da develop só a subpasta de arquitetura falha (esperado).
- Teste instável: nenhum (nada falhou e passou de novo sem mudança).

## Bugs
Nenhum.
