---
tipo: revisao-seguranca
contrato: 1
pedido: impl-d1-agentes-registro
branch: melhoria/impl-d1-agentes-registro
commit: 195e36ca91db52bb6ce9fd25d8e7a603c130537c
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-22
---
# Review de segurança: impl-d1-agentes-registro

Escopo: `git diff c092f1b..195e36c` (F1 AGENTE-REGISTRO-PRESO, C1). Referência: desenho em `docs/propostas/aq/melhorias-f1-f10.md` §1 e modelo de ameaças `docs/security/ameacas/melhorias-f1-f10.md` §2.1 (T1-1 a T1-8) e controles C1-1 a C1-8. O C2 não entrou (spike negativo), então T1-7 e C1-7 não se aplicam.

## Gatilhos
Controle do Forge: o hook `agentes` guarda o `R-TETO` (teto e duplicado). A regra nova de saída do registro ("sessão morta libera") é uma via de esvaziar a contagem; a pergunta do review é se ela só dispara com prova de morte.

## Achados

## Detalhe dos achados
Conferência dos controles do modelo de ameaças, com evidência:

- **C1-1 / T1-1, T1-2 (tipo, faixa, PID enorme).** `hooks/agentes.py:117-118` (`pid_valido`: inteiro, não booleano, `1 <= pid <= pid_max`, com `pid_max` lido do sistema e padrão 4194304 em `hooks/agentes.py:99-114`) e `hooks/agentes.py:121-134` (`sessao_morta`: só `ProcessLookupError` vale `True`; `PermissionError`, `OverflowError` e os demais erros devolvem `False`). Não usa `pid_vivo` cru na decisão de morte. Sondas em cópia própria: `2**63`, `2**31`, `inf`, lista e dicionário devolvem `False`; o PID gigante não derruba o hook (fixture `pid-gigante-nao-derruba-o-hook.json`). Atendido.
- **C1-2 (vigentes não levanta).** `hooks/agentes.py:151-165`: cada registro em `try` próprio; no erro, o registro fica. Assinatura igual (o `bin/forge-check:1438-1458` segue chamando `vigentes(lista, agora, expira_s)`). Atendido.
- **C1-3 / T1-3 (namespace).** `hooks/agentes.py:102-107` grava `os.readlink("/proc/self/ns/pid")`; `hooks/agentes.py:127` exige o namespace gravado igual ao atual, e texto. Consequência conferida: o `forge-check` que conta agentes de dentro do sandbox do Bash vê outro namespace e mantém todos (conta a mais, lado seguro, e não regrava o arquivo). Atendido.
- **C1-4 / T1-5 (intermediário).** `hooks/agentes.py:137-148`: o PID só entra no registro com `session_id`, namespace legível, PID válido, vivo e `comm` fora de `CASCAS`. O `hooks/hooks.json:10-13` chama o hook na forma `command` + `args` (sem casca), então o pai é o próprio Claude Code. Atendido.
- **C1-5 / T1-4 (herança de PID entre sessões).** `hooks/agentes.py:224-239`: com sessão provada, o `SubagentStart` só casa a reserva da mesma `sessao` (ou a antiga, sem `sessao`); sem sessão provada, o registro confirmado perde `pid`, `pidns` e `sessao` e cai no prazo. O registro sem par recebe os dados do próprio evento. Fixtures `inicio-so-casa-reserva-da-mesma-sessao.json`, `inicio-sem-session-id-nao-leva-pid.json` e `inicio-casa-reserva-da-sessao-e-mantem-pid.json`. Atendido; o caso não casado deixa a reserva da outra sessão contando até os 5 min, o que é o lado seguro.
- **C1-6 / T1-8 (escape novo).** Nenhuma variável de ambiente nova; os testes usam PID real (`{pid_vivo}` = o processo de teste, `{pid_morto}` = processo encerrado) e o namespace real (`tests/test_hooks.py:65-70`). Atendido.
- **C1-8 (não muda).** Trava de carga, teto, duplicado, `expiracao_horas` e `RESERVA_S` intocados no diff; `FORGE_CARGA_LIVRE` segue só da carga. Atendido.
- **T1-6 (PID reaproveitado).** Processo vivo com o mesmo número mantém o registro até o prazo. Lado seguro, como o modelo aceita.
- **Falha aberta já existente.** Uma exceção em `da_sessao` dentro do `lancar` (`hooks/agentes.py:217`) cairia no `executar`, que libera; conferi que todas as leituras ali estão protegidas (`OSError`, `ValueError`, que cobre erro de decodificação) e que `pid_vivo` só é chamado depois do `pid_valido`. Não é comportamento novo do F1 (o hook já falha aberto por desenho, `docs/hooks.md`, seção "Estado e expiração").

Recomendações (não bloqueiam; dono: tech-lead, em pedido próprio se o dono do Forge quiser):

- **R1 (baixa). Namespace igual em máquinas diferentes.** O namespace de PID inicial tem o mesmo identificador em hospedeiros distintos. Se duas máquinas usarem a mesma cópia de trabalho por sistema de arquivos de rede, com sessões ao mesmo tempo, a máquina B acharia morta a sessão viva da máquina A e soltaria a vaga dela. Caminho realista só nesse arranjo raro; sem atacante (é falha de contagem, não abuso). Correção mínima: gravar também o `boot_id` do sistema (`/proc/sys/kernel/random/boot_id`) e exigi-lo igual, como o namespace. Esforço P.
- **R2 (informativa). `pid == pid_max` aceito como válido.** `hooks/agentes.py:118` usa `<=`; o sistema nunca dá esse número, então um registro com ele só existe por edição à mão e sai como morto. Sem efeito prático (o arquivo é protegido por caminho); segue o texto do C1-1.

## Riscos aceitos e ferramentas
Nenhum risco aceito novo. T1-6 segue aceito como no modelo de ameaças.
Verificação: leitura do diff, sondas de `sessao_morta`/`vigentes` e o teste `test_registro_de_agente_solta_so_com_prova_de_sessao_morta` numa cópia própria do commit em `$TMPDIR` (verde). Lacunas: `gitleaks`, `semgrep`, `zizmor`, `actionlint`, `osv-scanner` e `trivy` não estão no PATH deste ambiente; o diff não mexe em workflow, dependência nem imagem, e não traz segredo (leitura manual).
