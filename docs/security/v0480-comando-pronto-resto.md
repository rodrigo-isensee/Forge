---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-comando-pronto-resto
commit: dff23f769706eb32c04432a1a1c35fc3a9f2c5f1
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-23
---
# Review de segurança: v0478 E139.14 (PR #826, resto do comando pronto)

Revisado o diff `0e59c446..dff23f76` (Base-sha..Revisar-sha). O head do PR, `7bdf54de`, só acrescenta os pareceres de review e de QA (`git diff --stat dff23f76 7bdf54de`: `docs/qa/` e `docs/reviews/`), então o código lido é o mesmo. Classe C (`forge-check classe`: skill `qa-testing`).

## Gatilhos
Gatilhos: portão de teste (`bin/forge-testes`, mapa do plano dirigido do envio e do `--vermelho`).

## Achados

## Sondas

## Detalhe dos achados
**Só aperta ou neutro, por item:**
- `bin/forge-testes:250-252` (MAPA): só aperta. Simulei `planejar` e `planejar_afetados` na base e no head para `skills/qa-testing/SKILL.md`, `skills/esperar-estado/SKILL.md`, `skills/esperar-estado/envio-longo.md`, `agents/tech-lead.md` e `skills/fluxo-do-pedido/SKILL.md`. Nenhum caminho perdeu módulo. Os três primeiros ganham `test_comando_pronto`. O mapa é de primeiro casamento (`bin/forge-testes:354-357`), e o novo padrão `qa-testing` não encobre nenhuma regra posterior: a skill não tinha linha no mapa e o plano antigo está todo contido no novo.
- `skills/esperar-estado/SKILL.md:16,22` e `envio-longo.md:24`: neutro. Com `no checks reported`, o laço continua esperando; antes ele saía com `checks:1`. O laço só espera e não aprova nem mescla nada: o merge continua preso ao CI e aos pareceres. Com o `2>/dev/null` do `gh pr view`, a falha ainda sai `fim=erro` (`tests/test_esperar_estado.py`, `test_gh_que_falha_sai_com_erro`). O laço sem teto de `envio-longo.md` pode ficar preso num PR em que nenhum check chega nunca. Isso afeta só a disponibilidade da sessão principal e não abre caminho de ataque; fica como observação, não como achado.
- `skills/qa-testing/comandos.md:46-53` (simulação de merge): neutro. O clone é local (`--no-hardlinks`) e fica numa pasta de `mktemp -d`. A URL do `origin` vai só para o `.git/config` dessa cópia temporária e nunca aparece na saída (o comando imprime só o sha e a pasta). Com `--no-edit`, a cópia não fica esperando um editor. Nada sai para fora da máquina além do `fetch` do próprio remoto.
- `skills/qa-testing/SKILL.md:51-52`: tirar as crases de `forge-check` e de `bin/forge-testes` não muda nenhuma regra do oráculo (EXT-1). O texto continua o mesmo; isso já está no A1 recomendado do review.
- `skills/qa-testing/SKILL.md:75` e `comandos.md:24`: o `--vermelho` com `--modulos` restringe a rodada local do autor e do QA. Não troca prova: a suíte inteira continua no CI.
- `tests/test_comando_pronto.py` e `tests/test_esperar_estado.py`: só acrescentam asserções. `formas_que_falham` só soma erros e não remove nenhum.

**Suíte:** CI do PR #826 no head `7bdf54de`, com as 10 partes da suíte (3.12 e 3.14) verdes, mais `catraca`, `instalação` e `verificações longas` verdes. A `bateria`/`bateria (pareceres)` está vermelha à espera deste parecer. Rodei localmente só os testes dos arquivos tocados: `python3 -I -m unittest discover -s tests -p test_comando_pronto.py` (3 OK) e `... -p test_esperar_estado.py` (16 OK).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff e simulação de `planejar`/`planejar_afetados` em cópias `git archive` da base e do head. Não há segredo, dependência nem workflow no diff, então `gitleaks`, `osv-scanner` e `zizmor` não se aplicam.
