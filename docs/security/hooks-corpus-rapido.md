---
tipo: revisao-seguranca
contrato: 1
pedido: hooks-corpus-rapido
branch: melhoria/hooks-corpus-rapido
commit: 978d2d648ec19915cc3ac3b8d140669daa442cc5
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-27
---
# Review de segurança: hooks-corpus-rapido

Revisão do diff `363ceee...978d2d6` (pedido HOOKS-CORPUS-RAPIDO, etapa E2.1 do HOOKS-CORPUS-RAPIDO-REV): a classe `CorpusHeredocVoltaUnica` sai de `tests/test_hooks.py` para `tests/test_hooks_volta_{corpus,lancador,propriedades}.py` com o apoio em `tests/apoio_volta_unica.py`, a decisão dos hooks passa a ser em lote, entra o teste de equivalência e o `tests/test_pesos_teto.py`, e o mapa do `bin/forge-testes` ganha `VOLTA_UNICA`.

## Gatilhos
`R-SEGURANCA`, controles do Forge: os testes que provam os hooks `conformidade` e `parecer` (o corpus da volta única e as propriedades) e o mapa do filtro do pre-push (`bin/forge-testes`).

## Achados
- A1 (bloqueante) bin/forge-testes:67 · defeito provado: os 3 módulos VOLTA_UNICA executam bin/forge-check (apoio_volta_unica.py:329 e o `rodar` do test_hooks) mas faltam em FORGE_CHECK; `forge-testes --listar bin/forge-check` não os roda, antes rodavam dentro do test_hooks
- A2 (recomendado) tests/test_hooks_volta_corpus.py:55 · a equivalência não pega divergência de argumentos do driver: com `critico=None`, sem `clone_do_forge` ou com a pasta do conformidade nos dois hooks, o teste segue verde (mutação local); conferir o driver contra o `__main__` de cada hook

## Detalhe dos achados
**O que foi conferido e está correto.**
- Caminho do hook real: o `DRIVER_DOS_HOOKS` (`tests/apoio_volta_unica.py:324` a `:348`) chama `_comum.executar(hook, modulo.principal, modulo.CRITICO, **argumentos)` com `regra_do_prazo="R-CONFORMIDADE"` no `conformidade` e `clone_do_forge=True, regra_do_prazo="R-REVIEW"` no `parecer`, iguais a `hooks/conformidade.py:1821` e `hooks/parecer.py:446`. Os ajustes de teste (`GIT_TIMEOUT_S` e `PRAZO_DA_DECISAO_S`) são os mesmos do `LANCADOR` de `tests/test_hooks.py:520`. O ambiente é o do `rodar` (`ambiente_limpo`, sem `FORGE_GUARDA_ABERTA` nem `FORGE_CARGA_LIVRE`, com `FORGE_NPROC=8` e `FORGE_PROC` por hook). Estado entre textos no mesmo processo: o vigia de prazo desarma o alarme a cada chamada (`hooks/_comum.py:2386`), os `lru_cache` de `_comum` são funções puras do texto, e o `conta_do_gh` (`hooks/conformidade.py:1305`), que guarda o resultado por processo, dá o mesmo valor no ambiente de teste. Erro, travamento ou saída fora do JSON no filho reprovam o teste (rc, `timeout=900`, contagem de códigos), sem liberar. Textos acima de 50 mil caracteres seguem pelo subprocesso com `como_o_claude_code=True`, como antes.
- O corpus e as asserções não encolheram: a comparação por AST entre a classe da base (`363ceee:tests/test_hooks.py`) e os novos módulos dá os 79 métodos e os 51 atributos de classe presentes, cada um uma vez, com o fonte idêntico, exceto `decisoes_dos_hooks` (trocou o subprocesso por texto pelo lote, mantendo o filtro do marcador e o caminho dos textos grandes). Entram `decidir_em_lote`, `amostra_da_equivalencia`, o teste de equivalência, `DRIVER_DOS_HOOKS`, `TEXTO_DO_PRAZO_DO_CLAUDE_CODE` e `DECIDIDOS`. As constantes de módulo e `corpus_da_volta_unica` foram para o apoio sem mudança, e o `tests/fixtures/heredoc-volta-unica.json` não mudou. Os mutantes de `tests/mutantes/lote-leitura-hook*.json` só trocaram o nome do teste. Os módulos novos não importam `Hooks` (nada roda em dobro).
- O teste de equivalência pega a divergência de resultado: passa em 11,8 s, e as mutações locais "guarda aberta no filho" e "código sempre 0" o deixam vermelho (335 subtestes).

**A1. FORGE_CHECK sem os módulos da volta única** (defeito provado; severidade baixa; esforço P; dono `tech-lead`).
- Evidência: `bin/forge-testes:65` declara que FORGE_CHECK "lista todo módulo que importa ou executa o script (inclui quem importa de um deles)". Os três módulos executam `bin/forge-check` pelo `_comum.forge_check()` do driver (`tests/apoio_volta_unica.py:329`) e pelo `rodar`/`LANCADOR` de `tests/test_hooks.py`, e importam `test_hooks` e `test_forge` (os dois em FORGE_CHECK) pelo apoio. Saída de `bin/forge-testes --listar bin/forge-check`: dirigido, com `test_hooks` e sem nenhum `test_hooks_volta_*`. Antes do diff, a classe estava dentro de `test_hooks` e rodava. O `MapaDoForgeCheck` (`tests/test_testes_tocados.py:518`) não percebe porque só segue `import test_*`, e o apoio se chama `apoio_volta_unica`.
- Caminho: uma mudança só em `bin/forge-check`, que os hooks carregam para decidir, chega ao pre-push sem passar pelo corpus nem pelas propriedades da volta única. O CI do PR roda a suíte inteira e segura antes do merge, por isso a severidade é baixa. Mesmo assim, o filtro do pre-push (decisão M8) deixa de valer o que diz e perde cobertura em relação à base.
- Correção mínima: incluir `VOLTA_UNICA` na regra `bin/forge-check` (`FORGE_CHECK + VOLTA_UNICA` na linha 86, ou na tupla) e fazer o `MapaDoForgeCheck.modulos_que_usam` seguir também os apoios de `tests/` (por exemplo `IMPORTA` aceitando `apoio_[a-z0-9_]+`, com o apoio entrando no fecho). Sem a segunda parte, o `sobram no mapa FORGE_CHECK` reprova a primeira.

**A2. Equivalência cega a divergência de argumentos** (recomendação; severidade informativa; esforço P; dono `tech-lead`).
- Evidência: com o driver alterado em `$TMPDIR` (sem tocar a branch), o `test_decisao_em_lote_igual_ao_subprocesso_do_hook` segue verde nas mutações `CRITICO -> None`, sem `clone_do_forge` e `os.chdir` na raiz do `conformidade` para os dois hooks. A amostra não passa pela falha fechada nem pelo clone do Forge.
- Hoje o driver está igual ao `__main__` (conferido acima), então não há defeito. O risco fica para o futuro: se o `__main__` de um hook ganhar ou mudar um argumento, as propriedades passam a provar outra coisa que não o hook real, e a equivalência não percebe.
- Correção mínima: um teste que leia por AST a chamada `executar(...)` do `__main__` de `hooks/conformidade.py` e `hooks/parecer.py` e a compare com `EXECUCAO` do driver. Opcionalmente, pôr na amostra um texto que caia em `falhar_fechado`.

**Informativo.** O driver roda `python -c` sem `-I`, com o diretório de trabalho no repositório montado pelo fixture. É a mesma postura do `LANCADOR` que já existia, sem entrada externa, e por isso não é achado. O `test_pesos_teto.py` lê só o `tests/pesos-d4.json` local, sem superfície nova.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: revisão estática do diff, comparação por AST (script em `$TMPDIR`), `bin/forge-testes --listar` e a execução local só do teste de equivalência e das suas mutações (`R-CUSTO`, sem rede). Não estavam no PATH: `gitleaks`, `semgrep`, `zizmor`, `actionlint`, `osv-scanner`. Isso é lacuna sem efeito aqui, porque o diff só mexe em testes e no mapa, sem segredo, dependência nem workflow.
