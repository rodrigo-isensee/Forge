---
tipo: revisao-seguranca
contrato: 1
pedido: hooks-corpus-rapido
branch: melhoria/hooks-corpus-rapido
commit: 2c14a56245b9dc4060903073c5e4e8227aecd6b3
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-27
---
# Review de segurança: hooks-corpus-rapido

Revisão do diff `363ceee...2c14a56` (primeira rodada em 978d2d6) (pedido HOOKS-CORPUS-RAPIDO, etapa E2.1 do HOOKS-CORPUS-RAPIDO-REV): a classe `CorpusHeredocVoltaUnica` sai de `tests/test_hooks.py` para `tests/test_hooks_volta_{corpus,lancador,propriedades}.py` com o apoio em `tests/apoio_volta_unica.py`, a decisão dos hooks passa a ser em lote, entra o teste de equivalência e o `tests/test_pesos_teto.py`, e o mapa do `bin/forge-testes` ganha `VOLTA_UNICA`.

## Gatilhos
`R-SEGURANCA`, controles do Forge: os testes que provam os hooks `conformidade` e `parecer` (o corpus da volta única e as propriedades) e o mapa do filtro do pre-push (`bin/forge-testes`).

## Achados

## Revalidação (delta 978d2d6..2c14a56)
- A1 (resolvido): `bin/forge-testes:67` agora tem `FORGE_CHECK = (...) + VOLTA_UNICA` e `test_doutor_relogio`. `bin/forge-testes --listar bin/forge-check` lista os três `test_hooks_volta_*` e `test_doutor_relogio` (25 módulos). O `MapaDoForgeCheck` (`tests/test_testes_tocados.py:529`) segue os apoios `apoio_*` importados, e `test_modulos_da_volta_unica_rodam_onde_o_test_hooks_roda` cobre cinco caminhos.
- A2 (resolvido): `test_driver_do_lote_chama_o_executar_como_o_main_de_cada_hook` (`tests/test_hooks_volta_corpus.py:80`) compara por AST a chamada `executar` do driver com a do `__main__` de cada hook (nome, `principal`, `CRITICO`, `clone_do_forge`, `regra_do_prazo`) e confere o `os.chdir` por hook. Mutação à mão em cópia do commit (`$TMPDIR`, branch intocada): base verde; `CRITICO -> None`, sem `clone_do_forge`, os dois hooks na pasta do conformidade e `regra_do_prazo` trocada deixam o teste vermelho (4 de 4).
- Delta fora de testes e do mapa: nenhum arquivo em `hooks/`, `scripts/` ou workflow mudou; sem segredo, dependência nem superfície nova. Os demais pareceres e `tests/mutantes/hooks-corpus-rapido.json` são dado.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: revisão estática do diff, comparação por AST (script em `$TMPDIR`), `bin/forge-testes --listar` e a execução local só do teste de equivalência e das suas mutações (`R-CUSTO`, sem rede). Não estavam no PATH: `gitleaks`, `semgrep`, `zizmor`, `actionlint`, `osv-scanner`. Isso é lacuna sem efeito aqui, porque o diff só mexe em testes e no mapa, sem segredo, dependência nem workflow.
