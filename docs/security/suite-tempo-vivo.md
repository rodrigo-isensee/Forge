---
tipo: revisao-seguranca
contrato: 1
pedido: v0457
branch: melhoria/suite-tempo-vivo
commit: 076dcc809c9a21f7fab45c4786a03a67a33ebf27
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-12
---
# Review de segurança: v0457 (E23.25, revalidado por delta em E23.31, suite-tempo-vivo)

Diff revisado: `8b5a44d5..5c067124` (E23.25) e, na volta, `5c067124..076dcc80` (`forge-check parecer delta`: no domínio só `scripts/suite-paralela.py`; fora, `tests/test_suite_paralela.py` e `tests/mutantes/v0457-suite-tempo-vivo.json`, lidos assim mesmo). Testes da classe nova `TemposAoVivoLogica` rodados isolados: 5 testes, OK.

## Gatilhos
`scripts/suite-paralela.py` é sensível da catraca (decide o veredito da suíte no pre-push e no CI), gatilho de `R-SEGURANCA`.

Conferido na E23.25 (segue válido no head):
- Os arquivos `p<i>.saida.json.tempos` ficam na pasta de `tempfile.mkdtemp` (modo 0700) e saem no `shutil.rmtree` do `finally` de `rodar_partes`, inclusive no sinal (`scripts/suite-paralela.py:782`).
- O conteúdo é só o nome da unidade e segundos; nada de ambiente, caminho de TMPDIR, saída de teste nem segredo.
- O dado lido não entra no veredito, no relatório nem no stdout: `TemposAoVivo` só escreve no stderr.

Conferido na volta (E23.31):
- A1 tratado: `encerrar(filhos)` vem antes de `tempos.imprimir_rodando()` (`scripts/suite-paralela.py:775`-`:776`), e o resumo passa por `informar`; stderr quebrado não impede mais o encerramento dos filhos.
- A2 tratado: a posição avança por linha, depois de tratá-la (`scripts/suite-paralela.py:543`); um sinal no meio reprocessa no máximo a linha corrente, e o reprocessamento é idempotente (`pop(nome, None)`; no pior caso, uma linha informativa repetida).
- O `except OSError` novo (`scripts/suite-paralela.py:545`-`:550`) não esconde falha real: envolve só o `print` informativo no stderr; `Interrompido` deriva de `Exception` (`:85`), não de `OSError`, e continua subindo; o veredito vem dos relatórios e do código de saída dos filhos e sai no stdout (`FAILED (interrompida)`, `decidir_veredito`), fora desse `try`. Antes, um stderr quebrado no laço de `esperar` derrubava a suíte com exceção (vermelho); agora a suíte segue e decide pelo mesmo critério de antes, sem verde novo por causa do stderr.
- `tempos.close()` no `finally` de `processo` (`:312`) e a duração reaproveitada (`:309`) não mudam o que é lido nem onde.
- Mutantes M1 a M8 da spec: os oito trechos de origem existem no head (o último commit só toca o teste).
- PA-7: AR-4 (o teste usa o `env` do brinquedo), AR-5 (a linha de lançamento dos filhos não mudou), AR-12 (spec atual) sem ocorrência nova.

## Achados

## Sondas

## Detalhe dos achados
Os recomendados A1 (`scripts/suite-paralela.py:767` no commit 5c067124) e A2 (`:534` no commit 5c067124) da E23.25 foram tratados na volta como propostos (evidência acima); sem achado novo.

## Riscos aceitos e ferramentas
Sem risco aceito. Revisão por leitura do delta e execução da classe de testes nova; varreduras de segredo e de workflow não se aplicam (o delta não toca workflow nem configuração).
