---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-versao-com-20
commit: 2e6da2d5b9a7cf5d9a7a35bb7319b4b23a28b894
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-27
---
# Review de segurança: v0481 E36.11, #928 (VERSAO-COM-20), volta 2 por delta

Delta lido (`forge-check parecer delta`): `b19c7f53..2e6da2d5`. No domínio, só `tests/config.json`, uma linha (`:849`). As rodadas anteriores ficam no git (`b4cd2755` e a volta 1, `commit: b19c7f53`).

CI do head 2e6da2d5 (run 45942545671): as 10 partes da suíte, instalação, verificações longas, passos, python 3.14 e teto de pulados verdes; `bateria`, `bateria (pareceres)` e `catraca` esperam parecer e rótulo (o log delas não foi lido: o acesso ao armazenamento de logs foi negado no sandbox). Local, com a trava: `RegrasInviolaveis.test_invariante_traz_regra_e_porque_e_o_legado_so_encolhe` e os testes `-k invariante` de `tests/test_forge.py` passam no head.

Gatilhos: invariantes e motivos em `tests/config.json` (proteção de regra, L35).

## Estado dos achados anteriores
- A1 (bloqueante, 1ª rodada): resolvido na volta 1; o delta não toca `bin/forge_autorizacao.py` nem os testes dele.
- A2 (recomendado, volta 1): resolvido. `tests/config.json:849` troca a chave para "a versão fecha quando a branch de integração soma 20 itens integrados, sem versão por dia", igual, letra a letra, ao invariante de `:656` e ao texto de `templates/projeto/CLAUDE.md:15`; o porquê novo diz o efeito da falta (o projeto novo volta a fechar versão por dia; diretriz 34). `regra` segue `R-FLUXO`; o JSON carrega.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do delta, `gh pr checks`, teste afetado local. Ausentes no ambiente (lacuna, não instaladas): gitleaks, semgrep, osv-scanner, zizmor; o delta não toca workflow, dependência nem segredo.
