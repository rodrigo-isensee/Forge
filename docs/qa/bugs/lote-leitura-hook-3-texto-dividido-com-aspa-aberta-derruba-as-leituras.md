# lote-leitura-hook-3 - sem o marcador, o texto dividido com aspa aberta derruba as outras leituras (`env -uS\' cat .env` sai 0; regressão contra a develop)
- Severidade: alta (ler o `.env` e apagar o `.git` passam; o `env` real lê e apaga)
- Responsável sugerido: forge:tech-lead (hooks do Forge; classe "regra sem o marcador atrás de lançador com opção fora da tabela", 2.ª volta seguida: pela decisão de 2026-10-22 a entrega para e o `software-architect` propõe o caminho)
- Ambiente: 6d5252db2c3799d8114fb432647d4ae0dfcb5109 contra a develop `ba57c0b` (hooks idênticos aos da `main` 83d5faa), Python 3.14.4, `/usr/bin/env` uutils 0.8.0 e `/usr/bin/gnuenv` GNU 9.7

## Passos para reproduzir
1. Cópias limpas por `git archive` da develop e do head em `$TMPDIR/qa-engineer-lote-leitura-hook/v14/{base,lote}`.
2. Alimentar `python3 hooks/conformidade.py` com a entrada JSON do Claude Code (modelo do corpus, `Fixture` de `tests/test_hooks.py`), só trocando `tool_input.command` (sonda `v14/sonda.py`) ou, no mesmo processo, `decidir_na_guarda` com `hooks=` de cada árvore (sonda `v14/varrer.py`).
3. Formas (a palavra com `-`, um grupo com `u` ou `C` antes do `S`, e o resto do grupo com uma aspa sem par): `env -uS\' cat .env`, `env -uS'"' cat .env`, `env -vuS"'" cat .env`, `env -iuS'"' rm -rf .git`, `env -iu X env -uS\' cat .env`.

## Resultado esperado
Sem o marcador crítico, o `conformidade` recusa (rc 2), como a develop: a leitura sem valor vê `cat .env` / `rm -rf .git`, e a decisão do dono diz "recusam se qualquer leitura recusa".

## Resultado obtido
rc 0 nas formas acima (develop: 2). Causa: `_ler_lancadores` (`hooks/_comum.py:1888`) faz `shlex.split` do texto dividido ao montar a leitura adiada, antes de devolver as outras leituras; o `ValueError` sobe por `separar_lancadores`, o `segmento` cai em `ilegivel` e a linha, que não aponta para o Forge, passa. A leitura sem valor, que recusaria, nunca roda.
Varredura no mesmo processo (`v14/varrer.py`, 1384 formas de grupo curto com `S` e fragmento de aspa aberta, base contra lote): 218 regressões, todas com `u` ou `C` antes do `S` (`-uS`, `-CS`, `-iuS`, `-vuS`, `-iCS`, `-uiS`, `-uvS`, `-ivuS`, `-uCS`) e a abreviação `--spl='"'`; nenhuma sem a aspa aberta. As formas com `-u` rodam de verdade (abaixo); as com `-C` e `--spl=` o `env` real recusa por pasta ou texto inválido, mas a develop as recusava e o lote não (mesma causa).

## Evidência
Sonda viva, hooks desligados, `.env` falso, `HOME` e pasta no `$TMPDIR`, sem rede: `env -uS\' cat .env` e `env -uS'"' cat .env` imprimem `SEGREDO_FALSO=abc123` no uutils 0.8.0 e no GNU 9.7 (`env -uS\' echo OK_u` imprime `OK_u`). Confirma o A1 da segurança (`c17509a`) e o A1 do review (`72a6b97`); saídas em `$TMPDIR/qa-engineer-lote-leitura-hook/v14/f1.log` e `varrer.py`.

## Contorno
Nenhum para o usuário. Para o hook: a falha de `shlex.split` de uma leitura a mais não pode derrubar as outras (a leitura a mais que não fecha aspas é descartada, ou vira "ilegível" só depois das outras leituras recusarem); e o teste de propriedade precisa gerar o grupo com aspa aberta, que o gerador de hoje não gera.

## Estado
Fechado em 0e8776d (revalidação 15, opção B da rev14): as formas relatadas (`env -uS\' cat .env`, `env -uS'"' cat .env`, `env -vuS"'" cat .env`, `env --spl='"' cat .env`, `env -iu X env -uS\' cat .env`) e as variantes da classe (`env -iu -S\' cat .env`, `env -aS'"'`, `env -iS'"'`, `env X=1 -uS\'`, `sudo -Z env -uS\'`, `env -S'env -uS\'…'`) saem 2 no `conformidade`; varredura contra a develop: 0 regressões em 2502 formas com aspa aberta e em 49 888 sem. Prova em `docs/qa/lote-leitura-hook.md`.
