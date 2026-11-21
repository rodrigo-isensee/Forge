---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-a2-concessao
commit: 9b6dca25db319a73277a5bc2bfaf151af8cd53a6
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0478 · PV-A2 (concessão `item:` presa ao commit), etapa E57.67 (revalidação)

Volta por delta sobre o parecer reprovado no head 4c325c55 (commit 5867d8ec; a rodada anterior fica no git). Referência: ADR 0018 (item 5) e Emenda PR-VERDE E1.

## Gatilhos
Gatilhos: controle de autorização do dono (ADR 0018), afrouxamento de regra (rótulo `afrouxa-regra`), execução de `git` por subprocesso.

## Delta lido
`forge-check parecer delta`, intervalo `4c325c55..9b6dca25`: no domínio, só `bin/forge_autorizacao.py`, lido inteiro no diff e com `normal`, `problemas`, `git` e `fora_do_revisado` em volta. Fora do domínio: `tests/test_autorizacao.py`, mutantes 1 a 4 e o fragmento do changelog. Do teste li só o que as sondas usam (`ItemPresoAoCommit`, `TIPOS`, `MARCAS`). As sondas rodam no repositório desse teste, com o módulo do head 9b6dca25.

## Achados anteriores
- A1 (bloqueante): corrigido. `--no-renames` em `bin/forge_autorizacao.py:195`, e cada arquivo mudado depois do Commit tem de ser um parecer com a `branch:` do próprio Ramo na ponta (arquivo apagado não tem frontmatter e é recusado). Sondas S1 e S8.
- A2 (bloqueante): corrigido por vocabulário fechado positivo (`:30`, `fora_do_vocabulario` em `:150`), que é a regra do item 5 da ADR 0018, e não por lista negativa. Sonda S2.
- A3 (recomendado): corrigido. O termo do ato é procurado como palavra inteira, na frase sem o trecho do alvo (`:162`). Sonda S3.
- A4 (recomendado): corrigido. `EXIGIDOS` (review, qa, revisao-seguranca) em `:37`, conferido na linha 201; o parecer de devops, se houver, também tem de aprovar. Sonda S4. Fica o A5 abaixo.

## Só aperta?
Sim, com uma exceção que corrige um falso positivo e não afrouxa nada:
- **Vocabulário:** toda mensagem que passa no vocabulário novo também passava na RESSALVA antiga, porque nenhuma marca da RESSALVA está no `VOCABULARIO` (`a` está, mas `a menos` exige `menos`, que não está; `desde que` exige `desde`). O teste `test_vocabulario_fechado...` confere que `MARCAS` e `VOCABULARIO` não têm palavra em comum. Data e hora só saem nas formas `18/11`, `12:00` e `18h`; número solto continua recusado (S7).
- **Exceção:** o trecho `item <CARTAO>` sai antes da checagem do vocabulário. Com um cartão chamado `NAO-1`, "pode aplicar o rótulo no item NAO-1" era recusado pela RESSALVA e agora sai ativa (S6). O nome vem do time, o casamento é exato (`marcado`, com bordas) e uma ressalva do dono fora do nome continua recusada. Aceito como correção.
- **Diff depois do Commit:** antes, bastava o arquivo estar sob `docs/{reviews,qa,security,devops}/`; agora, além disso, a renomeação conta como saída e entrada, e o frontmatter precisa trazer a `branch:` do Ramo. Só aperta.
- **Pareceres:** antes, "ao menos um, e todos aprovam"; agora, os três exigidos presentes, e todos aprovam. Só aperta.
- O consumidor segue o mesmo (`cmd_ler`, só leitura), e os alvos `pr:` e `versao:` não passam por `do_item` nem por `fora_do_revisado`.

## Achados
- A5 (recomendado) bin/forge_autorizacao.py:200 · o tipo do parecer vem só do frontmatter, sem conferir a pasta: um `docs/qa/x.md` com `tipo: revisao-seguranca`, a branch e o commit certos supre o EXIGIDO de segurança e a concessão sai ativa (S5). Exigir tipo coerente com a pasta.

## Sondas
- S1 · `git mv codigo.txt docs/qa/codigo.txt; git commit -m mv`, depois `concessoes()` · espera: ('inativa', 'Commit não é o head: o Ramo muda depois dele') · obtido: o mesmo
- S2 · "pode aplicar o rótulo no item PV-A2 depois do CI" / "... sem o teste" / "... antes do merge", Estado-inicial ativa · espera: adulterada · obtido: ('adulterada', 'ativa com ressalva ou palavra fora do vocabulário: ci, depois'); (... sem, teste); (... antes, merge)
- S3 · Alvos `item:ROTULO-1`, corpo "o item ROTULO-1 pode" · espera: adulterada · obtido: ('adulterada', 'ativa sem item <CARTAO> na frase do ato')
- S4 · `git rm docs/qa/pv-a2.md docs/security/pv-a2.md` depois do Commit · espera: inativa · obtido: ('inativa', 'Commit sem os pareceres aprovados nele')
- S5 · nenhum parecer em docs/security; `docs/qa/falso.md` com `tipo: revisao-seguranca`, a branch do Ramo, o commit certo e `parecer: aprovado` · espera: inativa · obtido: ('ativa', '')
- S6 · Alvos `item:NAO-1`, corpo "pode aplicar o rótulo no item NAO-1" · espera: ativa (nome do cartão não é ressalva; ver "Só aperta?") · obtido: ('ativa', '')
- S7 · "pode aplicar o rótulo no item PV-A2 18/11 12:00" e o mesmo com "2" no lugar da data · espera: ativa; adulterada · obtido: ('ativa', ''); ('adulterada', '... fora do vocabulário: 2')
- S8 · `git config diff.renames copies; git mv codigo.txt docs/reviews/codigo.txt; git commit -m mv` · espera: inativa · obtido: ('inativa', 'Commit não é o head: o Ramo muda depois dele')

## Detalhe do A5
Evidência: `bin/forge_autorizacao.py:199-201`. O `git grep` varre as quatro pastas de parecer, e o tipo sai só do frontmatter. Caminho de ataque: um agente com escrita em `docs/qa/` (o hook dá a cada papel a sua pasta) grava um parecer com `tipo: revisao-seguranca`, aprovado no Commit, e o EXIGIDO de segurança fica suprido sem o parecer do `security-engineer`. Proporção: hoje o estado `ativa` não libera nada (só `cmd_ler` o lê), o `forge-check docs` amarra tipo e pasta (`bin/forge-check:198-205`) e o merge confere a classe. O risco passa a contar quando o PV-A3 começar a confiar no `ativa`. Severidade: baixa. Correção mínima: no filtro de `pareceres`, exigir que o caminho de cada achado comece pela pasta do seu `tipo`: `review` em `docs/reviews/`, `qa` em `docs/qa/`, `revisao-seguranca` em `docs/security/`, `revisao-devops` em `docs/devops/`; e um caso de teste com a sonda S5. Esforço: P. Dono: `software-engineer`, com o teste a cargo do `qa-engineer`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodei as sondas S1 a S7 numa classe que herda `ItemPresoAoCommit` (16 testes, OK) e `tests.test_autorizacao` (16 testes, OK), contra o head. A suíte inteira não rodou localmente (o brief manda não rodar a suíte local) e o CI do head não foi conferido aqui (`gh` indisponível no ambiente); o portão de merge continua sendo o CI verde. `gitleaks` e o SAST da stack não estão no PATH (lacuna registrada); o delta não traz credencial nem dado pessoal.
