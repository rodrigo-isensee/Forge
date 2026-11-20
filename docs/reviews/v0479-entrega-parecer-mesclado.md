---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-parecer-mesclado
commit: cdf62e0a29a1dabf34c600bb0b802e9fd65bcf55
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 E50.2 (ENTREGA-PARECER-MESCLADO-ANTES-DO-AUTOR)

Primeira rodada: `git diff 8a503799..48153733` aprovado com A1 (ramo `cod` do rev-list sem teste) e A2 (`commit:` sem âncora no registro do Jarvis). Revalidação na volta E50.5 pelo delta (`forge-check parecer delta`, intervalo `48153733..cdf62e0a`): bin/forge-check, changelog.d, tests/test_selo_e_entrega.py e as specs `tests/mutantes/v0457-escopo-ponto-2.json`, `v0479-entrega-parecer-mesclado.json` e `-2.json`. Código da volta: cerca de 10 linhas, dentro do teto (H1).

## Sondas

## Parecer
Aprovado no head cdf62e0a.

A1 resolvido: `test_rev_list_que_falha_recusa` prova o caso aceito com o git certo e recusado com o `rev-list` do arquivo devolvendo erro; o falso só troca a chamada cujo último argumento é o nome exato do parecer (checklist 12). Mutante M14 (`if False or`) morre.

A2 resolvido: o `commit:` agora tem de ser igual ao `de`, que vem de `desde_valido` (sha40 de conferida do `## Histórico`, registro do Jarvis), e não mais qualquer commit do intervalo; o autor que cita o próprio código ou troca um reprovado por aprovado fica fora (testes novos, M7 morre). `commit_so_de_parecer` passou a aceitar só a pasta do tipo do parecer, fora de `docs/security/aceites/` (M12 e M13 morrem; o modelo de ameaças em `docs/security/` segue aceito, como o subteste mostra). `PASTA_E_REGRA[tipo]` é seguro: o chamador só chega com `tipo` da pasta. A ajuda do comando e o fragmento do changelog acompanham a regra nova. O M12 de v0457 ganhou trecho único depois da cópia do E50.1, sem mudar a guarda.

Rodei com ambiente limpo: `ParecerMescladoNaVolta` 14 testes OK; `test_forge_mutante.ConferirTodas` 4 testes OK; `forge-mutante` M12, M13, M14 (spec -2) e M4, M7, M8 (spec 1) morreram; `forge-mutante --conferir --base 48153733` acusa os trechos de cada spec no lugar. A suíte inteira fica com o CI do PR (`R-REVIEW`).
