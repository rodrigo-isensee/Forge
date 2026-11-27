---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-f3-develop-no-fim
commit: fe299c72efb4b606ccda44423ac9a241d157c38e
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (E30.3, F3 develop só no fim, #924, 1ª rodada completa)

## Gatilhos
Gatilhos: controle do Forge (bin/forge-check: portão de entrega `pronto`; bin/forge-fechar: fechamento e merge), teste de controle (tests/test_fechar_forge_check_real.py), skill de processo (skills/trabalho-em-paralelo/ritmo-e-corte.md). Classe C (`forge-check classe`).

## Lido
`ee05ee84..fe299c72`, 8 arquivos: bin/forge-check:1241-1244, bin/forge-fechar:11 (comentário), docs/fechamento-integrador.md:22, skills/trabalho-em-paralelo/ritmo-e-corte.md:20-22, changelog.d, tests/test_forge_pronto.py (BaseVelha), tests/test_fechar_forge_check_real.py (DevelopSoNoFim), tests/mutantes/v0481-f3-develop-no-fim.json. Também, sem mudança no diff mas agora a garantia declarada do F3: `commit_vale`, `vindos_da_base` e `arquivos_divergentes` (bin/forge-check:736-955) e bin/forge_pronto.py:26-120.

## Achados
- A1 (bloqueante) skills/trabalho-em-paralelo/ritmo-e-corte.md:20 · o CI do head revisado está vermelho (suíte parte 3/5 nas duas versões, test_comando_pronto); o mesmo defeito do A1 do review. Sem CI verde não há parecer aprovado: corrija a citação e reenvie.
- A2 (bloqueante) bin/forge-check:941 · explorável: S2, S3, S4. Merge da base que desfaz o que a base trouxe (`-s ours`, ou conflito resolvido com o lado da branch) mantém o parecer: sem arquivo em `fora`, o `commit_vale` sai antes do merge simulado. O F3 declara o contrário (fechamento-integrador.md:22).

## Sondas
- S1 · sonda_merge_a_mao.py: merge da develop com byte à mão em bin/, README.md, tests/, docs/guia.md e com hooks/h voltado ao texto antigo · espera: código à mão desatualiza · obtido: bin/ desatualiza nos dois; hooks/h, tests/ e docs/ só no review; README.md em nenhum
- S2 · base muda só hooks/h; autor faz `git merge -s ours develop` depois do parecer; commit_vale(base=develop) · espera: desatualizado (review e segurança) · obtido: vale nos dois; a develop é ancestral do head e o PR desfaria o conserto
- S3 · branch e base mudam hooks/h (conflito) e a base muda c; conflito resolvido com `checkout --ours` · espera: desatualizado nos dois · obtido: review desatualizado; segurança vale
- S4 · fixture DevelopSoNoFim com `git merge -s ours develop` do autor e o forge-fechar real · espera: para no passo 1 · obtido: rc 0 e o merge por squash do PR no head sem o arquivo c da develop (develop ancestral do head), com os pareceres de review e QA do commit anterior

## Detalhe dos achados
**A1.** Evidência: run 45911883182 em fe299c72, `suíte (python 3.12, parte 3/5)` e `(python 3.14, parte 3/5)` em fail; reprodução no S1 do review. Não é defeito de segurança; bloqueia porque a aprovação exige o CI do head verde. Correção mínima: a do A1 do review. Esforço P. Dono: tech-lead (autor do E30.1).

**A2.** Evidência: bin/forge-check:930-942. `fora` é o `git diff --name-only <commit do parecer> <head>`; um arquivo que o merge da base deixa igual ao do commit do parecer (o conserto da base jogado fora) não aparece ali. Com o domínio de segurança, os outros arquivos da base saem como `vindos_da_base` (linha 935); `fora` fica vazio e a linha 941 devolve "vale" sem chegar ao `arquivos_divergentes` (linha 943), que é a única peça que veria a perda (o merge simulado traria o texto da base). Sem domínio (review e QA), o mesmo acontece quando a base só mudou arquivos que o merge descartou (S2: a árvore do head é igual à do parecer).
Caminho de ataque: o autor de uma `melhoria/*` (agente que erra ou que foi induzido por texto de entrada) mescla a develop depois dos pareceres com `-s ours` ou resolve um conflito "ficando com a minha versão" num arquivo de controle (hooks/, bin/). O `forge-check pr --base` diz que os pareceres valem, o passo 2b vê a base já no head e segue, e o merge por squash leva à develop a reversão de um conserto (inclusive de segurança) que nenhum revisor viu; a catraca do CI, se usa o mesmo `commit_vale`, também passa. É exatamente o caso que o F3 promete cobrir ("byte à mão no merge os desatualiza", docs/fechamento-integrador.md:22, ritmo-e-corte.md:21) e que passa a ser a guarda principal, porque as revisões agora acontecem contra a base velha.
Severidade: alta (contorno de portão de revisão para regressão em controle; exige ação do autor, sem acesso externo). O código não é deste diff, mas o diff passa a depender dele como garantia; sem a correção, o F3 afrouxa mais do que a ordem do dono descreve.
Correção mínima: no `commit_vale`, com `base` e com o head tendo trazido a base (o merge-base da base com o head diferente do merge-base dela com o commit do parecer), não sair na linha 941 com `fora` vazio: rodar o `arquivos_divergentes` e filtrar pelo domínio como já se faz na linha 945. Testes: S2 e S3 como casos de abuso (`-s ours` com a base que só muda um arquivo de controle; conflito resolvido com o lado da branch), cada um desatualizando review e segurança. Esforço P/M. Dono: tech-lead.

**Recomendação já levada pelo review (não repito como achado):** com o A2 corrigido, a frase "byte à mão no merge os desatualiza" vale só para arquivo `codigo` do domínio do parecer (A2 do review). O S1 mostra os limites: README.md (classe texto) não desatualiza nenhum parecer; tests/ e docs/ não normativos ficam fora do domínio da segurança e só o review os vê. É o EST-M4 e o PARECER-CONTEUDO de antes; a união dos pareceres cobre todo `codigo`.

## O que aperta, o neutro e o que afrouxa
**Aperta:**
- Testes novos fixam o 2b como merge com a árvore do `git merge-tree` e pais (head revisado, base do servidor), uma vez por cadeia (test_o_2b_traz_a_base_uma_vez_e_o_parecer_do_head_revisado_vale), e o byte a mais no merge desatualizando (test_merge_da_base_com_mudanca_a_mao_desatualiza_o_parecer). Mutantes F3-1 e F3-2 mortos (conferência do review).
- O texto da skill e do fechamento deixa o 2b como o caminho normal da base, sem resolução à mão.

**Neutro:**
- bin/forge-fechar:11: só comentário.
- bin/forge-check:1244, `base = ancora`: o sha vem do `git merge-base` (hex, sem injeção de opção) e vai em lista de argumentos ao `forge-testes` e ao `forge-changelog`; o diff `ancora..HEAD` é o mesmo do `base...HEAD`. O `pr-texto` da catraca já usava a âncora.
- A lógica de validade do parecer (`commit_vale`) não mudou; o A2 é anterior ao diff.

**Afrouxa (ordem do dono de 26/11 19:31, Fase 1, F3; PR com o rótulo `afrouxa-regra`):**
- O `pronto` deixa de reprovar a base velha (rc 1 vira aviso) e a conferência da entrega deixa de forçar a base antes das revisões. Efeito de segurança: review, QA e segurança passam a ver a branch contra a base velha; a combinação com a base nova só é vista pelo merge simulado (A2) e pelo CI do head com a base (o 2b recomeça a cadeia, o 1c e os checks do passo 4 rodam no head novo). A quebra semântica sem conflito, risco aceito na E8 da 0.45.6, fica mais provável, porque a distância entre a base revisada e a de entrada cresce. Dentro do que o dono decidiu; o A2 é o que passa do decidido.
- docs/regras/R-FLUXO.md:26 ainda lista "base velha" como exceção para trazer a base antes (A3 do review); hoje só deixa o texto mais permissivo que a ferramenta, sem efeito de segurança.

## Resposta à pergunta do brief
Um merge da base com mudança à mão pode passar como limpo e manter um parecer velho? Byte **acrescentado** em código do domínio, não (S1, teste do item). Byte **retirado** do que a base trouxe, sim: `-s ours` e conflito resolvido com o lado da branch mantêm o parecer de segurança e, quando a base só mudou o que foi descartado, também o de review (S2, S3, S4). É o A2.

## Conferência
- CI: run 45911883182 em fe299c72 vermelho (A1). O head atual 181435bb (só o parecer do review) está com a suíte pendente e `bateria (pareceres)` em fail.
- Testes do item: rodados pelo review (6 OK); as sondas S1 a S4 rodaram nesta cópia em fe299c72, com a trava de teste no S4 (fixture DevelopSoNoFim, 1 teste OK).

## Riscos aceitos e ferramentas
Riscos aceitos: a quebra semântica sem conflito depois do merge (E8 da 0.45.6) e o afrouxamento do F3 (ordem do dono de 26/11 19:31). Nenhum risco novo aceito neste parecer. Ferramentas: leitura estática, git e as sondas em Python (biblioteca padrão) sobre repositórios temporários; nada instalado.
