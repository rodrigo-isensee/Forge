---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-achados-fora-dominio
commit: e31a7ba4e881798f49b0f145b9140bc1b294f29d
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047 (E2.254, item E2.252, achados recorrentes fora do domínio)

Parecer completo (não havia parecer anterior nesta branch), sobre o head e31a7ba4, base 98a191f7. Instância que não fez a entrega.

## Escopo lido
- Diff: `bin/forge-check` (6+/4-), `tests/test_parecer_conteudo.py` (49+/1-), spec `tests/mutantes/v047-achados-fora-dominio.json` e fragmento `changelog.d/`. Código e teste: 60 linhas, dentro da orientação M14.
- Pedido E2.252: `docs/engineering/achados-recorrentes.md` como anexo do portão, fora do domínio e aceito depois da entrega conferida. A entrega cria `ANEXOS_DO_PORTAO` (caminho exato, sem prefixo de pasta: `livre()` só trata como pasta a entrada com `/` final) e o soma às listas livres da conferência do head, do `pr` e do `parecer delta`. Faz o que o item pede, sem mais.
- O Forge não tem `docs/engineering/praticas.md`; o review segue o checklist da skill `engineering-practices` e `docs/engineering/achados-recorrentes.md` (PA-7).

## Verificação
- `python3 -m unittest tests.test_parecer_conteudo` no clone: 20 testes, OK (35 s).
- `bin/forge-mutante --processos 1 tests/mutantes/v047-achados-fora-dominio.json`: AF-M1 (forge-check:1488), AF-M2 (:1779), AF-M3 (:3143) morreram.
- `bin/forge-mutante --cobertura --base 98a191f7`: só `bin/forge-check:3143`, coberta por AF-M3. Três guardas mudadas, um mutante por linha; `ACHADOS_RECORRENTES = ANEXOS_DO_PORTAO[0]` não é guarda.
- Ramo de falha com teste de comportamento: o arquivo vizinho (`docs/engineering/praticas.md`) continua vencendo nos três pontos (`test_outro_arquivo_...`, `test_parecer_no_mesmo_commit_de_outro_arquivo_vence`, fim de `test_parecer_delta_nao_le_os_achados`). Isso também prova que a isenção é por nome exato, não pela pasta `docs/engineering/`.
- Subprocesso com `ambiente_limpo()` e `python -I` (AR-4, AR-5). Spec bate com a fonte (AR-12). Demais AR não alcançam o diff.
- Suíte inteira: fica para o CI do PR (não rerrodada aqui).
- Commit único, Conventional Commits em português, mensagem clara.

## Achados
- A1 (recomendado) bin/forge-check:2286 · so_de_parecer (AQ-5, sha_a_revisar) e cmd_delta (:2996) e :791 seguem só com LIVRES: commit de parecer junto do anexo não é 'só de parecer' e o `delta --parecer` ainda lista o anexo, ao contrário do `parecer delta`. Avaliar estender ANEXOS_DO_PORTAO a esses pontos em item próprio.

## Sondas

## Parecer
Aprovado. O anexo do portão deixa de vencer parecer e entrega conferida no `pr` e no `parecer delta`, por nome exato, com os três mutantes mortos e o ramo de falha testado. A1 é visto na leitura (não reproduzido) e fica fora do escopo do E2.252: não bloqueia.
