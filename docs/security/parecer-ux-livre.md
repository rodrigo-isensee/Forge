---
tipo: revisao-seguranca
contrato: 1
pedido: versao-033
branch: melhoria/parecer-ux-livre
commit: a061a495677e611fe38ee127d6b53fb225c02e11
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-04
---
# Review de segurança: versao-033, L05 (E9 PARECER-UX-LIVRE)

Diff revisado: `dc615c25a89cf801dbff0356ff3e07cf491e4567...a061a495677e611fe38ee127d6b53fb225c02e11` (um commit, três arquivos: `bin/forge-check`, `tests/test_forge.py`, `changelog.d/parecer-ux-livre.md`). Conferido contra a seção E9 do modelo `docs/security/ameacas/versao-033.md`; o C-4 foi cortado para o L08 (DECISÃO TÉCNICA de 2026-11-04 08:53) e não é cobrado aqui.

## Gatilhos
`R-SEGURANCA`: controle do Forge (`bin/forge-check`, validade dos pareceres contra o head) e afrouxamento (a isenção ganha uma pasta). O rótulo `afrouxa-regra` é do dono (E1.8).

## Achados
- A1 (recomendado) tests/test_forge.py:4916 · o teste do merge da develop também traz src/y.txt e passa com o mutante sem "docs/ux/" em LIVRES (a regra de merge da base já o cobre); não prova o efeito da entrada nova nesse caminho.

## Detalhe dos achados
**Conferência por controle e mudança proibida (E9):**
- **C-1 cumprido.** `bin/forge-check:141` ganha só `"docs/ux/"`, com barra, no fim da tupla; as seis entradas anteriores ficam iguais e na mesma ordem. A `livre()` (`bin/forge-check:404`) não mudou (prefixo só para entrada com `/`). O teste `tests/test_forge.py:4884` confere a tupla inteira por igualdade, que é exatamente `("docs/reviews/", "docs/qa/", "docs/devops/", "docs/security/", "KANBAN.md", "docs/kanban/", "docs/ux/")`; uma forma mais larga (`docs/`, `docs/ux` sem barra) quebra a igualdade.
- **C-2 cumprido.** Quem usa `LIVRES` segue o mesmo: a `commit_vale` (`bin/forge-check:459`, padrão, e `:759`, com o fragmento do changelog) e o `delta` (`:1327`). O diff não toca `gatilhos`, `arquivos_da_entrega`, as linhas `escopo:` do `entrega` nem `PASTA_E_REGRA`; nenhum deles lê `LIVRES` (grep na worktree), então `docs/ux/` continua visível ao conferente.
- **C-3 cumprido**, com a ressalva do A1. Os cinco casos estão em `tests/test_forge.py:4887` a `:4919`. Mutante local (cópia em `$TMPDIR`, `docs/ux/` retirado de `LIVRES`): falham o C-1, o commit só em `docs/ux/` e o renome; os nomes parecidos e o byte em `bin/` seguem recusando, como devem; o do merge passa (A1).
- **T-1 não ocorre**: nenhuma outra entrada, nem glob, nem caixa ignorada (`docs/UX/a.md` invalida, `:4892`).
- **T-2 não ocorre**: `LIVRES` não passou a ser lida por `entrega`, `gatilhos` nem `PASTA_E_REGRA`.
- **T-3 não ocorre**: a branch tem um só commit, só do E9; nada do E2 nem do E3.

**A1.** Evidência `tests/test_forge.py:4915-4919`. Caminho de ataque: nenhum direto; uma regressão que tirasse `docs/ux/` de `LIVRES` só no caminho do merge não seria pega por este teste (os outros a pegam no caminho simples). Severidade: informativa. Correção mínima: o `develop_anda` do teste trazer só `docs/ux/b.md` e um commit da branch, depois do merge, só em `docs/ux/`, ou registrar que o caso é coberto pela regra do merge da base. Esforço P. Dono: `forge:tech-lead`.

**Contexto do risco aceito pela decisão (Q12 = A):** `docs/ux/` é lido como instrução por papéis (`agents/qa-engineer.md:12`, critérios de aceite; `agents/ux-designer.md:12`; `stacks/node-react/agents/react-frontend.md:12`). Um commit ali depois dos pareceres não os invalida e, somado ao gate do CI que já pula a bateria para essa pasta (ver `docs/security/release-0.32.0.md`, A1), entra sem revisão nova. É a consequência que o dono aceitou; o aviso no papel de quem revalida é o C-4, no L08. No Forge, nada executa arquivo de `docs/ux/` (pasta vazia na base, sem referência em `bin/`, `hooks/` nem `.githooks/`).

## Riscos aceitos e ferramentas
Sem risco aceito novo neste parecer; a isenção é a decisão Q12 = A do dono. Ferramentas: leitura do diff, `grep`, `python3 -m unittest tests.test_forge.PareceresComDocsUx` (6 testes, OK) e um mutante manual. `gitleaks`, `semgrep`, `actionlint`, `zizmor` e `osv-scanner` não estão no PATH (lacuna; o diff não traz dependência, workflow nem segredo).
