---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/fechar-esperar-rotulo
commit: 6995fb14d13d9063003090aae617b6dbc6c01023
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-04
---
# QA: versao-033 (FECHAR-ESPERAR-ROTULO, cartão 14)

Links: não há `docs/ux` neste repositório; os critérios vêm do cartão 14 (`KANBAN.md`, linha FECHAR-ESPERAR-ROTULO da 0.34) e do pedido de QA. Código testado: 52cbbd4 (um commit sobre b45e40a). Review e segurança não foram lidos aqui; o parecer de segurança é do `security-engineer`.

Plano escrito depois do código, a partir do cartão e do diff: a independência é menor que a do plano antecipado. Escopo incremental: a suíte completa não foi rodada neste pedido.

## Achados
- A1 (recomendado) bin/forge-fechar:822 · R-QA, repete AR-1: as guardas 817, 819 e 822 mudaram sem mutante declarado. Q1 a Q4 (abaixo) as matam; o autor as declara no JSON. FECHADO em 6995fb1 (Q1 a Q4 declarados na spec; AR-1 em 7).
- A2 (recomendado) bin/forge-fechar:824 · a frase de espera (`aguardando ... pedido <gatilho>`) não tem teste que a afirme; lida à mão, correta (CA-7).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CA-1 (gatilho pelo título) | tests.test_fechar.Fechar.test_mensagem_do_passo_5_diz_que_o_gatilho_foi_o_titulo | título como primeira linha; caixa alta (CT-M9) | passou; cai na base |
| CA-2 (gatilho pelo item do corpo) | tests.test_fechar.Fechar.test_mensagem_do_passo_5_diz_que_o_gatilho_foi_o_item_do_corpo | item marcado; `[ ]` não entra (CT-M7) | passou; cai na base |
| CA-3 (prazo esgotado com a opção) | tests.test_fechar.Fechar.test_prazo_esgotado_com_esperar_rotulo_para_sem_mandar_repetir_a_opcao | `--espera 0`; sem `pr merge` | passou; cai na base |
| CA-4 (sem a opção, continua parando) | tests.test_fechar.Fechar.test_sem_a_opcao_o_rotulo_pedido_e_ausente_continua_parando | opção ausente | passou; já existia (passa na base) |
| CA-5 (nenhum caminho aplica o rótulo) | tests.test_fechar.Fechar.test_recusa_quando_item_do_rotulo_marcado_e_rotulo_nao_aplicado; tests.test_fechar.Fechar.test_script_nunca_usa_force_no_verify_nem_rotulo; teste do CA-3 | rótulo ausente; nenhum `pr merge` nem escrita de rótulo | passou |
| CA-6 (texto que só cita não para) | tests.test_fechar.Fechar.test_corpo_que_so_cita_o_nome_do_rotulo_nao_para | texto sem item marcado; item `[ ]` (CT-M7) | passou |
| CA-7 (mensagem clara ao dono) | leitura das mensagens (CT-M1 a CT-M9) | gatilho, o que o script não faz, próximo passo | passou; a frase de espera sem teste (A2) |

## Cenários e resultado real
Rodados com o harness dos testes, sem alterar o repositório. Cada linha é a saída real do `bin/forge-fechar`.
- CT-M1, título, sem a opção: rc 1; "...foi pedido pelo título e o dono ainda não o aplicou; o script nunca aplica rótulo; depois que o dono aplicar o rótulo, rode de novo com --esperar-rotulo". Sem merge, sem escrita de rótulo.
- CT-M2, corpo, sem a opção: rc 1; "...por um item marcado do corpo..." com a mesma dica.
- CT-M3 e CT-M4, com a opção e prazo zero: rc 1; a frase do gatilho, sem a dica.
- CT-M5, com a opção durante a espera (prazo 2 s, `FORGE_FECHAR_TESTE=1`): stdout "aguardando o rótulo afrouxa-regra do dono, pedido pelo título (o script nunca o aplica)..."; ao fim do prazo, rc 1 com a frase sem a dica.
- CT-M6 (texto cita o rótulo sem item marcado) e CT-M7 (`- [ ]`): rc 0, mescla.
- CT-M8 (título e corpo marcados): diz "pelo título", que tem precedência.
- CT-M9 (`- [X]` e `1) [x]`, e título em caixa alta): para com a frase certa.
- Escrita de rótulo: `grep` em `bin/forge-fechar` acha só leituras (`pr view --json labels`, linhas 748, 762 e 811). Nenhum `--add-label`, `gh label`, `pr edit` nem `--admin`.

## Execução
- `python3 -I -m unittest discover -s tests -p test_fechar_aviso_rotulo.py`: 6 OK, rc 0.
- `python3 -I -m unittest discover -s tests -p test_fechar_corrida_rotulo.py`: 7 OK, rc 0.
- `python3 -I -m unittest discover -s tests -p test_fechar.py`: 92 OK, rc 0 (82 s).
- `bin/forge-mutante tests/mutantes/fechar-esperar-rotulo.json`: rc 0; R1 (bin/forge-fechar:818), R2 (820), R3 (829) e R4 (829) morreram.
- Conferência da lista contra o diff: guardas mudadas em `bin/forge-fechar` são 817, 819, 822, 828 e 829. Sem mutante declarado: 817, 819 e 822 (A1). Q1 a Q4 do QA, na mesma rodada: `if false; then` em 817 morreu (test_mensagem...titulo); `elif false && ...` em 819 morreu (test_mensagem...item_do_corpo); `if true; then` em 822 morreu (test_corpo_que_so_cita...); `dica=""` em 828 morreu (test_mensagem...titulo). Spec suplementar fora do commit; reproduzível pelos blocos acima.
- `bin/forge-mutante --cobertura --base b45e40a`: rc 0; `bin/forge-fechar` sai `não coberto` (shell fora da medida); a conferência acima é a manual.
- Vermelho antes do verde: `bin/forge-testes --vermelho b45e40a --modulos test_fechar`, rc 0. Prova 3 por asserção (os três testes novos, que caem na base e passam no HEAD); 89 não provam por passar na base. Revertidos à base: `bin/forge-fechar` e o changelog; mantidos no HEAD: o JSON de mutantes e `tests/test_fechar.py`.
- Suíte completa: não rodada neste pedido (escopo incremental).
- Bugs abertos: nenhum.

## Revalidação (6995fb1)
Delta desde 52cbbd4 (o parecer anterior, 66e21fd, já é ancestral): `tests/mutantes/fechar-esperar-rotulo.json` (+Q1 a Q4), `docs/engineering/achados-recorrentes.md` (AR-1 de 6 para 7) e os pareceres de review e de segurança (`docs/reviews/`, `docs/security/`), que não entram na revalidação do QA. `bin/`, `hooks/`, `.githooks/` e `tests/catraca.py` não mudaram: o código testado segue o de 52cbbd4.
- `bin/forge-mutante tests/mutantes/fechar-esperar-rotulo.json` no head 6995fb1: rc 0; R1 (818), R2 (820), R3 (829), R4 (829), Q1 (817), Q2 (819), Q3 (822) e Q4 (828) morreram.
- A1 fechado: as guardas 817, 819 e 822 têm mutante declarado e morto.
- A2 segue aberto como recomendado (frase de espera sem teste).
- Parecer continua `aprovado`, sem bugs abertos.
