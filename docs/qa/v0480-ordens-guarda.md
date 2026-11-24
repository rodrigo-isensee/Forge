---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-ordens-guarda
commit: 9e460e4f1aa51ef214386390351faf9ebc749deb
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-23
---
# QA · guarda do arquivo de ordens (E123.28, PR #811)

Head 9e460e4f. Sem suíte local: a bateria inteira é o check-run `bateria` do CI do mesmo sha; aqui, só os testes dos arquivos tocados e os mutantes.

| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| ORDENS-SO-JARVIS: dev, segurança e variável não gravam `.forge/ordens/` (A1 E123.3) | `GuardaDasOrdens.test_conformidade_recusa_a_escrita_do_arquivo_de_ordens_na_sessao_do_forge` | jarvis libera, demais recusam | passou |
| Pasta das ordens e cópia principal (A1/A2 E123.8, S1-S4) | `test_conformidade_recusa_a_pasta_das_ordens_e_a_copia_principal` | cp, rm, ln, `../`, pasta corrente em variável | passou |
| Curinga no nome (A4 E123.12) | `test_conformidade_recusa_curinga_no_nome_das_ordens_do_projeto` (11 fixtures, mínimo afirmado) | `*`, classe, absoluto, tee | passou |
| `relativos_a_copia_principal` | `test_conformidade_ve_o_arquivo_pela_copia_principal` | fora do projeto, sem `.git`, repositório nu | passou |
| `.forge/ordens/` fora do git (A3 E123.8) | `ForgeInit.test_o_arquivo_de_ordens_fica_fora_do_git` | check-ignore | passou |
| `entrada_valida` (E123.19) | `Hooks` malformadas, 5 casos novos | caminho/motivo vazio, não texto, quem, branch vazia | passou |

Execução: `python3 -m unittest tests.test_hooks.GuardaDasOrdens tests.test_forge.ForgeInit` da raiz, sem -I: `Ran 16 tests ... OK` (GuardaDasOrdens 4, ForgeInit 12).

## Mutantes (R-QA)
`forge-mutante --cobertura --base fc488261d...`: toda condição Python mudada tem mutante declarado (conformidade.py:1610, 1642, 1645, 3605, 3608). `bin/forge-init` (shell) e `hooks/conformidade.json` (dado) saem `não coberto` pela ferramenta, mas têm M26 e M28/M30 que mataram a linha.

Saída (`forge-mutante --processos 3` nas duas specs v0480-ordens-guarda, rc 0): M15, M16, M22, M23, M24, M25, M26 (morreu por erro do teste sob o mutante, que passa sem ele), M28, M30, M31, M32, M33, M34, M35, M36, M37: todos `morreu`, zero sobrevivente.
`forge-mutante` na spec v0479-conformidade-trilha-7 (U6 editado no diff), rc 0: U1 a U8 `morreu`, incluindo `U6 · morreu · hooks/conformidade.py:3828`.

Vermelho antes do verde: não rerrodei `forge-testes --vermelho`; cada mutante que reverte a guarda derruba o teste declarado, o que equivale ao vermelho da guarda.
