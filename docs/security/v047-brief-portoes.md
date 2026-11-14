---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-brief-portoes
commit: cc0cf87618c960ef64319823f29e32910f861067
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: v047 (desenho do BRIEF-NAO-SEGURA-VAGAS)

Intervalo `origin/develop..cc0cf876`: `docs/propostas/brief-portoes-por-ferramenta.md` (desenho, sem código) e o fragmento `changelog.d/v047-brief-portoes.md`. Parecer sobre o desenho, antes da implementação (etapa E1.227), contra as ameaças T1 a T7 da seção 8 e a opção 3.3b. O desenho conferido contra o código da `develop` no mesmo clone: `bin/forge-check`, `hooks/conformidade.py`, `hooks/conformidade.json`, `hooks/agentes.py`.

## Gatilhos
`R-SEGURANCA`: o desenho cria um subcomando que grava no pedido (`## Etapas` e o selo no `## Histórico`) e em `docs/briefs/`, muda o significado do selo que o hook `agentes` cobra e mexe nas guardas de `hooks/` (Z10, registro do brief). Classe C quando implementado (`bin/`, `hooks/`). Sem código nesta entrega: não há suíte a rodar; o parecer é de desenho.

## Achados
- A1 (bloqueante) docs/propostas/brief-portoes-por-ferramenta.md:32 · `brief portoes` grava por padrão (pedido e docs/briefs), mas o hook só vê escrita do `brief` com `selar` ou `--gravar`; qualquer papel, inclusive os só de leitura, gravaria no pedido do jarvis. O desenho precisa pôr o subcomando no hook.
- A2 (recomendado) docs/propostas/brief-portoes-por-ferramenta.md:76 · Opção 3.3b aceita com condições: id da etapa calculado dentro da trava (ler, numerar e gravar sob o mesmo lock), linha conferida por expressão fechada antes de gravar, todas as etapas gravadas antes de gerar os briefs.
- A3 (recomendado) docs/propostas/brief-portoes-por-ferramenta.md:84 · Selo de reprodução: o gerador usa origin/B e o `selar` de hoje calcula Revisar-sha e head pela branch local; uma só fonte do head nos dois, e conteúdo que depende de rede (linha do CI pelo gh) fora do que se reproduz.
- A4 (recomendado) docs/propostas/brief-portoes-por-ferramenta.md:25 · `ETAPAS_DE_PARECER` existe em três cópias (bin/forge-check:2216 e 8261, hooks/agentes.py:574); somar `devops` numa só abre Z10 diferente no hook e no gerador. Uma fonte, e o brief de devops limitado a gravar docs/devops/.
- A5 (recomendado) docs/propostas/brief-portoes-por-ferramenta.md:35 · T7: comparar o local com `origin/B` sem buscar o remoto aceita dois refs igualmente velhos; conferir o head pelo remoto de agora (ls-remote) antes de gerar, recusando se diverge.
- A6 (recomendado) docs/propostas/brief-portoes-por-ferramenta.md:70 · Faixa no Fora do escopo: "buraco reprova" quebra pedido real com id faltando (o próprio v047 não tem E1.102); a regra segura é a expansão igual aos ids do pedido menos o `Cobre:`, e a faixa nunca contém o `Cobre:`.

## Sondas
- S1 · `grava_no_pedido(livres_do_forge_check(a), a)` e o teste de `--gravar` do hooks/conformidade.py com a = `brief portoes --pedido v047 --branch melhoria/x` · espera: escrita no pedido ou em docs/briefs reconhecida · obtido: grava_no_pedido=False escrita_brief=False

## Detalhe dos achados

**A1 (alta, bloqueante).** Evidência: o desenho define `forge-check brief portoes` gravando por padrão (seção 3, linha 32; só `--so-mostrar` não grava, linha 48), gravando a etapa em `## Etapas` (3.3b, linha 76) e o selo no `## Histórico` (seção 4). O hook `conformidade` decide se uma linha do `forge-check` grava por `grava_no_pedido` (`hooks/conformidade.py:669`, só `brief selar` e `entrega --pedido`) e, para `docs/briefs/`, por `FORGE_CHECK_ESCRITAS` com `--gravar` (`hooks/conformidade.py:480` e `:1601`). A sonda S1 mostra que a forma desenhada não é vista como escrita. Além disso, a lista dos papéis só de leitura (`hooks/conformidade.json:111`) libera `forge-check brief` inteiro. Caminho de ataque: um agente de autor ou um papel só de leitura (`conferente`, `leitura`) roda `forge-check brief portoes` e grava em `docs/pedidos/` e `docs/briefs/`, que são só do `jarvis` (`hooks/conformidade.json:56-64`, VV-2, `R-DECISAO`): acrescenta etapas ao pedido, sela briefs e muda o `## Histórico` que o hook `agentes` e o `forge-check entrega` leem. O texto do brief é fixo, então o ganho não é injeção, mas quebra da fronteira de quem escreve o pedido. Correção mínima no desenho (seção 10, parte 3, no mesmo PR do subcomando): (1) `grava_no_pedido` devolve True para `brief portoes` sem `--so-mostrar`, e para `entrega --portoes`; (2) a regra do hook para o `brief` passa a ser falha fechada: todo subcomando do `brief` grava, menos uma lista fechada dos que só leem (`brief fila`, `brief portoes --so-mostrar`, `brief` sem subcomando de checagem); (3) teste do hook com as formas abreviadas (`--so`, `--so-m`) e com o papel `conferente`. Esforço P. Dono: autor do subcomando (`tech-lead`), com o corpus do hook `conformidade`.

**A2 (opção 3.3b, T4).** Parecer sobre a pergunta do desenho: a 3.3b é aceitável, porque o texto é fixo e só leva valores calculados, desde que A1 restrinja quem roda o subcomando ao `jarvis` (então a escrita no pedido continua do papel dono). Condições: o id `E<n>.<m>` é calculado dentro da mesma trava exclusiva que grava a linha (`gravar_no_historico`, `bin/forge-check:8510`, faz só o acréscimo; a numeração lida antes da trava corre com outra execução de outra branch e repete id); a linha passa por expressão fechada (`- E\d+\.\d+ \(<papel da tabela>\): \[branch <nome_seguro>\] parecer de <tipo> no código [0-9a-f]{12} \(gerado\)`) antes da gravação; com vários portões na mesma execução, todas as etapas entram antes de gerar o primeiro brief, para o `Fora do escopo` de cada um já listar as irmãs. Severidade baixa. Dono: `tech-lead`.

**A3 (T3).** O selo deixa de provar leitura humana e passa a provar reprodução; isso está coberto pela ordem do dono de 14/11 15:53 ("O selo continua obrigatório", geração por ferramenta). O risco que fica é de disponibilidade, não de segurança: `corrigir_revisar_sha` (`bin/forge-check:8663`) e `corrigir_derivados` usam a branch local, e o desenho usa `origin/B`; a linha do CI (`linha_do_ci_do_parecer`) depende do `gh` e muda quando o PR nasce. Reprodução não determinística falha fechada (não sela), sem furo, mas devolve a vaga ao Jarvis. Correção: uma só função para o head nos dois lados e o trecho de rede fora dos bytes reproduzidos (ou calculado uma vez e gravado). Baixa. Dono: `tech-lead`.

**A4 (Z10).** `ETAPAS_DE_PARECER` em `bin/forge-check:2216`, `bin/forge-check:8261` e `hooks/agentes.py:574`. A etapa entra na lista de quem não escreve a branch (Z10). Somar `devops` só no gerador faz o hook tratar o brief de devops como escrita (fila travada); somar só no hook isenta da trava um papel que pode gravar workflow e infra. Hoje o brief de devops já sai com `Etapa: review` (isento), então não é furo novo, mas a parte 2 da seção 10 deve: uma fonte só para a lista (o hook já importa o `forge-check`), o Entregar do portão de devops limitado a `docs/devops/<pedido>.md`, e teste de que as três leituras batem. Baixa. Dono: `tech-lead`, com o `devops-engineer` no texto do portão.

**A5 (T7).** O desenho recusa se o local difere de `origin/B`, mas os dois podem estar velhos sem `git fetch`. O efeito é brief e parecer sobre código antigo; o `forge-check pr` aponta o delta depois (falha fechada no fim), então é custo de uma rodada, não furo. Correção: `git ls-remote origin refs/heads/B` igual a `origin/B` antes de gerar, recusando se diverge, sem rede caindo em recusa. Baixa. Dono: `tech-lead`.

**A6 (3.2).** A expansão de faixa contra `## Etapas` precisa de semântica exata: o conjunto expandido é o conjunto dos ids do pedido menos o `Cobre:` (nem mais, nem menos); id da faixa que não existe é ignorado só se o pedido realmente não o tem, e a faixa que engloba o `Cobre:` reprova (senão a etapa delegada pode sumir para "fora do escopo"). Também: a mudança de texto de `R-BRIEF` exige destaque no título do PR (`invariantes`), como o desenho já diz. Baixa. Dono: `tech-lead`.

**Sem achado nas demais ameaças.**
- T1: modelo fixo no código, revisado em PR de classe C, versão `MODELO_PORTOES`, teste de ouro; aceitável.
- T2: só a linha da etapa coberta entra, entre aspas, por `sem_controle` (`bin/forge-check:2790`) e `caractere_disfarcado` (`bin/forge-check:7831`); valores pelo `NOME_SEGURO_DE_BRIEF` (`bin/forge-check:8427`) e `interpolacao_segura` (`bin/forge-check:8133`, com `git check-ref-format` para a branch). O agente já lê o pedido hoje; sem ganho para o atacante.
- T5: pré-condição de `entrega conferida` no mesmo sha, fila sem o vencido e o `forge-check pr` pelo delta; o portão sobre código que andou falha fechado.
- T6: classe só sobe, catraca que não carrega dá C (`catraca_da_classe`, `bin/forge-check:972`); aceitável.
- Fila (seção 5): só leitura, não lança agente; o hook `agentes` continua cobrando selo, teto e Z10. Perder o `agentes.json` gera parecer duplicado, custo e não furo.

Revalidação: a volta só precisa acrescentar ao desenho a correção de A1 (e, de preferência, as condições de A2); a releitura vai pelo `forge-check parecer delta` deste parecer.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do desenho e do código da `develop` no clone, e a sonda S1 sobre as funções do hook `conformidade` (só leitura, sem gravar nada). Sem varredura de segredo nem de dependência: a entrega é só texto, sem dependência nova.
