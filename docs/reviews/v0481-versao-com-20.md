---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-versao-com-20
commit: 6e77f72a3a6a38e3dbdcc12b43e0525f5cb26113
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-27
---
# Review: v0481

Code review, 1ª rodada completa (E36.2), do #928: `git diff 346a7860..6e77f72a`, 19 arquivos (+104/-267). Ordem do dono de 26/11 21:57: versão com 20 itens, sem corte diário. O aceite e a reprovação do QA (`docs/qa/v0481-versao-com-20.md`: M6 sobrevivente, textos com "até 2 por dia" fora do diff) são do domínio dele e não se repetem aqui.

- ci: 6e77f72a3a6a38e3dbdcc12b43e0525f5cb26113 verde

## Achados
- A1 (recomendado) docs/adr/0018-autorizacao-do-dono-gravada.md:209 · O R1 ainda compara o `ler --ato rotulo-pelo-time` "como o `--ato corte-diario` de F3", que a Retirada VERSAO-COM-20 apagou; trocar por "como o `--ato so-aperta-com-seguranca`" ou citar a Retirada.
- A2 (recomendado) tests/mutantes/v0481-autorizacoes-fixas.json:68 · A guarda de M7 e M8 ainda diz "sem corte-diario ativa, o corte sai com 1" e "só a concessão ativa autoriza o corte"; o trecho agora serve a qualquer ato sem prazo. Ajustar o texto da guarda (o de/para e os testes já estão certos).
- A3 (recomendado) bin/forge_autorizacao.py:477 · `cmd_corte` ficou sem corte: lê a concessão ativa de qualquer ato sem prazo. Renomear (por exemplo `cmd_ler_ato`) junto com o comentário de `executar`.
- A4 (recomendado) bin/forge-fechar:202 · Fora do diff, preexistente: o `--promover <sha>` aceita qualquer commit de marca sem reler o `forge-contador`; a regra dos 20 itens vale só pelo `--corte`. Cartão: o `--promover` conferir `N de 20` na marca.

## Parecer
Aprovado no meu domínio; recomendações viram cartão depois do merge.

- **Faz o que a ordem pede.** O `corte_diario` saiu do `bin/forge-fechar` inteiro (função, argumento `[autorização]` do `corpo_da_marca` e do `anexar_na_marca`, seção "Autorização usada" do corpo da marca). O V4 virou uma guarda só (`bin/forge-fechar:1636`): `N -ge teto` ou "ainda não fecha", sem ler autorização. O teto vem do `bin/forge-contador` (`TETO_PADRAO = 20`, `teto_versao` do `.forge/config.json`), sem mudança. `grep` na árvore do head: nenhum `corte_diario` nem chamada a `autorizacao ler --ato corte-diario` sobra em `bin/`, `hooks/`, `scripts/`, `agents/` e `skills/`; o `agora_teste` que fica no `forge-fechar` é o do aviso de PR parado do `--laco` (linha 1359), que não muda.
- **Nada mais mudou de comportamento.** Em `bin/forge_autorizacao.py`, sai só `corte-diario` de `FIXOS`, o termo `corte` de `ATO_DO_TERMO` e as palavras `corte diario todo dia` do `VOCABULARIO_FIXO`; `so-aperta-com-seguranca`, `rotulo-pelo-time`, `rotulo-afrouxa-regra` e `merge-main` ficam iguais. O `cmd_corte` perde o padrão `ato="corte-diario"`, e a única chamada (`executar`, linha 492) já passa `a.ato`. Concessão `corte-diario` gravada passa a ler `adulterada` ("Ato fora da lista"), testado em `tests/test_autorizacao.py:418`; o `ler` sem `--ato` diz "nada barra", e nenhuma concessão desse ato existe na raiz do Forge (só `rotulo-afrouxa-regra` e `merge-main`).
- **ADR e textos.** A Retirada VERSAO-COM-20 no fim da ADR 0018 traz a ordem do dono, o que sai, o que deixa de barrar e o critério de reversão (`R-DECISAO`); o Estado ganha a linha da emenda. `jarvis.md`, `fluxo-do-pedido`, `ritmo-e-corte.md`, os invariantes de `tests/config.json` e as diretrizes 21 e 34 da fixture dizem "versão com 20 itens". O invariante novo de `ritmo-e-corte.md` troca "até 2 por dia, ou mais se couber" por "A versão fecha com 20 itens integrados na `develop`": aperta, não afrouxa.
- **Testes e mutantes.** Saem os testes `CorteDiario` e M10 a M18 junto do código que vigiavam. A guarda nova da linha 1636 tem dois mutantes: M1 (`v0481-versao-com-20.json`, `true ||`) e o M25 (`v0480-d4-corte-contador-4.json`, `-ge` → `-gt`), reescrito para a guarda nova. Rodei os dois na fila (`flock trava-teste-b`): `M1 · morreu · bin/forge-fechar:1636` e `M25 · morreu · bin/forge-fechar:1636`. `python3 -m unittest tests.test_fechar_corte tests.test_autorizacao`: 63 testes OK. O `test_abaixo_do_teto_nao_ha_corte_diario` prova o ramo às 06:00 com zero chamadas ao `forge-check`.
- **Mapa de testes.** `test_fechar_corte` sai de `FORGE_CHECK` em `bin/forge-testes`, porque o módulo não executa mais o `forge-check`; o `MapaDoForgeCheck` confere a lista no CI.
- **Tamanho (H1).** Código fora testes e documentação: +16/-43 em `bin/` (`git diff --numstat`), quase tudo remoção; um comportamento só.
- **CI.** `gh api .../commits/6e77f72a/check-runs`: suíte (3.12 e 3.14, 5 partes cada), bateria (python 3.14), bateria (passos), bateria (verificações longas), instalação (python 3.14), teto de pulados e "árvore já provada na develop" concluídos em `success`; `bateria`, `bateria (pareceres)` e `catraca` esperam os pareceres (G3).
- **Commits.** Quatro commits em Conventional Commits em português, com o pedido e a etapa; o M25 reescrito vem no commit próprio dele.
