---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-f4-vigia-fluxo
commit: 04b508f60417897819537305b78a9e4db5258971
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-27
---
# Review de segurança: v0481 (E34.8, #931, F4 do hook `vigia`, volta 1, por delta)

Delta lido (`forge-check parecer delta`, `8d755e50..04b508f6`), no domínio: `bin/forge-check`, `bin/forge_estado.py`, `hooks/vigia.py`, `docs/adr/0003-hooks-deterministicos-e-silenciosos.md` (item 7), `docs/hooks.md`, a fixture renomeada `tests/hooks/vigia/time-parado-sem-rede-gh-ignorado.json` e `tests/test_hooks.py`. A rodada anterior fica no git.

Gatilhos: controles do Forge (hook `vigia`, que bloqueia o `Stop` do Jarvis), dado externo do `gh` que chega ao contexto do modelo, arquivo de estado novo.

## Achados
- A1 (bloqueante) hooks/vigia.py:617 · resolvido: bin/forge_estado.py:82 tira o PR com isCrossRepository verdadeiro, ausente ou de outro tipo; teste do fork e mutante da guarda presentes.
- A2 (bloqueante) hooks/vigia.py:717 · resolvido: a guarda apagada da base está isenta com motivo na spec (tests/mutantes/v0481-f4-vigia-fluxo.json:89); catraca do head verde.
- A3 (bloqueante) tests/test_forge_mutante.py:1564 · explorável: S1. Suíte parte 4/5 vermelha: M7 e M8 de tests/mutantes/v0481-s1-status.json casam 2 vezes em bin/forge_estado.py, porque papel_do_pr repete as duas linhas; alinhar o `de` das duas specs no mesmo commit.
- A4 (recomendado) bin/forge_estado.py:140 · erro de escrita da lista (pasta sem escrita, disco cheio, diretório no caminho) sobe de prs_abertos como exceção, não NaoVerificavel: o forge-check status quebra (contrato rc 0) e o proximo idem no renovar. Envolver a gravação em OSError calado.

## Sondas
- S1 · bin/forge-mutante --conferir --todas (na cópia, head 04b508f6) · espera: nenhuma linha de v0481-s1-status · obtido: `M7 · o trecho aparece 2 vezes em bin/forge_estado.py (precisa de uma)` e o mesmo para `M8`
- S2 · python3 -I -c: pasta temporária com o diretório prs-abertos.json e gravar_prs_abertos(<ele>, [PR válido], agora) · espera: nada gravado, sem exceção · obtido: IsADirectoryError

## Detalhe dos achados
**A3 (defeito provado pelo CI).** Job `suíte (python 3.12, parte 4/5)` do run 45955075917, vermelho; a S1 reproduz o motivo na cópia. Correção mínima: dar ao `de` de M7 e M8 de `tests/mutantes/v0481-s1-status.json` um trecho único (a linha seguinte ou a anterior de `grupo_do_pr`), ou extrair o teste comum para uma função usada pelas duas. Esforço P. Dono: autor do E34.6.

**A4 (média para baixa, sem atacante externo).** `gravar_json` (`hooks/_comum.py:2573`) e o `os.chmod` levantam `OSError`; `executar` de `bin/forge_estado.py` só captura `NaoVerificavel`, e o `renovar_prs_abertos`, chamado pelo `forge-check proximo` depois da saída, não captura nada (a docstring promete "falha não muda nada"). Caminho: só o próprio usuário ou o sandbox de um subagente sem escrita na pasta de estado; o efeito é o controle de status sair com traceback, não abrir nada. Correção mínima: `except OSError: pass` em volta da gravação nas duas chamadas, com teste da S2. Esforço P. Dono: autor do E34.6.

**O que conferi e passa.** Sem rede no hook: `subprocess` saiu do `vigia`, e a fixture com `gh` falso prova que ele não é chamado. Arquivo local: escrita por arquivo temporário `O_EXCL|O_NOFOLLOW` e `os.replace` (não segue link plantado no destino nem no temporário), `0600` depois da troca (modo `0o600` medido; a janela anterior com o umask não expõe nada: só número, branch e papel de PR do próprio repositório, e no clone a pasta é `0700`), até 100 itens, só PR com papel. Leitura no `vigia` (`hooks/vigia.py:633`): `ler_quadro` sem seguir link nem esperar FIFO, só arquivo regular, teto de 64 KiB, `gravado_em` inteiro entre 60 s no futuro e 15 min no passado (`:637`), e cada item revalidado por lista positiva (número de 1 a 9999999, branch `[A-Za-z0-9._/-]{1,100}`, papel de `PAPEIS`); a branch só é comparada, nunca vai ao `reason`. Quem escreve a lista é o mesmo usuário que escreve o `agentes.json`: mesma fronteira de confiança. Filtro de fork: `is not False` cala também o campo ausente ou de outro tipo (sonda em processo: `True`, ausente, `"false"`, `0` e o fork com `ACTION_REQUIRED` dão `None`; só `False` dá papel). Teto de 280 (`hooks/vigia.py:712`): as partes têm tamanho limitado (3 PRs, 1 preso com `tipo` cortado em 24) e o laço corta a última parte inteira, mantendo o sufixo fixo. A emenda do item 7 da ADR 0003 descreve o que o código faz e mantém o item 2 (sem rede no hook); o rótulo `afrouxa-regra` é decisão do time registrada no pedido.

Testes afetados rodados na cópia: `tests.test_hook_vigia_f4`, `tests.test_vigia_parado` e `tests.test_forge_status_estado`, 88 testes, OK. CI do head `04b508f6` (run 45955075917): partes 1, 2, 3 e 5 da suíte, passos, verificações longas, instalação, `python 3.14`, árvore já provada e catraca verdes; parte 4/5 vermelha (A3); `bateria (pareceres)` e `bateria` vermelhas pela falta dos pareceres deste head.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do delta, sondas em processo (biblioteca padrão), `forge-mutante --conferir --todas` e `gh pr checks`. O log do job da parte 4/5 não foi baixado (o domínio de armazenamento do log foi negado nesta sessão); o motivo vem da S1 local. Varredura de segredo e de dependência sem objeto: o delta não toca credencial, configuração nem dependência.
