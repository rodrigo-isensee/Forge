---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-k152-sem-skip
commit: 1600898d0c5dbf16b3ea1ab3bc88f7fc63b6a291
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0479-k152-sem-skip

Etapa E85.3 (pedido v0478). Diff lido `ad3b3b6f..1600898d`: `tests/test_prepush_k152.py` (+23 −4) e o fragmento `changelog.d/v0479-k152-sem-skip.md`. Nenhum código de produção, hook, workflow nem configuração muda.

## Gatilhos
Gatilhos: teste de controle de envio (pre-push do modelo de projeto), sem mudança no controle em si.

## Avaliação
Só aperta. O teste ponta a ponta `EnvioDaCopiaNova` deixava de rodar (`skipTest`) em máquina com as ferramentas do pronto rápido da stack instaladas, o que esvaziava a prova justamente onde o CI ou o mantenedor as têm. Agora:
- o `skipTest` sai (`tests/test_prepush_k152.py:209-212`); o teste roda em toda máquina;
- o envio roda com um PATH controlado (`path_sem_pronto`, `tests/test_prepush_k152.py:99-110`): pasta temporária própria do teste, só links simbólicos para os utilitários listados em `PROGRAMAS_DO_ENVIO`/`OPCIONAIS_DO_ENVIO` (`:29-31`), resolvidos pelo PATH de quem roda; as ferramentas da stack nunca entram, então a cópia fica de fato sem dependências;
- utilitário obrigatório ausente falha o teste (`assertIsNotNone`, `:108`), sem pular;
- nova asserção `assertNotIn("command not found", ...)` (`:230`) prova que o hook rodou inteiro com o PATH reduzido, e não que barrou por acidente; a mensagem da asserção de código de saída passa a trazer o stderr (`:227`).

As asserções anteriores (mensagem de falta, comando de instalar, remoto vazio) ficam todas. Nenhuma asserção foi afrouxada nem removida.

Superfície: tudo em `tempfile.TemporaryDirectory`, HOME/TMPDIR isolados, remoto local `--bare`, sem rede, sem segredo, sem escrita fora da pasta temporária. Os links apontam para binários que o próprio PATH do executor já expõe: nenhum ganho de privilégio nem caminho de ataque realista. O fragmento de changelog é texto.

## Achados

## Sondas

## Detalhe dos achados
Sem achados.

## Riscos aceitos e ferramentas
Sem riscos aceitos. Prova local: `python3 -m unittest tests.test_prepush_k152` no head 1600898d, 10 testes, OK (o caso ponta a ponta rodou, sem skip, numa máquina comum). Suíte inteira: só no CI; a branch ainda não tem PR nem execução de CI no momento deste parecer, e o merge segue condicionado ao CI verde (`R-FLUXO`). Ferramentas ausentes no PATH: varredor de segredos e SAST (lacuna registrada; diff sem superfície para eles).
