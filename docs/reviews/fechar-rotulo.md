---
tipo: review
contrato: 1
pedido: fechar-rotulo
branch: melhoria/fechar-rotulo
commit: 32fb00871dc99c096d76469c54ff558eb3123def
parecer: aprovado
revisor: forge:tech-lead (outra instância)
data: 2026-10-20
---
# Review do FECHAR-ROTULO (revalidação por delta da volta E1.1v)

Escopo: o delta da volta do autor, `git diff ce3221797902030b831a71e4e1d649559d8666ba 32fb00871dc99c096d76469c54ff558eb3123def` (commits 937714d e 32fb008: bin/forge-fechar, changelog.d/fechar-rotulo.md, docs/fechamento-integrador.md, tests/test_fechar.py). Este parecer substitui o anterior (commit 8b619b3).

## Delta lido e o que ficou como já lido
- `forge-check delta --parecer docs/reviews/fechar-rotulo.md` (intervalo 8b619b3..32fb008) listou: `bin/forge-fechar` 6, 66-69, 84, 95-98, 154-160; `changelog.d/fechar-rotulo.md` 2; `docs/fechamento-integrador.md` 10, 17; `tests/test_fechar.py` 5, 178, 180, 184-212, 246-252, 257-264. Li só essas faixas. A ferramenta avisou que a cópia vigente está atrás do repositório (0.24.0, commit 50997b7). O Jarvis já registrou esse aviso no pedido: no Forge ele só avisa.
- Já lido no parecer anterior e fora do delta: os passos 1 a 4, 6 e 7 do script, as guardas de base e de main, a falha fechada das leituras do `gh` no passo 5 e o caminho do dry-run até a importação da catraca.

## O que conferi
- Título para: o passo 5 (`bin/forge-fechar:154-160`) olha a primeira linha do texto lido do `gh`, que é o título (`--jq '.title, .body'`). Se ela cita `afrouxa-regra` e o rótulo não está aplicado, o passo para. Os testes cobrem os dois lados: `test_titulo_que_cita_o_rotulo_sem_o_rotulo_aplicado_para` (para, sem `pr merge`) e `test_titulo_que_cita_o_rotulo_com_o_rotulo_aplicado_segue`. Isso segue a segunda DECISÃO TÉCNICA do pedido.
- Corpo só citado não para: o corpo (`tail -n +2`) só para com item marcado. `test_corpo_que_so_cita_o_nome_do_rotulo_nao_para` tirou o nome do título e mantém a menção livre e o item desmarcado. Esse era o falso positivo do #226.
- Marcadores: a expressão `^[[:space:]]*([-*+]|[0-9]+[.)])[[:space:]]+\[x\]` com `grep -i` aceita `-`, `*`, `+`, `1.` e `1)` e também `[X]`. Os testes cobrem `- [x]`, `* [X]` com recuo, `+ [x]`, `1. [x]` e `12) [X]` (subTest).
- Dry-run não fica mudo: o heredoc agora roda o `git diff` pela `c.git` da catraca e sai com 1 quando o código de retorno não é zero, e o script cai no aviso "não consegui conferir". Reproduzi `bin/forge-fechar fechar-rotulo --ref melhoria/nao-existe-xyz --dry-run`: rc 0, com a linha de aviso (no parecer anterior saía mudo). Com `--ref melhoria/fechar-rotulo` não sai nenhum aviso, o que está certo, porque o diff não toca `PROTEGIDOS`. O doc diz que a falta do aviso não dispensa a catraca, como a segurança recomendou.
- Corpo gerado: a seção `## Checklist` traz `- [ ] Rótulo afrouxa-regra pedido ao dono` (`bin/forge-fechar:66-69`), e `test_corpo_gerado_traz_o_item_do_rotulo_desmarcado` confere o item e a ausência de `[x]`. Um PR aberto pelo script, sem mudança no corpo, não para no passo 5.
- O que o 8b619b3 já cumpria não quebrou: o item `- [x]` sem rótulo para, o item com rótulo segue, `* [X]` com recuo para, o dry-run com `hooks/parecer.py` avisa sem chamar nada e o erro do `gh` no passo 5 para. `python3 -m unittest tests.test_fechar -q`: 32 testes, OK. Rodei só esse módulo, não a suíte inteira (R-TETO). A suíte de 961 testes e o vermelho, 6 de 32 com 8b619b3, vêm do relatório do autor, e reproduzi-los é do QA.
- R1 atendida, pelo caminho de falha descrito acima.
- R2 atendida: o teste "sem controle" agora afirma que `aviso` não aparece no stdout nem no stderr, e `test_dry_run_avisa_quando_nao_consegue_ler_o_diff` cobre a ref ausente.
- R3 atendida: o teste anticópia carrega `tests/catraca.py`, afirma mais de 5 itens em `PROTEGIDOS` e procura cada um deles no script. A exceção é o próprio `tests/catraca.py`, que o script precisa citar para carregar a lista. A suposição está registrada no Histórico e procede.
- Documentação e changelog: `docs/fechamento-integrador.md` (passo 5 e `--dry-run`), o cabeçalho e a linha do passo 5 no dry-run mudaram junto com o código. O fragmento `changelog.d/fechar-rotulo.md` descreve o comportamento final, e o `CHANGELOG.md` não foi editado.
- Regras: as regras aparecem pelo ID (R-CONFORMIDADE), sem trecho de regra entre aspas (AntiDuplicacao). R-CUSTO e R-NEUTRO valem: o dry-run segue sem rede e sem `gh`, e não entrou termo de projeto. O delta não toca `bin/forge-check`, `.github/` nem `tests/config.json`.
- Ferramentas: o Forge não tem `docs/engineering/praticas.md`. O `shellcheck` não está nesta máquina e fica pendente para a bateria do CI no PR, sem revisão manual no lugar.
- Segurança: a revalidação do passo 5 é da E1.3 (`docs/security/fechar-rotulo.md`), que roda em paralelo. Não refaço essa análise aqui.

## Achados

## Detalhe dos achados
- R4 (recomendado) bin/forge-fechar:95 · o dry-run repete os argumentos do `git diff` de `alterados()` (`tests/catraca.py:80`) para enxergar o código de retorno. Se a catraca mudar a forma do diff, as duas cópias podem divergir. Não afrouxa nada, porque o controle é a Catraca no CI. Sugestão para um cartão futuro (`tests/catraca.py` está fora do escopo): `alterados()` passa a sinalizar o erro, o mesmo ponto da melhoria registrada no parecer anterior, e o script volta a chamá-la.
