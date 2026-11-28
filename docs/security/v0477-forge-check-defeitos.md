---
tipo: revisao-seguranca
contrato: 1
pedido: v0477
branch: melhoria/v0477-forge-check-defeitos
commit: 4603cde822b5484bbd5965327f10060e5c51abc9
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0477 (E1.3, VEREDITO-TROCADO-LENTO)

Primeira rodada, head 4603cde8, base 038249c5. Diff lido inteiro: `bin/forge-check` (só `veredito_trocado`), `tests/test_selo_e_entrega.py` (2 testes), `tests/mutantes/v0477-forge-check-defeitos.json`, fragmento do changelog.

## Gatilhos
Gatilhos: controle do Forge (`bin/forge-check`, conferência do anexo do portão, R-CONFORMIDADE).

## Análise
Pergunta: o filtro `git grep -l -F` (bin/forge-check:2807) pode deixar de fora uma versão que o código antigo marcaria como veredito trocado?
- **Superconjunto provado por construção.** O teste final continua `fm.get("commit") == revisado`, e `ler_frontmatter` (bin/forge-check:244) só faz `strip` do valor da linha `chave: valor`, sem aspas nem escape. Logo, toda versão que o código antigo marcava contém `revisado` (40 hex minúsculos, ancorado no `Revisar-sha:`) literal no blob; o `grep -F` de substring a acha. Sha abreviado, maiúsculo, entre aspas ou noutra forma já não casava a igualdade antes: o filtro não muda o resultado.
- **Renomeado e subpasta:** o grep roda sobre a árvore de cada versão (`de` e cada commit de `rev-list --full-history`), não sobre o diff; renomear não esconde a versão antiga (sonda S1 abaixo).
- **Binário e atributos:** `git grep -l` lista arquivo com NUL e com `binary` no `.gitattributes`; CRLF também (conferido em repositório de sonda).
- **Nomes com aspas do git** (não ASCII, tab): o grep sai `sha:"docs/…"` e o `ls-tree` sai `"docs/…"`, o par casa igual; o `git show` desse caminho falha e a versão fica de fora, igual ao código antigo (ver A1, preexistente, sem regressão).
- **Falha fechada:** código > 1 conta como trocado (bin/forge-check:2808); 1 é só "nenhum cita", que dá `False` correto (nenhuma versão poderia casar a igualdade). Timeout segue o `git()` comum (exceção sobe), como as outras chamadas.
- **Injeção de argumento:** `-e` antes do padrão e `--` antes da pasta; `revisado` é 40 hex validado na origem.
- Saída do grep e do `ls-tree` usam o mesmo nome de revisão (`de` como recebido, shas completos do `rev-list`), então o `f"{sha}:{versao}"` (bin/forge-check:2816) casa.

## Verificação
- `python3 -m unittest tests.test_selo_e_entrega.ParecerDoPortao`: 23 testes, OK (inclui A5, A7, A8 das voltas anteriores e os 2 novos).
- Mutantes M1 e M2 aplicados numa cópia (`git archive HEAD`): cada teste listado falha (mutante morto).
- `python3 -I tests/catraca.py --base origin/develop`: sai 1 só pelo R-CONFORMIDADE (mudança em `bin/forge-check` pede o rótulo `afrouxa-regra` do dono depois do último push); governança esperada, não defeito desta entrega.
- Sondas executadas (nenhuma prova bloqueante): S1 parecer `reprovado` com `commit:` entre aspas, depois sem aspas, depois renomeado para `docs/security/sub/y.md` e trocado para `aprovado` → `veredito_trocado(..., "aprovado")` = True; S3 `git grep` devolvendo 128 → True.
- Suíte inteira: só no CI do PR (não rodada aqui).

## Achados
- A1 (recomendado) bin/forge-check:2812 · Preexistente: versão de parecer com nome que o git cita entre aspas (não ASCII, tab) sai do ls-tree e do grep com aspas e o git show falha; fica fora. Sem caminho realista (o nome é do revisor). Correção: -z no ls-tree e no grep.

## Sondas

## Detalhe dos achados
A1 · evidência bin/forge-check:2812 e :2817 (o `git show` do caminho citado devolve 128, conferido) · caminho de ataque: esconder um `reprovado` exigiria que a versão do revisor tivesse nome citado pelo git; o nome é escolhido pelo revisor e a versão original segue na árvore do commit dele, então o autor não chega lá · severidade: informativa · correção mínima: `ls-tree -z` e `grep -z` (separar por NUL, com `nomes_z`) · esforço P · dono: o autor da E1.1, num pedido futuro; não bloqueia.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: só git e a biblioteca padrão; varredor de segredos e SAST ausentes no PATH (lacuna registrada; o diff não toca segredo nem configuração).
