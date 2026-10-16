---
tipo: review
contrato: 1
pedido: ta-5
branch: melhoria/ta-5-fechamento
commit: 27f38686da3f52bcbd5cdd3aade87fc42e8c45ee
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-16
---
# Review independente: script dos passos mecânicos de fechamento (TA-5)

Escopo: `15660a3...27f3868` (base 15660a346640; o autor não é este revisor). 6 arquivos, 2 commits (`ab924c6` feat, `27f3868` docs).

Veredito: **REPROVADO** por 1 achado que bloqueia (o merge não fica preso ao head conferido). Os outros 5 são recomendados. Tudo volta ao autor; este revisor não corrige o diff.

## Ferramentas (citadas, não refeitas)
- `python3 -m unittest tests.test_fechar -q`: `Ran 10 tests in 4.847s` / `OK`.
- shellcheck: não está instalado nesta máquina (`command -v shellcheck` sem saída). **Pendência:** a bateria do CI no PR o roda sobre `bin/forge-fechar`; não houve revisão manual no lugar dele.
- `tests/config.json`: fora do diff (nada removido nem afrouxado).
- Modo do arquivo: `100755 bin/forge-fechar`.

## Conferência contra o Entregar do brief da implementação
| Item | Resultado |
|---|---|
| Ordem dos passos e parada no primeiro erro | ok: 1 `forge-check pr` → 2 `ls-remote` → 3 PR → 4 checks → 5 rótulo → 6 merge → 7 limpeza; cada passo usa `die` (`bin/forge-fechar:74-116`); limpeza vira aviso, documentado |
| Recusa da base main | ok: `origin/main` e `main` recusadas, qualquer outra base fora do fluxo também (`bin/forge-fechar:34-39`); testado |
| Nada de `--force`, `--no-verify` nem rótulo | ok: teste lê o código sem comentários (`tests/test_fechar.py:157-160`); `git branch -D` é a limpeza de `R-FLUXO`, não `--force` |
| `--dry-run` sem efeito | ok: sai antes de qualquer `git`/`gh`/`forge-check` (`bin/forge-fechar:58-68`); teste compara branches, `develop` e `ls-remote` antes e depois |
| Testes cobrindo os casos | ok: dry-run, paradas nos passos 1, 2, 4 (vermelho e pendente), 5, base main e fora do fluxo, fluxo completo |
| Documentação | ok: `docs/fechamento-integrador.md` (uso, passos, o que nunca faz, teste, reversão), `agents/tech-lead.md:29`, `docs/economia-de-tokens.md` regra 2 |
| Neutralidade (`R-NEUTRO`) | ok: só nomes da própria fábrica (Forge, branches de integração), nada de projeto |
| Fragmento | ok: `changelog.d/ta-5-fechamento.md`, `### Adicionado` |

## Achados
1. `bin/forge-fechar:114` · **problema:** `gh pr merge "$ref" "$metodo"` mescla o head que o PR tiver naquele momento. Os pareceres (passo 1) e a igualdade local = remoto (passo 2) valem para `local_sha`, mas entre o passo 2 e o 6 há até `--espera` (30 min por padrão); um push na branch nesse intervalo faz o script mesclar um commit sem parecer, e os checks lidos no passo 4 podem ser os do commit novo. É o portão que o script promete não tirar ("nenhum portão sai", pedido, Suposições). · **sugestão:** `gh pr merge "$ref" "$metodo" --match-head-commit "$local_sha"` e, no teste, o `gh` falso recusar (`exit 1`) quando o sha não bate, com um caso que prove a parada no passo 6 sem `MERGED`. · **severidade: bloqueia.**
2. `bin/forge-fechar:93` · **problema:** logo depois do `gh pr create` o GitHub ainda não registrou os checks e `gh pr checks` responde "no checks reported" (saída sem tabulação); o script para no passo 4 na primeira leitura, no caso mais comum (PR recém-aberto). Falha fechado, mas obriga a rodar de novo. · **sugestão:** tratar "sem checks" como pendente dentro de `--espera` (só parar ao estourar o limite), com teste. · **severidade: recomendado.**
3. `bin/forge-fechar:33-36` e `docs/fechamento-integrador.md:7,18` · **problema:** `--base origin/homolog` (com `--merge`) é anunciado, mas a única branch que vai para a `homolog` é a `develop` (`R-FLUXO`: nada pula degrau) e `--ref develop` é recusado na linha 33; a opção nunca tem uso válido, e a limpeza do passo 7 apagaria a branch de origem se a recusa saísse. · **sugestão:** tirar `origin/homolog` do script e da documentação (a promoção segue manual), ou tratá-la como modo próprio (ref `develop` só com base `homolog`, sem `forge-check pr` de pedido e sem passo 7), com teste. · **severidade: recomendado.**
4. `bin/forge-fechar:83-87` · **problema:** o PR reusado pode estar em rascunho (`R-FLUXO`/tech-lead: "PR de melhoria nasce em rascunho"); o script não o tira de rascunho e o merge falha no passo 6, depois de esperar os checks. · **sugestão:** pedir também `isDraft` no `gh pr view` e, com o passo 1 já aprovado, rodar `gh pr ready "$ref"` (mesmo portão do hook `parecer`), ou parar no passo 3 com a instrução; documentar em `docs/fechamento-integrador.md:15`. · **severidade: recomendado.**
5. `bin/forge-fechar:107-108` · **problema:** o passo 5 falha aberto: se `gh pr view` falhar, `|| true` deixa `texto` vazio e o rótulo passa sem ser conferido. Hoje a catraca (check do passo 4) cobre o caso, então é defesa em profundidade, mas um portão do script não deve passar por erro de leitura. · **sugestão:** sem `|| true`; erro do `gh` → `die "parou no passo 5: ..."`, com teste (`gh` falso com saída de erro em `title,body`). · **severidade: recomendado.**
6. `bin/forge-fechar:70-71` · **problema:** `bin/` fica no PATH enquanto o plugin está ativo, então o script existe também nas sessões de projeto; ele roda `gh pr merge` dentro de um script, onde os hooks `parecer` e `conformidade` (que leem o texto do Bash) não o veem, e `R-CONTRIB` proíbe merge por sessão de projeto. · **sugestão:** recusar quando a raiz não é um clone do Forge (mesmo critério do hook, `.forge/versao` presente = projeto). **Encaminhado ao `security-engineer`** (parecer dele em `docs/security/`, em paralelo); não reavaliado aqui. · **severidade: recomendado.**

## Fora deste parecer
Segurança (`docs/security/`, em paralelo) e QA (`docs/qa/`, depois). Sem pipeline, contêiner nem IaC no diff: sem parecer de devops.
