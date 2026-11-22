---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-mp9-guia
commit: 048b5baa53dc327d642bece4b0b90310b19b28dd
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: v0479-mp9-guia (E24.4)

Escopo: o guia "Vários projetos na mesma máquina" (README e `templates/projeto/CLAUDE.md`, MP9, diretriz 35) e o teste novo `tests/test_guia_varios_projetos.py`. Só os testes do diff rodaram (máquina carregada); a suíte inteira fica no check-run `bateria` do CI do PR, sem rerrodar.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Guia no README traz cada parte do desenho (janela por projeto no modo auto, partes iguais, `peso`, `FORGE_CARGA_LIVRE=1`, `[<projeto>]`, `Projeto: <nome>`, `--maquina`) | `test_readme_tem_a_secao_com_cada_parte` | seção ausente ou menor que 200 caracteres | passou |
| Modelo de projeto traz o resumo e aponta o guia | `test_modelo_de_projeto_traz_o_resumo_e_aponta_o_guia` | `## Sessão` sem alguma parte | passou |
| O `peso` do exemplo vale no hook (faixa 0 a 10) | `test_peso_do_guia_cabe_na_faixa_do_hook` | `PESO_MAXIMO` mudar sem atualizar o guia | passou |
| Seção ausente é acusada | `test_secao_ausente_e_acusada` | título inexistente | passou |
| Citação do README por teste registrada | `test_reval_delta.py` (10 testes) | nova leitura de README sem registro | passou |

## Vermelho antes do verde
`forge-testes --vermelho` passou do prazo de 120 s na máquina carregada e foi interrompido (sem veredito, não vale como vermelho). No lugar, feito à mão: cópia da base `0c47762a` em `$TMPDIR` com o teste novo copiado; `python3 -I -m unittest discover -s tests -p test_guia_varios_projetos.py` deu `Ran 4 tests ... FAILED (failures=8)` (README sem a seção; modelo sem 7 partes). No head: `Ran 4 tests ... OK`.

## O comando do guia funciona como dito
- `peso` em `.forge/config.json`: o hook lê (`hooks/agentes.py:247`, `peso_valido`); 2 vale, e a faixa 0 (exclusivo) a 10 confere com o texto.
- `forge-status --maquina`, `FORGE_CARGA_LIVRE=1` (só pula a trava de memória) e `[<projeto>]`/`Projeto: <nome>` existem nas fontes e batem com o texto.
- O `jq ... > config.novo && mv` não pôde ser executado aqui: `jq` não está instalado nesta máquina. `scripts/preparar-estacao.sh:474` o instala na estação do dono. Não é defeito do diff.
- Não rodei o comando contra um `.forge/config.json` real; a leitura do `peso` pelo hook está coberta por testes existentes, não por este parecer.

Mutação: não se aplica (diff só de texto e teste; sem regra de código).

## Revalidação (head a8d4dce4, escopo incremental)
`forge-check parecer delta` (2054ef3b..a8d4dce4): no domínio do QA só `tests/test_reval_delta.py`, 1 linha, remoção de comentário duplicado em `CITACOES_CONHECIDAS`; sem mudança de comportamento. Rodados com TMPDIR: `test_reval_delta.py` (10 testes, OK) e `test_guia_varios_projetos.py` (4 testes, OK). Suíte inteira: check-run `bateria` do CI do PR, sem rerrodar. Aprovado mantido.

## Revalidação (E24.13, head abb581a5)
Delta desde a8d4dce4: merge da develop (duas linhas em `templates/projeto/CLAUDE.md`, fora da seção do guia) e a linha `test_guia_varios_projetos: 0.1` em `tests/pesos-d4.json`. Rodados: `python3 -I -m unittest discover -s tests -p test_guia_varios_projetos.py` (4 testes, OK) e `python3 -m unittest tests.test_forge.PesosDaSuite` (3 testes, OK). Suíte inteira não rodou (check-run `bateria` do CI). Parecer: aprovado.

## Revalidação (E24.19, head 862d9ecb)
`forge-check parecer delta` (abb581a5..862d9ecb): no domínio do QA só `bin/forge-testes` (`test_guia_varios_projetos` entra em `LEITORES_DE_TEXTO` e no mapa do `README.md`) e `tests/test_guia_varios_projetos.py` (import de `agentes`, que liga `hooks/agentes.py` ao teste no mapa). Rodados com TMPDIR: `test_testes_tocados.py` (196 testes, OK; 1 pulado pelo próprio sandbox, `/proc` de outro namespace) e `test_guia_varios_projetos.py` (4 testes, OK). Suíte inteira: check-run `bateria` do CI do PR, sem rerrodar. Parecer: aprovado.

## Revalidação (E24.24, head e266490b)
`forge-check parecer delta` (862d9ecb..e266490b, sem o que veio da base): no domínio do QA `README.md`, `bin/forge-testes`, `tests/pesos-d4.json` e `tests/test_reval_delta.py`; o delta é o merge da develop com dois conflitos de lista resolvidos com os dois itens: `FORGE_CHECK` e `LEITORES_DE_TEXTO` em `bin/forge-testes` (`test_comando_pronto`, `test_retro_pendentes`, `test_comparar` junto de `test_guia_varios_projetos`; os módulos existem) e `CITACOES_CONHECIDAS` em `tests/test_reval_delta.py` (entradas da develop e a do guia presentes); `pesos-d4.json` segue JSON válido. Rodados com TMPDIR: `test_guia_varios_projetos.py` (4 testes, OK), `test_testes_tocados.py` (196 testes, OK; 1 pulado pelo sandbox) e `test_reval_delta.py` (10 testes, OK). Suíte inteira: check-run `bateria` do CI do PR, sem rerrodar. Parecer: aprovado.

## Revalidação (E24.29, head 048b5baa)
`forge-check parecer delta` (e266490b..048b5baa): no domínio do QA só `tests/test_conferir_reversao.py`; o delta é uma linha no `setUp` (cria `tests/test_guia_varios_projetos.py` no repositório falso, pois o MAPA leva `README.md` também ao guia) e o comentário que a explica; sem código de produção. Rodados com TMPDIR: `test_conferir_reversao.py` (13 testes, OK), `test_guia_varios_projetos.py` (4, OK) e `test_testes_tocados.py` (196, OK; 1 pulado pelo sandbox, o mesmo da rodada anterior). Suíte inteira: check-run `bateria` do CI do PR, sem rerrodar. Parecer: aprovado.
