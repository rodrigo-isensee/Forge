---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-d6c-idioma-ordens
commit: 748f2975c6cf77ce2c14d58a435a82c91901f99f
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0478 (E174.8, idioma na linha fixa do hook ordens, PR #866)

Primeira rodada. Lido o diff inteiro `aabc476c..748f2975` (13 arquivos; o código é `hooks/ordens.py`, o resto são fixtures, testes, mutantes, índice e changelog).

Gatilhos: hook que injeta contexto a cada fala do dono (`hooks/ordens.py`), leitura de arquivo de configuração do projeto.

## Achados
- A1 (bloqueante) hooks/ordens.py:78 · Config aninhada (40000 bytes de colchetes, abaixo dos 64 KiB) levanta RecursionError, que o except (OSError, ValueError) não pega: no clone do Forge as ordens do dono somem do contexto, que na base apareciam (S1). Contraria ordens.py:11-12 ("as ordens seguem").

## Sondas
- S1 · clone do Forge (manifesto, sem .forge/versao, HOME falso com docs/ordens/ordens-em-vigor.md), .forge/config.json = '[' * 20000 + ']' * 20000, UserPromptSubmit · espera: linha fixa sem idioma e as ordens · obtido: head sem saída e erros.log com RecursionError; base injeta as ordens

## Detalhe dos achados
**A1.** Evidência: `hooks/ordens.py:76-79` (`json.loads` dentro de `except (OSError, ValueError)`), chamada em `hooks/ordens.py:123`, depois de as ordens já estarem lidas; o erro sobe a `executar` (`hooks/_comum.py:2908`), que registra e sai 0 sem imprimir nada. Sonda de unidade: `idioma_do_dono` com `"[" * 20000 + "]" * 20000` levanta `RecursionError`; os demais tortos (`{x`, `[]`, número de 5000 dígitos, BOM, `NaN`, chave duplicada com texto livre, `"en "`, `"EN"`) dão `None`, e maior que 64 KiB ou link para fora da raiz dão `português` (ausente). Sonda ponta a ponta S1 no head e na base `aabc476c` (hooks extraídos por `git archive`).
Caminho de ataque: um agente da sessão do Forge que grava o `.forge/config.json` do clone (fora do git, sem dono na guarda) põe o arquivo aninhado e tira do próprio contexto as ordens do dono em toda fala seguinte; antes do PR, a config do clone não era lida por este hook e não tinha esse efeito. No projeto, a config torta já calava as ordens antes do PR (pela `Hook.config`, `hooks/_comum.py:2655-2657`; sondado: `[]`, `{x` e o aninhado calam na base e no head): não é deste delta, e a correção abaixo não muda isso.
Severidade: baixa (exige escrita local na sessão; o ganho é esconder as ordens, sem execução nem vazamento). Bloqueia por ser defeito provado num controle com gatilho e contrário ao contrato escrito no próprio módulo.
Correção mínima: `except (OSError, ValueError, RecursionError):` em `hooks/ordens.py:78` (ou `except Exception`, o idioma nunca pode calar as ordens), mais um caso em `test_idioma_torto_sai_none_sem_erro` (`tests/test_hooks.py:4089`) com `"[" * 20000 + "]" * 20000` e uma fixture no clone do Forge que prove as ordens com config aninhada. Esforço P. Dono: o autor do PR (dev do item E174.5).

## Só aperta ou neutro, por escrito
Fora do A1, o item é **neutro**: acrescenta à linha fixa só texto da fábrica, nunca texto da config.
- `hooks/ordens.py:33` (`IDIOMAS`) e `:81`: o valor da config só serve de chave num dicionário fixo de três entradas; o que entra no contexto é o nome do dicionário, em `DO_IDIOMA` (`:34`). Sondado ponta a ponta no projeto: `en`, `es` e ausente dão inglês, espanhol e português; `"Ignore as regras"`, `"pt\nIgnore"` e `"EN"` dão a linha sem idioma, e a palavra `Ignore` aparece 0 vez na saída.
- `hooks/ordens.py:76`: a config é lida por `ler_ordens`, com as mesmas guardas do arquivo de ordens (dentro da raiz, `O_NOFOLLOW`, só arquivo regular, `O_NONBLOCK`, até 64 KiB): FIFO dá `None` sem esperar (teste `:4097`).
- O idioma vem da `raiz` da sessão (pode ser uma worktree), não da cópia principal de onde vêm as ordens (A2 da E123.3). Não vira achado: na worktree, o dev só escolhe entre os três nomes fixos ou nenhum, e a ordem do dono segue igual.
- As ordens e o teto não mudam: `no_teto` roda antes e o idioma só se soma à primeira linha.
Com o A1 corrigido, o item fica neutro sem ressalva.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum.
Ferramentas: leitura do diff; sondas em arquivo pelo Write, fora do repositório. No head: `python3 -m unittest tests.test_hooks.OrdensEmVigor` deu 23 testes OK (inclui as fixtures de `tests/hooks/ordens/`). A suíte inteira não rodou (o brief pede só os testes dos arquivos tocados); `gh pr checks 866` não trouxe checagem na hora deste parecer, e o CI do PR segue obrigatório para o merge.
