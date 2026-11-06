---
tipo: revisao-seguranca
contrato: 1
pedido: versao-034
branch: melhoria/lote-estoque-a
commit: 9e7d397ebe03ea3fc5c32cc8759ae32017e6e1fd
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-05
---
# Review de segurança: lote-estoque-a

Junção do lote A do E7 (ESTOQUE-PRONTO), etapa E2.3 pela decisão técnica do Histórico de 2026-11-05 22:29. Intervalo lido: d9b26bb..9e7d397 (11 merges na linha principal e 9 commits que não são de junção nela, pela contagem de `git log --first-parent --no-merges`: f99351a, 4b24838, a039ced, 47cd72c, c32d320, c565e9d, 8ea4c84, 432d18a e 9e7d397). Cada item já tem os próprios pareceres; aqui se lê o que a soma dos itens, as resoluções de conflito e a volta da E2.1 (f99351a a 9e7d397) mudam nos controles do Forge.

## Gatilhos
Controles do Forge (R-SEGURANCA): texto de regra (docs/regras/R-DECISAO.md, docs/regras/R-FLUXO.md), agentes e skills que regem portões, modelos de parecer (docs/security, templates/projeto/docs/*/_modelo.md), invariante em tests/config.json, script de fechamento (bin/forge-fechar) e o mapa do forge-testes (bin/forge-testes). Sem CI, hooks nem dependência neste lote.

Linha por item que toca a área:
- achado-teto-doc: textos de agentes e modelos sobre o limite do achado; só aperta (o limite segue barrado no pre-push e no forge-check docs).
- invariante-gatilho: etapa de segurança já no modelo de pedido, inclusive para invariante novo em tests/config.json; aperta.
- modelos-parecer-avisos-2: avisos nos modelos de parecer; sem efeito em portão.
- pergunta-maior-menor: troca texto de docs/regras/R-DECISAO.md:11: o ";" que fechava o parêntese da fonte do número vira "," e entra o critério de dizer se o custo da opção fica maior ou menor que o das outras; nada do texto anterior sai nem muda de sentido, então é só acréscimo de exigência. Vem com invariante novo em tests/config.json (só uma linha a mais; nenhum item sai); aperta.
- permissao-agentes-md: skills/trabalho-em-paralelo/SKILL.md:15; o aviso ao dono só cai quando a regra de permissão já existe; o agente recusado segue parando sem contornar (R-CONFORMIDADE). Não afrouxa controle.
- textos-034: textos de agentes; a resolução de conflito ficou com a redação refinada dos itens irmãos, sem perder trecho de controle.
- aq1-texto-v2 e aq3-texto-v2: agile-coach passa a mandar mudança de agente, skill, script ou teste do Forge ao tech-lead; arquiteto lista gatilhos_seguranca no frontmatter (agents/software-architect.md:20) e classifica afrouxamento; ux veda URL externa no protótipo. Apertam.
- pareceres-033: pareceres dos itens da 0.33; sem efeito em controle.
- conferente-leitura-git (b3d6067 e 602e04f, fora da linha principal, entram pelo merge 42b1741 do pareceres-033): só testes, parecer de QA, parecer de segurança e a lista de mutantes tests/mutantes/versao-033-qa.json; nenhum arquivo de hooks/ muda. tests/test_guarda_conferente.py:152 acrescenta casos de abuso que exigem recusa (encadeamento, substituição, redirecionamento, `-c`, `--git-dir`, `--work-tree`, worktree lock/move/repair e mudança de upstream) à guarda de leitura de git do conferente. Toca controle do Forge só pelo lado do teste, e aperta: prende o comportamento da guarda.
- f22-release-v2: R-FLUXO ganha o passo a passo do PR de release (docs/regras/R-FLUXO.md:15): lista antes de criar, recusa fork, base diferente e autor inesperado, corpo por arquivo, sem mesclar a main (R-MAIN). Aperta.
- fechar-esperar-rotulo: bin/forge-fechar:816-830 só separa a mensagem pelo gatilho (título ou item marcado); a condição de parada e o die são os mesmos; nenhum comando aplica rótulo.

Volta da E2.1: 4b24838 junta os fragmentos de changelog e a039ced e 47cd72c são o parecer de review; nenhum dos três toca controle. c32d320 põe no mapa (bin/forge-testes:111 e :115) os testes que leem os modelos de parecer, então mudança nesses modelos passa a rodar mais testes, não menos; c565e9d e 8ea4c84 só trocam a citação da regra pelo ID, sem mexer em commit nem veredito dos pareceres; 432d18a deixa o modelo de segurança da raiz e do template iguais; 9e7d397 só dá peso a 20 módulos em tests/pesos-d4.json, que reparte a carga da suíte e não tira módulo dela; f99351a troca uma asserção pela redação refinada, e a parte de controle (não contornar) segue presa em tests/test_textos_034.py:53 e tests/test_permissao_agentes_md.py:17.

## Achados

## Detalhe dos achados
Sem achados. Nenhuma linha do intervalo tira texto de docs/regras/ nem item de tests/config.json. A única troca de texto de regra é a de docs/regras/R-DECISAO.md:11 (pontuação e critério novo de custo, PERGUNTA-MAIOR-MENOR), julgada acima como acréscimo de exigência; R-FLUXO só ganha linha. As duas resoluções de conflito (3b2fb5c em tests/test_forge.py, 7759b69 em agents/qa-engineer.md, skills/modo-iniciante, skills/trabalho-em-paralelo e o modelo de pedido) não deixam marcador de conflito e ficam com a versão mais recente do item dono do texto. Nota fora da área de segurança, já com o review: o template templates/projeto/docs/security/_modelo.md:22 passa a citar o Forge (R-NEUTRO).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes dos arquivos tocados (test_textos_034, test_permissao_agentes_md, test_modelos_parecer_avisos_2, test_invariante_gatilho, test_pergunta_maior_menor, test_aq1_texto, test_achado_teto_doc, test_fechar): 110 testes, OK. O linter de shell em bin/forge-fechar: sem aviso. A suíte inteira fica com o QA (D-5). Faltaram no ambiente o varredor de segredos, o SAST, os verificadores de workflow e o auditor de dependências; o lote não toca workflow nem dependência, e o diff lido não traz credencial.
