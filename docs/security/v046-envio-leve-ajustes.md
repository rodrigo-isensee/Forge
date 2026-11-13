---
tipo: revisao-seguranca
contrato: 1
pedido: v046
branch: melhoria/envio-leve-ajustes
commit: 1beb0d5aee9f14ae6db5a1fd1b4053ddd581caaf
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-12
---
# Review de segurança: v046 (E19.6, ajustes do envio leve), revalidação por delta

Escopo: revalidação por delta, `git diff 55ea12e5..1beb0d5a` (1 commit: 1beb0d5a), 1 arquivo: `bin/forge-testes:139`. Parecer anterior aprovado em 73d0017a (trazido para a branch aqui); o merge da develop (55ea12e5) foi só texto e o restante da branch segue coberto por ele. Depois do 1beb0d5a a branch só recebeu os pareceres de review e QA (`docs/reviews/`, `docs/qa/`), sem código.

## Gatilhos
Mapa de seleção de testes do envio (`bin/forge-testes`), que decide quais provas do controle de segredo rodam quando `scripts/verificar-contribuicao.sh` muda. `R-SEGURANCA`, `R-VERIFY`.

## Achados
- A1 (recomendado) .githooks/pre-push:256 · sem refs/remotes/origin/develop a lista do diff fica vazia e as baratas não conferem nada (sintaxe, neutralidade, sentinela, changelog), sem aviso; só o segredo avisa. Mantido dos pareceres anteriores; o delta não o toca.

## Sondas
- S1 · `bin/forge-testes --listar scripts/verificar-contribuicao.sh` no head 1beb0d5a · espera: inclui test_pre_push_leve · obtido: inclui `test_pre_push_leve`
- S2 · mesma chamada com o `bin/forge-testes` de 55ea12e5 · espera: não inclui · obtido: 0 ocorrências de `pre_push_leve`

## Detalhe dos achados
**A1.** Inalterado (informativa, dono tech-lead, esforço P): em `caminhos_do_envio`, quando `base_dev` está vazio, imprimir `pre-push: aviso: sem refs/remotes/origin/develop; checagens baratas sem a lista do diff (o CI confere).`.

**Conferido sem achado no delta.**
- `bin/forge-testes:139`: só acrescenta `test_pre_push_leve` à tupla do padrão `scripts/(validar-plugin|configurar-ambiente-local|preparar-estacao|verificar-contribuicao)\.sh`; nenhum teste sai, a regex não muda, nenhum controle é afrouxado. Efeito de segurança positivo: mudar o script de varredura de segredo passa a rodar no envio a prova de que o envio leve ainda barra segredo (`tests/test_pre_push_leve.py:47` e `:109` leem e sobrescrevem o script). S1 e S2 provam a seleção nova.
- `tests.test_pre_push_leve` e `tests.test_testes_tocados` no head: 157 testes OK (1 skip pré-existente). Delta sem segredo nem caminho pessoal (leitura).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do delta, `bin/forge-testes --listar` no head e na base (S1, S2), testes dos arquivos tocados. `forge-check parecer delta` não se aplica (o parecer entra na branch neste commit); delta lido com `git diff 55ea12e5..1beb0d5a`. Ausentes no PATH (lacuna, não instaladas): varredor de segredos dedicado, SAST, auditoria de dependências e linters de workflow; o CI do PR cobre a varredura.
