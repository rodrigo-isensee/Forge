---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-jargao-medida
commit: 95e7a6ad678839d3a2f5fe2a734e129a79401d68
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: v047 (medida de jargão no Stop, E7.4; revalidação E2.244, volta 1)

Escopo: revalidação por delta (`forge-check parecer delta`) de `b8d4cda8..95e7a6ad`; no domínio, `hooks/meta.py` e a fixture `tests/hooks/meta/jargao-mensagem-de-200-kb-decide-e-mede-no-teto.json` (lidos inteiros no diff); fora do domínio (testes, mutantes, índice de fixtures, fragmento), só conferidos pelo que tocam no hook. A pergunta da revisão anterior continua a mesma: a medida S6 pode mudar a decisão da catraca S4 (`avaliar_meta`, `R-PROVA`)? Não mais: a decisão vem antes, a medida lê no máximo `TETO_DA_MEDIDA` caracteres e as duas expressões quadráticas ficaram lineares.

## Gatilhos
Hook do Forge que decide (`hooks/meta.py`, catraca S4, `R-PROVA`); controle que analisa entrada livre (`last_assistant_message`), com orçamento de tempo e tamanho (`cyber-security`, matriz de dimensões; `R-SEGURANCA`). Não toca pipeline, dependência, segredo nem `hooks/conformidade.json`.

## Achados

## Sondas
- S1 · classes_de_jargao("E1.1 " * 5000) (25 KB, sem o teto) · espera: abaixo de 1 s · obtido: 0,19 s (antes 5,2 s)
- S2 · classes_de_jargao("E1.1 " * 20000) (100 KB, sem o teto) · espera: abaixo de 1 s · obtido: 0,60 s (antes passou de 80 s); 200 KB: 1,08 s, linear
- S3 · classes_de_jargao("AB" * 8000 + "-" + "A-" * 8000 + "a") (32 KB) · espera: abaixo de 1 s · obtido: 0,009 s (antes 36,6 s); 200 KB: 0,11 s
- S4 · hook meta.py, meta.json armado, checagem ["false"], last_assistant_message "AB"*50000+"-"+"A-"*5000+"a", timeout 300 · espera: rc=2 e R-PROVA · obtido: rc=2, R-PROVA, 294 ms, linha em mensagens.jsonl com cortado true

## Detalhe dos achados
Os quatro achados da revisão anterior (commit `b8d4cda8`) estão resolvidos no head:

A1 (era bloqueante) resolvido. `hooks/meta.py:170`: `explicado` divide só a janela de `JANELA_DA_FRASE` (200) caracteres antes do termo; e `hooks/meta.py:192` limita o texto medido a `TETO_DA_MEDIDA` (20000). As sondas S1 e S2 chamam `classes_de_jargao` sem o teto e mesmo assim ficam lineares.

A2 (era bloqueante) resolvido. `hooks/meta.py:145`: `[A-Z]{2}[A-Z0-9]*` não disputa mais letras com o prefixo; o grupo repetido é separado por hífen (sem ambiguidade) e a lookbehind só deixa começar no início do token. S3 cai de 36,6 s para 9 ms; 200 KB em 0,11 s. A regra de "duas letras no início" do desenho continua.

A3 (era bloqueante) resolvido. `hooks/meta.py:208`: `avaliar_meta` roda primeiro; `bloquear` (`hooks/_comum.py`) sai por `sys.exit(2)`, que levanta `SystemExit`, e o `finally` roda a medida, com a falha dela no `erros.log`. A medida ainda atrasa a saída do processo, mas agora com custo limitado pelo teto (S4: 294 ms; com 400 KB misturando etapas e token de cartão, 414 ms, rc=2). A fixture nova (200 KB, seis classes, token longo) prende rc=2, `R-PROVA`, `cortado: true` e a ausência dos termos na linha gravada; o teste de abuso que pedi ao QA está nela.

A4 (era recomendado) resolvido. `hooks/meta.py:193`: a tabela "Em vez de" também lê só `medido`, então o teto vale para a medida inteira.

Demais pontos do delta, sem achado: `fora_de_codigo_e_citacao` com cerca ``` ou ~~~ fechada pela mesma cerca é linear e só decide o que conta, não o que bloqueia; a etapa com `(?!\w|\.\w)` é lookahead de largura fixa; `mensagens.jsonl` continua com só contagens e `cortado` (sem termo nem texto). A leitura do transcrito (`LEITURA_MAXIMA`, 4 MB) é anterior ao diff e linear. `AR-5` (intérprete sem `-I` em caminho que decide) não se aplica ao delta: a linha de `hooks/hooks.json` não mudou. Nenhum segredo nem dado pessoal novo.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do delta, sondas de tempo na biblioteca padrão em `$TMPDIR` importando `hooks/meta.py` do clone no head, execução de ponta a ponta do hook num projeto temporário (controle `pronto`: rc=2, `R-PROVA`). Testes do item: `python3 -m unittest tests.test_meta` (15 testes, OK, 5,2 s). A suíte inteira fica para o CI do PR. Sem varredura de segredos nem de dependências: o delta não toca nenhuma das duas.
