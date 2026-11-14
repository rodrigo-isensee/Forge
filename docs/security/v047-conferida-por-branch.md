---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-conferida-por-branch
commit: 7c91b13d795b743b129ef41f55ab755b5eee4ad2
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: v047 (conferida por branch, E1.185)

Intervalo `origin/develop..7c91b13d` (merge-base 6517ff14): `bin/forge-check` (nova `ja_na_base` e o `base_ref` passado a `desde_valido`, `base_sha_como_desde`, `desde_da_branch`, `desde_e_a_base` e aos quatro chamadores), dois testes de `MergeDaBaseDepoisDoBrief` em `tests/test_selo_e_entrega.py`, o teste novo `tests/test_conferida_por_branch.py`, dois arquivos de mutantes e o fragmento do changelog. Parecer da classe C pela `R-SEGURANCA`, com `R-REVIEW`, `R-CONFORMIDADE` e `R-PROVA` como critério.

## Gatilhos
Controle do Forge (`forge-check entrega`, o portão da conferência de entrega): mexe na escolha do Desde, que decide o intervalo cujo escopo é conferido.

## Achados
- A1 (recomendado) bin/forge-check:2186 · O `--desde` vindo de `revisados` ainda testa só `e_ancestral(desde, base_sha)`, sem `ja_na_base` com o `base_ref`; alinhar à regra nova para que um commit revisado já na develop também não vire Desde (só tira candidata, o intervalo cresce).

## Sondas

## Detalhe dos achados
**Os dois testes que mudaram de expectativa não afrouxam controle.**
- `test_merge_base_sem_ancora_fica_o_base_sha` (rc 1 para 0): antes, a `entrega conferida` de outro item, trazida pela develop sem âncora, virava o Desde, e o `agents/outro.md` da develop aparecia como fora do escopo, um falso positivo (arquivo que o autor não mudou). Agora o Desde é o Base-sha (intervalo maior, a branch inteira), e o arquivo da develop sai pelo filtro de integração que já existia (o que difere dos dois pais), não por nada novo. As asserções novas fixam o intervalo (`intervalo: <Base-sha>..`) e a linha `base:`, mais estritas que a anterior. O par desse teste com o autor mexendo no arquivo da develop continua reprovando: ver S1 e S2 abaixo.
- `test_head_ja_na_develop_mantem_o_base_sha`: troca `assertNotIn("pendente: intervalo vazio")` por `assertIn("intervalo: <Base-sha>..")`. A asserção nova implica a antiga (o Desde é o Base-sha, nunca o head) e é mais precisa; o teste segue sem checar o rc, como antes.

**Direção da mudança.** `ja_na_base` só tira candidatas a Desde; sem candidata, cai no Base-sha (`base_sha_como_desde`) ou, se o Base-sha não for ancestral do head, no `desde=None`, que o `linhas_de_entrega` já trata (Base-sha fora da branch reprova). O `base_ref` é a `origin/<base>` local, que o autor reescreve (`git update-ref`); reescrevê-la para incluir a própria conferida só alarga o intervalo. O filtro L08 do `escopo_pelo_primeiro_pai`, que também usa essa ref, esconderia os arquivos até a conferida, mas eles já foram conferidos nela; o que vem depois segue à vista (S3). A perda do `desfeitos` (só calculado com Desde) não abre caminho: sem Desde, o diff é a branch inteira contra o Base-sha, e um arquivo devolvido ao estado da base não é mudança líquida da entrega.

**Sondas executadas (nenhuma prova bloqueante; registro do método).** Script em `$TMPDIR`, herdando `MergeDaBaseDepoisDoBrief`, rodado no head e numa cópia da develop:
- S1: sem âncora, depois do merge da develop o autor muda `agents/outro.md`; espera rc 1 com o arquivo fora; obtido rc 1, `escopo: fora do declarado no brief "agents/outro.md"` (igual na develop).
- S2: sem âncora, merge da develop com edição maligna em `agents/outro.md` e `fora.txt` no próprio commit de merge; espera rc 1 com os dois; obtido rc 1 com os dois (igual na develop).
- S3: conferida própria C, commit `fora.txt` depois, `origin/develop` reescrita para C; espera rc 1 com `fora.txt`; obtido rc 1, Desde vira o Base-sha e `fora.txt` fora do declarado (na develop, rc 1 com Desde C).
- S4: `origin/develop` reescrita para o head; obtido rc 1 (`pendente: intervalo vazio`), igual à develop: falha fechada já existente, não introduzida aqui.

**A1** · evidência `bin/forge-check:2186` · caminho: um `Revisar-sha` de portão da própria branch que depois entrou na develop seria aceito como `--desde`; exige a forma antiga com `--desde` explícito e um commit que já passou por portão, e o resultado é um intervalo menor que o da regra nova, não um arquivo escondido do que é desta branch depois dele · severidade baixa · correção mínima: trocar `not e_ancestral(raiz, desde, base_sha)` por `not ja_na_base(raiz, desde, base_sha, base_ref)` nessa linha, com um teste · esforço P · dono: o autor do `bin/forge-check` (classe C).

**Suíte.** Não há PR nem CI para o head ainda (o brief manda não abrir PR); vale o PQ conferido: `docs/pedidos/v047.md` traz `entrega conferida 7c91b13d795b743b129ef41f55ab755b5eee4ad2`. Rodei aqui `tests.test_conferida_por_branch` e `tests.test_selo_e_entrega.MergeDaBaseDepoisDoBrief`: 12 testes, OK. A bateria completa fica no CI do PR, obrigatório para o merge.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, git e as sondas acima; varredura de segredos e SAST locais não estavam no PATH (lacuna registrada; o diff não toca credencial nem rede).
