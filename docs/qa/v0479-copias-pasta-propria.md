---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-copias-pasta-propria
commit: 48a6e19b88bac450f1b749c1351d6396db35632e
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: v0479-copias-pasta-propria

Escopo: `bin/forge-copia` (cópia de projeto em `<projeto>/.forge/wt`, fora do git por `.gitignore` `*`; o Forge segue em `~/.forge-contrib`). Sem suíte inteira local (o CI do PR roda a bateria).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Projeto clona em `.forge/wt`, git do projeto limpo | `Projeto.test_clone_fica_em_forge_wt_e_fora_do_git_do_projeto` | pasta fora do git | passou |
| Projeto recusa a pasta do Forge | `Projeto.test_projeto_recusa_a_pasta_do_forge` | destino fora da liberada | passou |
| De dentro de uma cópia vale a pasta do projeto | `Projeto.test_de_dentro_de_uma_copia_vale_a_pasta_do_projeto` | cwd aninhado | passou |
| `.gitignore` existente não é tocado | `Projeto.test_gitignore_que_ja_existe_nao_e_tocado` | arquivo pré-existente | passou |
| Forge (`.claude-plugin/`) segue no home | `Projeto.test_o_forge_segue_com_a_pasta_do_home` | projeto x Forge | passou |
| Fora de git vale o home | `Projeto.test_fora_de_git_vale_a_pasta_do_home` | sem repositório | passou |
| Limpar apaga a cópia do projeto | `Projeto.test_limpar_apaga_a_copia_do_projeto` | limpeza | passou |

## Cenários e resultado real
- `test_forge_copia`: 64 testes, OK (classe Projeto: 7). `test_forge_fechar`: 34 testes, OK.
- `forge-mutante tests/mutantes/v0479-copias-pasta-propria.json`: M1 a M7 morreram (rc 0). `--cobertura --base` lista as 5 condições mudadas como cobertas, nenhuma sem mutante.
- Vermelho: `forge-testes --vermelho 5e3ca873 --modulos test_forge_copia`, rc 0: `prova (asserção)=5` (clone, de_dentro, gitignore, limpar, recusa), nenhum cai no HEAD; `fora_de_git` e `o_forge_segue` guardam regressão e passam na base (por desenho).
