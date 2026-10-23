---
tipo: revisao-seguranca
contrato: 1
pedido: impl-d4-textos-dono2
branch: melhoria/impl-d4-textos-dono2
commit: 832649c3b42360e4d1fb9285d7711d4c4166022f
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-23
---
# Review de segurança: RET-TEXTOS-DONO2

Escopo: os commits `2a96c99`, `8c1b650` e `be4a398` sobre a base `38c58247` (F7, revisão de UX só com interface; F10, aviso `entrada-sem-registro` no `hooks/vigia.py`; textos de `R-DECISAO`, `agents/jarvis.md`, `docs/hooks.md`, `docs/economia-de-tokens.md`; 13 fixtures novas em `tests/hooks/vigia/`). O merge do `tech-lead` sobre a `develop` fica fora deste parecer.

## Gatilhos
- Controles do Forge: hook `hooks/vigia.py` (nova checagem que lê a transcrição da sessão).
- Instruções do Jarvis (`agents/jarvis.md`) e regra com ID (`docs/regras/R-DECISAO.md`).
- Dado do dono: a checagem lê o texto que o usuário digitou.

## Achados

## Detalhe dos achados
Nenhum bloqueante. O que foi conferido:

- **Vazamento do texto do dono:** `hooks/vigia.py:221` só devolve o texto para contagem; a saída usa o texto fixo (`hooks/vigia.py:433`, `TEXTOS_FIXOS`) e `violacoes.jsonl` recebe só a contagem e o id da mensagem, saneado para `[0-9A-Za-z_-]{1,64}`. Sem injeção na `systemMessage` (o id saneado e um inteiro). A fixture `entrada-sem-registro-texto-fixo-sem-trecho` prova a ausência do trecho no log. Nada vai a `additionalContext` (ADR 0003).
- **Confiança da entrada:** só conta mensagem `type: user` sem `isMeta`, `isSidechain`, `toolUseResult` nem `sourceToolUseID`, com conteúdo só de blocos `text` e que não começa por `<`. Resultado de ferramenta e lembrete de sistema (conteúdo controlado por terceiros) não disparam o aviso: fixtures `tool-result-nao-conta` e `lembrete-de-sistema-nao-conta`.
- **Negação de serviço:** a regex `_ITEM` não tem repetição aninhada; medi 5 entradas patológicas de 64 KB (espaços, dígitos, marcadores repetidos), todas abaixo de 4 ms. Leitura limitada a 64 KB por mensagem; o deslocamento próprio (`estado["entradas"]`) evita reler a transcrição, e a poda o amarra a `transcricoes`. Erro interno continua saindo 0 com registro em `erros.log` (aviso, não controle de bloqueio: falhar aberto é o certo aqui).
- **Escopo do evento:** só `hook_event_name == "Stop"`; o `SubagentStop` não consome o deslocamento (fixture `subagentstop-antes-do-stop-avisa`).

Recomendação (informativa, sem caminho de ataque com ganho; não bloqueia): `grava_registro` (`hooks/vigia.py:239`) aceita como gravação qualquer Bash com operador de escrita cuja linha cite um dos destinos, inclusive em comentário, e também a chamada que foi barrada ou falhou; o efeito em `hooks/vigia.py:270` é zerar as listas pendentes e calar o aviso. Um agente pode silenciar o lembrete, mas o aviso é heurístico e não é portão: o ganho é só esconder um lembrete, e `R-DECISAO` continua verificada pela revisão de transcrições. Correção mínima, se quiserem: só contar a gravação cujo `tool_result` correspondente não veio com `is_error`. Esforço P. Dono: autor da branch (`forge:tech-lead` decide se vira cartão).

## Riscos aceitos e ferramentas
- Riscos aceitos: nenhum.
- Ferramentas: leitura estática do diff; `python3 -m unittest tests.test_textos_dono_f10 tests.test_textos_dono_f7` (5 testes, OK); `python3 scripts/suite-paralela.py` (1599 testes: todas as fixtures de `vigia/` passam; 4 falhas, `test_hooks` em `conformidade/contrib-falha-fechada-pela-raiz-cwd-{home,wt}-bloqueia` e `test_erro_interno_com_lista_de_permissao_falha_fechado`, e `test_pre_push_shellcheck.test_shellcheck_no_hook`, que falham igual na base `38c58247` e vêm do ambiente, não desta branch); medição de tempo da regex `_ITEM`.
- Lacunas: `gitleaks` e `semgrep` não estão no PATH; a varredura de segredos das fixtures fica para o CI. Pela leitura, as fixtures só trazem textos de exemplo, sem credencial.

## Revalidação por delta (REVAL-288)
Delta `be4a398..832649c` (o parecer anterior vale para `be4a398`): merge da `develop` `7423c44` (PR #288, FIX-SUITE-LOCAL e os registros da 0.28.0), alinhamento do `pedido:` e pareceres de review e QA. Decisão do dono "C" (2026-10-23): revalidar por delta, sem afrouxar. Os arquivos que o parecer cobre (`hooks/vigia.py`, `agents/jarvis.md`, `docs/regras/R-DECISAO.md`, as fixtures de `tests/hooks/vigia/`) não aparecem no delta.
- `.githooks/pre-push:242`: só a diretiva de shellcheck (`SC2317,SC2329`); sem mudança de comportamento.
- `tests/apoio_pathlib_312/sitecustomize.py` (novo), `tests/test_hooks.py:56-57,362-363,1046` e as duas fixtures `contrib-falha-fechada-pela-raiz-cwd-*`: o `PYTHONPATH` com o `sitecustomize` só é posto pelos testes, no processo do hook de teste; o módulo restaura a semântica de `Path.exists/is_dir/is_file` da 3.12 (re-levanta `OSError` fora de ENOENT/ENOTDIR/EBADF/ELOOP); não é lido em produção. Sem caminho de ataque, sem rede, sem segredo.
- `changelog.d/*`, `docs/reviews|qa|security/*`: só documentação.
Superfície de segurança da branch inalterada. Veredito: aprovado, sem achado novo; a recomendação informativa acima segue valendo. Ferramentas: `forge-check delta` e leitura estática; `gitleaks` e `semgrep` fora do PATH (lacuna igual à anterior).
