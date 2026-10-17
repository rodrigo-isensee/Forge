---
tipo: review
contrato: 1
pedido: conf-tabela-rotulo
branch: melhoria/conf-tabela-rotulo
commit: 0adabf58936dde660aaabe9a23cf554784594ec1
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-17
---
# Review: CONF-TABELA-ROTULO, tabela do conferente alinhada à Catraca

Escopo: `0095d29...51500c2` (base 0095d299b9b9383ecf9eba336e83c764f707ae5f), 3 arquivos em 2 commits. O revisor não é o autor. Comparei o diff com o "Entregar" de `conf-tabela-rotulo-tech-lead-1.md` e com a decisão do dono de 2026-10-17 ("A").

Veredito sobre `51500c2`: **APROVADO**, sem achados que bloqueiem.

## Ferramentas (citadas, não refeitas)
- `python3 -m unittest tests.test_forge -q`: `Ran 238 tests in 24.926s` / `OK` (o sandbox negou uma saída de rede para `api.anthropic.com`, sem efeito no resultado). Suíte completa e `scripts/validar-plugin.sh` ficam com o QA e o CI.
- Segurança (`R-SEGURANCA`; o diff toca `tests/config.json`) tem parecer próprio do `security-engineer`, em paralelo; não o refiz.

## Conferência do diff
1. `agents/conferente.md:93` (`merge-integracao`): o rótulo `afrouxa-regra` só é exigido quando o check `catraca` do head pede (`fail` por falta de rótulo); os checks são conferidos pela execução mais recente de cada um, e a linha `fail` antiga substituída por `pass` mais nova do mesmo check no mesmo head não reprova. Comando coerente (`gh pr checks`, `gh pr view --json labels`). Confere com a decisão do dono.
2. `agents/conferente.md:94` (`pedido-de-merge-ao-dono`): segue por remissão a `merge-integracao`, com o lembrete do rótulo só quando a `catraca` pede; comando "idem" preservado.
3. Nada mais de `agents/conferente.md` mudou (2 linhas trocadas, nenhuma outra seção). `tests/catraca.py`, `.github/`, `hooks/`, `docs/regras/` intocados.
4. `tests/config.json:111-112`: invariantes só por acréscimo (nenhuma linha removida); as duas frases novas existem no texto do agente. A frase antiga não era protegida, então não havia o que trocar.
5. `changelog.d/conf-tabela-rotulo.md`: fragmento com o nome da branch, tipo `Alterado`, texto neutro (`R-NEUTRO`), sem nome de projeto. Sem custo (`R-CUSTO`).

## Achados
Nenhum que bloqueie.
- `agents/conferente.md:93` · linha longa na tabela, difícil de ler · sem ação necessária (padrão das linhas vizinhas) · severidade: recomendado, não exige mudança.

## Revalidação após a volta curta
Escopo: `b8634fb..b2e4250`, 1 arquivo, 1 linha trocada. O B-1 do QA foi corrigido só na coluna de comando de `merge-integracao` (`agents/conferente.md:93`): a regra, as outras linhas e `tests/config.json` (nenhuma linha removida nos invariantes) não mudaram. Mas o comando novo não funciona no `gh` local, e o parecer passa a **REPROVADO** (ajustes necessários).

- B-2 · `agents/conferente.md:93` · severidade: bloqueia · `gh pr view <b> --json statusCheckRollup,headRefOid` é recusado no `gh` 2.4.0 (`Unknown JSON field: "headRefOid"`; executado contra o PR 189). Como a chamada inteira falha, o conferente não obtém nem `statusCheckRollup`, que sozinho funciona (traz `name`, `status`, `conclusion`, `startedAt`, `completedAt`, `detailsUrl`). O comando prometido para provar "execução mais recente" e "mesmo head" fica inexecutável para quem o usa. Sugestão: trocar `headRefOid` por `commits` com `--jq '.commits[-1].oid'` (funciona no 2.4.0 e dá o head) e manter `gh run view <id> --json headSha,conclusion` para ligar cada execução ao head; confirmar `gh run view --json headSha` no 2.4.0 antes de citá-lo, pois não foi testado aqui. O `statusCheckRollup` não traz o sha do head, então o par com `commits` é necessário.

## Revalidação após a segunda volta curta
Escopo: `7d4aad6..0adabf5`, 1 arquivo (`agents/conferente.md`), 2 linhas trocadas (70, prova `push`; 93, `merge-integracao`). O B-2 está corrigido: nenhum `headRefOid` resta em `agents/`, `tests/config.json` ou `changelog.d/` (as duas ocorrências em `tests/test_ci_local.py` são fixtures de outra coisa, fora do diff). Os comandos novos rodam no `gh` 2.4.0: `gh pr view 189 --json commits --jq '.commits[-1].oid'` devolveu `e61d0e417b99dd7a5a0397322921b21d5af0ad3a` e `gh run view 39027705842 --json headSha,conclusion` devolveu `{"conclusion":"success","headSha":"3f0702a5..."}`. A troca da linha 70 é a mesma correção (`commits --jq` no lugar de `headRefOid`), sem mudar a regra nem outras linhas. `tests/config.json` não mudou nesta volta, então nenhum invariante mudou. B-2 resolvido; o parecer volta a **APROVADO**, sem achados que bloqueiem. Segurança e QA seguem com pareceres próprios.
