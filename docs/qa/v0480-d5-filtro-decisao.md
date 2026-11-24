---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-d5-filtro-decisao
commit: 8916a422b5b7b811f858847881a686e7f3108f19
parecer: reprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0478 · E173.20 (PR #863, filtro de decisão D5, volta E173.12)

Delta de `6c4a7dcc..8916a422` (domínio: código e testes): a confirmação da segurança passa a ser lida pelo git (HEAD da raiz, igual na árvore, modo 100644, até 1 MiB), com frontmatter `tipo: revisao-seguranca`, `parecer: aprovado`, `revisor: forge:security-engineer`, `pedido:` igual ao `--pedido` e a linha própria `Só aperta: <porta>`. A parte de `anotar --tipo pergunta` não mudou; vale o parecer anterior (E173.6).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Arquivo fora do git, mudado na árvore ou no índice, link, 100755, acima de 1 MiB, raiz que não é a do repositório, git ausente: pergunta | `ConfirmacaoDaSeguranca.test_arquivo_fora_do_git_vira_pergunta`, `test_arquivo_mudado_na_arvore_ou_no_indice_vira_pergunta`, `test_link_simbolico_no_git_vira_pergunta`, `test_parecer_executavel_no_git_vira_pergunta`, `test_parecer_acima_do_teto_vira_pergunta`, `test_raiz_que_nao_e_a_do_repositorio_vira_pergunta`, `test_git_ausente_vira_pergunta` | modo, 1 MiB, raiz, PATH sem git | passou |
| Frontmatter de outro tipo, reprovado, outro pedido, sem pedido, outro revisor, sem abertura, sem fechamento, chave repetida: pergunta | `test_frontmatter_que_nao_e_da_seguranca_aprovada_do_pedido_vira_pergunta`, `test_parecer_de_outro_item_ja_na_develop_vira_pergunta` | cada campo, chave duplicada | passou |
| Frase solta, pergunta, negação, recuo, minúscula, porta outra ou com sobra: pergunta | `test_frase_solta_pergunta_ou_negacao_vira_pergunta` | linha inteira, porta exata | passou |
| Confirmação válida decide, porta com espaços normalizados | `test_confirmacao_valida_decide_com_a_porta_de_espacos_normalizados`, `test_as_quatro_condicoes_de_pe_decide_e_imprime_a_linha_do_commit` | espaços | passou |
| Caminho fora de `docs/security/<nome>.md` com parecer válido commitado | `SoApertaComSeguranca.test_confirmacao_fora_de_docs_security_vira_pergunta` | `..`, absoluto, .txt, subpasta | passou |

## Execução local (só arquivos tocados)
`test_decisor` 20 OK, `test_forge_dono` 94 OK, `test_anotar` 18 OK. Suíte inteira: check-run `bateria` do CI do PR.

## Vermelho antes do verde
`bin/forge-testes --vermelho 6c4a7dcc9856c3718599c0bdb06185a58afcbdcf --modulos tests.test_decisor`, rc 2:
```
vermelho: base=6c4a7dcc9856 head=8916a422b5b7 módulos=test_decisor (restrito por --modulos)
contagem: não prova (passa na base)=12; prova (asserção)=7; sem veredito=1
```
O "sem veredito" é `test_git_ausente_vira_pergunta` (B=erro: a base não tem a assinatura nova de `confirmacao_escrita`); o comportamento é provado pelo mutante D5M18, que morre. Os 7 testes de abuso novos caem na base.

## Mutação
`bin/forge-mutante` das 4 specs do pedido, `--processos 3`, rev 8916a422: D5M1, D5M6 a D5M28 todos `morreu` (23 mutantes, inclusive D5M18 e D5M7 com `(erro)` do teste sob o mutante). `--cobertura --base 6c4a7dcc` (rc 1) lista duas condições mudadas sem mutante: `bin/forge_decisor.py:57` (`not k.startswith('GIT_')`) e `:106` (`texto is not None`).
Mutantes que somei em spec fora da árvore:
```
Q1 · sobreviveu · bin/forge_decisor.py:57   (de: if not k.startswith("GIT_")  para: if True)
Q2 · morreu · bin/forge_decisor.py:106
```
Q1 sobrevive: nenhum teste roda com `GIT_DIR`/`GIT_WORK_TREE` no ambiente (os testes chamam `sem_git_herdado`), então a limpeza que impede um `GIT_DIR` herdado de apontar o git para outro repositório e confirmar um parecer que não é o da raiz não tem prova.

Sem bug aberto; sem acessibilidade aplicável (CLI).

## Achados
- A1 (recomendado) docs/regras/R-DECISAO.md:21 · `decisoes registrar` exige `--so-aperta` e `--seguranca`, e `anotar --tipo pergunta` exige `--tipo-pergunta`; a regra e os textos de agente não os citam. Atualizar em cartão (herdado do parecer E173.6).
- A2 (recomendado) tests/test_forge_dono.py:857 · `test_tipo_pergunta_fora_da_pergunta_e_recusado` sai "sem veredito" no `--vermelho`; chamar pela CLI (`self.rodar`) o torna prova (herdado do parecer E173.6).
- A3 (bloqueante) bin/forge_decisor.py:57 · o mutante Q1 (`if not k.startswith("GIT_")` -> `if True`) sobrevive: nenhum teste exporta `GIT_DIR` ao `decisoes registrar`. Pedir mutante na spec e teste com `GIT_DIR` de outro repositório no ambiente, que deve virar pergunta.
