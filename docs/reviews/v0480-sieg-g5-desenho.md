---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-sieg-g5-desenho
commit: acf0b227882000b1fe351077f327f3d7d3448e54
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 · desenho do SIEG-G5 (decisão ao dono em formato fixo), etapa E135.4

Revisão completa, única, do PR #818 no head acf0b227 (base develop 0e59c446). Diff: `docs/propostas/sieg-g5-decisao-formato-fixo.md` (88 linhas) e `changelog.d/v0480-sieg-g5-desenho.md`. Só texto: sem código, guarda nem mutante; sem suíte local (o CI do PR a roda).

## Achados
- A1 (bloqueante) docs/propostas/sieg-g5-decisao-formato-fixo.md:47 · "não há hook novo nem trava nova" é falso: F1 a F4 e F6 são cinco recusas novas com rc 2 no anotar, uma trava de processo. A regra 3 do dono (21/11 20:54) pede que saia ou se simplifique outra: nomeie qual ou declare trava nova e leve ao dono.
- A2 (bloqueante) docs/propostas/sieg-g5-decisao-formato-fixo.md:85 · a reversão pela taxa `violacoes` não mede o formato novo: `grupos_de_opcoes` só vê opções A a F maiúsculas (bin/forge_transcricao.py:255), não `1a)` (S1); depois do C1 a taxa cai por construção. Meça C0 e reversão com a mesma régua (ex.: `sem_codigo` do C3).
- A3 (recomendado) docs/propostas/sieg-g5-decisao-formato-fixo.md:39 · F6 diz "num lugar só" sem dizer como: `TETO_DA_MENSAGEM` vive em hooks/meta.py:40 e a recusa em bin/forge_dono.py; o oráculo do C1 (linhas 66 e 79) passa com o 1200 duplicado. Diga quem importa de quem e ponha um teste de identidade.
- A4 (recomendado) docs/propostas/sieg-g5-decisao-formato-fixo.md:67 · o pronto do C2 (`tests/test_clareza.py` verde) passa sem a frase nova; cite a frase exata e o arquivo:linha onde ela deve aparecer.

## Sondas
- S1 · `grupos_de_opcoes("Qual caminho?\n1a) manter [reversível]\n1b) cortar [irreversível]\n")` de bin/forge_transcricao.py no head, python3 -I · espera: um grupo visto · obtido: [] (com `A)`/`B)` no mesmo texto: [(1, False)])

## Leitura
- Provas arquivo:linha conferidas no head, todas batem: `skills/modo-iniciante/SKILL.md:31-38`, `skills/falar-com-o-dono/SKILL.md:10`, `resposta-curta.md:7`, `bin/forge_dono.py:97-137`, `:125-126` (duas opções da mesma questão), `:128-134`, `:198-208` (`recusa_de_corte`), `:316-330` (`cmd_resposta`), `bin/forge-check:5278` (a linha `if tipo == "pergunta"` com a E6), `:5254-5257` (`recusa_do_campo` e `recusa_da_forja`), `:10572` (`--resposta`), `hooks/meta.py:10` e `:40`, `bin/forge_transcricao.py:278-342`.
- Trava nova (A1): a fonte é a DECISÃO DO DONO 2026-11-21 20:54, item 3, em docs/pedidos/v0478.md. O texto a chama "regra da retro"; ela foi escrita para cartões de retrospectiva, e o SIEG-G5 vem de cartão do dono (16/11). Mesmo assim o desenho a invoca e se declara fora dela, e isso não se sustenta: juntar a `recusa_de_corte` dentro de `recusa_do_formato` muda o nome, não simplifica nada, e a extensão do Stop rejeitada nunca existiu, então não é a trava que sai. Duas saídas aceitáveis: apontar a trava que sai ou fica mais simples (por exemplo, se a medida S6 do `hooks/meta.py` ou a medida posterior deixam de ser necessárias), ou escrever "trava nova; a regra 3 não alcança cartão do dono" e pôr isso no item "Em aberto" para o dono.
- Corte C0 a C3: C0, C1 e C3 têm pronto medível (saída `total:`, casos por regra com mutante, transcrito sintético). C2 não tem (A4). A ordem tem uma dependência que o A2 expõe: se a linha de base usar a métrica do C3, o C0 vem depois do C3, não antes.
- Teto 1200 (A3): o número é o mesmo do S6 e o texto pede um lugar só, mas o C1 não tem oráculo disso. Não bloqueia porque a intenção está escrita; o brief do C1 deve trazer a regra.
- Changelog: o fragmento está em `changelog.d/` com o nome da branch; nada no `CHANGELOG.md`.
- Afrouxa: não. Nada sai de `docs/regras/`, de `tests/config.json` nem de controle; neutralidade sem termo de projeto.

## Parecer
Reprovado por A1 e A2. Os dois se resolvem no texto da proposta, sem código: A1 ajusta a frase da linha 47 (e o "Hook novo: nenhum" da linha 5 pode ficar), A2 troca a régua da reversão e acerta a ordem C0/C3. A3 e A4 são recomendados: podem entrar na mesma volta, ou viram cartão depois do merge.
