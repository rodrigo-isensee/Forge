---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-meta85-forge-check
commit: dd6e111021f53ee783e47dc4649767d8f35289f8
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0478 META85 (bin/forge-check), E34.4, revalidações E34.8 e E34.12

A rodada 1 (E34.4, head 6853e0ee) e a revalidação E34.8 (head 99f474bb) ficam no git. A revalidação mais recente é a do head dd6e1110 (E34.24), abaixo; a do 19e81adc (E34.20) segue; a do a281e4a5 (junção, E34.16) e a do 06abb4fa (E34.12) seguem.

## Revalidação (E34.24, head dd6e1110)
Delta lido: `forge-check parecer delta docs/security/v0479-meta85-forge-check.md`, intervalo `19e81adc..dd6e1110`: "nenhum arquivo do domínio
mudou". `git diff --stat` confirma `bin/`, `hooks/`, `scripts/`, `.githooks/`, `.github/` sem diferença. Fora do domínio, lidos só como
conferência: `tests/test_revisor_wt.py` (teste novo `test_ausente_sem_base_e_sem_develop_o_diff_literal_leva_o_previo`, que mata o M7 do
`pr --previo` sem `--base`), `tests/mutantes/z075-pr-previo.json` (M7 passa a apontar para esse teste) e `tests/mutantes/v0433-integracao-2.json`
(I26 lista só `tests.test_aq5_parecer_novo`); docs de QA e review. Estado dos achados anteriores: A1 resolvido (sem mudança). Achado novo: nenhum.

**Só aperta, reconfirmação (`afrouxa-regra`):** a mudança do item continua só apertando. O código de decisão (`pr_da_cli`, `cmd_pr`,
`veredito_do_parecer`, `commit_vale`) é byte a byte o já confirmado; o delta só acrescenta teste e reaponta specs de mutante, que cobram mais
(um mutante antes sem teste que o mate agora tem) e não afrouxam guarda nenhuma. O teste novo exige o comportamento seguro: sem develop e sem
`--base`, `pr --previo` sai 0 com aviso e `pr` sem `--previo` sai 1 com a violação de "sem parecer", ou seja, o `--previo` só rebaixa a aviso
quando pedido e o `pr` de verdade segue recusando. O encolhimento da lista do I26 para um teste só não remove proteção do produto; vale
enquanto o `aq5` mata o mutante (conferência de QA e CI do PR). Sem segredo no delta (revisão manual). Sem suíte local (CI do PR, pelo brief);
`python3 -m unittest tests.test_revisor_wt` (39 testes, OK) rodado como conferência.

## Revalidação (E34.20, head 19e81adc)
Delta lido: `forge-check parecer delta docs/security/v0479-meta85-forge-check.md`, intervalo `a281e4a5..19e81adc`. No domínio, só
`bin/forge-check:3215-3217`: a constante `PROVAS_DO_PQ` passa de `.forge/run/{mutantes,pronto}.log` para
`${TMPDIR:-/tmp}/forge-{mutantes,pronto}.log`. Fora do domínio (não relidas): specs de mutante, `tests/pesos-d4.json`, três testes, docs.
Estado dos achados anteriores: A1 resolvido (sem mudança). Achado novo: nenhum.

**Só aperta, reconfirmação (`afrouxa-regra`):** a constante só entra no texto do PQ que o `brief gerar` escreve (:4155, :9064); nenhuma
decisão a lê. O que aceita ou recusa a prova é `motivo_da_prova` (:3234-3252) e `provas_da_entrega` (:3220), intactos: exigem `head=<sha40>`
na 1.ª linha, `rc=0` na última, teto de 8 MiB, e só para etapa `codigo` com código no escopo. O caminho do log vem de `--mutantes/--pronto`
e nunca foi restringido, então o local do arquivo não muda o que passa. `cmd_pr`, `veredito_do_parecer`, `commit_vale`, `pr_da_cli`: sem
diferença desde a a281e4a5. O `forge-check pr` e o selo não aceitam nada que antes recusavam; o único efeito é o `brief selar` deixar de
recusar o PQ que o próprio gerador escrevia (`.forge/run/` é estado dos hooks, escrita barrada em `hooks/conformidade.json:35`), ou seja,
corrige recusa por defeito do gerador, sem afrouxar guarda: o brief continua selado pelo mesmo conferente.

**Gravar no temporário não abre falsificação:** (1) a prova nunca foi assinatura: o `forge-check` só lê, e quem escreve o log podia
escrever `head=<sha>`/`rc=0` à mão em `.forge/run/` igualmente (nesse diretório a barreira era só do hook, para o agente; o autor não
ganha poder novo aqui). (2) O log é preso ao head pelo sha40 da 1.ª linha; log velho ou de outro commit é recusado. (3) A prova do autor
é só uma das camadas: a mutação e o pronto rodam de novo no CI do PR e o parecer de QA e o review conferem o mesmo head; a linha do
`entrega` é pré-parecer (`pendente:` que reprova), não portão final. (4) Com `TMPDIR` não definido o nome em `/tmp` é previsível, e em
máquina compartilhada outro usuário poderia criar o arquivo antes; o ambiente do Forge é de usuário único (sandbox com `$TMPDIR` próprio da
sessão) e o ganho seria o mesmo de forjar o log, sem caminho realista acima do que o autor já podia: recomendação, não achado.
Sem segredo no delta (revisão manual). Sem suíte local (CI do PR, pelo brief); `tests.test_meta85_entrega` (12 testes, OK)
rodado como conferência.

## Revalidação (E34.16, head a281e4a5)
Delta lido: `forge-check parecer delta docs/security/v0479-meta85-forge-check.md`, intervalo `06abb4fa..a281e4a5` (junção com a
develop 5ae868eb; conflitos em `bin/forge-testes`, `tests/test_testes_tocados.py` e `skills/briefs-e-conferencia/autor-ate-o-merge.md`).
No domínio: `bin/forge-testes` (o que veio da develop: `progresso()` só no stderr, ordem dos módulos, nomes de teste no mapa) e a skill
(texto). `tests/test_testes_tocados.py` fora do domínio. O delta traz só o que veio da base, sem código do item.
Resolução dos conflitos conferida contra a base (`git diff 5ae868eb a281e4a5`): `bin/forge-testes` difere da develop só por três nomes
acrescentados ao mapa `FORGE_CHECK` (`test_meta85_entrega`, `test_meta85_revalida`, `test_meta85_item_arquivos`: o mapa pede mais
teste, não menos); a skill difere só pela linha da retomada por `revalida: sim` (texto do item). Nenhuma proteção removida.
`bin/forge-check`: sem diferença entre 06abb4fa e a281e4a5; `base_sem_flag_do_pr`, `pr_da_cli`, `cmd_pr` e `parecer_delta` seguem como
lidos. Achados anteriores: A1 resolvido (sem mudança). Achado novo: nenhum.

**Rótulo `afrouxa-regra`, reconfirmação depois da junção:** a mudança do item continua só apertando. O `pr` não aceita parecer antes
recusado (o `bin/forge-check` é byte a byte o do 06abb4fa e a equivalência do `pr_da_cli` vale); a junção não toca `veredito_do_parecer` nem `commit_vale`; a única mexida do item em `bin/forge-testes` aumenta a cobertura do mapa. Sem segredo no delta
(revisão manual). Sem suíte local (CI do PR, pelo brief).

## Revalidação (E34.12)
Delta lido: `forge-check parecer delta docs/security/v0479-meta85-forge-check.md`, intervalo `99f474bb..06abb4fa`. No domínio, só
`bin/forge-check`: a função nova `base_sem_flag_do_pr` (:1537-1544), o `pr_da_cli` (:1570) e o `parecer_delta` (:3585). Fora do
domínio: `tests/test_meta85_revalida.py` e a spec de mutante 7. Já lido e não relido: o resto de `eca1d21b..99f474bb`.

Estado dos achados anteriores: A1 (resíduo de base do `revalida:`) **resolvido** no 57510a3a/06abb4fa. O `revalida:` recebe
`base_sem_flag_do_pr(raiz, ate, None, base)`, a mesma fonte que o `pr_da_cli` usa para decidir a base: numa branch de trabalho (a da
ref ou a única cujo head é o sha), a ref da develop resolvida por `base_do_delta`, que é o mesmo `resolvida` que o `pr_da_cli` (:1586)
entrega ao `cmd_pr`; fora dela, ou com o head já contido na base, None, como o `pr` (:1573-1580). Testes conferidos e rodados:
`test_base_que_ja_contem_o_head_revalida_como_o_pr`, `test_fora_da_branch_de_trabalho_revalida_pelo_diff_literal`,
`test_branch_de_trabalho_pelo_sha_simula_a_base_como_o_pr` (`python3 -m unittest tests.test_meta85_revalida`: 10 testes, OK).
Sem achado novo. Nota sem caminho de ataque: com `parecer delta --base homolog|main`, o `revalida:` usa essa base e o `pr` sem
`--base` usa a develop; é escolha explícita de quem chama, e a linha segue informativa (nenhum portão a lê).

## Gatilhos
Gatilhos: controle do Forge (`bin/forge-check`: `pr_da_cli` escolhe a base do portão de merge, `cmd_pr` decide); rótulo `afrouxa-regra` pedido.

## Confirmação para o rótulo `afrouxa-regra` (head 06abb4fa)
A mudança **só aperta**: o `forge-check pr` sem `--base` não aceita nenhum parecer que antes recusava.
1. **`pr_da_cli` (:1568-1571), equivalência exata.** Antes: `if branch and branch not in BASES_DO_FLUXO and base_do_delta(raiz, "develop", ref)[0]`.
   Agora: `if base_sem_flag_do_pr(raiz, ref, branch)`, que (a) recalcula `branch` só se ela vier falsa, e ela chega calculada pela
   mesma expressão da linha :1569, logo é o mesmo valor; (b) com `branch` verdadeira e fora de `BASES_DO_FLUXO`, devolve
   `base_do_delta(raiz, "develop", ref)[0]` (o `nome` padrão é `"develop"` e o `pr_da_cli` não passa outro); (c) nos demais casos,
   None. A veracidade do teste é idêntica à da condição antiga em todos os casos, e o efeito (`base = "develop"`) não mudou: mesma
   base, mesmo `cmd_pr`, mesmo veredito.
2. **`cmd_pr`, `veredito_do_parecer`, `commit_vale`:** fora do delta, inalterados desde a confirmação no 99f474bb (os ramos 1 a 5
   dela seguem valendo e ficam no git).
3. **`revalida:`** segue só informativo; passou a usar a base do `pr`, o que só alinha as duas respostas.
Nenhum caminho do `pr` mudou de resultado; nenhum parecer antes recusado passa a ser aceito.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Teste rodado no head 06abb4fa: `python3 -m unittest tests.test_meta85_revalida` (10 testes, OK); a suíte
inteira fica com o CI do PR (sem suíte local, pelo brief). Sem segredo no delta (revisão manual; só código Python).
