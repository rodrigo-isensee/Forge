---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-vigia-agentes-pesado
commit: 25c60be778696f894a488b8a266d5874db63ef9b
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0478 (E172.37, PR #859, VIGIA-AGENTES-PESADO), revalidação por delta

## Gatilhos
Gatilhos: hook de controle (vigia de prazo em `agentes` e `pesado`), falha fechada no PreToolUse.

## Resumo
Revalidação da rodada anterior (E172.25, reprovado em e54654c9; texto no git). Delta lido com `forge-check parecer delta`, intervalo `e54654c9..25c60be7`. No domínio só entra `tests/test_hooks_volta_propriedades.py`. Os specs `tests/mutantes/v0455-prazo.json` e `tests/mutantes/v0480-vigia-trava-critica.json` ficam fora do domínio, mas foram lidos porque são o objeto do A1. `hooks/` não mudou no intervalo, e a conclusão da rodada anterior continua valendo: o código só aperta ou fica neutro, nunca libera.

- O teste passa a usar `sem_manutencao` (`tests/ambiente_git.py:25`): só junta chaves de configuração do git a um ambiente que já era limpo (`PATH`, `HOME`). É neutro.
- Os specs mudaram só o `de`/`para` e o texto da guarda, para as linhas novas `hooks/_comum.py:2861`, `:2863` e `:2900`. Nenhuma guarda foi apagada: M2 (fora da sessão vigiada) e M4 (depois da ferramenta) voltam a cobrir a forma nova. Só aperta, porque a prova de morte do VIGIA-PRAZO-TRAVA volta.

Estado dos achados anteriores:
- A1 (bloqueante): corrigido. Os 5 mutantes aplicam e morrem (S1, S2), e a conferência de todas as specs passa.
- A2 (bloqueante): corrigido. `tests/test_hooks_volta_propriedades.py:314` passa pelo ponto único, e `test_ambiente_git.LeituraEstatica` passa.

## Sondas
- S1 · bin/forge-mutante tests/mutantes/v0480-vigia-trava-critica.json · espera: M1-M5 morrem · obtido: M1, M2, M3, M4, M5 morreram (M2 e M4 por erro do teste declarado, não por asserção)
- S2 · bin/forge-mutante tests/mutantes/v0455-prazo.json --ids P11 · espera: morre · obtido: P11 morreu, hooks/_comum.py:2900

## Testes rodados (só os dos arquivos tocados)
- `python3 -m unittest tests.test_forge_mutante.ConferirTodas.test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes tests.test_hooks_volta_propriedades.VigiaAgentesPesado tests.test_ambiente_git.LeituraEstatica`: 15 testes, OK.
- Suíte inteira no CI do head 25c60be7 (run 45440138432): as partes 1/5 a 5/5 em 3.12 e 3.14, os passos e as verificações longas estão verdes. Seguem vermelhos `bateria (pareceres)`, porque este parecer ainda era o reprovado, e `catraca` (run 45440138842). A catraca acusa duas coisas. A primeira é o `R-CONFORMIDADE`, que só passa com o rótulo `afrouxa-regra` do dono: é decisão do dono, e o mérito, que só aperta, está acima. A segunda é o `R-QA`, "guarda apagada sem mutante declarado" sobre `regra_do_prazo and critico is not None` (base `hooks/_comum.py:2894`). Pelo lado da segurança, esse ramo está coberto por `tests/mutantes/v0480-vigia-agentes-pesado.json` M3 (o arme sem o marcador). Fechar o check é com o QA e o `tech-lead`. Nada disso é achado de segurança.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática, `unittest` e `forge-mutante` locais, `gh pr checks` e `gh run view --log-failed` (só leitura). `gitleaks`, `osv-scanner`, `zizmor` e `actionlint` não se aplicam: o delta não tem segredo, dependência nem workflow.
