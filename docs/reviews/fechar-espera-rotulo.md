---
tipo: review
contrato: 1
pedido: fechar-espera-rotulo
branch: melhoria/fechar-espera-rotulo
commit: 9930be95b0ee3ab10c6bb1c4c7d971f1d6d41471
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-21
---
# Code review: forge-fechar --esperar-rotulo (E1.2)

Escopo: `10c838fa..9930be95` (`bin/forge-fechar`, `tests/test_fechar.py`, `docs/fechamento-integrador.md`, `changelog.d/fechar-espera-rotulo.md`); li o script inteiro e o arquivo de teste. Este revisor não é o autor (D-ETAPAS-INST).

Veredito: **APROVADO**, sem bloqueante, com 4 recomendações.

## Conferido
- Faz o que o pedido pede (E1, decisão P1 = A): a opção é opt-in; sem ela o fluxo roda uma vez só e para como antes (`test_sem_a_opcao_o_rotulo_pedido_e_ausente_continua_parando`).
- Nunca mescla com a Catraca vermelha: a troca `catraca fail -> pending` (`bin/forge-fechar:192-196`) só transforma vermelho em pendente, nunca em verde; o laço interno só sai para o passo 5 quando não há pendente (`:216`), então o merge exige todos os checks `pass`/`skipping` na mesma leitura. Qualquer outro check vermelho para na hora (`:212-215`; teste `outro_check_vermelho_para_sem_esperar`).
- Suposição do autor (vermelho da Catraca como pendente sem rótulo e por até 10 leituras depois): coerente com o gatilho da Catraca, que roda de novo em `labeled` (`.github/workflows/catraca.yml:8`) e tem o job com o nome `catraca` que o awk compara. Esgotada a tolerância, o vermelho real para no passo 4 com a saída impressa (teste `catraca_vermelha_com_rotulo_aplicado_para_apos_a_tolerancia`). Falha fechada nos dois lados.
- Nunca aplica rótulo nem marca item: nenhuma chamada de escrita nova no `gh`; o teste afirma ausência de `--add-label` e de `pr edit`. A frase de cabeçalho que proíbe aplicar rótulo segue intacta (`:15`).
- Preso ao head: relê `headRefOid` a cada volta e para se mudou (`:182-183`); leitura falha deixa passar, mas o merge continua com `--match-head-commit` do passo 2 (`:258`), então não abre brecha.
- Prazo: conferido só nos passos 4 e 5 (`:201`, `:217-220`, `:235`); o excedente fica limitado a um `intervalo` mais as releituras de `ler`. Prazo esgotado sem rótulo para com a mesma mensagem de passo 5 de antes (testes `prazo_esgotado_*`, com `--espera 0`). Sem custo novo: só leituras do `gh` (R-CUSTO).
- Testes: 7 casos novos, determinísticos (`FORGE_FECHAR_INTERVALO=0`); `python3 -m unittest tests.test_fechar`: 54 testes, OK, 7,1 s. A suíte inteira fica com o QA e o pre-push (1201 OK no relato do autor).
- Documentação e fragmento: `docs/fechamento-integrador.md` (uso e passo 5) e `changelog.d/fechar-espera-rotulo.md` (tipo Adicionado) fiéis ao código; sem termo de projeto (R-NEUTRO). Commit único em Conventional Commits em português.
- Regras "ferramenta": `git diff --check` sem saída; `shellcheck` não está instalado nesta máquina, fica com o CI (pendência de ambiente, não de código).
- Segurança do controle de merge tem parecer próprio do security-engineer (E1.3); não refeito aqui.

## Achados

## Recomendações (não bloqueiam)
1. `bin/forge-fechar:192-196` e `:218` · com a opção, todo vermelho da Catraca vira pendente enquanto o rótulo não está, mesmo quando o PR não pede o rótulo (Catraca vermelha por corpo sem seção, por exemplo): o script espera até `--espera` (1800 s por padrão) e sai com a mensagem de rótulo ausente, que fala em título ou item marcado, sem imprimir a saída dos checks. Falha fechada, mas a mensagem engana e o tempo se perde. Sugestão: imprimir `$saida` antes desse `die` e dizer "a Catraca seguiu vermelha e o rótulo não apareceu".
2. `bin/forge-fechar:194` · o 10 é número mágico; sugestão: constante nomeada no topo (ou derivada de tempo, por exemplo 300 s), porque com `FORGE_FECHAR_INTERVALO` diferente de 30 a tolerância muda de duração.
3. `bin/forge-fechar:223` · cada volta do laço reimprime `[4] checks (até 1800s)`; em 30 min são 60 linhas iguais. Sugestão: imprimir o passo 4 uma vez e, nas voltas, uma linha curta ou nada.
4. `tests/test_fechar.py` (`catraca_vermelha_com_rotulo_aplicado_para_apos_a_tolerancia`) · o teste prova que para, não que a tolerância é de 10 leituras; sugestão: contar as chamadas de `pr checks` no registro e afirmar o limite.
