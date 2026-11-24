---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-prepush-testes
commit: 9add4d15d59a0ff569d50107464582e896a28917
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-23
---
# Review de segurança: v0478 (E137.28, testes do envio local, PR #824)

Base 0e59c446, head 9add4d15 (classe C). Delta: `tests/test_pre_push_afetados.py`, `tests/test_pre_push_leve.py`, `changelog.d/v0480-prepush-testes.md` e o parecer de review. `.githooks/pre-push` e `scripts/suite-paralela.py` intocados.

## Gatilhos
Gatilhos: testes de guarda do envio local (hook pre-push, trava da suíte, prova de árvore verde e carimbo K6).

## Só aperta ou neutro
- `reprova_sem_esperar` (`tests/test_pre_push_afetados.py:306`): aperta. Troca o teto de 15 s por prova sem relógio: `flock` falso na frente do PATH do hook (`:294`) com registro vazio (`:316`), mais trava ainda segura pelo processo de fora (`:319-320`) e ausência das mensagens de fila (`:317-318`). O hook chama `flock` pelo nome, sem PATH fixo (`.githooks/pre-push:80,96,120,544`), então o registro enxerga toda chamada; a S1 do review (espera de 18 s antes das checagens baratas) reprova. As asserções anteriores (código 1, nenhuma marca, sem "pre-push: entrou") seguem.
- `NeutralidadeECaminhoCedo` (`:404`) herda o mesmo método: aperta os casos de neutralidade e caminho cedo.
- `test_suite_inteira_com_processo_morto_nao_anota_prova_nem_carimbo` (`tests/test_pre_push_leve.py:142`): aperta. Teste novo: no opt-in `1`, um teste morto por SIGKILL reprova o envio e não grava `.verde` nem o carimbo `forge-suite-verde` (falso verde reaproveitável).
- Fragmento do changelog: neutro.
- O script do `flock` falso interpola só caminhos de `tempfile.mkdtemp` e de `shutil.which`, em diretório temporário do próprio teste, removido no cleanup; sem entrada externa, sem caminho de ataque.

## Achados

## Sondas

## Detalhe dos achados
Sem achado. Verificação: testes dos arquivos tocados no head 9add4d15 (`tests.test_pre_push_leve`, `ChecagensBaratasAntesDaTrava`, `NeutralidadeECaminhoCedo`): 20 testes, OK (1 pulado: shellcheck fora do PATH), 19 s. Suíte inteira só no CI: run 45298587332 no head 9add4d15, conclusão success (cinco partes nas duas versões, instalação, catraca, pareceres, teto de pulados).

## Riscos aceitos e ferramentas
Sem risco aceito. Ferramentas: leitura estática do delta e do hook. Lacuna: o varredor de segredos não está no PATH desta estação (o delta é só de teste e changelog, sem credencial lida a olho); o CI cobre a varredura.
