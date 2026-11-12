---
tipo: revisao-seguranca
contrato: 1
pedido: v0457
branch: melhoria/suite-tempo-vivo
commit: 5c06712475d096d89f2cf27098fb6b12265ff5c5
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-12
---
# Review de segurança: v0457 (E23.25, suite-tempo-vivo)

Diff revisado: `8b5a44d5..5c067124` (`scripts/suite-paralela.py`, `tests/test_suite_paralela.py`, `changelog.d/suite-tempo-vivo.md`). Testes novos rodados isolados: 2 testes, OK.

## Gatilhos
`scripts/suite-paralela.py` é sensível da catraca (decide o veredito da suíte no pre-push e no CI), gatilho de `R-SEGURANCA`.

Conferido:
- Os arquivos `p<i>.saida.json.tempos` ficam na pasta de `tempfile.mkdtemp` (modo 0700, só o dono), ao lado do relatório, e saem no `shutil.rmtree` do `finally` de `rodar_partes`, inclusive no sinal (`scripts/suite-paralela.py:749`, `:774`).
- O conteúdo é só o nome da unidade (módulo de `tests/`, já impresso hoje no `::group::` do CI) e segundos; nada de ambiente, caminho de TMPDIR, saída de teste nem segredo. Nada sensível no log público do CI.
- O dado lido não entra no veredito, no relatório nem no stdout: `TemposAoVivo` só imprime no stderr (`:514`-`:556`); o filho que escrevesse linhas falsas é código de teste, com a mesma confiança que já tem (roda código arbitrário no CI).
- Sinal: `imprimir_rodando` roda depois de os três sinais irem a `SIG_IGN` (`:765`-`:767`), sem reentrada; o `Interrompido` segue repassado e a saída continua diferente de 0.
- PA-7: AR-4 (o teste usa o `env` do brinquedo), AR-5 (a linha de lançamento dos filhos não mudou) sem ocorrência nova.

## Achados
- A1 (recomendado) scripts/suite-paralela.py:767 · imprimir_rodando vem antes de encerrar(filhos): stderr fechado (SIGHUP sem terminal) faz o print falhar e pular o encerramento; os filhos só morrem pelo vigiar_pai, até 1 s depois. Pôr o resumo em try/except OSError ou depois de encerrar.
- A2 (recomendado) scripts/suite-paralela.py:534 · atualizar avança a posição antes de imprimir; sinal no meio do laço perde as linhas fim restantes e o resumo pode listar como rodando unidade que já terminou. Avançar a posição por linha processada.

## Sondas

## Detalhe dos achados
A1: evidência `scripts/suite-paralela.py:767` (e as impressões em `esperar`, `:564`). Caminho: não há atacante; é robustez do fluxo de sinal (sessão do pre-push encerrada com o terminal). O print no stderr quebrado levanta `OSError` e `encerrar(filhos)` não roda; antes da mudança, o print que falhava vinha depois do encerramento. A rede de segurança `vigiar_pai` (`:275`) encerra o grupo do filho em até 1 s, e o `rmtree` do `finally` roda, então o efeito é limitado. Severidade: baixa. Correção mínima: `try: tempos.imprimir_rodando()` / `except OSError: pass`, ou chamar depois de `encerrar`. Esforço P. Dono: `devops-engineer`.

A2: evidência `scripts/suite-paralela.py:534`-`:544`. Caminho: nenhum de ataque; exatidão da evidência informativa no corte por timeout. Severidade: informativa. Correção mínima: somar à posição o tamanho de cada linha depois de tratá-la. Esforço P. Dono: `devops-engineer`.

## Riscos aceitos e ferramentas
Sem risco aceito. Revisão por leitura do diff e execução dos dois testes novos; varreduras de segredo e de workflow não se aplicam (o diff não toca workflow nem configuração).
