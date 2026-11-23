---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-relato-desenho
commit: 0f881803bdce6d28d18e56da00747adf5ca719d0
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 (E131.3, desenho do RELATO-DOS-AGENTES, PR #815)

Diff `0e59c446..0f881803`: `docs/propostas/relato-dos-agentes-desenho.md` (65 linhas, novo) e `changelog.d/v0480-relato-desenho.md`. Item só de texto, sem código nem teste tocado; sem suíte local (o CI do PR a roda).

## Achados
- A1 (recomendado) docs/propostas/relato-dos-agentes-desenho.md:22 · a regra 3, aplicada como escrita, leva skills/fluxo-do-pedido/SKILL.md a 5261 caracteres contra o teto 5224 de tests/fixtures/metricas-texto.json (teto que só desce); a F1 deve prever mover ou encurtar, não subir o teto
- A2 (recomendado) docs/propostas/relato-dos-agentes-desenho.md:37 · ler_respostas_do_jarvis (forge_transcricao.py:305-327) devolve só o texto final de cada turno, sem hora nem a mensagem que abriu o turno; sem_dono e rajadas pedem um leitor novo, não reaproveitamento
- A3 (recomendado) docs/propostas/relato-dos-agentes-desenho.md:46 · a meta "falas sem_dono por hora ativa ≤ 4" não sai dos campos listados (respostas, sem_dono, rajadas, taxa): falta o campo de horas ativas ou a definição de hora ativa na F2
- A4 (recomendado) docs/propostas/relato-dos-agentes-desenho.md:48 · a suposição sobre `<task-notification>` já tem forma lida no repositório (hooks/agentes.py:399, bin/forge-check:6601); citar essas linhas no lugar de deixá-la a confirmar

## Parecer
**Aprovado.** O desenho responde ao pedido (`docs/pedidos/relato-dos-agentes.md`, escopo e etapas) e às quatro perguntas do brief.

- **Provas do que está em vigor:** conferidas linha a linha na base 0e59c446 e todas batem: `agents/jarvis.md:14,15,16,17,23`; `skills/falar-com-o-dono/SKILL.md:10,18`; `toda-mensagem.md:9-11`; `skills/fluxo-do-pedido/SKILL.md:8,12,31`; `tests/config.json:234-236` e `:895-897`; `hooks/meta.py:40` e `:344-351`; `docs/arquitetura/visao-de-foco.md:167`; `docs/economia-de-tokens.md:12`; `bin/forge-check:7253` e `:9562`; `bin/forge_transcricao.py:305,345,369-371`; `v047.md:1312` e `decisoes-estudos.md:108`. A proposta de origem de fato não existe (`ls` falha).
- **As três faltas são reais:** nenhuma linha escreve o formato nem a ordem do resumo (decisão no topo só existe no pedido de decisões, `falar-com-o-dono/SKILL.md:18`); `fluxo-do-pedido/SKILL.md:12` ainda manda contar "ao fim de cada etapa"; `grep mensagens.jsonl bin/` dá 0 ocorrências, e `transcricao decisoes` mede forma, não volume.
- **Corte F2, F1, F3:** cada fatia tem oráculo medível (fixture de 3 sessões e saída `chave=número`; suíte verde, invariantes 234-238 intactos e `grep` das duas linhas; linha "depois" ou cartão com número). A ordem F2 antes da F1 para gravar o "antes" está certa, e F1 e F2 não dividem arquivo. A1 a A3 são ajustes de precisão que a própria fatia pega no seu oráculo (A1 deixa a suíte vermelha na F1; A2 e A3 aparecem ao escrever a F2), por isso não bloqueiam (`R-REVIEW`); entram como cartão para o desenho ou para o brief da fatia.
- **Nada afrouxa:** nenhuma linha de `docs/regras/` nem de `tests/config.json` sai; a F1 só acrescenta invariante. A regra 2 cabe na folga do `jarvis.md` (simulação: 7768 contra o teto 7795). Traz critério de reversão (linha 47) e "Por que o existente não basta" com evidência (linha 59), como pede `R-DECISAO`. A F2 passa pelo `security-engineer` (linha 58), coerente com `R-SEGURANCA`.
- **Commits:** dois commits claros, em Conventional Commits; o fragmento de changelog segue o padrão.

Medição de A1 (simulação, sem escrita): `tests/test_metricas_texto.medir` no texto com a regra 3 aplicada dá `caracteres=5261`; no texto atual, 5183; teto 5224.
