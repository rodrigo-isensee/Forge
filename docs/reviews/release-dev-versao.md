---
tipo: review
contrato: 1
pedido: release-dev-versao
branch: melhoria/release-dev-versao
commit: c3b7be0e97b98da13a35b3dddfa660fb3b0a979a
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-23
---
# Review: release-dev-versao (rodada 2, revalidação da volta 1)

## Achados
- A4 (recomendado) bin/forge-changelog:113 · A gravação textual ainda troca o primeiro "version" do texto, não o de topo: sonda `{"deps": {"version": "9.9.9"}, "version": "0.1.0"}` deu rc=0, gravou 0.2.0 no aninhado, deixou o de topo em 0.1.0 e apagou o fragmento. A volta validou só na leitura (`ler_manifestos`), sem a conferência pós-troca sugerida na rodada 1. Não bloqueia: os dois manifestos reais têm o "version" de topo na linha 3, antes de qualquer objeto aninhado, e o `test_versao_igual_a_do_forge` pega a divergência no pre-push. Sugestão para um cartão: em `gravar_versao`, conferir `json.loads(novo_texto)["version"] == versao` antes de gravar (ou mover a conferência para `ler_manifestos`, calculando o texto novo lá) e um teste do caso aninhado.

## Parecer
**Aprovado.** Os dois bloqueantes da rodada 1 estão resolvidos.

- A1 (manifesto inválido): `ler_manifestos` carrega cada manifesto existente com `json.loads` e sai com `sys.exit` nomeando o arquivo; roda na linha 137, antes de qualquer escrita no CHANGELOG.md, nos manifestos ou nos fragmentos. Resolvido.
- A2 (sem "version" de topo): recusa quando o JSON não é objeto ou `version` de topo não é string, também antes de qualquer escrita. Sonda com `{"name":"x"}` na raiz: rc=1, mensagem `.claude-plugin/plugin.json: sem a chave 'version' de topo.`, CHANGELOG.md intacto e `changelog.d/x.md` presente. Resolvido.
- A3 (CRLF): fora do escopo por decisão técnica registrada no pedido; não reaberto.
- A4: ficou só na leitura (acima), recomendado.
- Extra da volta (R1 a R3 da segurança): recusa de link simbólico e de caminho que resolve fora da raiz; o parecer de segurança cobre o mérito, aqui só a legibilidade e os testes, que estão corretos.

Testes novos provam cada caso: `test_manifesto_que_nao_e_json_falha_sem_gravar_nada` (A1), `test_manifesto_sem_version_de_topo_falha_sem_gravar_nada` (A2, inclusive com "version" só aninhado), `test_manifesto_link_simbolico_e_recusado_sem_gravar_nada` e `test_manifesto_que_resolve_fora_da_raiz_e_recusado_sem_gravar_nada`. O auxiliar `_nada_gravado` afirma rc != 0, o nome do arquivo no stderr, CHANGELOG.md e manifesto da raiz intactos e o fragmento presente; os dois de link conferem ainda que o alvo não mudou. Os quatro falham contra o `bin/forge-changelog` de `f50b9d4` (vermelho real) e passam no head.

Commits limpos: `b9a8208` teste vermelho, `c3b7be0` correção, Conventional Commits em português. `R-NEUTRO` e `R-CUSTO` sem impacto (só biblioteca padrão).

## Revalidação (volta por delta)
- `forge-check delta --parecer docs/reviews/release-dev-versao.md`: intervalo `4805d77..c3b7be0`; delta lido: `bin/forge-changelog` linhas 12, 88-92, 95, 97-98, 100-114, 137, 144 e `tests/test_changelog.py` linhas 138-180.
- Já lido na rodada 1 (não reaberto): o resto de `bin/forge-changelog` (gravação nos dois manifestos, sem criar o `dev/`), o fragmento `changelog.d/release-dev-versao.md` e os testes anteriores de `tests/test_changelog.py`.

## Evidência
- `python3 -m unittest tests.test_changelog`: `Ran 35 tests ... OK (skipped=1)`; `tests.test_forge -k test_versao_igual_a_do_forge`: `Ran 1 test ... OK`.
- Vermelho: com o `bin/forge-changelog` de `f50b9d4` numa cópia em `$TMPDIR/tech-lead-reldevversao2/`, `FAILED (failures=4, skipped=1)`, os quatro testes novos.
- Sondas em `$TMPDIR/tech-lead-reldevversao2/` (HOME próprio, repositório descartável): sem "version" de topo rc=1 e nada gravado; "version" aninhado antes do de topo rc=0 e troca do aninhado (A4).
- Ferramentas (shellcheck, validação do plugin, suíte completa): ficam com o pre-push do autor (suíte 1796 OK no histórico do pedido), não refeitas aqui.
