---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/f22-release-v2
commit: 1662e935dd6d8df041831dfb0d78ace2f2c8c289
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-04
---
# QA: versao-033 (F22, PR de release)

## Achados
- A1 (recomendado) tests/config.json:421 · nenhum invariante guarda "um só por candidato" nem "nunca --base"; sugerir em PR próprio (R-FLUXO).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Texto não manda o que o ci.yml recusa (PR só da homolog, versão e CHANGELOG) | leitura do diff contra ci.yml | base main, head homolog | passou |
| Texto não manda mesclar nem mudar base (release.yml só após merge; forge-fechar recusa base main) | leitura contra release.yml e bin/forge-fechar | R-MAIN | passou |
| Sem contradição nas skills, agentes e regras que falam de release | grep -rn release skills/ agents/ docs/regras/ | n/a | passou |
| Suíte estrutural | test_forge.py | n/a | passou |
| Neutralidade | tests/neutralidade.py | n/a | passou |

## Cenários e resultado real
Só texto (R-FLUXO, tech-lead, ci-cd, fragmento); sem código, sem vermelho/mutação aplicáveis.
- `python3 -I -m unittest discover -s tests -p test_forge.py`: 491 testes, OK, rc=0.
- `python3 -I tests/neutralidade.py`: rc=0.
- ci-cd, R-FLUXO e tech-lead dizem o mesmo (listar, conferir, editar só título e corpo, parar; mesclar é do usuário). Os checks citados existem como exemplos no ci.yml.
