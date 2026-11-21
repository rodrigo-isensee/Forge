---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-comando-pronto
commit: 34b6bf7bf5732b299a39d22c59dbf86950536286
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0479-comando-pronto (v0478 E66.4)

Escopo lido: `git diff bead3e53..34b6bf7b` (9 arquivos: três skills e um detalhe de skill, fragmento de changelog, `bin/forge-testes` só no mapa e na tupla `FORGE_CHECK`, `tests/pesos-d4.json`, `tests/test_anotar.py`, `tests/test_comando_pronto.py` novo).

## Gatilhos
Gatilhos: teste novo que executa as ferramentas da fábrica (`bin/forge-*`) em subprocesso; texto do Jarvis sobre comandos de controle (`anotar`, `brief selar`, `forge-fechar`).

## Detalhe dos achados
Sem achado bloqueante nem recomendado.

- Execução em subprocesso (`tests/test_comando_pronto.py:30-36`): argv em lista, sem shell; o interpretador roda com `-I`; ambiente reduzido a `PATH`, `LANG` e `TMPDIR`; `timeout=60`; só `--help`. As palavras vêm do texto das skills versionadas (mesma fronteira de confiança do código revisado), não de entrada externa. `bin/forge-fechar` trata `-h/--help` imprimindo o cabeçalho e saindo com 0 sem log (`bin/forge-fechar:25`): sem efeito colateral. Rodado: 3 testes OK, árvore limpa depois.
- Exceção `SEM_OBRIGATORIAS` (`tests/test_comando_pronto.py:22-25`): afrouxa só a cobrança de opção obrigatória de uma citação (`escape registrar`), o subcomando segue cobrado e o teste falha se a exceção ficar sem uso. Não afrouxa controle de segurança.
- Skills: as mudanças completam comandos com as opções obrigatórias e encurtam frases; nenhuma regra com ID, bloqueio ou passo de portão sai do texto (`R-BRIEF`, `R-PROVA`, `R-CUSTO`, `R-FLUXO`, `R-DECISAO` seguem citados). A conferência dos invariantes e da neutralidade fica com o CI.
- `bin/forge-testes:153,246`: só inclusão do módulo novo na tupla e no mapa de seleção; o seletor não perde cobertura (a regra nova soma módulos).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Suíte inteira: só no CI (brief E66.4: sem suíte local); rodado localmente só o teste novo. `gitleaks` ausente no PATH (lacuna); o diff não contém credencial nem configuração sensível, lido à mão.
