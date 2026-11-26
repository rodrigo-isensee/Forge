---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-g2-mitigacoes
commit: d1c2d815f94d240bd5962a056824e8f81cdaa4a7
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 E26.3 (#919, 1º corte das mitigações do G2: M18.1, 1ª rodada completa)

## Gatilhos
Gatilhos: controle do Forge (`pr_aberto` e `repositorio_do_remoto` em `bin/forge_pareceres.py`, arquivo protegido, chamados pelo portão `forge-check parecer publicar`)

- ci: d1c2d815f94d240bd5962a056824e8f81cdaa4a7 verde

## Escopo lido
`git diff 707fea56..d1c2d815`: `bin/forge_pareceres.py:14-15,48-75`, `tests/test_forge_pareceres.py` (fixture com `origin` e a classe `RemotoDoPr`), `tests/mutantes/v0481-g2-mitigacoes.json` (M50 a M53) e o fragmento do changelog. Também li o chamador `cmd_parecer_publicar` e `recusa_do_publicar` (`bin/forge-check:3886-3932`), o resto de `publicar` (`bin/forge_pareceres.py:78-124`) e T18, M18.1 e C23 em `docs/security/ameacas/g2-parecer-status.md:75,123,154`.

## Mitigações do modelo de ameaças
- **M18.1** (T18): cumprida neste corte. O `origin` da cópia vira (host, dono, repo) por `fullmatch` (`bin/forge_pareceres.py:54-57`). Sem `origin` ou com forma não lida, recusa. O PR achado pelo `gh` tem de ter `isCrossRepository` igual a `False` (`:70`; ausente ou `None` também recusa) e URL do mesmo repositório (`:72-73`). Tudo isso roda antes de qualquer POST. A parte "o PR é da `branch:` do texto" já vinha da base: `--head` com o `branch:` do frontmatter (`bin/forge-check:3925`), mais o `headRefName` exato (`:65`). Agora fecha também o fork com o mesmo nome de branch, que o `--head` sozinho deixava passar. Provas: `test_c23_remoto_diferente_do_pr` (o teste citado no modelo), `test_c23_pr_de_fork_com_a_mesma_branch`, `test_c23_pr_de_outro_repositorio_com_o_mesmo_dono`, `test_c23_sem_origin_ou_origin_fora_das_formas` e `test_formas_do_remoto_que_valem`, que é o corpus de legítimos.

## Achados
- A1 (recomendado) bin/forge_pareceres.py:14 · `REMOTO` aceita `http://` (`https?`), mas a docstring (:49), a recusa (:56) e a M18.1 do brief dizem "https ou ssh"; tire o `?` e ponha `http://github.com/dono/repo.git` no corpus de recusa do teste
- A2 (recomendado) bin/forge_pareceres.py:73 · a M18.1 confere a URL do PR, mas os POST (:80, :108) usam `{owner}/{repo}`, que o `gh` resolve de novo a cada chamada; monte os caminhos com o (dono, repo) já conferido, para que a escrita vá ao repositório que a M18.1 provou

## Sondas

## Detalhe dos achados
**A1.** Evidência: `bin/forge_pareceres.py:14`. A sonda no scratchpad, com o `REMOTO` do head, dá `http://github.com/dono/repo.git -> ('github.com', 'dono', 'repo')`. Não há caminho de ataque: a forma do `origin` não muda o repositório onde se grava, e a comparação com a URL do PR continua valendo. É divergência entre o código e o requisito escrito. Severidade baixa. Correção mínima: `https://` no lugar de `https?://` e o caso `http://` em `test_c23_sem_origin_ou_origin_fora_das_formas`. Esforço P. Dono: o autor do #919 (E26.1).

**A2.** Evidência: `bin/forge_pareceres.py:72-73`. A tupla conferida é descartada, e `:80`, `:87`, `:108` e `:111` seguem com `repos/{owner}/{repo}`. O `gh api` resolve esse marcador pelo `GH_REPO` ou pelos remotos do diretório, como diz `gh api --help`, a cada chamada e sem o `-R` do `pr list`. Hoje o `GH_REPO` vale igual para os dois. Os remotos também, salvo diferença na escolha do remoto base entre o `pr list` e o `api` quando a cópia tem vários remotos e um `gh repo set-default`, que não provei. A checagem do `html_url` do comentário (`:114`) já impede o status em outro repositório. O que sobra é o comentário gravado num issue de mesmo número no outro repositório antes da recusa. Severidade baixa. Correção mínima: `pr_aberto` devolve o (dono, repo) conferido, e `publicar`, `gravar_status` e `agregado` usam `repos/<dono>/<repo>/...` literal, com `--hostname <host>` quando o host não é o padrão. Um teste com o `gh` falso confere que todos os POST levam o dono e o repo do `origin`. Esforço P. Dono: o autor do #919 (E26.1).

**O que aperta:**
- A sessão de projeto com `GH_REPO` no Forge, ou a cópia cujo `origin` é outro repositório, não publica mais no PR do Forge. A recusa vem antes de qualquer gravação.
- O PR de fork (`isCrossRepository` verdadeiro, ausente ou `None`) com o mesmo nome de branch é recusado. Antes, o `--head` casava só pelo nome.
- A cópia sem `origin` ou com `origin` local, `file://`, `ext::`, `git+ssh://` ou caminho extra é recusada. O `fullmatch` impede que um trecho do tipo `...x@github.com:dono/repo` dentro de outra URL case (M53 prova).
- As mensagens não ecoam a URL do `origin`. A forma com credencial (`https://x-access-token:...@`), aceita no corpus, não vaza na recusa.

**O que é neutro:**
- A comparação usa minúsculas, o que bate com o GitHub. A fixture `GhFalso` ganha o `origin` e o `isCrossRepository: False`, e os testes da base continuam passando: 40 OK em `tests.test_forge_pareceres`.
- O `git remote get-url` herda o ambiente, como o `gh`, que também lê os remotos. Os dois veem a mesma cópia.
- Algumas formas legítimas falham fechado. São elas: host apelido do ssh (`git@github-trabalho:...`, o host não bate com o da URL do PR), ssh com porta (`ssh://git@github.com:22/...`) e scp sem usuário (`github.com:dono/repo`). O custo é uma recusa com mensagem clara, não uma abertura. Se algum agente usar essas formas, vira cartão.

**O que afrouxa:** nada. Nenhuma checagem da base sai e nenhuma condição fica mais fraca. Também não há entrada que a base recusava e o head aceite. Mexer em `bin/forge_pareceres.py`, arquivo protegido, pede o rótulo `afrouxa-regra`, que é decisão do dono. A `catraca` está vermelha só por isso.

**Lacuna que fica (T18 [B], como o modelo já registra):** a M18.1 pega o desvio por engano, mas não uma sessão determinada. Quem publica de um clone do Forge, ou troca o `origin`, passa, porque o token é o mesmo. Isso fecha só com o G4, passo 4. O PR não muda nada aqui.

**Mutantes:** `bin/forge-mutante tests/mutantes/v0481-g2-mitigacoes.json` no head: M50, M51, M52 e M53 morrem.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodei `python3 -m unittest tests.test_forge_pareceres` (40 OK no head), os mutantes acima e a sonda do `REMOTO` com 14 formas de URL (scratchpad, fora do repositório). O CI do head `d1c2d815` está verde nas suítes, nas verificações longas e na instalação. Estão vermelhos só `bateria (pareceres)` (faltam os pareceres), `bateria` (que agrega o anterior) e `catraca` (falta o rótulo), os três fora da linha do CI. Usei o `gh` só para ler checks e logs. Não usei gitleaks nem osv-scanner, porque o diff não traz segredo nem dependência.
