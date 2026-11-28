---
tipo: qa
contrato: 1
pedido: v048
branch: melhoria/v048-git-controle-gc1
commit: 29bdda157d3e984cf5cafd71c9647874b4769f1b
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-28
---
# QA: v048 (GC1, bin/forge_git.py)

- ci: 29bdda157d3e984cf5cafd71c9647874b4769f1b verde

## Achados
- A1 (recomendado) bin/forge_git.py:35 · LEITURA aceita `branch -r -D x` e `remote -v add x <url>` (basta uma opção de leitura em `resto`): grava ref e config da cópia, sem executar programa (sonda); cartão depois do merge, R-SEGURANCA.

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
