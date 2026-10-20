---
tipo: review
contrato: 1
pedido: suite-concorrente
branch: melhoria/suite-concorrente
commit: aed7b97a61e2e0449cec5741175fba9d44164631
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-20
---
# Review: trava da suíte no pre-push (SUITE-CONCORRENTE, E1.2)

Escopo: `50997b7..aed7b97`, 4 arquivos (`.githooks/pre-push`, `docs/hooks.md`, `tests/test_pre_push_trava.py`, `changelog.d/suite-concorrente.md`). Revisor diferente do autor (outra instância, D-ETAPAS-INST). A segurança do hook é do `security-engineer` (E1.3, `docs/security/`), aqui só citada.

## Conferência do escopo
- **E1 (trava que espera):** `flock` em `forge-suite-<uid>.lock` na primeira pasta gravável entre `XDG_RUNTIME_DIR`, `TMPDIR` e `/tmp`, fora do repositório. Pega a trava depois das checagens de ref (envio barrado não espera a vez). Sem a vez, imprime uma linha e espera até `FORGE_TRAVA_ESPERA` (padrão 1200 s); estourado, sai 1 com a mensagem "a vez não chegou em N s; a suíte não rodou" e aponta o `--status`. Limite não inteiro é recusado. Nenhum teste é pulado: a linha `python3 -m unittest discover -s tests -q` e o `|| { ...; exit 1; }` estão iguais à base, então o código de saída segue o mesmo da develop (0 verde, 1 falha).
- **E2 (`--status`):** documentado em `docs/hooks.md` (seção nova do hook git `pre-push`), com o significado da saída (0 = há suíte, 1 = não há) e a troca do `pgrep`. Cita `R-TETO` pelo ID, sem copiar o texto da regra; o `AntiDuplicacao` passa na suíte do autor (958 OK).
- **E3 (testes):** os 7 testes de `tests/test_pre_push_trava.py` rodam o `.githooks/pre-push` de verdade (`subprocess`, repositório descartável com suíte mínima, trava em `XDG_RUNTIME_DIR` temporário, então não disputam a trava da suíte que os roda). Cobrem: código preservado (verde 0, falha 1 com a mensagem), espera da segunda execução, `--status` antes, durante e depois, trava órfã (processo dono morto com SIGKILL, arquivo fica e não bloqueia), limite estourado (não roda a suíte), limite inválido e trava que é link simbólico. Sem `skip`. Rodei aqui: `python3 -m unittest tests.test_pre_push_trava -v` · `Ran 7 tests in 3.072s` · `OK`. O vermelho com o hook da develop (6 de 7) fica com o QA (E1.4).
- Fragmento `changelog.d/suite-concorrente.md` presente; `CHANGELOG.md` intocado.
- Invariantes: `tests/config.json` fora do diff; nenhum trecho protegido saiu.
- `R-NEUTRO`, `R-CUSTO`: só `bash`, `flock` (util-linux) e Python padrão; nada de projeto, nada pago, nenhuma regra afrouxada.
- Regras de ferramenta: shellcheck não está instalado nesta máquina (`shellcheck: command not found`); fica para a bateria do CI no PR, que o roda.

## Limite entre sandbox e terminal: caminho fixo?
Não. Medido nesta sessão (sandbox): `XDG_RUNTIME_DIR=/run/user/1000/` não é gravável, `TMPDIR=/tmp/claude-1000` é, e `/tmp` é somente leitura (`touch: cannot touch '/tmp/forge-teste-2': Read-only file system`). Um caminho fixo `/tmp/forge-suite-<uid>.lock` quebraria o hook dentro do sandbox, justo onde rodam os agentes em paralelo que motivaram o pedido. A ordem atual põe todos os agentes sob sandbox na mesma trava (`/tmp/claude-1000`, comum às sessões do mesmo usuário) e o terminal em `/run/user/<uid>`; o caso que fica de fora (um push do terminal junto com um de agente) é raro e está documentado como limite. Se um dia valer cobrir, o caminho é uma variável de pasta da trava (ex.: `FORGE_TRAVA_DIR`) que os dois lados apontem para o mesmo lugar, não um caminho fixo.

## Achados

## Detalhe dos achados
Recomendações, nenhuma bloqueia:
- R1 (recomendado) `.githooks/pre-push:72` · o descritor 9 da trava é herdado pela suíte e pelos filhos dela; um processo de fundo esquecido por algum teste seguraria a trava depois do fim do hook (o `subprocess` do Python fecha os descritores por padrão, um `&` de shell não). Sugestão: `python3 -m unittest ... 9>&-`; a trava continua com o processo do hook.
- R2 (recomendado) `docs/hooks.md:105` · "o código de saída é o da suíte" diz mais que o código: o hook devolve 1 em qualquer falha (como antes). Sugestão: "o código de saída é o de antes (0 verde, 1 falha)".
- R3 (recomendado) `.githooks/pre-push:26` · o `--status` pega a trava por um instante com `flock -n`; um pre-push que chegue nesse instante imprime "esperando a vez" e espera milissegundos. Inofensivo; só registro.
- Para o `security-engineer` (E1.3), sem refazer aqui: a checagem de link (`-L`) vem antes do `exec 9>>` e do `printf >`, que seguem link (janela entre checagem e uso), e no recuo para `/tmp` a pasta é compartilhada com outros usuários (arquivo pré-criado por outro usuário pode barrar ou segurar a trava). Nas duas pastas usadas na prática (`/run/user/<uid>` e `/tmp/claude-<uid>`, 0700) isso não se alcança.
