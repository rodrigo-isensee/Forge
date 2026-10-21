---
tipo: review
contrato: 1
pedido: conf-so-leitura-fix
branch: melhoria/conf-so-leitura-fix
commit: f3d68cb9933219014b82279d730c2dd525393eed
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-20
---
# Review: conf-so-leitura-fix (conferente só de leitura na sessão do Forge)

Escopo: diff de `0f480c884f8a3f5af1ea8eba861fb937d61f9619` a `f3d68cb`: `hooks/conformidade.json` (+1 linha), 3 fixtures, `tests/test_forge.py` (+2 -1), fragmento em `changelog.d/`. Quem revisa não é o autor. Segurança (E1.3) e QA (E1.4) têm parecer próprio; este não os refaz.

## Achados

## Parecer
Aprovado, sem achados.

- Causa e correção: em `principal` (`hooks/conformidade.py`, ~1654-1670) o papel fora de `escrita_permitida` sai antes de `Guarda.bash` na sessão do Forge. Com `"conferente": ["/dev/null"]`, `com_lista` fica verdadeiro e o hook avalia o papel, aplicando `so_leitura` e a gramática. Mudança de política só em JSON, sem tocar o `.py`, como a proposta de segurança pedia. A lista não vazia atende `escrita_valida`.
- Sondas do hook real (sessão do Forge, `agent_type` conferente): `python3 -V`, `sh`, `bash -c`, `env python3` e `cat x > y` saem com 2; `git log -1`, `git status`, `grep`, `cd <dir> && git diff`, `forge-check delta`, `gh pr view`, `test -f` e `ls | wc -l` saem com 0. Nada que o conferente precisa ler deixou de passar.
- Outros papéis: as mesmas sondas com `forge:dev` e `forge:tech-lead` saem com 0 como antes. `com_lista` só muda para o conferente (a chave é por papel); o `aq` não é tocado. Efeito colateral aceito e coerente: erro interno do hook passa a falhar fechado para o conferente. Ele tem só Read, Grep, Glob e Bash, então a lista de escrita nunca bloqueia uma ferramenta de arquivo que ele use.
- Mutação (cópia de `git archive` do HEAD em `$TMPDIR`, `tests.test_hooks.Hooks.test_fixtures`): com a linha, 1 teste OK; sem a linha, falham exatamente `conferente-sessao-forge-python-bloqueia` e `conferente-sessao-forge-redirecionamento-bloqueia` (a de `git log` segue verde, como guarda contra regressão). As fixtures provam a correção.
- `tests/test_forge.py`: a linha ajustada é a comparação exata de `escrita_permitida`, consequência direta da correção; aperta o teste, não o afrouxa. O mínimo de 460 fixtures em `tests/test_hooks.py` segue folgado (822 arquivos).
- Fragmento `changelog.d/conf-so-leitura-fix.md` presente, tipo Corrigido. Mensagens de commit em Conventional Commits em português. Sem mecanismo novo nem afrouxamento (endurece); critério de reversão trivial: remover a linha.
- Registrado e fora do escopo, como o pedido diz: a frase em `agents/conferente.md` e o R1 do `grep` têm cartão próprio.
- Não rodei a suíte inteira (R-TETO): só `test_fixtures`, em cópia. O comando de pronto completo é do autor (1082 OK, segundo o pedido) e do QA.
