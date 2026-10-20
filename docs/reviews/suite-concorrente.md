---
tipo: review
contrato: 1
pedido: suite-concorrente
branch: melhoria/suite-concorrente
commit: 82c32f816268d0f32ee8298946043b9b3a0ff22b
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-20
---
# Review: trava da suíte no pre-push (SUITE-CONCORRENTE, E1.2, revalidação por delta)

Revalidação da volta do autor (E1.1v, `733f626` fix e `82c32f8` docs). O revisor não é o autor (outra instância, D-ETAPAS-INST). A segurança do hook continua com o `security-engineer` (E1.3, `docs/security/`); aqui ela só é citada.

## Delta lido
`forge-check delta --parecer docs/reviews/suite-concorrente.md`, intervalo `aed7b97..82c32f8` (a parte de código é igual a `af586f1..82c32f8`; o `af586f1` só traz o parecer de segurança):
- `.githooks/pre-push` +51 -12: linhas 8-11, 13-14, 17-34, 38, 41-52, 54-57, 94-99, 101, 109-111.
- `docs/hooks.md` +2 -2: linhas 105 e 107.
- `tests/test_pre_push_trava.py` +107 -7: linhas 42-46, 82-89, 91-92, 97-109, 207-285.
- `changelog.d/suite-concorrente.md` +1: linha 3.

Já lido e não revisto: o resto desses quatro arquivos (aprovado no parecer anterior, sobre `aed7b97`): as checagens de ref e de envio direto (pre-push:61-86), a espera com `FORGE_TRAVA_ESPERA` e a mensagem de limite estourado (92-93, 102-108), e os 7 testes antigos (só rodados, não relidos).

## Recomendações anteriores
- R1 (descritor 9 herdado pela suíte): atendida. `pre-push:111` roda `python3 -m unittest discover -s tests -q 9>&- >&2`. O teste `test_descritor_da_trava_nao_vaza_para_a_suite` faz a suíte mínima gravar `os.path.exists("/proc/self/fd/9")` e espera `False`. Com o hook de `af586f1` ele falha.
- R2 (frase de `docs/hooks.md` sobre o código de saída): atendida. `docs/hooks.md:105` agora diz "o código de saída é o de antes (0 com a suíte verde, 1 em qualquer falha)", que é o que o hook faz.
- R3 (`--status` segura a trava por um instante): atendida no que dá para atender. `pre-push:55-57` abre a trava só para leitura (`9<`: não cria nem trunca), confere o arquivo aberto e, se pega a trava, solta na hora (`flock -u 9`). O `flock -n` ainda pega a trava por um instante, e com `flock` não tem como ser diferente. `docs/hooks.md:107` descreve isso ("só testa a trava e a solta na hora").

## O que mudou
- A1 da segurança (`--status` só com um argumento exato): `pre-push:50` faz `[ "$#" -eq 1 ] && [ "$1" = "--status" ]`. O git chama o pre-push com dois argumentos (nome e URL do remoto), então um remoto chamado `--status` segue o caminho normal: espera a trava, roda a suíte e barra envio direto. Dois testes cobrem isso: `test_remoto_chamado_status_segue_o_caminho_normal` (também com `--status extra`) e `test_envio_direto_continua_barrado_com_trava_e_com_status` (develop, homolog e main, com `origin` e com `--status` como nome do remoto). A segurança julga se isso basta (E1.3).
- Subpasta `forge-<uid>` no recuo (`pre-push:15-39`): `XDG_RUNTIME_DIR` continua com o arquivo direto na pasta (privada do usuário). Em `$TMPDIR` e `/tmp`, o hook cria a subpasta com `mkdir -m 700` (modo `criar`). A subpasta é recusada se for link, se não for pasta ou se não for do usuário (`-O`). O `--status` não cria nada: sem subpasta, informa que não há suíte. Se o `mkdir` falha, a subpasta não existe ou não é pasta e o hook falha fechado (linha 30). Os dois ramos estão cobertos por teste.
- Pasta de recuo sem escrita (observação do autor e DECISÃO TÉCNICA do Jarvis de 2026-10-20): a linha 16 (`[ -w "$d" ]`) pula a pasta e passa à próxima. Ela não falha fechado. Concordo que isso não abre caminho: a pasta que acaba sendo usada passa pela mesma conferência da subpasta, e sem nenhuma pasta válida o hook sai 1 (linha 38). `docs/hooks.md:105` já diz "primeira pasta gravável", o que bate com o código. O comentário da linha 10 ("não há recuo para outra pasta") fala da subpasta, mas pode ser lido como se valesse para a pasta de recuo (R4 abaixo). A segurança julga o risco (E1.3).
- Abrir uma vez e conferir o arquivo aberto (`pre-push:41-47`, `94-101`): a checagem `-L` antes do `exec 9>>` continua necessária, porque o `>>` criaria o alvo de um link. O teste `test_trava_link_dentro_da_subpasta_e_recusada` confere que o alvo não nasce. Depois de abrir, `trava_confere` confere `-O /proc/self/fd/9`, ou seja, o arquivo aberto e não o caminho.
- `: > /proc/self/fd/9` (`pre-push:109`), ponto que a DECISÃO TÉCNICA mandou ao review: esse comando reabre o arquivo pelo link do `/proc`, que no Linux leva ao inode já aberto no descritor 9, e não ao caminho atual. Uma sonda numa cópia em `$TMPDIR` mostra isso. O script abre `a` no descritor 9, renomeia `a` para `b`, cria outro `a` ("intruso") e roda `: > /proc/self/fd/9` e `printf novo >&9`. Resultado: `b=novo a=intruso`. Ou seja, a truncagem e a escrita caem no arquivo aberto, sem a janela entre checagem e uso de reabrir pelo caminho. Não é literalmente "escrever pelo mesmo descritor" (há um `open` novo), mas o alvo é o mesmo inode, e o bash não tem `ftruncate` para fazer de outro jeito. O `printf` vai pelo próprio descritor 9 (linha 110), que está em modo de acréscimo, então depois da truncagem ele escreve a partir do início. O `/proc` amarra o hook ao Linux, o mesmo limite que o `flock` (util-linux) já impunha e que o pedido registrou (macOS). Isso não é regressão. Se a R1 da segurança aceita essa forma, quem decide é o `security-engineer` (E1.3).
- `docs/hooks.md:105,107` e `changelog.d/suite-concorrente.md:3` descrevem o que o código faz. As regras aparecem só pelo ID (`R-TETO`).
- Neutralidade (`R-NEUTRO`) e custo (`R-CUSTO`): o delta só usa `bash`, `flock`, `/proc` e Python padrão. Nada é pago e nenhuma regra fica mais frouxa. `tests/config.json` (invariantes) está fora do delta.

## Testes
- No HEAD `82c32f8`, na worktree (trava conferida antes: `.githooks/pre-push --status` · `nenhuma suíte do Forge rodando`, rc=1): `python3 -m unittest tests.test_pre_push_trava -v` · `Ran 15 tests in 5.258s` · `OK`. Os 7 testes antigos (`test_suite_sem_concorrente_roda_e_devolve_o_codigo_da_suite`, `test_segunda_execucao_espera_a_vez`, `test_status_acompanha_a_trava`, `test_trava_orfa_de_processo_morto_e_liberada`, `test_limite_estourado_sai_com_erro_e_nao_roda_a_suite`, `test_limite_invalido_e_recusado`, `test_trava_que_e_link_simbolico_e_recusada`) seguem verdes. O que o `aed7b97` já fazia não quebrou.
- Vermelho, numa cópia em `$TMPDIR` com o hook de `af586f1` e os testes de `82c32f8`: `Ran 15 tests` · `FAILED (failures=8, errors=1)`. O resultado bate com o relatório do autor. As 8 falhas vêm de 6 testes (`test_envio_direto_...` conta 3 subtestes) e o erro, de `test_recuo_cria_subpasta_700_do_usuario`. Ou seja, 7 dos 8 testes novos falham com o hook antigo. O oitavo, `test_status_nao_cria_subpasta_nem_trava`, passa também no hook antigo, que não criava nada no `--status`. Ele é guarda contra regressão do modo `criar`, não um vermelho. Isso está certo, só não deve ser contado como vermelho.
- Os testes provam o que o nome diz: cada um olha o efeito, e não só o código de saída. Verifiquei que a suíte não rodou (`rodou` ausente), que o alvo do link não nasceu, que a pasta de recuo continua vazia no `--status`, o modo `0o700` e o `fd9` como `False`. Nenhum `skip`. O `hook()` passou a ler o stdin de um arquivo (as linhas de ref), e não mais de `DEVNULL`.
- Regras de ferramenta: shellcheck não está instalado nesta máquina (`sem shellcheck`), então fica para a bateria do CI no PR. Aqui rodei só `bash -n .githooks/pre-push` · `sintaxe-ok`. A suíte completa (966 OK, do autor e do conferente) não foi refeita aqui: o pre-push deste envio a roda.

## Achados

## Detalhe dos achados
Recomendações. Nenhuma bloqueia.
- R4 (recomendado) `.githooks/pre-push:10` · "não há recuo para outra pasta" vale para a subpasta, mas pode ser lido como se valesse para a pasta de recuo, que é pulada quando não tem escrita (linha 16). Sugestão: "pasta sem escrita é pulada; a subpasta que existe e não pôde ser criada ou conferida falha fechado".
- R5 (recomendado) relatório do autor e QA (E1.4) · o vermelho é "7 de 8 testes novos" (8 falhas contando subtestes, mais 1 erro). `test_status_nao_cria_subpasta_nem_trava` é guarda e passa nos dois hooks. Basta registrar isso assim na reprodução do QA.
- Para o `security-engineer` (E1.3), sem refazer aqui: a forma de truncar `: > /proc/self/fd/9` (sonda acima: atinge o inode aberto, não o caminho), a pasta de recuo sem escrita pulada e o fato de a subpasta já existente não ter o modo conferido (só dono, tipo e link; uma subpasta do próprio usuário com modo mais aberto é aceita).
