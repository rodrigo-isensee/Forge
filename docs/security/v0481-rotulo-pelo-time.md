---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-rotulo-pelo-time
commit: ab5871d1dedead9ff0021f4063b629794f6f9f00
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (E24.4, #918, FORGE-ROTULO-PELO-TIME, 1ª rodada completa)

Lido: `git diff 3c833f3f..ab5871d1` (merge-base com a `develop`), 10 arquivos: `bin/forge_autorizacao.py`, a Emenda ROTULO-PELO-TIME da ADR 0018, o fragmento do changelog, os dois módulos de teste e as cinco specs de mutantes. Também li o contexto que não mudou: `git()` (`bin/forge_autorizacao.py:188`), `estado()` e `leitura()`, a guarda R-CONTRIB do rótulo (`hooks/conformidade.py:3507-3523`) e os consumidores de `forge-check autorizacao` (só `bin/forge-fechar:1616`, que usa `--ato corte-diario`).

- ci: ab5871d1dedead9ff0021f4063b629794f6f9f00 verde

CI do head (run 45857943188): as 10 partes da suíte, os dois tetos de pulados, `bateria (python 3.14)`, `bateria (passos)`, `bateria (verificações longas)`, `instalação (python 3.14)`, `catraca` e `árvore já provada na develop` estão verdes. Há dois vermelhos, e os dois vêm da ordem da construção. `bateria (pareceres)` (job 140041137242) cai em R-REVIEW porque no `ab5871d1` ainda não havia parecer de review aprovado; o parecer chegou depois, no `ce98c550`. O agregador `bateria` (job 140046759733) cai só por `pareceres: failure` e registra `partes: success`.

Rodado aqui, no `ab5871d1`: `python3 -m unittest tests.test_autorizacao tests.test_autorizacao_gravar` (63 testes, OK). `forge-mutante` nas duas specs novas (M1 a M10, todos mortos; o M10 morre por erro do teste, porque um manifesto em lista quebra o `.get`) e nas três specs de AUTORIZACOES-FIXAS com o trecho ajustado (todos mortos).

Gatilhos: controle do Forge (autorização gravada do dono, ADR 0018), afrouxamento de regra por ordem do dono (R-CONFORMIDADE, R-DECISAO).

## O que aperta, o que é neutro e o que afrouxa
**Aperta:**
- O termo `homologacao` passa a ser termo de ato (`bin/forge_autorizacao.py:309`). Uma mensagem de `rotulo-afrouxa-regra` ou de `merge-main` que cite a homologação agora nasce `pendente-confirmacao` por "mais de um ato". Antes ela já nascia pendente, porque a palavra estava fora do `VOCABULARIO`. O efeito é falha fechada, sem concessão nova.

**Neutro:**
- `ler --ato` com qualquer ato sem prazo vai ao `cmd_corte` (`bin/forge_autorizacao.py:483`). Para `so-aperta-com-seguranca`, a saída deixa de ser a lista de todas e passa a ser a ativa mais nova (rc 0) ou nenhuma (rc 1). Nenhum consumidor usa esse ato no `ler`, e a resposta só fica mais estreita.
- `VOCABULARIO_FIXO` ganha `homologacao` (`bin/forge_autorizacao.py:41`), que vale para os três atos sem prazo. Com `corte` ou `aperta` na mesma mensagem, ela cai em "mais de um ato", então os atos de F1 não ganham frase nova que nasça ativa.
- No `ab5871d1`, nada consome o ato. Ele não aparece em hook, na catraca nem em `forge-fechar`, e o rótulo `afrouxa-regra` segue atrás da guarda R-CONTRIB (`hooks/conformidade.py:3507`). O código desta entrega só grava e lê a concessão.
- O slug do `origin` (`bin/forge_autorizacao.py:230`) aceita qualquer host antes de `github.com/` (sonda S1: `https://<outro-host>/github.com/<slug>` e `file:///…/github.com/<slug>.git` dão "é o Forge"). Isso não é caminho de ataque: quem escreve `remote.origin.url` já pode gravar a URL exata do Forge. O padrão é o mesmo do `slug_do_forge` (`hooks/parecer.py:933`), que o hook usa. A fronteira de fato contra projeto é o `.forge/versao`.

**Afrouxa (por ordem do dono, 26/11 12:57):**
- No repositório do Forge, uma concessão `rotulo-pelo-time` ativa autoriza o time a pôr o rótulo `afrouxa-regra` sem o dono item a item, sem prazo, até a retirada `R-<Id>`. A conferência de cada afrouxamento pelo dono passa a acontecer só no PR da `main` (R3). O merge na `main` segue só do dono (`R-MAIN`), e nos projetos nada muda.

**O limite ao repositório do Forge é sólido?** Sim, para o ato desta entrega. A conferência fica em `fora_do_forge` (`bin/forge_autorizacao.py:235`), e cada falha deixa a concessão `inativa`:
- Raiz com `.forge/versao` é sempre projeto, mesmo com o `origin` do Forge. A sonda S2 e `test_outro_origin_ou_projeto_deixa_inativo` provam isso. Apagar esse arquivo desligaria os hooks inteiros, e a guarda de `hooks/conformidade.py:2892` barra isso. O ato novo não abre esse caminho.
- O `repository` esperado vem do `plugin.json` do plugin carregado (`Path(__file__)`, no cache somente leitura), nunca do manifesto da raiz. Um projeto não consegue declarar a si mesmo como Forge.
- O `git` roda sem as variáveis `GIT_*` herdadas (`bin/forge_autorizacao.py:190`), então `GIT_CONFIG_COUNT` e similares não trocam o `origin` só para uma chamada.
- Sem `git`, sem `origin`, com o manifesto ilegível, em lista ou sem `repository`, a concessão fica inativa (`test_plugin_sem_repositorio_nao_faz_o_forge`).
- Sem a frase do dono digitada na sessão, nenhum ato nasce ativo (gravador, sha256 e transcrição da ADR 0018). Mesmo que o dono de um projeto digite a frase, a concessão fica inativa.

## Achados
- A1 (recomendado) docs/adr/0018-autorizacao-do-dono-gravada.md:203 · R1 vale no merge e R3 só no PR seguinte: no intervalo o time pode rotular (o gh roda na conta do dono, a guarda R-CONTRIB passa) e a condição do dono, a lista na main, fica sem conferência. Correção: R1 só produz efeito com R3 na develop

## Sondas
- S1 · script em arquivo: repositório sem `.forge/versao` com origin `https://<outro-host>/github.com/<slug>` e depois `file:///tmp/github.com/<slug>.git`; `fora_do_forge` · espera: "" (o padrão aceita) · obtido: "" nos dois
- S2 · script em arquivo: raiz com `.forge/versao` e origin igual ao `repository` do plugin; `fora_do_forge` · espera: inativa por projeto · obtido: "só vale no repositório do Forge: a raiz é projeto ou o plugin não diz o repositório"

## Detalhe dos achados
**A1.** Evidência: `docs/adr/0018-autorizacao-do-dono-gravada.md:203` ("R1 vale a partir do merge na `develop`; R3 vem no PR seguinte") e `:211` (R3). Os PRs do Forge saem na conta do dono (`PR_AUTOR` no log do job 140041137242), e `exigir_dono` (`hooks/conformidade.py:3514`) compara só a conta. Por isso, depois do merge, o que segura o rótulo pelo time é o procedimento, que lê a concessão. Caminho: entre o merge desta entrega e o do PR de R3, o time rotula itens que afrouxam. Se o PR da `main` da versão nascer sem a lista, o dono mescla sem ver o que afrouxou, que é justamente a condição que ele pôs. Severidade: baixa (exige uma versão no intervalo e não abre acesso novo). Correção mínima, em uma linha da emenda: "R1 só produz efeito (o time põe o rótulo) depois do merge de R3 na `develop`; até lá o rótulo segue com o dono". A alternativa é o PR da `main` do intervalo trazer a lista à mão, conferida no parecer de segurança da versão. Esforço: P. Dono: `tech-lead` (autor do E24.1).

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum; o afrouxamento é decisão do dono registrada no pedido (26/11 12:57), não risco aceito deste parecer. Ferramentas: `git diff`, os dois módulos de teste, `forge-mutante` (5 specs), duas sondas em arquivo e o `gh api` dos check-runs e do log dos jobs vermelhos. Faltou o `gitleaks` no PATH; o diff não traz credencial.
