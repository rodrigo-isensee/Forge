---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-g2-0-adr-status
commit: 36f0c14a5bc926bbc9a48b2839b29864202f4ed4
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0481 (E6.2, PR #872, ADR 0019 parecer como status do commit; classe T)

Diff revisado: `8d7914bc..36f0c14a` (ADR 0019 nova, linha no `docs/adr/README.md`, link na tabela do G2.0 do desenho, fragmento em `changelog.d/`). Classe pela ferramenta: `forge-check classe --base 8d7914bc` dá `classe: T`, `pareceres: review`. CI do head 36f0c14a no momento da leitura: catraca, `bateria (passos)`, `bateria (pareceres)`, `bateria (verificações longas)` e instalação verdes; partes da suíte ainda sem conclusão (o review não roda a suíte, R-REVIEW).

## Achados
- A1 (bloqueante) docs/adr/0019-parecer-como-status.md:87 · A evidência contradiz a tese: no #867 a base trazida deu `revalida: não` nos três, ou seja, a regra de hoje (domínio + merge simulado da ADR 0004) já mantém a aprovação; a releitura foi rodada de processo. Linhas 12, 20 e 90 dizem que a aprovação vence; corrija tese e medida.
- A2 (bloqueante) docs/adr/0019-parecer-como-status.md:91 · Medida sem instrumento: `forge-check metricas` só dá p50 (`bin/forge_governanca.py:616-620`), não P75; `relogios:` do `voltas` conta do primeiro movimento do cartão, não do primeiro commit; `revalidacoes` conta toda linha `revalid`, sem separar a causa base.
- A3 (recomendado) docs/adr/0019-parecer-como-status.md:63 · Só o G2.5 fica preso à D3 a); o desenho (seção 5, linha do G2.4) prende também o G2.4 a ela (espera o agregado `pareceres` na proteção). Alinhe os dois textos.

## Parecer
Reprovado, por dois defeitos na parte que o brief pede conferir (a medida), ambos de texto e baratos de corrigir.

O que está certo e não volta: a ADR segue o desenho (seção 3) no fluxo, na API, na lista fechada de contextos sem barra, no agregado, em quem grava e quem lê, na tabela de prova e auditoria e no que sai; os desvios do desenho (sha256 inteiro e origem em 40 hex, código confiável fora do `publicar`) estão declarados e apertam; a conta de 123 caracteres da descrição mais longa confere (123; a da herança tem 125, também abaixo de 140). A D3 do desenho fica como pendência do dono na seção 8, sem escolha nem aplicação, com a consequência de cada metade (sem b, o G2.1 não publica; sem a, o G2.5 não entra) e a distinção do D3 do pedido v0481. Critério de reversão, alternativas e "Por que o existente não basta" presentes (R-DECISAO); a ADR diz que não afrouxa sozinha, como o desenho (seção 6, linha G2.0). As referências conferidas batem: `ci.yml:614` (comentário do gate, "roda a suíte uma vez a mais"), `ci.yml:739` (job `pareceres`), `bin/forge-check:2495` (`PREFIXO_DE_PARECER`), `bin/forge-check:1828` (`exigidos_do_pr`), `bin/forge-fechar:138` (`--armar` recusado) e `:1001` (`mesclar_direto` com `--match-head-commit`), `hooks/parecer.py:17` (rascunho passa sem parecer).

A1 · linhas 12, 20, 87 e 90. O `parecer delta` imprime `revalida: não (não barrou e o domínio não mudou; o parecer segue valendo)` pelo mesmo veredito do `forge-check pr` (`revalida_do_parecer`, `bin/forge-check:3837`, META85 "uma fonte só"), e a `R-REVIEW` diz que commit fora do domínio não invalida o parecer. Os pareceres também ficam em `LIVRES`, então o commit de um parecer não vence o outro. Logo, no caso citado a aprovação não venceu: o que custou foi a rodada de portão disparada para ler o delta. O ganho real do G2 nesse ponto é a herança automática pela ferramenta (`parecer herdar` no passo 1 do `forge-fechar`) no lugar dessa rodada, além do head que não muda e do CI uma vez por head. Sugestão: trocar "a aprovação vence" por "o head novo dispara uma rodada de portão, mesmo com `revalida: não`", e redefinir a medida como "rodadas de portão por head novo com `revalida: não`" (ou "portões chamados por base trazida"), com o esperado zero depois do G2.3.

A2 · linha 91 (e a linha da tabela de Leituras). A meta do dono é mediana e P75 "do primeiro commit até a `develop`"; os instrumentos citados não dão nenhuma das duas coisas como estão: não há P75 no `metricas`, o `relogios:` mede `aberto_ate_develop` a partir do primeiro movimento do cartão (`bin/forge-check:58-61`) e o contador `revalidacoes` (`bin/forge_governanca.py:43`, regex `revalid`) não distingue a revalidação pela base da revalidação por mudança no domínio, que é o que a A1 pede medir. Sugestão: nomear o que já existe com o nome certo (p50 do `aberto_ate_develop`; execuções de CI por branch pelo `metricas --gh`) e declarar o que falta (P75 e a contagem por causa) como item do corte, com dono e etapa, ou como leitura manual descrita passo a passo na primeira linha de Leituras.

A3 · linha 63 contra a linha G2.4 da seção 5 do desenho ("G2.3; D3 (contexto na proteção)"). Sem efeito na decisão; vira cartão depois do merge se não for ajustado na volta.

Na volta, o review lê só o `forge-check parecer delta` deste parecer.
