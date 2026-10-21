---
tipo: qa
contrato: 1
pedido: sessao-versao-carregada
branch: melhoria/sessao-versao-carregada
commit: d9524fd60a3f6dbb08f074182bc37198f5fb855e
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-20
---
# QA: sessao-versao-carregada

Links: pedido `~/.forge-contrib/docs/pedidos/sessao-versao-carregada.md`; review `docs/reviews/sessao-versao-carregada.md`. Sem UX nem API. Código testado em d9524fd; HEAD da branch 95d17f3 (só o review veio depois).

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: instalada maior que a carregada avisa "feche e abra a sessão", sem `claude plugin update` | `test_instalada_maior_que_a_carregada_avisa_para_reabrir` e sonda manual | instalada = carregada + diferença | passou |
| E1: versões iguais, silêncio | `test_sessao_em_dia_fica_em_silencio` e sonda | igualdade | passou |
| E1: instalação ausente ou formato estranho, sem aviso | `test_instalada_menor_ou_formato_estranho_nao_avisa` e sondas (ausente, JSON quebrado, `plugins` lista, versão "abc") | arquivo ausente, tipo errado, versão ilegível | passou |
| E1: plugin realmente atrasado ainda manda atualizar | `test_plugin_realmente_desatualizado_ainda_manda_atualizar` | instalada = carregada < projeto | passou |
| E1: `forge-atualizar` diz a frase nova e cita `forge voltar-versao` | `test_caminho_feliz_cita_o_comando_para_voltar_e_o_aviso_da_sessao` | n/a | passou |
| E2: fragmento do changelog | presente em `changelog.d/sessao-versao-carregada.md`; testes estruturais da suíte | n/a | passou |

## Execução real
- Suíte: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q` na worktree: 1087 testes, OK (275 s). `scripts/validar-plugin.sh`: "Validation passed".
- Vermelho antes do verde: cópia de HEAD com `bin/forge-doutor` e `bin/forge-atualizar` de origin/develop, `python3 -m unittest tests.test_sessao_versao_carregada`: 3 falhas de 5 (aviso do doutor, plugin atrasado, frase do atualizar); com o código novo, 5 OK.
- Sondas como usuário (cópia do `bin` em `$TMPDIR`, HOME temporário, `installed_plugins.json` falso, projeto git temporário, `--rapido`): carregada 0.0.1 e instalada 0.26.0 imprime "O Forge 0.26.0 está instalado, mas esta sessão roda a 0.0.1: feche e abra a sessão." e nenhum `claude plugin update` (a versão do projeto igual à instalada); iguais e instalada menor, sem aviso; arquivo ausente, JSON quebrado, `plugins` em formato de lista e versão "abc", sem aviso de sessão (as mensagens antigas de plugin ausente e desatualizado seguem como antes, e aí o `claude plugin update` é o certo). Nada gravado fora de `$TMPDIR`; sem rede.
- Mutação: não rodada (a stack do Forge não traz ferramenta de mutação); o vermelho acima cobre as três ramificações novas.

## Riscos e observações (sem defeito)
- R2 do review (maior versão entre escopos de `forge@*`) pode gerar aviso que reabrir não resolve numa instalação manual fora do fluxo do Forge; fora do caminho normal.
- R3 (frase "esta sessão roda a" fora de sessão) segue a decisão M7 = A.

## Bugs
Nenhum aberto.
