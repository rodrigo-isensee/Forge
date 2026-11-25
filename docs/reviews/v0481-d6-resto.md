---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-d6-resto
commit: 50a40e28844435d4bf43c8b23d3880e1b37af7b9
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Code review: hook salvar só grava na cópia local, volta E11.18 (D6 parte a; v0481 E11.19, PR #877)

Revisado por delta: `1afd54b5..50a40e28`, lido pelo `forge-check parecer delta` sem o que veio da develop (merge `9f264141d`). Domínio lido: `changelog.d/v0481-d6-resto.md`, `docs/adr/0003-hooks-deterministicos-e-silenciosos.md`, `docs/indice-forge.md`, `docs/regras/R-LIMITES.md`, `hooks/hooks.json`, `hooks/salvar.py`, `tests/mutantes/v0481-d6-resto{,-2,-4,-5,-6}.json` e `tests/test_hooks.py`. Os commits do item são `cfd24cee5`, `b6c98cb27`, `88fc382a7` e `50a40e288`. O `docs/hooks-fixtures.md` mudou só pelo merge da develop. Parecer anterior: reprovado no `1afd54b5`, por A1.

## Parecer
**Aprovado.** A volta segue a DECISÃO DO DONO de 25/11, opção (b): o hook só faz o commit na cópia local, sem rede, e o envio fica com o fechamento.

**A1 anterior (segredo em commit anterior levado pelo push): saiu junto com o envio.** O `hooks/salvar.py` não tem mais `push`, `fetch`, `ls-remote`, `VARREDURA` nem `HEAD^`. As únicas menções a `remote` restantes são a leitura da config (`remote.origin.url` na lista `PERMITIDAS` e a comparação com a cópia principal, linhas 32 e 61-62). Sem envio, o pre-push roda inteiro no envio de sempre, e o segredo fica barrado ali. A base da varredura lida de ref local (`refs/remotes/origin/<branch>`), apontada pela segurança, saiu pelo mesmo motivo.

**M8 e M9 vivos pelo fixture não rastreado (QA): resolvido.** O `docs/a.md2` agora é rastreado no `setUp`. Em `test_salva_so_o_escopo_na_copia`, ele aparece como ` M docs/a.md2` fora do commit, e isso mata o mutante do prefixo, que antes passava porque o arquivo não era rastreado.

**Testes.** Os testes do envio e da varredura saíram. `salvo()` lê o commit WIP no HEAD da cópia. O teste novo, `test_branch_ja_no_remoto_fica_como_esta`, prova que o hook não envia nem busca: a ref do remoto e a `origin/melhoria/x` da cópia ficam iguais. O caso da branch de integração passou a conferir que não há commit nem linha no log. `88fc382a7` aplica o `remoto_sem_manutencao` aos três bare que o `test_ambiente_git` exigia, e `50a40e288` troca o `README.md` da fixture por `notas.txt`, para o `test_reval_delta.Guarda` não contar citações a mais. Nenhuma das duas trocas muda o que a asserção prova.

**Mutantes.** Saíram M26, M36 e M37, porque as guardas deles saíram do código. O M34 segue o novo `fora = ("XDG_CONFIG_HOME",)`. As specs que citavam testes renomeados apontam para os nomes novos. Não há guarda nova no delta: o `salvar()` perdeu ramos e não ganhou nenhum.

**ADR 0003 e R-LIMITES.** A emenda D6 diz que o item 2 vale sem exceção e põe "qualquer chamada de rede dele" no critério de reversão. A exceção ao R-VERIFY fica só na regra 4 da emenda, e o `R-LIMITES.md` volta ao texto da base: no diff contra a `develop` ele não muda. O motivo dado (o orçamento do núcleo do Jarvis) é aceitável, e o título do PR segue com `[afrouxa-regra: R-VERIFY core.hooksPath]`.

**Verificadores.** No `50a40e28`, `python3 -m unittest tests.test_hooks.SalvarAoParar` com ambiente limpo: 29 testes, OK. Não rodei a bateria inteira. O CI do head tem verdes as 5 partes da suíte em python 3.12 e 3.14, `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, `instalação`, `teto de pulados` e `árvore já provada na develop`. `bateria` e `bateria (pareceres)` falham porque os pareceres de review e de QA ainda estão reprovados (lido no log do run 45652375754). A `catraca` (run 45652375891) falha por `R-QA: guarda de hooks/salvar.py mudada sem mutante declarado`: o M29 só tem nota de equivalente (`salvar.py:127`) e a linha `__name__ == '__main__'` (`salvar.py:156`) não tem mutante. A mesma causa já aparecia no `1afd54b5` (linhas 130 e 165), então não vem do delta. A catraca aceita o rótulo `afrouxa-regra`, que só o dono aplica e de que este PR já precisa pelo R-VERIFY.
- ci: 50a40e28844435d4bf43c8b23d3880e1b37af7b9 verde
