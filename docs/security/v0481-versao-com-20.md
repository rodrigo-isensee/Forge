---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-versao-com-20
commit: b19c7f53a1a564059901a406a0e7ddf74ae63b24
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-27
---
# Review de segurança: v0481 E36.7, #928 (VERSAO-COM-20), volta 1 por delta

Delta lido (`forge-check parecer delta`): `6e77f72a..b19c7f53`. No domínio: `agents/tech-lead.md`, `bin/forge_autorizacao.py`, `docs/adr/0018-autorizacao-do-dono-gravada.md`, `skills/falar-com-o-dono/nao-trava.md`, `templates/projeto/CLAUDE.md`, `tests/config.json`, `tests/test_fechar_corte.py`. Lidos também, por serem a correção do A1 e a guarda dos mutantes: `tests/test_autorizacao_gravar.py`, `tests/test_autorizacao.py`, `tests/mutantes/v0481-autorizacoes-fixas.json` e `-2.json`. A 1ª rodada fica no git (`b4cd2755`).

CI do head b19c7f53 (run 45939103472): as 10 partes da suíte, instalação, verificações longas, passos e teto de pulados verdes; `bateria`, `bateria (pareceres)` e `catraca` falham só por pareceres e pelo rótulo. A catraca acusa o que o corpo do PR lista em "Afrouxa": a troca dos invariantes (inclusive o do modelo de projeto), os 6 testes de `CorteDiario`, o renomeado `test_corte_diz_a_corte_diario_ativa_mais_nova_e_sem_ela_rc_1` e o valor esperado trocado em `test_vocabulario_novo_so_nos_atos_fixos_e_sem_marca` (este aperta: mata o M6). Nada afrouxado fora da lista.

## Gatilhos
Gatilhos: autorização do dono gravada (ADR 0018, `bin/forge_autorizacao.py`), invariantes trocados em `tests/config.json`.

## Estado dos achados anteriores
- A1 (bloqueante, 1ª rodada): resolvido. `tests/test_autorizacao_gravar.py:531` usa "pode mesclar a main 0.47.3, o time decide" e afirma o motivo "decide, time"; as asserções em `:532` e `:533` provam que `decide` e `time` ficam fora do `VOCABULARIO` e dentro do `VOCABULARIO_FIXO`. `bin/forge-mutante --rev b19c7f53` nas specs `v0481-autorizacoes-fixas.json` e `-2.json`: M1 a M9 morrem, M6 em `bin/forge_autorizacao.py:378` (log em `/root/.forge-contrib/wt/_sec131-v0481-mut.log`).

## O que o delta muda
- `cmd_corte` vira `cmd_ler_ato` (`bin/forge_autorizacao.py:477`, chamada em `:492`): só renome; a falha fechada (rc 1 sem concessão ativa do ato; só `ativa` conta) segue igual, M7 a M9 mortos.
- ADR 0018 R1 (`:209`) passa a comparar com `--ato so-aperta-com-seguranca`: texto, sem mudança de controle.
- `agents/tech-lead.md:44`, `skills/falar-com-o-dono/nao-trava.md:19` e `templates/projeto/CLAUDE.md:15`: a versão fecha com 20 itens, sem versão por dia (A2 de QA); o invariante do modelo em `tests/config.json:656` segue o texto novo.
- `tests/test_fechar_corte.py:105` e `tests/test_autorizacao.py:395`: só comentários com as sondas.

## Achados
- A2 (recomendado) tests/config.json:849 · o motivo do invariante do modelo ficou na chave com o texto velho ("até 2 por dia"); o novo (:656) fica sem motivo próprio e o checador, que só conta trechos, não vê. Renomear a chave para o texto novo, com o porque da versão com 20 itens.

## Sondas

## Detalhe dos achados
**A2.** Evidência: `tests/config.json:656` (invariante novo de `templates/projeto/CLAUDE.md`) e `:849` (`invariantes_motivo_trecho`, chave com o texto que saiu, porque "segura a versão para uma vez só de manhã"). `problemas_de_motivo` (`tests/test_forge.py:570`) compara só quantidades por arquivo, sem casar a chave com um trecho de `invariantes`, por isso a suíte fica verde. Caminho de ataque: nenhum exploratório; é metadado de proteção de regra (L35) apontando para um trecho que não existe mais, e quem mexer no invariante novo não lê o porquê dele. Severidade: baixa. Correção mínima: em `tests/config.json:849`, trocar a chave por `a versão fecha quando a branch de integração soma 20 itens integrados, sem versão por dia` e o porque por um que diga o efeito da falta (o projeto novo não recebe o fechamento com 20 itens, diretriz 34). Esforço: P. Dono: `tech-lead` (autor do #928). O checador não casar a chave com o trecho é anterior a este delta: vai como cartão, não como achado.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do delta, `forge-mutante` (M1 a M9 no head), `gh pr checks`. Ausentes no ambiente (lacuna, não instaladas): gitleaks, semgrep, osv-scanner, zizmor; o delta não toca workflow, dependência nem configuração com segredo.
