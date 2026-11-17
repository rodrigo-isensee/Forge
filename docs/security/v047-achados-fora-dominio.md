---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-achados-fora-dominio
commit: e31a7ba4e881798f49b0f145b9140bc1b294f29d
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: v047 (E2.252, achados recorrentes fora do domínio dos pareceres)

Etapa E2.255. Diff revisado: `98a191f7..e31a7ba4` (bin/forge-check, tests/test_parecer_conteudo.py, tests/mutantes/v047-achados-fora-dominio.json, changelog.d/v047-achados-fora-dominio.md).

## Gatilhos
Controle do Forge (`R-SEGURANCA`): muda a lista de caminhos que não vencem parecer (`LIVRES`) no `pr`, na conferência do head e no `parecer delta`, isto é, o que pode entrar depois de um parecer sem nova revisão.

## Achados
- A1 (recomendado) bin/forge-check:187 · o anexo livre só tem o formato das linhas AR- avisado (stderr), não barrado; prosa fora das linhas AR- passa depois do parecer sem revisão e é lida pelo autor via ## Ler; exigir no forge-check docs o formato do arquivo inteiro

## Sondas

## Detalhe dos achados
Verificado sem achado:
- Correspondência exata: `livre()` (bin/forge-check:556) trata a entrada sem `/` final como caminho exato. Sonda local: `docs/engineering/achados-recorrentes.md` livre; `.../achados-recorrentes.mdx`, `.../achados-recorrentes.md/x`, `./docs/...`, `DOCS/...` e `docs/engineering/praticas.md` continuam vencendo o parecer (`desatualiza` = True).
- O aceite do usuário não é afetado: `desatualiza()` (bin/forge-check:564) continua tratando `docs/security/aceites/` à parte; o anexo não tem esse prefixo.
- As três chamadas (conferência do head, `pr`, `parecer delta`) usam a mesma tupla `ANEXOS_DO_PORTAO`, sem divergência entre caminhos; `ACHADOS_RECORRENTES` passa a derivar dela (fonte única).
- Leitura do arquivo segue sem seguir link simbólico e com teto de bytes (bin/forge-check:5035), inalterada.
- Testes do item usam `-I` e ambiente limpo (PA-7: AR-4, AR-5 conferidos); sem segredo no diff.

A1 (baixa; esforço P; dono `tech-lead`/autor do `forge-check`): evidência bin/forge-check:187 com bin/forge-check:5021-5051. Caminho: um agente (ou conteúdo injetado num agente) acrescenta, depois dos pareceres, prosa imperativa fora das linhas `- AR-` em `docs/engineering/achados-recorrentes.md`; com a mudança, o parecer continua válido e o merge segue sem que revisor algum leia o acréscimo, e o texto chega ao `## Ler` de todo brief de código. A mesma classe já existe em `docs/reviews/` e `docs/security/` (livres e lidos por agentes), e o PR mostra o diff a quem mescla; por isso é recomendação. Correção mínima: no `forge-check docs` (e no pre-push), reprovar o arquivo quando `problemas_dos_achados` acusar algo, e restringir a seção `## Achados` a linhas `- AR-`; alternativa: só tratar o anexo como livre quando o delta depois do parecer tocar apenas linhas `- AR-` no formato.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do diff e sondas locais na função `livre`/`desatualiza`; testes do item rodados no clone: `python3 -m unittest tests.test_parecer_conteudo` (20 OK) e `tests.test_erros_no_brief` (49 OK). Suíte inteira: só no CI, que ainda não rodou para esta branch (sem PR); o portão de merge a exige. Faltaram no ambiente: gitleaks, zizmor, actionlint, Semgrep (nenhum workflow mudou).
