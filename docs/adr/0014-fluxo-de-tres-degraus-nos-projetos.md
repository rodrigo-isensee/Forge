# 0014 - Fluxo de três degraus nos projetos

Estado: proposta. Data: 2026-11-02. Destrava: o PR da fase E do lote-unico-032 (L38 a L42), que traz o texto da `R-FLUXO`, o modelo de projeto, a migração e a checagem do Dependabot; vira `vigente` nesse PR.
Propósito: decidir que todo projeto que usa o Forge segue `branch própria` → `develop` → `homolog` → `main`, como a própria fábrica, e o que cada degrau garante. Público: quem mantém o Forge e quem usa a fábrica num projeto. Revisão: 2026-12-02.

## Contexto
No Forge o fluxo tem três degraus (`R-FLUXO`, "No Forge"): a `develop` recebe o trabalho por PR, a `homolog` repete a bateria sobre o conjunto que vai subir e a `main` só muda por PR mesclado pelo usuário (`R-MAIN`). Nos projetos, a `R-FLUXO` ("No projeto") descreve só dois: branch de trabalho e branch de integração, que chega à `main` por PR. Consequências medidas no pedido FLUXO-PROJETOS-HOMOLOG:
- o modelo de projeto não cria a `homolog` e o `pre-push` do modelo protege só a `main` (`templates/projeto/.githooks/pre-push:3`); um agente consegue enviar direto à integração (BP-2 do INCIDENTE-BYPASS-1);
- o modelo não traz CI que rode a bateria no PR (`templates/projeto/.github/` só tem `dependabot.yml`);
- o Dependabot sem `target-branch` abre PR direto na `main` (decisão do dono, 2026-10-17: "o dependabot esta fazendo errado atualizando direto a main").

O dono decidiu em 2026-10-17: "em todos os projetos que usam a forge sempre vai ser aplicado na develop, depois joga a develop na homolog e daí abre o PR para que o usuario aprove para a main".

## Decisão
1. **Três degraus em todo projeto.** Trabalho em branch própria (`feature/`, `fix/`, `docs/`, `chore/`, `refactor/` + slug) → PR na `develop` → promoção `develop` → `homolog` por PR (`tech-lead`, todos os checks verdes) → PR `homolog` → `main` que só o usuário mescla (`R-MAIN`). Ninguém commita nem envia direto à `develop`, à `homolog` nem à `main` (BP-6 mantida; a leitura "commit direto na `develop`" foi recusada pelo dono em 2026-10-17).
2. **A fonte é a `R-FLUXO`** (ADR 0002): a seção "No projeto" ganha os três degraus; os agentes e as skills citam o ID e não repetem o texto.
3. **Modelo de projeto.** `forge-init` e `forge-novo-projeto` criam a `homolog`; o modelo traz um CI (`templates/projeto/.github/workflows/forge-ci.yml`) que roda a bateria do projeto no PR para `develop` e para `homolog`; o `pre-push` do modelo recusa envio direto às três branches.
4. **Migração** (ADR 0005). `forge atualizar` cria a `homolog` a partir da `main`, com o "s" do usuário e um aviso, e nunca troca branch existente.
5. **Dependabot.** Toda entrada de `dependabot.yml` traz `target-branch: develop`; a skill `ci-cd` e o `devops-engineer` exigem o campo; `forge doutor` reprova arquivo sem ele ou com `main` ou `homolog`; a migração corrige.
6. **Branch de integração diferente.** O `CLAUDE.md` do projeto ainda pode declarar outra branch de integração no lugar da `develop` (a `R-FLUXO` já prevê); os três degraus valem com o nome dela.

## Alternativas
| Opção | Prós | Contras |
|---|---|---|
| Manter dois degraus nos projetos | Sem mudança | Projeto sem a bateria repetida sobre o conjunto que sobe; `pre-push` do modelo e Dependabot continuam abertos |
| Commit direto na `develop` | Menos PRs | Contraria a BP-6; sem PR não há review nem QA |
| `homolog` opcional por projeto | Flexível | Duas regras de fluxo; a checagem do CI e do `pre-push` ficariam condicionais |

## Consequências
- Mais fácil: um fluxo só na fábrica e nos projetos; o Dependabot e o agente deixam de alcançar a `main`; a migração é mecânica.
- Mais difícil: projeto pequeno passa a ter mais um PR por promoção; o CI do modelo gasta minutos de Actions (repositório público; `R-CUSTO`: nada pago, e o modelo não ativa serviço cobrado).
- Projetos que trabalham fora da regra (commit direto na integração, `pre-push` local) param até migrar; o `forge atualizar` avisa antes e a mensagem de recusa traz o contorno.
- Controles novos nascem no código da fase E; até lá a ADR é texto, e os modelos de projeto e a `R-FLUXO` seguem como estão.

## Por que o existente não basta
O que existe é a seção "No projeto" da `R-FLUXO` (dois degraus), o `pre-push` do modelo (só `main`) e o `dependabot.yml` do modelo (`templates/projeto/.github/dependabot.yml:17`, com o campo). A evidência de execução: o incidente BP-2 mostrou envio direto à integração por alias, e o dono viu o Dependabot abrir PR na `main` de um projeto sem o campo. Nenhum deles tem a `homolog`, nem CI do modelo no PR, nem checagem do campo.

## Critério de reversão
Reverter se, nas duas primeiras releases depois do PR da fase E, mais de 2 projetos pedirem por `forge sugerir` a retirada da `homolog` por custo de PR sem terem tido um defeito pego nela.

## Leituras
| Data | Medida | Veredito (manter, ajustar, reverter) |
|---|---|---|
| 2026-12-02 | pedidos de retirada da `homolog` em `forge sugerir`; defeitos pegos na `homolog` dos projetos | pendente |
