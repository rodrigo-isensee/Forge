---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-d1-versoes
commit: 0204884e682798a4a0b83e3538c75bff62248620
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-pv-d1-versoes (PR-VERDE D1, v0478 E57.59)

Primeira rodada, no head 0204884e (base d4f0b10a). Diff lido inteiro: `bin/forge-testes` (+79), `tests/test_testes_tocados.py` (classe `Versoes`, +144), dois arquivos de mutantes e o fragmento do changelog.

## Gatilhos
Gatilhos: ferramenta do envio do Forge (`bin/forge-testes`), execução de intérprete do PATH por subprocesso, escrita de log em `.forge/run/`.

## Resumo
- **A versão vem da configuração versionada, não do ambiente:** `bin/forge-testes:1061` só aceita `"\d+\.\d+"`, então o nome do log (`afetados-<X.Y>.log`, `:1112`) e o nome do intérprete (`python<X.Y>`) não recebem separador de caminho nem metacaractere. Sem versão, sai 2 (`:1085`), fechado na falha.
- **Intérprete:** `interprete` (`:1074`) resolve `python<X.Y>` pelo PATH e confere a versão com `-I -c`, sem casca (lista de argumentos). Quem controla o PATH já controla o `python3` que roda a ferramenta: não abre fronteira nova. Ausente vira `rc=ausente` e saída 1, nunca verde (`test_interprete_ausente_e_aviso_e_nao_verde`, `test_interprete_que_se_diz_de_outra_versao_nao_vale`).
- **Prova presa ao head:** recusa árvore suja, inclusive arquivo novo (`:1090`, `--untracked-files=all`), antes de gravar `head=<sha40>`; o log não atesta código que não está no commit. O comando roda o mesmo plano dirigido (`comando_dirigido`, que já recusa script por link) só trocando o intérprete (`:1109`); `--versoes` só combina com `--base` (`:1175`).
- **Escrita em `.forge/run/`:** `write_text` segue link, como o `testes.log` já fazia (`:616`). Caminho de ataque sem ganho: plantar o link exige uma branch que o autor roda, e quem escreve a branch já executa código nos testes que ela traz. Sem achado.
- **Teste rodado no head:** `tests.test_testes_tocados.Versoes`, 9 testes, OK. Suíte inteira: não rodada (brief); ainda não há PR nem execução do CI na branch, e o CI do PR é obrigatório para o merge.

## Pergunta do autor: `--versoes` leve em `hooks/pesado.py`
Basta o cartão PESADO-VERSOES-FORA-DA-FILA; não bloqueia este item. Sonda no head: `pesado.pesado("bin/forge-testes --versoes", PESADOS_DO_FORGE)` dá `False`, igual a `bin/forge-testes` sem opção; `--completa` dá `True`. Motivos: (1) o diff não toca `hooks/` nem caminho protegido, e o tema é carga da máquina (R-TETO), não um gatilho de R-SEGURANCA; (2) `--versoes` roda o plano dirigido, que nunca é a suíte completa (`planejar_afetados`), em série, uma vez por versão (hoje duas: 3.12 e 3.14), ou seja, no máximo o dobro de uma forma que já é leve; (3) ninguém ganha acesso nem contorna controle por isso: o pior caso é disputa de memória entre sessões, o que o cartão trata. Correção mínima do cartão: incluir `--versoes` entre as opções que tornam `bin/forge-testes` pesado em `hooks/pesado.py:296` (hoje `--completa` e `--vermelho`), com teste em que `bin/forge-testes --versoes`, `--vers` e `--versoes=x` contam como pesados; dono `devops-engineer`.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: varredor de segredos, SAST e linters de workflow fora do PATH (lacuna; o diff não toca workflow, segredo nem dependência).
