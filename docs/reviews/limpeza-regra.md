---
tipo: review
contrato: 1
pedido: limpeza-regra
branch: melhoria/limpeza-regra
commit: e4616591cabfba0388b7c6db9d716728fbd7ec30
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-23
---
# Review: limpeza-regra

## Achados
- A3 (recomendado) docs/regras/R-FLUXO.md:18 · classe: lista residual menor que a da exceção · a frase "Nunca apague `develop`, `homolog` nem `main`" continua sem `master` e sem a branch de integração do projeto; não contradiz (a lista completa está no mesmo parágrafo), mas é a lista antiga repetida; unificar numa próxima mexida
- A4 (recomendado) agents/jarvis.md:72 · classe: lista residual menor que a da exceção · mesmo caso do A3 ("nunca `develop`, `homolog` nem `main`" antes da lista completa)
- A5 (recomendado) docs/fechamento-integrador.md:20 · classe: condição da branch local · o script também apaga a branch local cujo head "já estiver na base", caso que a `R-FLUXO` (passo 2) não lista; é mais seguro que perigoso (nada se perde), mas os dois textos não dizem exatamente o mesmo

## Parecer
Achados anteriores: A1 (bloqueante, `docs/retomada-de-sessao.md:285`) resolvido, a tabela agora traz a exceção da `R-VERIFY` com o recorte da branch de trabalho e a lista das branches que nunca entram. A2 (recomendado, `docs/propostas/retomada-de-sessao.md:185`) resolvido, com a nota datada em `:187` que diz que a regra mudou e que vale a `R-VERIFY`.

Aprovado. Revalidação por delta: `forge-check delta --parecer docs/reviews/limpeza-regra.md` listou o intervalo `15dab75..e461659` (o mesmo conteúdo de `d1e45a6..e461659` do pedido; `15dab75..d1e45a6` só trazia os pareceres de review e de segurança), 8 arquivos e uma linha cada: `agents/jarvis.md:72`, `agents/tech-lead.md:29`, `changelog.d/limpeza-regra.md:2`, `docs/fechamento-integrador.md:20`, `docs/propostas/retomada-de-sessao.md:187-188`, `docs/regras/R-FLUXO.md:18` e `:24`, `docs/regras/R-VERIFY.md:13`, `docs/retomada-de-sessao.md:285`. Li só essas linhas; o resto da branch ficou como "já lido" na rodada anterior (commit `15dab75`).

Os cinco lugares conferidos dizem o mesmo:
- Exceção só para branch de trabalho, nunca `main`, `master`, `develop`, `homolog` nem a integração do projeto (decisão "A" do dono): `R-VERIFY:13`, `R-FLUXO:18` e `:24` (com os prefixos e o `--delete-branch` sob a mesma restrição), `jarvis.md:72` e `tech-lead.md:29`. Fecha o A1 da segurança.
- Head local igual ao `headRefOid` para apagar a branch local sem confirmação, commit local a mais pede confirmação: `R-FLUXO:18` (passo 2), `jarvis.md:72`, `tech-lead.md:29` e `fechamento-integrador.md:20`. Fecha o A2 da segurança. A `R-VERIFY` fala só da branch já enviada (head remoto), o que está certo: commit não enviado é da `R-FLUXO`.
- Nenhum dos cinco repete a regra antiga sem a exceção (`grep` por "antes de apagar ou reescrever" e "sem nova confirmação": só a `R-VERIFY` com a exceção e a proposta com a nota datada). `bin/forge-fechar:56` já recusa `main`, `develop` e `homolog` como ref; sem `master`, que o Forge não tem.
- Fragmento `changelog.d/limpeza-regra.md` atualizado com o recorte. O PR precisa do rótulo `afrouxa-regra` do dono e do destaque no título (pedido LIMPEZA-REGRA-PR).

Regras "ferramenta": a suíte roda no pre-push deste envio; nada refeito aqui. Segurança: parecer próprio em `docs/security/limpeza-regra.md`, revalidação a cargo do `security-engineer`.
