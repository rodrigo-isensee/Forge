---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-jargao-medida
commit: b8d4cda82594978d6edd6f309721a742848a3b81
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: v047 (medida de jargão no Stop, E7.4; revisão E2.220)

Escopo: `e13aed85..b8d4cda8`, `hooks/meta.py` (`CLASSES_DE_JARGAO`, `EXPLICACAO`, `fora_de_codigo_e_citacao`, `explicado`, `classes_de_jargao`, `mensagem_ao_dono`, `medir_mensagem`), a fixture `tests/hooks/meta/jargao-classes-da-mensagem-do-evento.json`, `tests/test_meta.py`, mutantes, índice de fixtures e fragmento do changelog. Pergunta: a medida nova (S6, que só mede) pode mudar a decisão da catraca do mesmo hook (S4, `avaliar_meta`, que bloqueia o Stop por `R-PROVA`)? Sim: o custo da medida cresce com o quadrado do tamanho da mensagem, roda antes da decisão, sem vigia de prazo, e o timeout do Claude Code (300 s em `hooks/hooks.json`) mata o hook e libera o Stop com o objetivo armado e não provado.

## Gatilhos
Hook do Forge que decide (`hooks/meta.py`, catraca S4 do objetivo armado, `R-PROVA`); controle que analisa entrada livre (a mensagem final do agente, campo `last_assistant_message`), o que pede orçamento de tempo e de tamanho da entrada (`cyber-security`, matriz de dimensões; `R-SEGURANCA`). Não toca pipeline, dependência, segredo nem `hooks/conformidade.json`.

## Achados
- A1 (bloqueante) hooks/meta.py:162 · explicado() faz re.split do prefixo inteiro a cada termo achado: custo quadrático; 25 KB de "E1.1 " levam 5 s e 100 KB passam de 80 s (S1, S2). Sem teto de entrada nem vigia, a medida come o prazo da catraca S4 (A3)
- A2 (bloqueante) hooks/meta.py:142 · a classe cartao tem [A-Z]{2,}[A-Z0-9]* ambíguos antes do grupo repetido: um só token de maiúsculas com hífens tem custo quadrático (32 KB em 36 s, S3); 110 KB passam do timeout de 300 s do Stop (S4)
- A3 (bloqueante) hooks/meta.py:198 · medir_mensagem roda antes de avaliar_meta, sem prazo: mensagem final longa (A1, A2) faz o Claude Code matar o hook no timeout e o Stop passa com objetivo armado e checagem falhando (S4); medir com teto de tamanho, ou depois da decisão
- A4 (recomendado) hooks/meta.py:184 · o S6 antigo (tabela "Em vez de", uma busca por palavra sobre a mensagem inteira) também cresce com o tamanho; o teto de entrada de A1 deve valer para a linha inteira de medir_mensagem, não só para classes_de_jargao

## Sondas
- S1 · classes_de_jargao("E1.1 " * 5000) (25 KB) · espera: abaixo de 1 s (medida linear) · obtido: 5,2 s
- S2 · classes_de_jargao("E1.1 " * 20000) (100 KB) · espera: abaixo de 1 s · obtido: passou de 80 s (timeout 100 do comando com outras sondas antes)
- S3 · classes_de_jargao("AB" * 8000 + "-" + "A-" * 8000 + "a") (32 KB) · espera: abaixo de 1 s · obtido: 36,6 s (2000→2 s, 4000→8,2 s: quadrático)
- S4 · hook meta.py com meta.json armado, checagem ["false"], last_assistant_message = "AB"*50000+"-"+"A-"*5000+"a", sob timeout 300 · espera: rc=2 e R-PROVA (como com mensagem curta) · obtido: rc=124 em 300 s, sem R-PROVA, meta.json intocado (repeticoes 1)

## Detalhe dos achados
Sondas em `$TMPDIR` (fora do repositório), importando `hooks/meta.py` do clone no head revisado. Controle da S4: o mesmo projeto temporário, a mesma `meta.json` armada (`checagens: [["false"]]`) e `last_assistant_message: "pronto"` dá rc=2 com `R-PROVA: objetivo do pedido x ainda não entregue (1/4)` em 1,2 s.

A1. Evidência `hooks/meta.py:162` (`frase = re.split(r"[.!?\n]", texto[:inicio])[-1]`), chamada por `hooks/meta.py:169` para cada termo de cada classe. Cada chamada copia e divide o prefixo inteiro: com N termos numa mensagem de tamanho L, o custo é N×L. Caminho: o próprio agente (ou um agente sob injeção de texto que lê) fecha a resposta com um relatório longo cheio de identificadores (as listas de etapas dos briefs, como o `## Fora do escopo`, já têm ~8 KB só de `E<n>.<m>`); não precisa de entrada exótica. Severidade média (quebra o portão da catraca por A3). Correção mínima: olhar só a janela antes do termo (`texto[max(0, inicio - 200):inicio]`, a frase de "o que é" cabe nela) e limitar o texto medido (por exemplo `texto[:20000]`, registrando `cortado: true`). Esforço P. Dono: autor da E7.4 (tech-lead).

A2. Evidência `hooks/meta.py:142`. `[A-Z]{2,}` e `[A-Z0-9]*` disputam as mesmas letras: para cada divisão possível do início do token, `(?:-[A-Z0-9]+)+(?![\w-])` percorre o resto antes de falhar. Caminho: um token longo (sigla repetida, base64 em maiúsculas com hífen, saída colada de ferramenta) na mensagem final. Severidade média pelo mesmo efeito de A3. Correção mínima: `[A-Z][A-Z0-9]+` sem a sobreposição (exige 2 caracteres e pelo menos uma letra inicial; se a regra "2 letras" importa, `[A-Z]{2}[A-Z0-9]*`), mais o teto de entrada de A1. A matriz de dimensões da família (`cyber-security`) pede, para cada expressão, um caso de tamanho no teto com tempo medido; hoje `tests/test_meta.py` não tem caso de tamanho. Esforço P. Dono: autor da E7.4.

A3. Evidência `hooks/meta.py:198` (`medir_mensagem(hook)`) antes de `hooks/meta.py:201` (`avaliar_meta(hook, raiz)`); `executar("meta", principal)` sem `regra_do_prazo`, logo sem `vigia_de_prazo`; `hooks/hooks.json` dá 300 s ao `meta.py`. O próprio Forge registra a premissa em `hooks/_comum.py` (comentário do vigia de prazo): o Claude Code mata o hook no timeout e libera a ação, por isso a decisão de um hook que recusa tem de vir antes. O `except Exception` de `principal` não pega o kill. Caminho: o agente com objetivo armado (`forge-check meta --armar`) cuja checagem falha encerra a resposta com mensagem longa; a catraca, que existe para impedir o agente de parar sem provar (`R-PROVA`), não decide. Antes deste diff a medida era linear (só a tabela) e lia o transcrito. Severidade média: o portão é contornável pelo próprio agente vigiado, sem privilégio, e nada fica no `erros.log` (o processo morre). Correção mínima, qualquer uma basta: (a) teto de tamanho no texto medido e janela local em `explicado` (A1, A2), mantendo a ordem; ou (b) decidir primeiro e medir depois, com a medida num `finally` ou antes do `bloquear` (que sai do processo). Recomendo (a) e (b) juntos. Teste de abuso pedido ao QA: mensagem de 200 KB com termos das seis classes e um token longo de cartão, objetivo armado com checagem falhando: rc=2 com `R-PROVA` em menos de 10 s. Esforço P. Dono: autor da E7.4.

A4. Evidência `hooks/meta.py:184`. Linear por palavra, sem o efeito quadrático; recomendado só para que o teto valha para a medida inteira. Esforço P.

Demais pontos conferidos, sem achado: `mensagem_ao_dono` aceita só `str` não vazia e recua ao transcrito; `mensagens.jsonl` recebe só contagens por classe (`json.dumps`, sem o termo nem o texto; a fixture confere a ausência de `E7.4`, `e13aed85` e `meta.py`), sem injeção de linha (JSON numa linha); a classe `commit` (lookaheads limitados pela lookbehind ao início do trecho hex), `caminho`, `etapa` e `regra` como expressões isoladas são lineares (`caminho` e `hex` com 40 KB em 0,06 s; a lentidão de `etapa` e `regra` é a de A1); falha da medida que levanta exceção continua sem trocar a decisão (`except` em `principal`). Nenhum segredo nem dado pessoal novo gravado.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, sondas de tempo na biblioteca padrão em `$TMPDIR`, execução de ponta a ponta do hook num projeto temporário. Testes do item: `python3 -m unittest tests.test_meta` (9 testes, OK, 7,9 s). A suíte inteira fica para o CI do PR (não há PR aberto nesta etapa). Sem varredura de segredos nem de dependências: o diff não toca nenhuma das duas.
