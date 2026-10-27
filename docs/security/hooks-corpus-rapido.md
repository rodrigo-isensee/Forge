---
tipo: revisao-seguranca
contrato: 1
pedido: hooks-corpus-rapido
branch: melhoria/hooks-corpus-rapido
commit: 1ead0ed775d77d8bdb15034e8350521fda23434c
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-27
---
# Review de segurança: hooks-corpus-rapido

Revisão do diff `363ceee...1ead0ed` (primeira rodada em 978d2d6, revalidações em 2c14a56 e 1ead0ed) (pedido HOOKS-CORPUS-RAPIDO, etapa E2.1 do HOOKS-CORPUS-RAPIDO-REV): a classe `CorpusHeredocVoltaUnica` sai de `tests/test_hooks.py` para `tests/test_hooks_volta_{corpus,lancador,propriedades}.py` com o apoio em `tests/apoio_volta_unica.py`, a decisão dos hooks passa a ser em lote, entra o teste de equivalência e o `tests/test_pesos_teto.py`, e o mapa do `bin/forge-testes` ganha `VOLTA_UNICA`.

## Gatilhos
`R-SEGURANCA`, controles do Forge: os testes que provam os hooks `conformidade` e `parecer` (o corpus da volta única e as propriedades) e o mapa do filtro do pre-push (`bin/forge-testes`).

## Achados
- A1 (recomendado) tests/test_hooks_volta_lancador.py:68 · o mínimo de 20 formas vivas vale com qualquer env que aceite `-a`, mas numa máquina com GNU anterior ao 9.5 e uutils juntos as 10 formas só-GNU com `-a` são puladas e sobram 18: falha espúria, sem afrouxar controle; ajuste opcional (por exemplo, contar as formas que alguma família viva aceitaria)

## Revalidação (delta 978d2d6..2c14a56)
- A1 (resolvido): `bin/forge-testes:67` agora tem `FORGE_CHECK = (...) + VOLTA_UNICA` e `test_doutor_relogio`. `bin/forge-testes --listar bin/forge-check` lista os três `test_hooks_volta_*` e `test_doutor_relogio` (25 módulos). O `MapaDoForgeCheck` (`tests/test_testes_tocados.py:529`) segue os apoios `apoio_*` importados, e `test_modulos_da_volta_unica_rodam_onde_o_test_hooks_roda` cobre cinco caminhos.
- A2 (resolvido): `test_driver_do_lote_chama_o_executar_como_o_main_de_cada_hook` (`tests/test_hooks_volta_corpus.py:80`) compara por AST a chamada `executar` do driver com a do `__main__` de cada hook (nome, `principal`, `CRITICO`, `clone_do_forge`, `regra_do_prazo`) e confere o `os.chdir` por hook. Mutação à mão em cópia do commit (`$TMPDIR`, branch intocada): base verde; `CRITICO -> None`, sem `clone_do_forge`, os dois hooks na pasta do conformidade e `regra_do_prazo` trocada deixam o teste vermelho (4 de 4).
- Delta fora de testes e do mapa: nenhum arquivo em `hooks/`, `scripts/` ou workflow mudou; sem segredo, dependência nem superfície nova. Os demais pareceres e `tests/mutantes/hooks-corpus-rapido.json` são dado.

## Revalidação 3 (delta 2c14a56..1ead0ed, DECISÃO DO DONO 14:32, C)
Só `tests/test_hooks_volta_lancador.py` mudou em teste (o resto é parecer e changelog); `hooks/`, `bin/` e workflow intactos.
- Decisões dos hooks: o laço que asserta 2 em cada texto (`:36-41`) e o `assertGreaterEqual(len(textos), 75)` vêm antes de qualquer sonda ou pulo; a adaptação não toca nelas, e o texto de `-a` segue recusado por ambos os hooks em todos os envs.
- `USA_ARGV0` (`:61`): avaliada sobre os 28 moldes de `FORMAS_DO_LANCADOR`; casa exatamente os 22 que usam `-a`, `-ia`, `-ax`, `--argv0`, `--ar` e `--argv0=` e não casa os 6 sem a opção (4 `rev A2` com `-S`/`-f`/`-i`, os 2 controles); sem falso positivo que esconda forma viva.
- `env_aceita_argv0` (`:67`): roda `env -a x true` e usa o código de saída. Onde o env recusa `-a` (GNU 9.4), a forma não é comando e não há o que provar; onde aceita, a forma segue provada viva por `rodou_com_o_env`. Conferido: uutils 0.8 e GNU 9.7 desta máquina aceitam, e o teste passa (1,2 s); o `coreutils` multi-chamada recusa `-a` e não entra em `envs_da_maquina`.
- Mínimo `20 if any(com_argv0.values()) else 2`: com um env que aceita `-a` o limiar de 20 fica; o 2 só vale quando nenhum env o aceita, e então as formas com `-a` não rodam na máquina. Não deixa passar forma que roda e não é recusada (a recusa é asserida para todas). A ressalva é o A1 acima, de falha espúria e não de controle.
- Lacuna aceita pelo dono: no CI (GNU 9.4) a prova de 20 formas vivas não roda até o cartão CI-ENV-ARGV0; as decisões dos hooks seguem integrais lá.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: revisão estática do diff, regex sobre os moldes e execução do teste do lançador (só local), comparação por AST (script em `$TMPDIR`), `bin/forge-testes --listar` e a execução local só do teste de equivalência e das suas mutações (`R-CUSTO`, sem rede). Não estavam no PATH: `gitleaks`, `semgrep`, `zizmor`, `actionlint`, `osv-scanner`. Isso é lacuna sem efeito aqui, porque o diff só mexe em testes e no mapa, sem segredo, dependência nem workflow.
