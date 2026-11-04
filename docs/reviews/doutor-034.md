---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/doutor-034
commit: 5bd8bdc7fc5657fe591ab47d024e2c08b004b0e4
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-04
---
# Code review: melhoria/doutor-034 (AVISO-VERSAO-UMA-VEZ e N-DOUTOR-F8-CAMINHO)

Escopo da rodada 1: `b45e40a...4bfc92e`, commits 8d097be (AVISO-VERSAO-UMA-VEZ, `hooks/doutor.py` e `tests/test_doutor.py`), 9db3c4b (N-DOUTOR-F8-CAMINHO, `bin/forge-doutor` e `tests/test_doutor_protecao_gh.py`) e 4bfc92e (fragmento `changelog.d/doutor-034.md`). A rodada 2 (5bd8bdc, só o AVISO-VERSAO-UMA-VEZ) está em "Revalidação".

## Rodada 1 (4bfc92e): teto e comportamentos (M14)
`git diff --numstat --no-renames b45e40a...HEAD`: código e teste somam 34 linhas (`bin/forge-doutor` 3, `hooks/doutor.py` 7, `tests/test_doutor.py` 23, `tests/test_doutor_protecao_gh.py` 1); o fragmento fica fora. Dentro das 150 linhas. Em `hooks/` há uma classe de comportamento só (o cache do aviso de versão).

O PR carrega dois comportamentos de dois cartões, em arquivos diferentes: o silêncio do aviso de versão já dito (`hooks/doutor.py`) e o texto do aviso de branch sem proteção (`bin/forge-doutor`). Não é lote por arquivo (a regra do pedido para a 0.34, `docs/propostas/backlog/versao-0.34.md:3`, é "cada cartão em PR próprio ou lote por arquivo"), e a dispensa da DECISÃO DO DONO de 2026-11-03 10:06 vale para o resto da 0.33, não para estes cartões da 0.34. Pela decisão M14 é achado bloqueante (A1), como no PREPUSH-LEVE desta mesma frente. O conteúdo dos dois commits está revisado aqui e correto: a volta é só a divisão, e a revalidação de cada parte sai por delta.

## Rodada 1 (4bfc92e): correção
- AVISO-VERSAO-UMA-VEZ (`hooks/doutor.py:104`): no dia novo, `avisado` herda `True` só se o cache anterior já tinha avisado o mesmo par (`atual`, `ultima`) e a consulta de hoje segue `defasada`. Casos conferidos na leitura: versão ainda mais nova volta a avisar (o par muda); atualização do plugin para uma intermediária, ainda atrás, volta a avisar (muda `atual`, e o texto muda junto, pois cita a versão em uso); dia de consulta que falha preserva `avisado`, `atual` e `ultima` (`{**antigo, "falhou_em": ...}`); dia de consulta desligada grava `avisado` falso e o dia seguinte com rede avisa de novo, o que é aceitável (o desligado não avisou); em dia apaga o par. O ramo do mesmo dia não mudou. O cache segue provando o atraso (`defasado: true`), que o `forge-check` lê.
- N-DOUTOR-F8-CAMINHO (`bin/forge-doutor:388`): o aviso passa a citar `docs/engineering/protecao-de-branch.md`, o passo a passo que o `forge-init` cria desde o N-TPL-a, e mantém a skill `ci-cd`. Faz o que o cartão pede. Ressalva em A2.

## Rodada 1 (4bfc92e): testes
Rodados no HEAD 4bfc92e, só os módulos tocados (D-5):
- `python3 -I -m unittest discover -s tests -p test_doutor.py`: 72 testes, OK (84 s; o `test_abrir_em_menos_de_cem_ms_em_media` passou na primeira).
- `python3 -I -m unittest discover -s tests -p test_doutor_protecao_gh.py`: 14 testes, OK.

Reprovam sem a mudança: com `hooks/doutor.py` e `bin/forge-doutor` da base b45e40a e os testes do HEAD, `test_a_mesma_versao_nova_nao_avisa_de_novo_no_dia_seguinte` falha ("Saiu a versão 0.32.1" de novo no dia seguinte) e `test_main_sem_protecao_vira_problema_que_cita_a_branch_e_a_skill_ci_cd` falha (caminho ausente). `test_versao_ainda_mais_nova_avisa_no_dia_seguinte` passa na base, como deve: é a guarda contra silenciar demais, e mata a mutação que deixa de comparar `ultima`. Os arquivos foram restaurados ao HEAD depois da prova (`git status` limpo).

Ferramentas: não há shell no diff (`shellcheck` não se aplica). Não veio spec de mutação (`tests/mutantes/<pedido>.json`) nem saída do `bin/forge-mutante` na entrega: fica como pendência do autor (V2), em A4, sem review manual no lugar.

## Revalidação (rodada 2, HEAD 5bd8bdc)
O autor reescreveu a branch: `melhoria/doutor-034` em 5bd8bdc (um commit sobre b45e40a, só AVISO-VERSAO-UMA-VEZ) e o N-DOUTOR-F8-CAMINHO foi para `melhoria/doutor-f8-caminho` (85c5b80, sobre b45e40a, parecer próprio em `docs/reviews/doutor-f8-caminho.md`).

Delta lido: `bin/forge-check delta --parecer docs/reviews/doutor-034.md` respondeu `delta: 4bfc92e não é ancestral de 5bd8bdc` (a branch foi reescrita, não acrescida). Li no lugar dele `git diff 4bfc92e 5bd8bdc`: em `hooks/doutor.py`, a docstring rearrumada e o `try/except OSError` em `principal` ao redor de `aviso_de_relogio`; em `tests/test_doutor.py`, 3 testes novos; `tests/mutantes/doutor-034.json` novo; o fragmento reescrito; e a saída da parte do F8 (`bin/forge-doutor`, `tests/test_doutor_protecao_gh.py` e a linha do fragmento). Já lido na rodada 1 e igual: a linha de `avisado` em `hooks/doutor.py:105` e os dois primeiros testes do dia seguinte.

- Rodada 1, A1: resolvido: um comportamento só no PR. `git diff --numstat --no-renames b45e40a...5bd8bdc`: `hooks/doutor.py` 13 e `tests/test_doutor.py` 52, 65 linhas contadas (a spec de `tests/mutantes/` e o fragmento ficam fora). Uma classe em `hooks/`.
- Rodada 1, A2: saiu com o F8 e é revalidado no parecer `doutor-f8-caminho`.
- Rodada 1, A3: resolvido: a docstring fala no par `atual`/`ultima`, em linhas dentro da largura do arquivo.
- Rodada 1, A4: resolvido: `test_versao_em_uso_diferente_com_a_mesma_ultima_avisa_no_dia_seguinte` cobre o `atual`, e a spec tem M1 a M4.
- O `try/except OSError` em `principal` (o A2 da segurança) é consequência do mesmo comportamento: agora o aviso de versão fica marcado como dito antes do relógio rodar, e uma falha ao gravar o relógio o perderia para sempre, não só por um dia. O `except` é estreito (só `OSError`), tem comentário, e o aviso do relógio é de melhor esforço. Aceito como escopo do cartão.

Ferramentas, no HEAD 5bd8bdc:
- `python3 -I -m unittest discover -s tests -p test_doutor.py`: 75 testes, OK (53 s; o `test_abrir_em_menos_de_cem_ms_em_media` passou na primeira).
- `bin/forge-mutante tests/mutantes/doutor-034.json`: `rev=5bd8bdc7fc56`, M1, M2 e M3 morreram em `hooks/doutor.py:105` e M4 em `hooks/doutor.py:188`; rc=0. A reversão para `avisado = False` já foi provada na rodada 1 (o teste do dia seguinte reprova).

## Achados
- A1 (recomendado) hooks/doutor.py:77 · a docstring tem uma linha curta no meio ("None. Consulta desligada ... Consulta que"); juntar na próxima vez que o arquivo for tocado, sem volta

## Parecer
Aprovado na rodada 2. Os achados da rodada 1 estão resolvidos: A1 pela divisão, A3 e A4 no código, e o A2 foi junto com o F8, revalidado no outro parecer. Os testes do comportamento reprovam sem a mudança (rodada 1) e a spec de mutação mata os quatro mutantes. Fica um recomendado de forma, que não devolve. Segurança: `hooks/doutor.py` tem parecer próprio do `security-engineer`, que este review não refaz.

Histórico da rodada 1 (4bfc92e, reprovado): A1 bloqueante, dois comportamentos de dois cartões no PR (M14); A2 recomendado, caminho do passo a passo inexistente no clone do Forge e em projeto antigo; A3 recomendado, docstring; A4 recomendado, sem spec de mutação e o `atual` sem teste.
