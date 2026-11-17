---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-h4-atualiza-branch
commit: ea5c12c8e3c4cbcadbcc5cff62130ea0b0038cc1
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v047 (H4, forge-fechar traz a develop por merge)

Intervalo revisado: origin/develop (73a0ab81)..ea5c12c8 (`bin/forge-fechar`, testes e fragmento). Primeira rodada, sem delta anterior.

## Achados
- A1 (recomendado) bin/forge-fechar:767 · o merge-tree que agora vira commit enviado lê os atributos locais: um merge=union na worktree torna limpo um conflito e o fechamento envia conteúdo misto que ninguém viu; use a árvore vazia como fonte de atributos, como a juncao_limpa (bin/forge-check:2538)

## Sondas

## Gatilhos
Gatilhos: controle do Forge (forge-fechar: envio a branch remota, cadeia de pareceres, R-VERIFY, R-FLUXO).

## Verificado (sem achado)
- Sem forçar e sem pular o hook: o envio é `git push origin <sha>:refs/heads/<ref>` sem `--force`, `+` nem `--no-verify` (bin/forge-fechar:796); o pre-push roda como em qualquer envio; envio recusado (não fast-forward, corrida) para com `die`, sem PR.
- Só em `melhoria/*` e só na develop: o merge só nasce no `case melhoria/*` (bin/forge-fechar:821); a base só pode ser `origin/develop` (:165); `--ref` em main, master, develop, homolog ou na branch de integração do CLAUDE.md é recusado (:155) e o nome passa por `check-ref-format` (:163), o que barra `:`, `..` e espaço no refspec. Nenhum caminho escreve em develop, homolog ou main.
- Commit sem conteúdo à mão: a árvore é a do merge-tree limpo, validada como hash de 40 ou 64 hex (:784); os pais são o head conferido e a base lida do servidor (:785). A branch local anda por compare-and-swap (`update-ref` com o valor antigo, :793) ou por fast-forward na worktree só limpa (:790-791).
- Pareceres no head novo: a cadeia recomeça inteira (:798), com o passo 1 (`forge-check pr`) sobre o sha novo; o parecer só segue valendo se o head novo for o patch do parecer sobre a base nova (merge simulado de `commit_vale`, ADR 0004 item 3), o que é a política vigente; o CI (catraca, check exigido) refaz a conferência no servidor.
- Laço: `--trazida` limita a uma trazida por cadeia (:822; teste `test_h4_com_trazida_nao_traz_a_base_de_novo`); passar `--trazida` à mão só volta ao comportamento E8 (avisa e segue), sem afrouxar nada. A marca `FORGE_FECHAR_LOTE_PAI=$$` no recomeço só repete um `--item-de-lote` que o pai já aceitou; não dá esse modo a quem não o tinha.
- Teste novo rodado: `tests/test_fechar_base_andou.py`, 37 testes, OK (inclui envio recusado, worktree suja, falha de cada passo e conflito sem merge nem envio).

## Detalhe dos achados
A1. Evidência: `conflito_com` chama o merge-tree sem `--attr-source` (bin/forge-fechar:767), e o resultado limpo agora vira commit e envio (:785, :796). Na `juncao_limpa` o Forge já trata isso como ameaça (segurança A1, bin/forge-check:2528-2538). Sonda local (repositório descartável em `$TMPDIR`): com `f merge=union` nos atributos, um conflito real de `f` sai com rc 0 e a árvore junta as duas linhas (`RAMO` e `BASE`). Caminho: quem escreve na worktree onde o fechamento roda (um `.gitattributes` não commitado, ou um commitado na branch que passou no review como inofensivo) faz o passo 2b gerar e enviar uma mistura de dois lados conflitantes; o `forge-check pr` local repete o mesmo merge simulado com os mesmos atributos e pode aceitar os pareceres antigos. Barreira que resta: a catraca do CI (check exigido) refaz no servidor sem os atributos locais e recusa; por isso não bloqueia. Severidade: baixa. Correção mínima: em `conflito_com`, `git --attr-source=<árvore vazia> merge-tree ...` (a árvore vazia via `git hash-object -t tree /dev/null`), como na `juncao_limpa`; registrar que `.git/info/attributes` continua valendo mesmo assim (a sonda mostrou que a árvore vazia não o anula), coberto só pela catraca. Esforço: P. Dono: tech-lead (autor do `bin/forge-fechar`).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff e sonda passiva com git num repositório descartável; suíte inteira não rodada aqui (só no CI, a citar no PR); sem PR nem CI desta branch ainda (o brief pede sem PR).
