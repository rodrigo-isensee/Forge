---
tipo: revisao-seguranca
contrato: 1
pedido: conf-tabela-rotulo
branch: melhoria/conf-tabela-rotulo
commit: 0adabf58936dde660aaabe9a23cf554784594ec1
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-17
---
# Review de segurança: conf-tabela-rotulo

Escopo: `git diff 0095d299b9b9383ecf9eba336e83c764f707ae5f...51500c2f60488d9b8729cd58b19a0afb9f474f28`, 3 arquivos (+6 / -2): `agents/conferente.md`, `tests/config.json`, `changelog.d/conf-tabela-rotulo.md`. Revisão estática, sem ferramenta externa; a suíte não foi rodada por este papel.

## Gatilhos
`R-SEGURANCA`: o diff toca `tests/config.json` (invariantes), controle do Forge.

## Resumo
**Aprovado.** Nenhum invariante saiu, a Catraca não foi tocada e o rótulo continua exigido sempre que ela o pede. Um achado informativo, nenhum bloqueante.

- **Invariantes:** o diff de `tests/config.json` só acrescenta (+2, 0 remoções): `tests/config.json:111` e `:112`, em `agents/conferente.md`. Nenhum item existente foi removido nem alterado; a frase antiga da tabela não era protegida por item algum, então não havia o que trocar. Os campos `dono`, `custo_permitido` e `excecoes` não mudaram.
- **Rótulo × Catraca:** a Catraca (`tests/catraca.py`, intocada) decide por conta própria e falha fechada sem o rótulo do dono aplicado depois do último push (`tests/catraca.py:388`, `:416-433`). A tabela do conferente (`agents/conferente.md:93`) passou a deferir a ela: o conferente só pede o rótulo quando o check `catraca` do head está em `fail` por falta dele. Como o check `catraca` é o que bloqueia o merge, nenhum merge que ela barraria passa: se ela pede o rótulo, o check fica `fail` e o conferente reprova; se não pede, o rótulo é desnecessário. O conferente não substitui a Catraca, só reflete o resultado dela.
- **Execução mais recente:** `agents/conferente.md:93` aceita a substituição de um `fail` só por `pass` mais nova do mesmo check no mesmo head. Uma `pass` de outro head ou de outro check não entra, pela redação ("do mesmo check no mesmo head"), e `pending` continua reprovando. `agents/conferente.md:94` herda a regra por remissão para o PR `homolog` → `main`, a qual segue com aprovação só do dono.

## Achados
1. **Informativo, `agents/conferente.md:93`:** a regra é prosa e depende de o conferente ler a saída de `gh pr checks <b>` pela execução mais recente e pelo head certo; a saída não traz o head, então a conferência do "mesmo head" exige olhar também o head do PR. Caminho de ataque: nenhum realista, pois o controle efetivo é o check `catraca` exigido na proteção de branch, e o conferente é checagem de processo, não barreira. Sugestão (opcional, fora deste pedido): citar `gh pr view <b> --json headRefOid` no comando para fixar o head. Dono: `tech-lead`.

## Revalidação após a volta curta
Revalidação após a volta curta (b2e4250, B-1 do QA): `git diff b8634fb..b2e4250` toca só `agents/conferente.md:93` (+1 / -1); `tests/config.json` e `changelog.d/` sem mudança. A volta só acrescentou à coluna de comando da linha `merge-integracao` leituras `gh pr view <b> --json statusCheckRollup,headRefOid` e `gh run view <id> --json headSha,conclusion`, ambas já cobertas por `gh pr view` e `gh run view` (com `--json`) em "Comandos permitidos" (`agents/conferente.md:23`): a lista não ganhou comando, é só leitura e sem custo. A regra do rótulo ficou igual (só quando o check `catraca` do head está em `fail` por falta dele; execução mais recente de cada check, mesmo head). O achado 1 (informativo) foi atendido: o head agora entra na conferência. Observação informativa do conferente: no `gh` local 2.4.0 o campo `headRefOid` é recusado; o efeito é fail-safe (a linha vira `não verificável`, nunca aprovação indevida) e `gh run view --json headSha` serve de alternativa; sem ação de segurança. Parecer mantido: aprovado.

Revalidação após a segunda volta curta (0adabf5, B-2 do review): `git diff 7d4aad6..0adabf5` toca só `agents/conferente.md`, linhas 70 e 93 (+2 / -2); `tests/config.json` e `changelog.d/` sem mudança. A volta trocou `headRefOid`, recusado pelo gh 2.4.0, por leituras `gh pr view <b> --json statusCheckRollup`, `gh pr view <n> --json commits --jq '.commits[-1].oid'` e `gh run view <id> --json headSha,conclusion`, todas dentro de `gh pr view` e `gh run view` (com `--json`) em "Comandos permitidos" (`agents/conferente.md:23`): a lista não ganhou comando, é só leitura e sem custo. A regra do rótulo ficou igual (só quando o check `catraca` do head está em `fail` por falta dele; execução mais recente, mesmo head). Parecer mantido: aprovado.

## Lacunas
Nenhuma ferramenta usada; sem varredura de segredo, pois o diff não contém valores sensíveis.

## Riscos aceitos
Nenhum.
