---
tipo: review
contrato: 1
pedido: conf-anexo-pareceres
branch: melhoria/conf-anexo-pareceres
commit: d574bf4c1c6fce19c655200c7d1d594f2e8246f0
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-17
---
# Review: CONF-ANEXO-PARECERES, pareceres de segurança e devops como anexos implícitos do conferente

Escopo: `f636d27...d574bf4` (base f636d27c95bd1fdc9137baa830e0f53905863eaf), 3 arquivos em 2 commits (`agents/conferente.md` +1/-1, `changelog.d/conf-anexo-pareceres.md` +2, `tests/test_forge.py` +11). Não sou o autor. Comparei o diff com o Escopo E1 a E3 do pedido `docs/pedidos/conf-anexo-pareceres.md`.

Veredito sobre `d574bf4`: **REPROVADO**. Há 1 achado que bloqueia: a mudança afrouxa uma verificação, e o dono decidiu que nada pode afrouxar o processo (2026-10-15). Há também 1 observação fora do escopo. A correção é pequena e volta ao autor.

## Cobertura declarada (VV-1)
- **Lido:** o diff inteiro. Em `agents/conferente.md`, li só o item 2 "Escopo" do modo entrega (linha 71). Para cruzar as listas de caminhos, li `hooks/conformidade.json` (linhas 44 a 48), `bin/forge-check` (linha 60, `LIVRES`, e `aceite_do_usuario`, linhas 442 a 456), `docs/regras/R-SEGURANCA.md:13` e `docs/adr/0004-contrato-verificavel-entre-agentes.md:20`.
- **Rodado:** `python3 -m unittest tests.test_forge -q` → `Ran 248 tests ... OK`. Seguindo a R-TETO, não rodei a suíte inteira nem o `validar-plugin`: o autor rodou os dois (786 OK), e o QA e o CI vão rodá-los de novo.
- **Não lido:** o resto de `agents/conferente.md`, e os outros testes e hooks fora dos trechos citados acima.

## Achados por classe

### Afrouxamento de verificação (bloqueia)
1. `agents/conferente.md:71` · **Problema:** o item novo `docs/security/` é um prefixo e, por isso, cobre também `docs/security/aceites/`. Essa pasta guarda o aceite de risco, que é do usuário e é escrito à mão por ele: nenhum agente a grava, segundo `R-SEGURANCA.md:13` e `hooks/conformidade.json:47` (`"quem": []`). Antes desta mudança, um arquivo de aceite incluído na entrega do autor caía em `escopo: fora` e reprovava. Agora ele vira `escopo: ok (anexo)`. O hook `conformidade` lê o Bash só como texto, e o próprio cabeçalho admite que "um script ou ofuscação passa" (`hooks/conformidade.py:7`). Por isso o conferente era a segunda camada contra um aceite forjado por agente, que é o arquivo que libera `parecer: riscos-aceitos` no `forge-check pr` (`bin/forge-check`, `aceite_do_usuario`). O defeito relatado no cartão envolvia só o parecer de outro papel (`docs/security/<pedido>.md`), não o aceite.
   **Como reproduzir:** `git -C ~/.forge-contrib/wt/conf-anexo show d574bf4:agents/conferente.md | grep -c 'docs/security/aceites'` retorna `0` (não há exceção). `grep -n 'docs/security/aceites/' ~/.forge-contrib/wt/conf-anexo/hooks/conformidade.json` retorna a linha 47, `quem: []`.
   **Sugestão:** manter `docs/security/` na lista e acrescentar a exceção no mesmo trecho, por exemplo: "`docs/security/` (salvo `docs/security/aceites/`, que é do usuário e continua `escopo: fora`)". No `tests/test_forge.py:241`, o teste deve prender também a exceção, com um `assertIn` do texto dela. Assim a correção fica do tamanho do defeito: só o parecer de outro papel vira anexo, e o aceite continua como antes.

### Correção funcional (sem achado)
- E1: a lista ganhou `docs/security/` e `docs/devops/` sem perder nenhum item, e a regra "só por acréscimo" e a verificação de `anexo com remoção` continuam valendo para os itens novos (`git diff --numstat --no-renames f636d27...d574bf4` mostra `1 1 agents/conferente.md`, que é só a troca da linha). Os itens novos alinham o conferente com o `LIVRES` do `forge-check` (`bin/forge-check:60`), que já trata esses caminhos como pareceres.
- E2: o teste `test_conferente_lista_de_anexos_implicitos` (`tests/test_forge.py:233`) prende a lista exata e a frase "`tests/config.json` nunca é anexo". Ele falha antes da mudança, porque na base a lista não tinha os dois itens novos, e passa depois. A lista tem 8 itens, e o `assertEqual` serve como mínimo de itens (checklist 11). O `tests/config.json` não foi tocado, o que está correto: a invariante só entraria por acréscimo, e o teste já protege o trecho. O fragmento do changelog está em `changelog.d/` e o `CHANGELOG.md` não foi editado.
- E3: `grep -n 'anexos implícitos' docs/regras/R-PROVA.md` volta vazio, então não havia documentação a atualizar. Está correto.

### Commits e regras (sem achado)
- Os 2 commits seguem Conventional Commits em português e têm a atribuição. Não há `--no-verify` nem `--force`. R-NEUTRO e R-CUSTO não foram afetados (só texto e teste da biblioteca padrão).

### Observação fora do escopo (não bloqueia; vira cartão)
- `docs/adr/0004-contrato-verificavel-entre-agentes.md:20` lista os caminhos livres do `commit_vale` sem `docs/devops/` e `docs/security/`, enquanto o código já os inclui (`bin/forge-check:60`). É uma divergência entre a ADR e o código que já existia antes deste pedido. Sugiro um cartão próprio para emendar a ADR.

## Afrouxa alguma verificação?
Sim, num ponto só: o achado 1 (`docs/security/aceites/`). Fora isso, a mudança só restringe o motivo de reprovação ao que é escopo do autor e mantém a regra do acréscimo.

## Pareceres de outros papéis
O parecer de segurança (E2.2, R-SEGURANCA) corre em paralelo (VV-4) e não é refeito aqui. O achado 1 também é matéria de controle de segurança e fica registrado para o `security-engineer`.
