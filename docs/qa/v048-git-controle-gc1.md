---
tipo: qa
contrato: 1
pedido: v048
branch: melhoria/v048-git-controle-gc1
commit: 841c557ea6eb82bddf4eec7bf48c816683b533b0
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-28
---
# QA: v048 (GC1, bin/forge_git.py)

- ci: 841c557ea6eb82bddf4eec7bf48c816683b533b0 verde

## Achados
- A1 (recomendado, tratado na volta 1: `_so_leitura` recusa `branch -r -D x` e `remote -v add`; sem cartão) bin/forge_git.py:81 · LEITURA aceitava `branch -r -D x` e `remote -v add x <url>` (basta uma opção de leitura em `resto`): grava ref e config da cópia, sem executar programa (sonda); cartão depois do merge, R-SEGURANCA.

## Critério → teste → resultado
Sem especificação de UX (pedido de controle); a obrigação é cada vetor do anexo E3.1 (seção 2) e cada guarda de 3.1.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Vetores: fsmonitor, sshCommand, credential.helper, diff.external e assinatura, driver por info/attributes, hooks plantados, insteadOf, uploadpack | `Vetores.*` (8) | cru executa o marcador, `forge_git` não | passou |
| Recusa: não-repositório, config ilegível, uma chave fora da lista basta, opção reativa (`--path=f`, `-O`), subcomando fora da lista ou misto, rede só ls-remote/fetch por https | `Recusas.*` (9) | vazio, limite da lista, forma com `=` | passou |
| Legítimos: cópia limpa passa em todos; pasta neutra fora do TMPDIR do agente | `Legitimos.*` (2) | n/a | passou |
| Mutação M1-M25 (inclui linhas 59-61, 75, 88 cobradas pela catraca) | specs 1 a 4 | cada linha de guarda | 25/25 morreram |

## Provas de QA
- CI: `gh pr checks 957` no head 29bdda15: bateria (passos, pareceres, python 3.14, verificações longas), suíte 1/5 a 5/5, catraca, catraca (conferência), instalação e teto de pulados todos `pass`; `bateria (espera parecer)` pass.
- Módulo local: `python3 -m unittest tests.test_forge_git` no head: Ran 19, OK. Sem `skip`/`expectedFailure` no arquivo. `test_textos_ci_custo` e `test_doutor_custo`: 16 OK (teste de custo, bin/ tocado; nada pago).
- Vermelho: `bin/forge-testes --vermelho 1ced5c092470 --modulos test_forge_git` saiu 1: `contagem: não prova (passa na base)=19`, falso negativo da ferramenta (ver Melhoria). Prova manual numa cópia com `bin/forge_git.py` removido: `python3 -m unittest tests.test_forge_git` dá `Ran 1 test, FAILED (errors=1)` (ImportError); no head, 19 OK. Os mutantes provam o comportamento.
- Mutantes: `bin/forge-mutante` das 4 specs, `--processos 4`: M1..M25 todos `morreu` (M20-M24 com `(erro)`, controle verde); sem sobrevivente.
- Cobertura: `bin/forge-mutante --cobertura --base 1ced5c092470` sem linha `não coberto`; rc 0.
- Sondas: `config -l -e` e `config --edit --get` não executam o `core.editor` da cópia (marcador ausente).

## Delta das voltas 1 e 2 (29bdda15 a 841c557e), mutação refeita pelo QA
Domínio: `bin/forge_git.py`, `tests/test_forge_git.py` e as 6 specs `tests/mutantes/v048-git-controle-gc1*.json` (`forge-check parecer delta`). Os logs do autor não valeram; tudo abaixo foi rodado por mim numa cópia própria no head 841c557e.
- ci: `gh run view 46145488828` (CI do 841c557e): suíte partes 1/5 a 5/5 `success` (a 5/5 pelo rerun), passos, python 3.14, verificações longas e instalação `success`; só `bateria (pareceres)` e `bateria` falharam, por esperarem os pareceres; catraca e catraca (conferência) `success`. Os envios dos pareceres de review e segurança (52b3bdf4, fc694b7b, só docs/) substituíram os runs seguintes.
- Mutação: `bin/forge-mutante --processos 3` das 6 specs juntas: M1..M38, 38 linhas `morreu`, nenhuma `sobreviveu` nem `sem veredito` (M20-M24, M27, M32, M33, M36, M38 com `(erro)` sob controle verde, válido). M26-M38 cobrem REATIVA abreviada, core.pager, posição da ação, branch só listagem, gitlink e chaves do VS Code.
- Cobertura: `bin/forge-mutante --cobertura --base 29bdda15`: toda condição Python mudada do diff `coberta`; a única `não coberto` é `hooks/conformidade.json`, que veio da develop no merge, fora do domínio.
- Vermelho: `bin/forge-testes --vermelho 29bdda15 --modulos test_forge_git`, saída 0: `contagem: não prova (passa na base)=18; prova (asserção)=6` (os 6 testes novos caem na base e nenhum cai no HEAD).
- Local: `python3 -m unittest tests.test_forge_git`: Ran 24, OK, sem `skip`/`expectedFailure`; `test_textos_ci_custo` e `test_doutor_custo`: 16 OK (teste de custo; nada pago).
- Sondas (git 2.43 local): `montar` recusa `--out`, `--ou=x`, `-Ofoo`, `branch --list -m a b`, `remote -v add`, `remote -- add`, `worktree -q add`, `worktree -- add`; `config` misto (`--get --unset`, `--list --replace-all`, `--get --add`) não gravou a config num repositório descartável. `branch --contains HEAD x` é aceito: sem escrita, o argumento vira padrão de listagem.
- Limite: o git do runner (2.56.1) difere do local; a sonda por `cat-file --textc` do autor fica coberta pelo CI verde.
