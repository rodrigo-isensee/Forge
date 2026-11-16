---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-catraca-hook-por-script
commit: b32853e6ac2a583a5ec2d0c619befa7b57715ded
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: v047-catraca-hook-por-script

Revalidação por delta `24256248..b32853e6` (volta 7), etapa E2.251 do pedido v047, lida por `forge-check parecer delta` (domínio: `tests/catraca.py`, `tests/test_catraca.py`). O que é da branch no intervalo é só o d896a0c2: um teste (CH-M30) que prova que `NaN`, `Infinity` e `-Infinity` em campo sem tipo (no topo e dentro do hook) acusam pela guarda `parse_constant` de `erros_de_forma` (`tests/catraca.py:378`). Sem mudança de código de controle. O resto do diff em `tests/catraca.py` (`PROMOCOES` com `promocao/X.Y.Z`, `promocao_aceita`, modo `degrau`) chegou da develop pelo merge 3bf73172 (PR #567, com o próprio review e rótulo do dono): não aparece em `git diff origin/develop HEAD` e fica fora deste parecer. A13 segue recomendado e sem mudança (S19 ainda dá OverflowError, falha fechada). Não sobra bloqueante. Parecer aprovado.

Volta 5 e 6 (registro): Revalidação por delta `230dfb01..24256248` (voltas 5 e 6), etapa E2.174 do pedido v047, lida por `forge-check parecer delta` (domínio: `tests/catraca.py`, `tests/test_catraca.py`). O A12 está corrigido: `erros_do_hook` (`tests/catraca.py:366`) exige `timeout` finito e maior que 0, e S17 (0, -1, `1e400`) acusa no corpus. O A6 do review também está corrigido: `EVENTOS_DO_HOOK` (`tests/catraca.py:340`) traz os 31 eventos do enum do binário do Claude Code 2.1.224, sem `PreModelSwitch` nem `PostModelSwitch`, que eu tinha listado por engano na correção do A10. S18 acusa. Conferi tudo contra `claude plugin validate`. Pela régua do dono (bloqueante só regressão ou fuga provada no `hooks.json` real), não sobra bloqueante. Fica um recomendado (A13): um `timeout` inteiro com mais de 308 dígitos derruba a catraca com `OverflowError`. Ela termina com rc 1, então a falha é fechada e não há fuga. Parecer aprovado.

Volta 4 (registro): Revalidação por delta `79899789..230dfb01` (volta 4), etapa E2.167 do pedido v047, lida por `forge-check parecer delta` (domínio: `tests/catraca.py`, `tests/test_catraca.py`). O A10 está corrigido: `erros_de_forma` (`tests/catraca.py:371`) confere o `hooks.json` do head por lista fechada de eventos e de tipos de campo, em falha fechada, e S12 a S16 acusam no corpus (36 sondas, o `hooks.json` real sem erro). Pela régua do dono para esta volta (bloqueante só regressão ou fuga com prova no `hooks.json` real), sobra um bloqueante: um hook **novo** com `timeout` 0, negativo ou infinito passa calado e faz a carga descartar todos os hooks (A12, S17). O conserto é uma linha.

Volta 3 (registro): Revalidação por delta `66a3a9a4..ee91a8f0` (volta 3), etapa E2.147 do pedido v047. A8 e A9 estão corrigidos: S8 a S11 acusam no corpus (`tests/fixtures/catraca-hooks/sondas.json`, 28 sondas), e os legítimos (`forma-shell`, `statusMessage`, `PR565`) passam. Esta volta relê o hook inteiro contra a especificação oficial (documentação dos hooks e o esquema que o Claude Code 2.1.224 aplica ao carregar o `hooks/hooks.json`). Sobra uma dimensão que nenhuma volta modelou: a **validade do arquivo**. A carga do plugin valida o arquivo inteiro de uma vez. Basta uma entrada fora do esquema, em qualquer hook, para nenhum hook do Forge ser registrado. A catraca não acusa nada disso (A10). É o último achado da família: não vi outra dimensão em aberto.

## Gatilhos
`R-SEGURANCA`: código de controle (`tests/catraca.py`, nos PROTEGIDOS) e a regra que guarda `hooks/hooks.json` (`R-CONFORMIDADE`).

## Achados
- A4 (bloqueante) tests/catraca.py:258 · Corrigido em 66a3a9a4; na volta 3 o `b` também saiu da lista inócua (`-bb` faz do aviso exceção), coberto em test_hook_neutralizado_sem_tirar_o_script_barra.
- A5 (bloqueante) tests/catraca.py:259 · Corrigido em 66a3a9a4: `-X` só com `utf8`, `utf8=0` ou `utf8=1`; `-W` volta à linha inteira. S6, S6-junto e S6-W acusam.
- A6 (bloqueante) tests/catraca.py:260 · Corrigido em 66a3a9a4: o interpretador é o 1º termo como escrito, e só um `env` do sistema sai da frente. S7 e S7-ponto acusam.
- A7 (recomendado) tests/catraca.py:307 · Corrigido em 66a3a9a4: `timeout` na chave; A7 (`timeout: 1`) acusa no corpus.
- A8 (bloqueante) tests/catraca.py:287 · Corrigido em ee91a8f0: com `args`, os termos são `[command] + args` sem dividir; sem `args`, fora do ASCII imprimível vira a linha inteira. S8, S9, S10, S10-aspas e S10-vazio acusam; PR565 e forma-shell passam.
- A9 (bloqueante) tests/catraca.py:263 · Corrigido em ee91a8f0: lista fechada de campos inócuos (`statusMessage`, `once`) e o resto na chave em JSON canônico. S11-if, -async, -asyncRewake, -onFailure e -shell acusam.
- A10 (bloqueante) tests/catraca.py:371 · Corrigido em 230dfb01: `erros_de_forma` com lista fechada de eventos e tipos, falha fechada; S12 a S16 acusam no corpus e o hooks.json real passa.
- A11 (recomendado) .github/workflows/ci.yml:521 · `claude plugin validate . --strict` na raiz valida só o marketplace: o esquema do hooks.json e o frontmatter dos agentes ficam sem conferência no CI (agents/devops-engineer.md:3 já falha na validação do plugin).

- A12 (bloqueante) tests/catraca.py:366 · Corrigido em 3f92e62f: `timeout` só número finito e maior que 0; S17-zero, -negativo e -infinito acusam no corpus, e `claude plugin validate` reprova os três.
- A13 (recomendado) tests/catraca.py:366 · `timeout` inteiro com mais de 308 dígitos faz `math.isfinite` lançar OverflowError: a catraca cai com rc 1 (falha fechada, sem fuga), mas sem a mensagem R-CONFORMIDADE. Trate o int fora do float como erro de forma.

## Sondas
- S8 · `command` `python3 -s -E ${CLAUDE_PLUGIN_ROOT}/hooks/conformidade.py\nexit 0`, sem `args`, no hook de conformidade · espera: 1 removido · obtido: 1 removido em ee91a8f0 (corpus S8, review-S1)
- S9 · igual a S8 com U+00A0 no lugar dos espaços · espera: 1 removido · obtido: 1 removido em ee91a8f0 (corpus S9)
- S10 · `command` `python3 -s` com `args`; `'python3'`; a linha inteira com `"args": []` · espera: 1 removido em cada · obtido: 1 removido em cada em ee91a8f0 (corpus S10, S10-aspas, S10-vazio)
- S11 · `if`, `async`, `asyncRewake`, `onFailure` ou `shell` acrescentado ao hook · espera: 1 removido em cada · obtido: 1 removido em cada em ee91a8f0 (corpus S11-*)
- S12 · campo `type` apagado do hook de conformidade · espera: acusa (validação do plugin: `hooks.PreToolUse.2.hooks.0.type: Invalid input`) · obtido: removidos 0
- S13 · `"timeout": "10"` no hook de conformidade · espera: acusa (validação: `expected number, received string`) · obtido: removidos 0
- S14 · `null` (também `1`) acrescentado ao fim de `args` do hook de conformidade · espera: acusa (validação: `args.3: expected string, received null`) · obtido: removidos 0
- S15 · evento novo `"PreToolUsee": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "true"}]}]` · espera: acusa (validação: `hooks.PreToolUsee: Invalid key in record`) · obtido: removidos 0
- S16 · grupo novo no PreToolUse com `"matcher": 1` ou com um hook de `"timeout": "1"` · espera: acusa (validação: `matcher: expected string, received number`) · obtido: removidos 0

- S17 · grupo novo no PreToolUse do hooks.json real com hook `{"type": "command", "command": "true", "timeout": 0}` (e -1, 1e400) · espera: acusa (validação: `timeout: Too small: expected number to be >0`) · obtido: removidos 0, `erros_de_forma` vazio em 230dfb01; acusa em 24256248 (corpus S17-*)
- S18 · evento novo `"PreModelSwitch": [{"hooks": [{"type": "command", "command": "true"}]}]` no hooks.json real · espera: acusa (validação: `hooks.PreModelSwitch: Invalid key in record`) · obtido: acusa em 24256248 (corpus S18)

## Detalhe dos achados
**A4 a A9** · releitura de `tests/catraca.py:257-349` no head. `termos_do_hook` (`:287`) segue a seção "Exec form and shell form" da documentação: com `args`, mesmo vazio, não há shell nem divisão do `command`. Sem `args`, o `split` só vale para ASCII imprimível. `-` e `#` antes do script e `;&|<>` e `$(` depois dele levam à linha inteira. `campos_extras_do_hook` (`:296`) usa lista positiva. `once` fica fora da chave com razão: pela documentação, ele só vale para hooks declarados no frontmatter de skill e é ignorado nos demais lugares. Rodados aqui: `python3 -m unittest tests.test_catraca.Hooks tests.test_catraca.CorpusDasSondasDeHook`, 12 testes, OK.

**A10** · evidência `tests/catraca.py:307` (`str(hk.get("type", "command"))` e `str(hk.get("timeout", "padrão"))`), `:290` (`str(a)` em cada item de `args`) e `:324-331` (`hooks_contados` só compara chaves, sem conferir a forma do arquivo). No binário do Claude Code 2.1.224, a carga do plugin lê `hooks/hooks.json` com `parse` do esquema dentro de um `try`. Um erro gera `hook-load-failed` ("Failed to load hooks for <plugin>"), e o `hooksConfig` do plugin fica vazio: nenhum hook do Forge é registrado. Os hooks bons do mesmo arquivo também se perdem. Fiz a prova estática com `claude plugin validate <cópia sem marketplace.json>`, que aplica o mesmo esquema. Ele reprova S12 a S16, e a catraca dá 0 removidos em todas. Caminho de ataque: o do A8. Um agente barrado pelo hook de conformidade edita `hooks/hooks.json` no PR e apaga um `type`, põe aspas num `timeout` ou acrescenta um hook com um campo errado. A catraca, a única guarda que pede o rótulo do dono, vê só acréscimo ou a mesma chave e fica muda. Depois do merge, a sessão roda sem nenhum hook: conformidade, teto, parecer e vigia. O CI não pega o erro (A11). Não é regressão (a base `cb45a962` também não acusava S12, S13, S15 e S16), mas fecha o objetivo do item pela mesma régua do A9. Severidade média, porque resta o review humano.

Correção mínima, em falha fechada:
- (a) Nada de valor padrão nem de `str()` na chave: `type` e `timeout` entram por `json.dumps` do valor cru (ausente vira `null`). `command` que não é texto ou `args` com item que não é texto fazem `termos_do_hook` devolver `None`.
- (b) A regra confere a forma do `hooks.json` do head e acusa com `R-CONFORMIDADE` "hooks.json fora do esquema: a carga descarta todos os hooks" quando o arquivo traz:
  - evento fora desta lista fechada: `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`, `PermissionDenied`, `Notification`, `UserPromptSubmit`, `UserPromptExpansion`, `SessionStart`, `SessionEnd`, `Stop`, `StopFailure`, `SubagentStart`, `SubagentStop`, `PreCompact`, `PostCompact`, `PermissionRequest`, `Setup`, `TeammateIdle`, `TaskCreated`, `TaskCompleted`, `Elicitation`, `ElicitationResult`, `ConfigChange`, `WorktreeCreate`, `WorktreeRemove`, `InstructionsLoaded`, `CwdChanged`, `FileChanged`, `DirectoryAdded`, `MessageDisplay`, `PreModelSwitch`, `PostModelSwitch`;
  - evento cujo valor não é lista, ou grupo sem `hooks` em lista;
  - `matcher` que não é texto;
  - hook com `type` diferente de `"command"` (o Forge só usa esse tipo; outro tipo pede o rótulo do dono);
  - `command` que não é texto;
  - `args` que não é lista de textos;
  - `timeout` que não é número (booleano não conta);
  - `async`, `asyncRewake` ou `once` que não é booleano;
  - `if` ou `statusMessage` que não é texto;
  - `shell` fora de `bash` e `powershell`;
  - `onFailure` fora de `continue` e `block`.
- (c) No corpus: S12 com `"tira": ["type"]`, S13, S14 (`null` e `1`), S15 e S16. Como legítimo, o `hooks.json` real inalterado (0 removidos e nenhum erro de forma).

Esforço P. Dono: tech-lead.

**A10 (volta 4)** · `regra_hooks` (`tests/catraca.py:399`) roda `erros_de_forma` sobre o `hooks.json` do head antes da contagem e acusa com `R-CONFORMIDADE`; `json.loads` com `parse_constant` recusa `NaN` e `Infinity` literais. Itens (b) e (c) da correção atendidos; o (a) (sem valor padrão na chave) ficou dispensável, porque `type` ausente, `timeout` texto e item não texto em `args` já acusam pela forma. Conferi contra `claude plugin validate` (2.1.224) numa cópia sem `marketplace.json`, além de S12 a S16: `matcher` nulo, `type` `http`, `shell` `Bash` e chave `hooks` duplicada com hook sem `command` acusam nos dois. Campo extra no hook, no grupo ou no topo, grupo de `hooks` vazio, `command` vazio, `timeout` fracionário e matcher com regex inválida passam nos dois (sem fuga). O BOM UTF-8 no início acusa na catraca e passa na carga: é falso positivo, em falha fechada, aceitável. Não é regressão.

**A12** · evidência `tests/catraca.py:363`: a condição só barra o `timeout` que não é número (ou booleano). O esquema da carga exige `timeout` maior que zero e finito, e `json.loads` lê `1e400` como `inf` sem passar pelo `parse_constant`. Para o hook de conformidade existente, trocar o `timeout` muda a chave e já acusa como remoção (A7). A fuga é por um hook **acrescentado** (S17), como em S16. Caminho de ataque: o do A10. Um agente barrado edita o `hooks/hooks.json` no PR e acrescenta um hook com `"timeout": 0`, que alguém também escreveria por engano, achando que é "sem prazo". A catraca fica muda, e depois do merge nenhum hook do Forge é registrado. Severidade média, como o A10 (resta o review humano). É bloqueante pela régua do dono desta volta: é uma fuga provada no `hooks.json` real.

Correção mínima: em `erros_do_hook`, `timeout` válido só se for `int` ou `float`, não booleano, `math.isfinite` e `> 0`. No corpus, entra S17 com `acrescenta` (`timeout` 0, -1 e `1e400`, este no texto, porque `json.dumps` escreve `Infinity`), com `fora_do_esquema: true`. Esforço P. Dono: tech-lead.

**A11** · evidência `.github/workflows/ci.yml:521`. Na raiz, `claude plugin validate . --strict` encontra `.claude-plugin/marketplace.json` e valida só o manifesto do marketplace. A validação do plugin (manifesto, agentes, hooks) só roda numa cópia sem o `marketplace.json`. Nela, o head já falha em `agents/devops-engineer.md:3` (o YAML do frontmatter não lê: `": "` dentro do `description` sem aspas), e na `main` também. A própria mensagem do validador diz que esse agente carrega sem metadados em tempo de execução. Correção: o job valida também o plugin, depois de corrigir o frontmatter. Assim o CI cobre o A10 pela fonte do esquema, como defesa em profundidade, sem substituir a catraca. Severidade baixa para este item. Esforço P. Dono: devops-engineer (o workflow é enviado pelo dono, que tem o escopo `workflow`). Fica fora do escopo deste item, como cartão.

**A12 e A6 (voltas 5 e 6)** · No head `24256248`, testei o `hooks.json` real com um hook acrescentado no PreToolUse, comparando `claude plugin validate` (2.1.224, cópia sem `marketplace.json` e sem `agents/`) com `erros_de_forma`. Os dois concordam em todas as variantes. `timeout` 0, -1, `1e400`, `-1e400`, `1e-400` (vira 0.0) e `-0` acusam nos dois. `0.0001` e `1e308` passam nos dois, então não há falso positivo. O evento `PreModelSwitch` acusa nos dois. O `hooks.json` real passa nos dois. A lista de eventos é igual, como conjunto, ao enum de 31 eventos extraído do binário (`/usr/local/bin/claude`). A cadeia `PreModelSwitch` não aparece no binário. A errata é minha: a lista da correção do A10 (acima) trazia `PreModelSwitch` e `PostModelSwitch`, que não existem. Vale a do código, com 31 eventos. Não é regressão: a mudança só aperta a forma.

**A13** · evidência `tests/catraca.py:366`. `json.loads` lê `1` seguido de 400 zeros como `int`, e `math.isfinite` lança `OverflowError` (S19, sonda local fora do corpus). A exceção não é capturada em `main` (`tests/catraca.py:1815` só pega `ErroDeGit`), então a catraca sai com rc 1 e o CI fica vermelho. A carga também reprova o valor (`expected number, received number`). Não há fuga, mas quem recebe vê um traceback em vez do `R-CONFORMIDADE`. Correção mínima: antes da comparação, tratar como fora do esquema o `int` com `abs` maior que `sys.float_info.max`, ou capturar `OverflowError`. Severidade informativa. Esforço P. Dono: tech-lead.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Volta 7 (head b32853e6): `python3 -m unittest tests.test_catraca.Hooks tests.test_catraca.CorpusDasSondasDeHook`, na raiz do clone, 14 testes, OK (o módulo inteiro passou de 300 s aqui e fica com o CI); sondas locais com `erros_de_forma` (`NaN` no topo e `-Infinity` no hook acusam como JSON ilegível; `timeout` de 400 dígitos ainda lança OverflowError, A13). CI do PR #575 no head b32853e6: só `bateria (pareceres)` vermelha, à espera dos pareceres deste head; `verificações` e `partes` verdes. Volta 6: Rodados aqui no head 24256248: `python3 -m unittest tests.test_catraca.Hooks tests.test_catraca.CorpusDasSondasDeHook`, 14 testes, OK; 8 variantes do `hooks.json` real em `claude plugin validate` (2.1.224) e em `erros_de_forma`; o enum de eventos extraído do binário. A suíte inteira fica com o CI. Volta 4: Rodados aqui na volta 4 (head 230dfb01): `python3 -m unittest tests.test_catraca.Hooks tests.test_catraca.CorpusDasSondasDeHook`, 14 testes, OK; 23 variantes do `hooks.json` real em `claude plugin validate` (2.1.224) e em `erros_de_forma`, e S17 nos dois. Na volta 3:
- os 12 testes de `Hooks` e `CorpusDasSondasDeHook` no head;
- S12 a S16 contra `tests/catraca.py` do head, com `hooks_contados` sobre o `hooks/hooks.json` real;
- `claude plugin validate` (2.1.224) numa cópia limpa sem `marketplace.json`, para cada variante e para o arquivo inalterado.

Fontes: a documentação oficial dos hooks (code.claude.com/docs/en/hooks.md, lida em 2026-11-15) e o esquema e a função de carga no binário instalado. Lacunas:
- a branch não tem PR nem CI (o brief pede sem PR), então a suíte inteira não foi conferida;
- não abri uma sessão do Claude Code com o arquivo inválido: a perda de todos os hooks vem da leitura do código de carga e do validador, não de uma execução.
