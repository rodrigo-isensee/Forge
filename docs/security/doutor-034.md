---
tipo: revisao-seguranca
contrato: 1
pedido: versao-033
branch: melhoria/doutor-034
commit: 5bd8bdc7fc5657fe591ab47d024e2c08b004b0e4
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-04
---
# Review de segurança: versao-033 (trilha doutor 0.34)

## Revalidação (volta 1)
HEAD revisado: 5bd8bdc, um commit só sobre b45e40a. A branch foi reescrita: a parte do `bin/forge-doutor` (N-DOUTOR-F8-CAMINHO) saiu daqui para a `melhoria/doutor-f8-caminho` (85c5b80), que não toca em `hooks/` e não entra neste parecer. Li à mão o delta `4bfc92e..5bd8bdc` em `hooks/doutor.py`, `tests/test_doutor.py`, `tests/mutantes/doutor-034.json` e `changelog.d/doutor-034.md`. Não rodei o `forge-check delta`, porque a reescrita tirou da branch o commit do parecer anterior.
- A decisão do aviso (`hooks/doutor.py:105`) é a mesma de 4bfc92e. Só a docstring mudou (linhas 75-79), agora dizendo "o mesmo par `atual`/`ultima`".
- A2 fechado: em `principal` (`hooks/doutor.py:186-189`), o `try` envolve só a chamada `aviso_de_relogio(hook)` e captura só `OSError`, que vira `relogio = None`. `aviso_de_versao_nova` (linha 183), a montagem da linha e o `print` (linha 193) ficam fora do `try`. O `try` não engole falha do diagnóstico nem do aviso de versão. Qualquer outra exceção do relógio (`ValueError`, `KeyError`...) continua subindo até `executar` (`hooks/_comum.py:2519-2522`), vai para o `erros.log`, e o hook sai 0, sem bloquear (sem `critico`, ADR 0003). A falha segura continua valendo. O `with hook.trava()` libera o `flock` mesmo com a exceção.
- Testes novos: `test_falha_do_relogio_no_stop_nao_come_o_aviso_de_versao` (troca `aviso_de_relogio` por uma função que levanta `OSError`, num subprocesso), `test_versao_em_uso_diferente_com_a_mesma_ultima_avisa_no_dia_seguinte` e `test_versao_nova_ainda_nao_avisada_de_dia_anterior_avisa_no_dia_seguinte`. Os mutantes M1 a M4 de `tests/mutantes/doutor-034.json` cobrem as guardas da linha 105 e o `except OSError`. `python3 -I -m unittest discover -s tests -p test_doutor.py`: 75 OK em 5bd8bdc.
- A1 virou cartão (orientação do coordenador). A linha citada foi atualizada para 105.
- A3 é novo e só recomendação: o `OSError` capturado não vai para o `erros.log`.

## Revisão inicial (4bfc92e)
Revisão estática do diff `b45e40a..4bfc92e` (commits 8d097be, 9db3c4b, 4bfc92e): `hooks/doutor.py` (+4 -3), `bin/forge-doutor` (texto do aviso da F8), `changelog.d/doutor-034.md` e testes (`tests/test_doutor.py`, `tests/test_doutor_protecao_gh.py`). Também li o contexto que o diff não toca: `aviso_de_versao_nova` inteira, `principal`, `gravar_json`, `ler_json`, `Hook.run`, `Hook.trava` e `executar` em `hooks/_comum.py`, e o consumidor do cache em `bin/forge-check` (`comparar_com_o_cache_do_projeto`).

## Gatilhos
Controle do Forge (`R-SEGURANCA`): `hooks/doutor.py` é hook do plugin. O que muda nele é só a decisão de repetir ou não o aviso de versão nova. O texto da F8 em `bin/forge-doutor` só troca uma mensagem: não mexe em rede, permissão nem decisão.

## Achados
- A1 (recomendado) hooks/doutor.py:105 · o cache local agora silencia o aviso por versão, não só por um dia: um `versao-nova` forjado com avisado=true e o par atual/ultima certo cala esse aviso até sair outra versão. A trava continua no forge-check. Virou cartão.
- A3 (recomendado) hooks/doutor.py:188 · o `except OSError` do relógio descarta o erro sem `hook.registrar_erro(erro)`: uma falha de disco repetida fica invisível no erros.log. Registrar antes de seguir.

## Detalhe dos achados
**Pergunta 1. Avisar uma vez por versão esconde um atraso real?** Não. Avisar uma vez por versão diminui a insistência, mas o registro do atraso continua. Em `hooks/doutor.py:107-109`, o cache de cada dia continua gravando `defasado`, `atual` e `ultima` a partir da consulta. Em `bin/forge-check` (`comparar_com_o_cache_do_projeto`, perto da linha 5935), o `forge-check` segue usando esse cache como prova positiva e bloqueia projeto atrasado, seja qual for o valor de `avisado`. O silêncio cai em três casos, todos verificados no código: versão ainda mais nova (`ultima` diferente), plugin atualizado mas ainda atrás (`atual` diferente) e um dia com a consulta desligada no meio (`avisado` volta a False e o aviso reaparece). Os três falham para o lado de avisar mais, não menos. O teste `test_a_mesma_versao_nova_nao_avisa_de_novo_no_dia_seguinte` confirma que o cache mantém `defasado: true` mesmo calado. Fica uma questão de produto, sem caminho de ataque: quem ignora o aviso no primeiro dia não o vê de novo na sessão. Lembrar de novo de tempos em tempos (por exemplo, semanalmente) é decisão do dono, não achado.

**Pergunta 2. O cache pode ser forjado ou envenenado?**
- Caminho: o hook monta `Hook.run()` como `<cópia principal>/.forge/run/` (`hooks/_comum.py:2341-2350`), com `.gitignore` `*`. A raiz `/.forge` também é ignorada no repositório. O caminho é fixo e não vem da entrada do hook.
- Conteúdo: `ler_cache_versao` (`hooks/doutor.py:58-63`) aceita só um `dict` e trata JSON inválido como `{}`. A expressão nova (linha 104) usa `antigo.get(...)` e compara com `is True` e com igualdade de tupla: nenhum tipo vindo do JSON levanta exceção ou é executado. O texto mostrado vem do cache só no mesmo dia (comportamento anterior, inalterado). No dia seguinte, ele é sempre regerado por `texto_de_versao_nova` a partir da consulta.
- Permissões e escrita: `gravar_json` (`hooks/_comum.py:2226-2229`) grava num arquivo temporário e usa `os.replace`, sob a trava `flock`. Nada mudou nesse ponto.
- A1, caminho de ataque: quem já escreve na cópia de trabalho (o próprio usuário, um processo local do mesmo usuário ou um repositório que versione à força `.forge/run/versao-nova`) pode gravar `{"avisado": true, "atual": X, "ultima": Y}` e calar o aviso de uma versão Y que precisa prever. Antes da mudança, o mesmo forjamento só calava um dia. Ganho do atacante: manter o usuário numa versão antiga sem o lembrete diário. O impacto é limitado por três coisas: (a) o `forge-check` continua lendo `defasado` e bloqueando nos projetos; (b) quem escreve na cópia de trabalho já tem poder maior (código, `CLAUDE.md`, hooks do projeto); (c) a consulta diária regrava `defasado` com o resultado real. Severidade **baixa**. Correção mínima, opcional: nenhuma; se o dono quiser, ignorar `avisado` quando o arquivo estiver rastreado pelo git. Esforço P. Dono: implementador do doutor (forge-dev).

**Pergunta 3. O hook continua falhando de forma segura?** Sim. `executar("doutor", principal)` roda sem `critico` (`hooks/doutor.py:192-194`). Qualquer exceção cai em `hooks/_comum.py:2519-2522`: é registrada em `erros.log` e o hook sai com 0, sem bloquear a sessão (ADR 0003). A linha nova não acessa rede, não abre arquivo e não levanta exceção (`resultado["atual"]` e `["ultima"]` já eram lidos no mesmo ramo antes). Testes: `python3 -I -m unittest discover -s tests -p test_doutor.py` deu 72 OK em 4bfc92e.
- A2 (FECHADO em 5bd8bdc, ver Revalidação), evidência original: `aviso_de_versao_nova` grava `avisado: True` (linha 114) antes de `principal` imprimir (linha 189). Entre um e outro roda `aviso_de_relogio` (linha 185), que trata os erros de rede (`bin/forge_versoes.py:200-225`) mas ainda pode falhar ao gravar (`OSError`, disco cheio). Nesse caso, o aviso daquela versão não é impresso e não volta mais: antes voltava no dia seguinte. Não há atacante. É uma falha de disponibilidade do aviso, e a prova de atraso continua no cache. Severidade **baixa**. Correção mínima: deixar a marca `avisado` para depois do `print`, ou proteger `aviso_de_relogio` com `try` dentro de `principal`. Esforço P. Dono: implementador do doutor.

`bin/forge-doutor:388-389` (só em 4bfc92e; saiu desta branch em 5bd8bdc): só trocava o texto. Sem achado.

**A3 (volta 1)**, evidência: `hooks/doutor.py:188`. O `OSError` vira `None` sem passar por `hook.registrar_erro`. Não há atacante: o efeito é perder diagnóstico, porque um disco cheio ou um `.forge/run` sem permissão de escrita deixa de aparecer no `erros.log` pelo lado do relógio. Severidade **informativa**. Correção mínima: `except OSError as erro: hook.registrar_erro(erro); relogio = None`. Esforço P. Dono: implementador do doutor.

## Riscos aceitos e ferramentas
Nenhum risco aceito (o parecer é `aprovado`; A1 e A3 são recomendações; A2 está fechado que não devolvem a entrega, `R-REVIEW`). Ferramentas: leitura do diff e do código ao redor, mais `python3 -I -m unittest discover -s tests -p test_doutor.py` (72 OK em 4bfc92e; 75 OK em 5bd8bdc). Lacuna: `gitleaks` e `semgrep` não estão no PATH deste ambiente. O diff não traz credencial nem dependência nova (só biblioteca padrão) e não usa rede nova (`R-CUSTO`).
