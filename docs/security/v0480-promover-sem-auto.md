---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-promover-sem-auto
commit: a438dcc37ffd41ea37bd580521824fd217fd300b
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-22
---
# Review de segurança: v0478 (E118.2, PROMOVER-SEM-AUTO-MERGE)

Revisão completa única do diff `38c37de9..a438dcc3` (base `develop`): `scripts/promover-homolog.py`, `docs/promocao-integrador.md`, `tests/test_promover_homolog.py`, `tests/mutantes/promover-auto.json`, `tests/mutantes/v0480-promover-sem-auto*.json`, `changelog.d/v0480-promover-sem-auto.md`. Todos os achados desta rodada estão aqui; não há outra rodada prevista.

## Gatilhos
Gatilhos: fluxo de merge e promoção (R-FLUXO, R-MAIN), controle do Forge (portão de checks antes do merge), decisão do dono de 21/11 20:15 (merge automático proibido em qualquer PR).

## Resumo
A mudança só aperta. Antes, o script imprimia `gh pr merge develop --auto ...` em todo caminho (verde, pendente ou sem check) e saía com 0. Agora:
- o `--auto` sumiu do único comando de merge (`scripts/promover-homolog.py:374`), e nenhum caminho o imprime;
- pendente ou sem check do evento `pull_request` sai com 4 (`PENDENTE`, `:47`, `:299-303`) sem comando de merge;
- o merge direto só sai depois de: nenhum check vermelho ou desconhecido (`:352-354`, inalterado), catraca sem pedir rótulo (`:356-357`), nenhum pendente (`:359-360`) e cada nome de `CHECKS_EXIGIDOS` com execução do PR e só em `pass` (`:306-328`, `:361-363`); `skipping` num obrigatório para com 1 (`:327`);
- a lista vem do `bin/forge-fechar` da pasta do próprio script (`:46`), não de cópia; arquivo ausente, linha ausente ou lista vazia param (`:310-317`): falha fechada;
- o comando segue preso ao head (`--match-head-commit <sha>`): se a `develop` andou entre o fetch e a leitura dos checks, o merge falha em vez de mesclar o que não foi conferido.

Nenhum caminho que antes parava passou a seguir; o único código de saída novo (4) não é 0, e o único consumidor automático do script (`bin/forge-fechar`, passo 1c) usa só `--conferir-ref` (`bin/forge-fechar:307`, `:1011-1035`), que este diff não toca.

## Verificações
- Casamento por nome (sem o workflow), igual ao `checks_do_head_verdes` do `bin/forge-fechar:870-872`: em `.github/workflows/` os nomes `bateria`, `bateria (python 3.14)` e `catraca` são únicos (`ci.yml:852`, `ci.yml:572`, `catraca.yml:19`); homônimo de outro workflow, se existisse, teria de estar em `pass` junto com o verdadeiro (`buckets != {"pass"}` para) e entraria por PR revisado. Sem caminho realista.
- Formato da lista: `readonly CHECKS_EXIGIDOS=(...)` igual na base e na branch irmã `melhoria/v0480-seg-quarentena-fechar` (`bin/forge-fechar:96` lá): a leitura por expressão não quebra com a integração dela; se quebrar, para (falha fechada).
- Mutantes: M9 (lista lida) e M10 (julgamento pelo nome) cobrem as duas condições novas; os testes novos cobrem pendente, sem check, obrigatório ausente, obrigatório pulado, só checks do `push`, leitura da lista real e lista ausente, vazia ou sem arquivo, e `test_nunca_imprime_merge_automatico`.

## Detalhe dos achados
Sem achado nesta revisão.

Fora do escopo (não bloqueia, registrado para triagem): `docs/regras/R-FLUXO.md:16` ainda diz que o `tech-lead` promove a `homolog` "por PR com merge automático", o que contraria a decisão do dono de 21/11 20:15 e o novo `docs/promocao-integrador.md`; o diff não toca a regra e o script já não imprime o `--auto`, mas o agente que ler a regra pode ligar o merge automático à mão (foi o caminho do #776). Cabe no cartão CONFORMIDADE-AUTO-MERGE-BLOQUEIA ou num item próprio. O `--auto` do `bin/forge-fechar` (incluindo `--promover`, `docs/fechamento-integrador.md:102`) está na branch `melhoria/v0480-seg-quarentena-fechar` (E114.1), fora daqui.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum.
Suíte: a suíte inteira fica com o CI do PR (a branch ainda não tem PR nem execução de CI); rodei só o teste que tira dúvida, `python3 -m unittest tests.test_promover_homolog`: 47 testes, OK. Ferramentas: leitura estática e `git`; nenhuma varredura externa.
