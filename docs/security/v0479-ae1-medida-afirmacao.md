---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae1-medida-afirmacao
commit: f15b9b85e5c42f9310f7523fc2c25c5a35b8d3b4
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-ae1-medida-afirmacao

Pedido v0478, etapa E58.22, sobre E58.20 (AE1.4). Diff lido inteiro: `ed5bfa02..f15b9b85` (5 arquivos: `hooks/meta.py`, `tests/test_meta.py`, `tests/mutantes/v0479-ae1-medida-afirmacao.json`, `agents/jarvis.md`, `changelog.d/v0479-ae1-medida-afirmacao.md`).

## Gatilhos
Gatilhos: hook do Forge (`hooks/meta.py`, medida do Stop).

## Achados

## Sondas

## Detalhe dos achados
Sem achado. O que foi conferido:

- **Só mede, nunca bloqueia (ADR 0003):** `afirmacao_sem_prova` (`hooks/meta.py:244-246`) só acrescenta um booleano à linha de `mensagens.jsonl` (`hooks/meta.py:293`); a chamada fica em `medir_mensagem`, que roda no `finally` depois da decisão do Stop e cuja exceção vai ao `erros.log` sem trocar a decisão (`hooks/meta.py:305-311`). Nenhum caminho novo de bloqueio ou de liberação.
- **Dado gravado (LGPD, vazamento):** a linha nova é só `true`/`false`; nenhum trecho da mensagem, nome de projeto ou caminho é gravado.
- **Custo de tempo (entrada livre):** as duas expressões (`hooks/meta.py:240-241`) não têm repetição aninhada nem retrocesso ambíguo, e a entrada já vem cortada em `TETO_DA_MEDIDA` (20000 caracteres, `hooks/meta.py:286`). Sonda local com 20000 caracteres de pior caso (`"feit"*5000`, `" \t>\`"*5000+"onde:"`, `"mesclad"*2857`): de 0,4 ms a 1 ms por chamada.
- **Falsificação da prova:** um agente pode escrever à mão uma linha `onde: ...` e zerar a medida. Não há caminho de ataque de segurança: o produtor da mensagem é o próprio agente medido, a medida não concede permissão nem libera portão, e quem confia no `onde:` é o dono lendo a saída do `forge-check onde`. Fica como limite da métrica, não como achado.
- **`agents/jarvis.md`:** troca de texto de instrução (colar a linha `onde:`; reescrita do passo 8 sem mudar o sentido de `vazio: sim`); nenhum afrouxamento de regra nem de invariante.
- **Testes:** `python3 -m unittest tests.test_meta.AfirmacaoSemProva` local, 4 testes OK (afirmação sem prova, afirmação em citação e código, prova em texto, citação e código, e prova fora do início da linha que não vale). Os mutantes M1 a M6 cobrem a negação, o `and`, a âncora, o `re.M`, o limite de palavra e o `re.I`.
- **Suíte:** não rodei a suíte inteira (brief: sem suíte local); ela roda no CI do PR, obrigatório para o merge (`R-REVIEW`). Não havia execução de CI visível para a branch no momento do parecer.

## Riscos aceitos e ferramentas
Sem risco aceito. Ferramentas de varredura (segredos, SAST, workflows, dependências) ausentes do PATH nesta estação: lacuna registrada; o diff não toca workflow, dependência nem configuração com segredo, e a leitura foi manual.
