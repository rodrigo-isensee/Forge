---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-meta85-forge-check
commit: 6853e0ee2ac9c19305db2419ddbcfbb3f5dcf1f0
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 1
bugs_baixos: 0
data: 2026-11-19
---
# QA: v0478 META85 em `bin/forge-check` (E34.5)

Head testado `6853e0ee` (o brief); o clone avançou por fast-forward até `f84d9f28` só com os pareceres de review e segurança.

## Achados
- A1 (bloqueante) tests/test_meta85_item_arquivos.py:50 · `forge-testes --vermelho` sai rc=2: na base o teste lê `json["arquivos_do_item"]` e dá KeyError (erro, não falha), "sem veredito" (R-QA). Troque por asserção que falhe na base, p. ex. `assertEqual(json.loads(saida).get("arquivos_do_item"), 10)`.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Cartão 1: entrega exige `--mutantes` e `--pronto` | `test_meta85_entrega` (12 testes): sem logs, log ausente, vazio, outro head, rc=1, acima do teto, linhas vazias nas pontas, só o pronto faltando, fora da etapa codigo, sem código, forma nova recusa as opções | log vazio, ausente, maior que 8 MiB, head divergente | passou (12/12); vermelho: 10 provam, 2 de não cobrança passam na base por natureza |
| Cartão 2: `parecer delta` com `revalida:` | `test_meta85_revalida` (4 testes): barrou, aprovado com domínio intacto, aprovado com domínio mudado, review aprovado com código mudado | domínio mudado × intacto | passou (4/4); 4/4 provam |
| Cartão 3: `classe` barra mais de 10 arquivos | `test_meta85_item_arquivos` (6 testes): 10 passa, 11 recusa, `--json`, acompanhantes não contam, módulo do portão em `tests/` conta, base ilegível | 10 × 11, base ilegível | passou (6/6); 4 provam, 1 dá erro na base (A1), 1 não prova (10 arquivos passa também na base) |

## Provas
- Vermelho: `bin/forge-testes --vermelho eca1d21b --modulos test_meta85_entrega,test_meta85_revalida,test_meta85_item_arquivos` (sem `--modulos` a suíte estoura o prazo do sandbox):
  `contagem: não prova (passa na base)=4; prova (asserção)=17; sem veredito=1` · `tests.test_meta85_item_arquivos.ItemAteDezArquivos.test_testes_mutantes_changelog_e_pareceres_nao_contam · H=ok · B=erro · sem veredito` · rc=2.
- Mutantes M1 a M21 (`bin/forge-mutante` nas 4 specs, `--processos 4`): M1 a M21 `morreu`, nenhum sobrevivente, rc=0, `rev=6853e0ee2ac9`. `--cobertura --base eca1d21b`: todas as condições do diff `coberta`, nada sem mutante.
- Testes que o CI pega: `tests.test_forge.AntiDuplicacao` OK (2); `test_testes_tocados` OK (162, 1 pulado pelo sandbox, sem `/proc`); `forge-testes --texto` (inclui `test_metricas_texto`, `test_orcamento_instrucao`) rc=0, 217 OK.
- Suíte inteira não rodada local; vale o check-run `bateria` do mesmo sha no CI do PR.

## Cenários e resultado real
Caminho feliz, bordas (10/11 arquivos, log vazio, teto de 8 MiB, base ilegível) e erros cobertos acima. Sem permissões nem acessibilidade (CLI). Médio A1 vira cartão se o autor não corrigir antes do reenvio; o código de produção está certo (mutantes e testes verdes).
