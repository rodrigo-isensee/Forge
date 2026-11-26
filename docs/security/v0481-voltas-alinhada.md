---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-voltas-alinhada
commit: e871982cedd65cf23e497336cb388bc173a3d3e1
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (#902, R-QA-VOLTAS-ALINHADA), volta E14.63

Revalidação por delta (E14.74). Li o `forge-check parecer delta` de `46000ed5..e871982c`. No domínio estão `bin/forge-check`, `docs/regras/R-QA.md`, `agents/jarvis.md:31` e `skills/briefs-e-conferencia/autor-ate-o-merge.md:10`. As specs de mutante, `tests/test_volta_por_delta.py` e o changelog ficam fora do domínio. A rodada anterior está no git.

O CI do head exato não está verde nas partes que contam, então não gravo a linha `ci:`. Falham `suíte` 3/5 (3.12 e 3.14), por causa do A4, e `suíte` 4/5 (3.12 e 3.14), em `test_forge_mutante.ConferirTodas`: o M23 de `tests/mutantes/v0480-g1-1-uma-volta-3.json` não confere mais com a fonte. Essa falha é fora do meu domínio, mas o CI segue vermelho e ela entra na mesma volta. A `catraca` também falha. Rodei a catraca aqui (`--modo regras`, `34ab6714..e871982c`) e só sobram os itens que pedem o rótulo `afrouxa-regra` do dono: o `bin/forge-check` mudado, cinco testes apagados ou renomeados (os do teto, que a ordem das 17:07 revogou) e as guardas apagadas `recusa_da_volta` e `voltas_autorizadas`, que não admitem mutante. Os dois avisos de valor esperado trocado (`test_conferencia_recusa_a_numeracao_contornada` e `test_volta_conta_o_item_e_nao_a_cadeia`) acompanham a contagem nova, sem perda de guarda.

Rodado aqui, só no que foi tocado: `tests.test_volta_alinhada`, `tests.test_voltas` e `tests.test_volta_por_delta` (168 testes, OK, 1 pulado já existente). `bin/forge-mutante` nas três specs do v0481 matou VA-M1 a VA-M20, e na `v0480-g1-1-uma-volta-2.json` matou M8 e M12 a M15. As sondas S1 a S7 estão em `/root/.forge-contrib/wt/_sec76-v0481-voltas-sonda.py` (`python3 -I <sonda> <clone> Sondas`).

Gatilhos: controle do Forge (`bin/forge-check`: contagem e marcas da volta, medida de teste enfraquecido, conferência do brief), regra com ID (`R-QA`), texto de agente e de skill que governa as voltas.

## O que aperta, o que é neutro e o que afrouxa
- **Afrouxa:** sai o teto de voltas. `recusa_da_volta` e `voltas_autorizadas` foram apagadas, e a 4ª volta em diante sai sem `DECISÃO DO DONO` e sem a oferta de corte. A DECISÃO DO DONO de 25/11 17:07 autoriza isso ("resolver, não cortar"). Pela catraca, o rótulo `afrouxa-regra` continua sendo ato do dono.
- **Aperta:** (a) `bin/forge-check:9150`, a lista de exclusão `TIPOS_DE_PORTAO`: brief sem `Tipo:`, `Tipo: volta` sem `Volta-de:` e `Tipo: codigo` numa branch reprovada agora são recusados (S1, S2; S3 mostra que o brief de portão continua passando). (b) `:4454` e `:4483`, a medida por teste da 3ª volta: asserção tirada de um teste e compensada noutro reprova (S4), e módulo apagado também reprova (S7). (c) `:4472`, a medida também dispara quando o brief traz a restrição, mesmo sem `(volta N)`. (d) `:4676`, as duas marcas, da 3ª e da 4ª, são cobradas pela contagem real do item, mesmo com a numeração contornada. (e) `:4595`, da 4ª volta em diante, a marca do trabalho em dupla, que nenhuma decisão do dono troca.
- **Neutro:** a linha de `R-QA.md:17`, `jarvis.md:31` e `autor-ate-o-merge.md:10`, que acompanham a ferramenta e a ordem das 17:07; o `import ast`; a falha fechada continua igual (sem catraca ou com o git falhando, reprova).

## Achados
- A4 (bloqueante) bin/forge-check:4679 · CI vermelho no guarda de saída sanitizada: `test_forge.SaidaSanitizada.test_todo_valor_de_caminho_numa_fstring_passa_pelo_sanitizador` falha porque a variável inteira `real` tem nome de caminho e é interpolada crua. Não há caminho de ataque (é um número), mas o guarda está vermelho.

## Sondas
- S8 · python3 -m unittest tests.test_forge.SaidaSanitizada.test_todo_valor_de_caminho_numa_fstring_passa_pelo_sanitizador · espera: OK · obtido: FAILED (failures=1), `4679: f'volta: Entregar (volta {real} do item)...'` em crus

## Detalhe dos achados
**Estado dos achados anteriores.** A1 (teto contra a ordem das 17:07): resolvido. Não há mais teto nem oferta de corte, e da 4ª volta em diante a marca de tech-lead e revisor juntos é cobrada (`:4595`, `:4676`). A2 (contagem só com `Tipo: codigo`): resolvido pela lista de exclusão (`:9150`). S1 e S2 agora dão rc 1 com "já tem parecer reprovado". A3 (compensação entre testes): resolvido pela medida por teste (`:4454`). S4 reprova com `test_b enfraqueceu: de (1, 0, 0) para (0, 0, 0)`. A observação de falso positivo com merge da develop continua sem prova, e a medida agora cobre só os módulos que o diff da volta altera.

**A4 (defeito provado, CI).** Evidência: `bin/forge-check:4676` define `real = max(n, n_anterior + 1, voltas + 1)`, e `:4679` o interpola. `real` está na `LISTA` de nomes de caminho de `tests/test_forge.py:5764`. O guarda é o abuso 18 (saída sem caractere de controle), e o CI da parte 3/5 falha nele nas duas versões. Caminho de ataque: nenhum, porque o valor é um inteiro. Severidade: baixa como risco, mas o defeito está provado e segura o CI. Correção mínima: renomear a variável (por exemplo, `contagem`) em `:4676` e `:4678-4679`, sem mexer no guarda nem na `LISTA`. Esforço: P. Dono: tech-lead (autor do #902).

**Fora do domínio, no mesmo CI vermelho:** `test_forge_mutante.ConferirTodas` aponta o M23 de `tests/mutantes/v0480-g1-1-uma-volta-3.json`, spec que este diff não ajustou e cuja fonte mudou. Dono: tech-lead. Entra no mesmo brief de volta.

**Sondas sem bloqueante (registro):** S5 troca `assertEqual(rc, 1)` por `assertTrue(True)` no mesmo teste, e S6 tira a asserção de um ajudante `self.checa` e soma `assertTrue(True)` noutro teste. A medida da volta (`forca_por_teste` usa `_forca_das_arvores`, que conta a asserção vazia e não segue ajudante) não acusa nenhuma das duas. Já a `catraca.regra_testes_afrouxados`, que roda no CI e é obrigatória para o merge, acusa as duas. Sem caminho até a develop sem o rótulo do dono, por isso não é achado (vai em `Melhoria vista:`).

## Riscos aceitos e ferramentas
Nenhum risco aceito. O fim do teto tem a DECISÃO DO DONO de 25/11 17:07; o rótulo `afrouxa-regra` é do dono. Ferramentas usadas: leitura do diff, os testes dos módulos tocados, `bin/forge-mutante`, a catraca local, as anotações do CI e sondas locais. Faltam no ambiente gitleaks, semgrep, zizmor, actionlint e osv-scanner (lacuna). O delta não traz workflow, dependência nem segredo.
