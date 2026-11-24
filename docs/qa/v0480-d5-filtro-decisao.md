---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-d5-filtro-decisao
commit: 6c4a7dcc9856c3718599c0bdb06185a58afcbdcf
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0478 · E173.6 (PR #863, filtro de decisão D5)

Obrigações (E173.3, regra do dono de 24/11): (1) `forge-check anotar --tipo pergunta` exige `--tipo-pergunta` de 7 valores, grava `tipo=<t>` antes do contexto e recusa pergunta sem opções ou com questão de uma opção só; `--tipo-pergunta` fora da pergunta é recusado; a trava E6 segue. (2) `forge-check decisoes registrar` exige `--so-aperta sim|nao` e `--seguranca docs/security/<parecer>.md` regular, sem atalho simbólico, até 1 MiB, com `só aperta` não negado; senão vira pergunta (rc 1).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Pergunta sem tipo ou tipo fora da lista recusada | `test_forge_dono.FiltroDaPergunta.test_sem_tipo_ou_tipo_fora_da_lista_e_recusada` e `test_cli_sem_tipo_pergunta_nao_grava` | None, vazio, caixa, espaço | passou |
| Cada um dos 7 tipos grava `tipo=<t>` e o O4 segue lendo | `test_cada_tipo_da_lista_grava_o_tipo_antes_do_contexto` | os 7 valores | passou |
| Sem opções ou questão com 1 opção recusada | `test_pergunta_sem_opcoes_e_recusada`, `test_questao_com_uma_opcao_so_e_recusada` | zero opções; 1 opção na 2ª questão | passou |
| `--tipo-pergunta` só com pergunta | `test_tipo_pergunta_fora_da_pergunta_e_recusado` | decisao, historico, ordem | passou |
| E6 continua | `test_o_corte_sem_origem_segue_recusado_com_o_tipo` | corte sem origem | passou |
| Decide só com só aperta e confirmação | `SoApertaComSeguranca.test_so_aperta_com_confirmacao_decide`, `test_nao_so_aperta_vira_pergunta`, `test_sem_so_aperta_nao_grava` | sim, nao, vazio (rc 2, nada gravado) | passou |
| Confirmação inválida vira pergunta | `test_confirmacao_fora_de_docs_security_vira_pergunta`, `test_confirmacao_ausente_ou_link_vira_pergunta`, `test_pasta_da_seguranca_por_link_vira_pergunta`, `test_confirmacao_sem_a_frase_ou_negada_vira_pergunta`, `test_confirmacao_grande_demais_vira_pergunta` | caminho `..`, absoluto, .txt, atalho no arquivo e na pasta, negação, 1 MiB | passou |
| Chamadores existentes adaptados | `test_anotar` (18), `test_decisor` (9) | n/a | passou |

## Execução local (só arquivos tocados)
`test_forge_dono` 94 OK, `test_decisor` 9 OK, `test_anotar` 18 OK. Suíte inteira: check-run `bateria` do CI do PR.

## Vermelho antes do verde
`forge-testes --vermelho 8a6f59075210b1d6b9484803263c69ea8ad13271 --modulos tests.test_forge_dono,tests.test_decisor,tests.test_anotar`, saída rc 2:
```
vermelho: 3 módulos em duas cópias, em série; prazo de 600 s por módulo e cópia (teto 3600 s)
contagem: não prova (passa na base)=65; prova (API ausente)=2; prova (asserção)=40; sem veredito=14
```
Os testes novos provam: `SoApertaComSeguranca` (8 de 8) e `FiltroDaPergunta` (6 de 7) caem na base. Os 14 "sem veredito" são B=erro (TypeError do argumento novo `tipo_pergunta` na base): 12 de `test_anotar` e 1 de `test_decisor` são testes existentes com ajudante adaptado, e 1 é `FiltroDaPergunta.test_tipo_pergunta_fora_da_pergunta_e_recusado`. O rc 2 não vale como vermelho; o comportamento desse último é provado pelo mutante D5M11 (abaixo).

## Mutação
`bin/forge-mutante` das 3 specs do pedido, `--processos 3`, rc 0, 17 mutantes, todos morreram:
```
forge-mutante: pedido=v0480-d5-filtro-decisao rev=6c4a7dcc9856 spec=a1b74dd4... spec=1db21cd7... spec=4dd3479a...
D5M1..D5M17 · morreu (bin/forge_decisor.py:31,44,53,56,58,140; bin/forge_dono.py:148,151,153,154; bin/forge-check:5358,5374,5375,5376,5392,5393)
D5M7 · morreu · bin/forge_decisor.py:140 · (erro) o teste declarado deu erro sob o mutante e passa sem ele
```
`--cobertura --base 8a6f590`: toda condição mudada tem mutante declarado; `spec editada · tests/mutantes/v0457-camadas-1.json`, e o M5 editado rodado: `M5 · morreu · bin/forge-check:5376`.

Sem bug aberto; sem acessibilidade aplicável (CLI).

## Achados
- A1 (recomendado) docs/regras/R-DECISAO.md:21 · `decisoes registrar` agora exige `--so-aperta` e `--seguranca`, e `anotar --tipo pergunta` exige `--tipo-pergunta`; a regra e os textos de agente não os citam, quem seguir só o texto recebe recusa. Atualizar em cartão.
- A2 (recomendado) tests/test_forge_dono.py:857 · o teste novo `test_tipo_pergunta_fora_da_pergunta_e_recusado` sai "sem veredito" (erro de API na base) no `--vermelho`; vira prova se chamar pela CLI (`self.rodar`), que a base recusa por argumento desconhecido (rc 2) e falha de asserção.
