---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-brief-portoes
commit: 21edf48a63d7351585725752aace5501fc71f970
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-15
---
# Review: v047 (desenho do BRIEF-NAO-SEGURA-VAGAS, classe T)

Etapa E2.107. Parecer completo (não havia parecer de review na branch), no head 0c879d97, cujo código a revisar é `21edf48a` (o 0c879d97 só acrescenta o parecer de segurança). Diff `7fff73e4...21edf48a`: `docs/propostas/brief-portoes-por-ferramenta.md` (214 linhas, texto `.md`) e `changelog.d/v047-brief-portoes.md`. `forge-check classe`: T (só documentação fora dos caminhos de controle); `bin/` e `hooks/` iguais à base. Sem código, sem mutante e sem suíte a citar; o CI do PR vale quando o PR existir.

## Achados
- A1 (recomendado) docs/propostas/brief-portoes-por-ferramenta.md:36 · A linha `entrega conferida <sha40>` não traz branch (ENTREGA_CONFERIDA, bin/forge-check:1392) e a igualdade ao Revisar-sha diverge de `conferencia_do_head` (:1420, aceita fragmento depois). Use essa função: uma fonte com o merge (R-PROVA).
- A2 (recomendado) docs/propostas/brief-portoes-por-ferramenta.md:50 · Portão em dia só com `commit:` igual ao Revisar-sha; o `pr` aceita parecer cujo delta não toca o domínio (`commit_vale`, bin/forge-check:795, R-REVIEW). Como está, gera brief de revalidação que o merge dispensa e ocupa vaga: use `commit_vale`.
- A3 (recomendado) docs/propostas/brief-portoes-por-ferramenta.md:66 · O `Ler` gerado manda rodar `forge-check proximo P`, que no v047 passa de 120 s (cartão PROXIMO-POR-ETAPA, citado no próprio brief desta etapa). O modelo fixo deve trazer etapa, passo e dono no brief e não mandar rodar o `proximo`.
- A4 (recomendado) docs/propostas/brief-portoes-por-ferramenta.md:67 · Contradição: a 3.1 tira o PQ do CI de `linha_do_ci_do_parecer`, e a seção 4 (linha 136, A3 da segurança) diz que o modelo não a chama e usa texto fixo. Alinhe a 3.1 à seção 4, senão o selo de reprodução depende do `gh`.
- A5 (recomendado) docs/propostas/brief-portoes-por-ferramenta.md:144 · `brief_vencido` chama `corrigir_derivados` e `corrigir_revisar_sha` sobre a branch local (bin/forge-check:8587, :8669), a fonte que a seção 4 tira do selo. Diga que a fila e o aviso do hook `agentes` usam `head_enviado` para brief com `Gerado-por:`.
- A6 (recomendado) docs/propostas/brief-portoes-por-ferramenta.md:35 · `--head H` (linha 32) não tem semântica: só o padrão é descrito. Defina que H só confere (igual ao `ls-remote`, senão recusa) ou tire a opção; head explícito velho é a ameaça T7.

## Sondas

## Parecer
Aprovado, com seis recomendações para quem implementa as partes da seção 10. O desenho atende à ordem do dono de 14/11 15:53 (briefs de portão gerados do pedido e do head, autor à mão, selo obrigatório), traz "o que já existe e por que não basta" com evidência (seção 2), medida e critério de reversão (seção 11), entrega em partes de um comportamento cada (M14) e mutantes por guarda (AR-1). As referências [COD] conferidas existem na base 7fff73e4 (`montar_brief`, `sha_a_revisar`, `conferir_corte`, `ETAPAS_DE_PARECER` em `bin/forge-check:2216` e `:8261` e `hooks/agentes.py:574`, a trava em `:8514`, `args_do_forge_check` em `hooks/conformidade.py:97`, `forge_check_grava` em `:1590`, a lista de leitura em `hooks/conformidade.json:111`).

Os achados são de consistência do desenho com as fontes que ele promete reaproveitar: A1 e A2 trocam uma regra própria pela função que o `forge-check pr` já usa (sem isso o gerador recusa ou gera onde o merge decide diferente); A3 evita mandar o agente a um comando que estoura o tempo em pedido grande; A4 e A5 fecham o "uma fonte do head e nada de rede nos bytes" (A3 da segurança) nos dois pontos que ficaram de fora; A6 define uma opção citada sem regra. Nenhum é defeito provado nem requisito não atendido: o documento é só desenho e cada parte volta ao review na sua classe (C em `bin/` e `hooks/`). Os achados A8 e A9 da segurança (`docs/security/v047-brief-portoes.md`) seguem abertos como recomendados e não são refeitos aqui.

Checklist (leitura): itens 1, 2, 3, 10 e 11 conferidos; 4 a 9 e 12 sem alcance (sem código). Achados recorrentes (PA-7): nenhum item da lista se aplica a texto sem código; nenhuma classe repetida neste pedido para gravar `AR-<n>`.
