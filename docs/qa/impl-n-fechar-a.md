---
tipo: qa
contrato: 1
pedido: impl-n-fechar-a
branch: melhoria/impl-n-fechar-a2
commit: bf0606059c9b082900fae957b7e4ab52e0324163
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-22
---
# QA: impl-n-fechar-a (lote N-FECHAR-a refeito, A1 a A6)

Escopo: `git diff a3dbe22..bf06060`. Os pareceres de review (0d36da3) e de segurança (504b03e) são sobre o mesmo código. Tudo rodou em cópia própria (`git archive` em `$TMPDIR`), sem rede nem `gh` real (`R-CUSTO`); o HEAD da worktree compartilhada não foi trocado. O código de produção é o de bf06060; depois dele só entraram pareceres.

## Achados

## Critério → teste → resultado
Obrigações do §2 do desenho e do adendo de ameaças (não há `CA-n`; cada item é uma obrigação).

| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A3: teto e piso de `FORGE_FECHAR_PAUSA` (1 a 30), `FORGE_FECHAR_INTERVALO` (5 a 120) e `--espera` (0 a 7200), antes do passo 1 | `tests/test_fechar_faixas.py` + sonda manual (`--espera 99999999999999999999`, `7201`, `08x`, pausa 0 e 99, intervalo 2) | vazio, 20 dígitos, logo fora do limite | passou |
| A1: registro órfão com `prune` negado imprime o prune e comandos escapados | `tests/test_fechar_orfao.py` | caminho e nome com metacaracteres | passou |
| A2: aviso de lock do config não passa por `branch=ok` | `tests/test_fechar_config.py` | `config.lock` ocupado, seção `a` × `a.b` | passou |
| A4: TERM, INT e HUP gravam `fim:` 143/130/129 e cortam a espera | `tests/test_fechar_sinal.py` | sinal no pid e no grupo, intervalo longo em curso | passou |
| A5: passo 2b para com base andada e arquivo em comum, e falha de leitura também para | `tests/test_fechar_base_andou.py` | renome, nome com quebra de linha, servidor mudo, diff falho | passou |
| A6: sha da branch local conferido antes de remover a worktree | `tests/test_fechar_sha_arvore.py` | arquivo ignorado preservado | passou |
| Guia `docs/fechamento-integrador.md` (corte por sinal, sem `pkill -f`, log sem `fim:`) | leitura contra o desenho | n/a | conforme |
| P3 = B: cada commit se reverte sozinho no HEAD | `git revert` de cada um sobre bf06060, com `tests/test_fechar*.py` depois | n/a | passou |

## Cenários e resultado real
- **Testes novos:** 32 testes dos seis arquivos, OK (6 s).
- **Vermelho antes do verde:** `bin/forge-fechar` de a3dbe22 (sem a mudança) com os 32 testes novos: `Ran 32 tests ... FAILED (failures=27, errors=1)`. Os 4 que passam são guardas de caminho feliz.
- **Reversão por commit (P3 = B):** `git revert` sem conflito e `python3 -m unittest discover -s tests -p 'test_fechar*.py'` OK depois de cada um: dd09940 (107 testes), 32c1c2f (109), 8543a6e (105), 7a2fad5 (107), f791d46 (102), f893326 (110).
- **Suíte completa** na cópia: 1404 testes, 2 erros, ambos por a cópia não ter `.git` (`SandboxDoBash`); os mesmos dois testes passam na worktree (14 testes OK com `NeutralidadeDoNucleo`). Nenhuma falha de código.
- **Sonda das faixas:** mensagens com a faixa, antes do passo 1; `bash -n` OK. `shellcheck` e `claude plugin validate` não rodaram aqui (shellcheck ausente; o `scripts/validar-plugin.sh` falhou na cópia sem `.git` e sem rede); ficam para o CI.
- **Mutação:** a stack não oferece ferramenta no Forge; sem mutação. O vermelho acima e a reversão fazem o papel de prova.

## Recomendações (não bloqueiam; já registradas nos pareceres de review e segurança)
- Aviso de `bin/forge-fechar:251` manda `git branch -D` sem citar commit não mesclado (ordem do A6 versus o caso "dentro da worktree"). Vai ao N-FECHAR-b.
- `tmp2b`, `dorme_pid` e `cfg_campo` sem valor inicial no topo; `trap - EXIT` antes de `trap '' TERM INT HUP` no `fim`. N-FECHAR-b.
- `diff_falha` derruba os dois lados do diff, então mutante em um só lado sobrevive (teste a refinar no N-FECHAR-b).
- `docs/fechamento-integrador.md:23`: dizer que a rodada seguinte só vale com branch local e remota ainda existentes; no resto vale `--limpar`.
