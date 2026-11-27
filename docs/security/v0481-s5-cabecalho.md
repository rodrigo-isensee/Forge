---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-s5-cabecalho
commit: c8c2e1384d3811c4380f295b0a72f72d191c3951
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 E25.7 (S5, cabeçalho dos pareceres na autorização), volta 1

Revalidação por delta (`R-REVIEW`). Delta lido: `e0d63675..c8c2e138` (um commit, `c8c2e138`). Do `forge-check parecer delta` (`e216aa71..c8c2e138`), no domínio só `bin/forge_autorizacao.py` (+2 linhas, `:219-220`); as specs de mutante e o `tests/test_autorizacao.py` ficam fora do domínio e foram lidos só para fechar A1 e A2, que eram meus. A rodada anterior está no git (`e0d63675`).

Gatilhos: autenticação ou autorização (`frente` e `fora_do_revisado`, leitor do veredito dos pareceres na concessão).

## Achados anteriores
- A1 (bloqueante): resolvido. M18 (`tests/mutantes/v0479-pv-a2-concessao-3.json:19`) mira `if linhas[0] != "---":` e M27 (`v0479-pv-a2-concessao-4.json:29`) mira `if ": " in campo)`. `test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes` OK local; CI: suíte parte 4/5 verde em 3.12 e 3.14.
- A2 (bloqueante): resolvido. A guarda apagada `texto.startswith("---\n")` ganhou isenção em `tests/mutantes/v0481-s5-cabecalho.json` com motivo que confere (a mesma regra é `linhas[0] != "---"`, coberta por M1 e M18). Catraca verde no head (run 45885857531).
- A3 (recomendado): resolvido. `bin/forge_autorizacao.py:219`: arquivo achado pelo grep com `frente(...) == {}` devolve "Parecer sem cabeçalho legível" (falha fechada). O teste `ItemPresoAoCommit.test_parecer_sem_fecho_anterior_ao_commit_barra_em_vez_de_sumir` reproduz a minha sonda da rodada 1 (parecer reprovado velho, sem fecho, anterior ao Commit) e espera `inativa`; o M5 (`if False:`) morre nele.

## Aperta, neutro e afrouxa (o delta)
- Aperta: `:219`. Parecer sem fecho, com CRLF no topo, sem `---` na 1.ª linha ou sem nenhum campo `chave: valor` agora barra a concessão em vez de sumir da lista. Fecha também o CRLF, que a base já ignorava.
- Neutro: a checagem vem antes da pasta do tipo e do veredito; só muda a mensagem quando há mais de um motivo, o estado é `inativa` nos dois. As specs e a isenção não mudam comportamento.
- Afrouxa: nada. Efeito colateral de disponibilidade, só para o lado fechado: o grep é `-F "branch: <ramo>"` em todo `docs/{reviews,qa,security,devops}/`, inclusive `ameacas/`, `bugs/` e `aceites/`, e casa por substring (ramo prefixo de outro). Um texto sem frontmatter que cite `branch: <ramo>` em prosa barra a concessão desse ramo. Varri o head: 2 arquivos sem cabeçalho citam `branch: ` (`docs/qa/bugs/SBX-03-denywrite-sem-pareceres-e-claude-md.md`, `docs/security/ameacas/g2-parecer-status.md`), ambos seguidos de crase, que nenhum ramo tem; nenhum barra hoje. Sem ganho para um atacante (só nega a concessão, nunca a concede); fica registrado para quem receber "Parecer sem cabeçalho legível" sem parecer quebrado.

Provas locais (clone próprio no head): `tests.test_autorizacao` e a conferência de specs, 27 testes OK; `bin/forge-mutante tests/mutantes/v0481-s5-cabecalho.json`, M1 a M5 morrem (M4 por erro do teste sob o mutante, como na rodada 1). CI do head `c8c2e138` (run 45885735709 e a catraca 45885857531): as 10 partes da suíte, catraca, instalação, passos, verificações longas, teto de pulados e árvore provada verdes; `bateria (pareceres)` e o agregado `bateria` vermelhos só por `pareceres: failure` (review, QA e este ainda não aprovavam; processual).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: o diff do delta, o executor de mutantes do Forge, os testes tocados, os logs do CI e uma varredura local (biblioteca padrão) dos arquivos sem cabeçalho que o grep da concessão alcança. Sem segredo, dependência nem configuração no delta.
