---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp3-s1-atalho
commit: 3e53ae726c2891e00dbcdcc66cb0ebc54318cba8
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0478 E39.13 (atalho durável, BP3 S1)

## Achados
- A1 (bloqueante) README.md:43 · o parágrafo novo cita `claude` solto sem `--permission-mode auto`; `tests/test_sessao_automatica.py` (AtalhosAbremNoAutomatico) falha no head e passa na base (regressão de entrega). Reescrever a linha sem o termo solto ou citar o modo.

## Critério → teste → resultado
| Critério (decisão do dono) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Reabre com `--continue` só em saída anormal (>=128, fora 129/130) | `test_atalho_duravel.py` + cenário manual (claude falso, exit 137) | 0, <128, 129, 130, 137 | passou |
| Teto de 3 reaberturas em 30 min, depois desiste | cenário manual: 4 execuções, 3 `reabre` + 1 `desiste` | 3.ª/4.ª queda | passou |
| `quedas.log` só com data, projeto, saída, tentativa, ação | cenário manual | sem texto do claude | passou |
| Fora do tmux só avisa e abre | `test_atalho_duravel.py` | `--sem-tmux`, tmux ausente | passou |
| Abre o `claude` mais novo (instalador × PATH) | `test_atalho_duravel.py` | empate, um candidato, sem `--version` | passou |
| Instruções de abertura sempre em modo auto | `test_sessao_automatica.py` | linha com `claude` solto | FALHOU (A1) |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_atalho_duravel.py`: 68 testes, OK. Sem `skip` novo.
- `python3 -I -m unittest discover -s tests -p test_sessao_automatica.py`: 13 testes, 1 falha: `README.md:43 abre o claude sem --permission-mode auto`.
- Cenário manual: `claude` falso saindo 137, `TMUX` definido, espera 0: 1 abertura + 3 reaberturas, cada uma com um só `--continue`, 4 linhas no `quedas.log` (3 `reabre`, 1 `desiste`).
- shellcheck ausente nesta máquina; roda no CI.
- `scripts/jarvis` e `scripts/jarvis-forge` diferem por desenho (cabeçalho e cópia vigente); mudança do supervisor é a mesma nos dois.

## Vermelho antes do verde
`forge-testes --vermelho 004ce869d641ca62394d705c4453d8a014002f15` (saída final):
`contagem: dívida pré-existente=36; falha da entrega (regressão ou sem veredito)=1; não prova (passa na base)=573; prova (asserção)=43; pulado=1; regressão=1; sem veredito=8`
Regressão: `tests.test_sessao_automatica.AtalhosAbremNoAutomatico.test_nenhuma_instrucao_manda_abrir_o_claude_sem_o_modo · H=falha · B=ok` (A1). 43 testes provam a entrega. Oito sem veredito: o autor deve rodar de novo; a dívida pré-existente (`test_oraculo_sempre_atual`) é de outro pedido e vira cartão.

## Mutação
`bin/forge-mutante tests/mutantes/v0479-bp3-s1-atalho-{1,2,3,4}.json`: 40 mutantes (M1 a M40), todos `morreu`, rc 0. `--cobertura --base` devolve `não coberto: scripts/jarvis` e `scripts/jarvis-forge` (shell não é conferido pela ferramenta); a lista cobre as guardas do diff lidas à mão: classificação do código de saída, teto, janela, `--continue` único, resolução de versão, avisos.

## Bugs
Nenhum arquivo em `docs/qa/bugs/`: o defeito é o achado A1 (severidade alta, contorno simples, mas bloqueia a suíte do CI).
