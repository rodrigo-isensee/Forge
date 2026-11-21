---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-trava-corrida
commit: ef5bb776e3a958119834407b76ab0185932bc88e
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0478 (E64.14, melhoria/v0479-trava-corrida)

Gatilhos: teste de controle do Forge (trava do pre-push, casos de abuso AB-6 e AB-12)

## Escopo lido
Diff `8ee73d15..ef5bb776`: `tests/test_pre_push_trava.py:56-70` (fixture `SUITE_COM_PID`) e `changelog.d/v0479-trava-corrida.md`. Nenhum código de produção, hook, workflow ou arquivo de controle mudou.

## Conclusão: só aperta
- A mudança está só no fixture: a suíte simulada grava o próprio pid em `suite-pid.<pid>` e o renomeia para `suite-pid` com `os.replace` (`tests/test_pre_push_trava.py:60-62`). A renomeação é atômica na mesma pasta (o repositório temporário do teste), e quem lê (`tests/test_pre_push_trava.py:567-570`) nunca vê o arquivo vazio. Isso tira o falso vermelho (`int('')`) sem mudar o que se prova.
- Nenhuma asserção mudou (o diff tem 0 linhas `assert` adicionadas ou removidas). O teste `test_parar_o_hook_para_so_a_propria_suite` segue provando AB-6 e AB-12: o `kill <pid>` impresso para só a própria execução, a suíte da primeira morre antes de a trava soltar (`os.kill(..., 0)` levanta `ProcessLookupError`), e a segunda segue e termina com 0.
- O pid gravado continua sendo o da suíte (`os.getpid()`), o mesmo valor de antes; o nome do temporário não sai da pasta do teste e não toca a pasta de controle.
- Sem caminho de ataque: o arquivo é fixture de teste rodado num `TemporaryDirectory`; nenhum dado de entrada externo chega a ele.

## Achados

## Sondas

## Detalhe dos achados
Sem achado.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Suíte inteira: fica com o CI do PR. Rodado aqui: o módulo `tests/test_pre_push_trava.py` inteiro (50 testes, OK, 4 pulados por ambiente) e `test_parar_o_hook_para_so_a_propria_suite` oito vezes seguidas (8 OK). Ferramentas de varredura não se aplicam a um diff só de fixture de teste.
