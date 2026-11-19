---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-sandbox-controle
commit: 64fca89083f7549aa5ea97ed4e716bec049f1306
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-19
---
# QA: v0478 E29.14 (trava de escrita do sandbox, revalidação no head 64fca890)

## Achados
- A1 (bloqueante, resolvido) tests/test_apoio_sandbox.py:77 · o teste de sonda do bwrap agora está na classe Sondas e roda (H=ok no vermelho); mutantes M1 e M2 morrem.
- A2 (recomendado, aberto) tests/test_sandbox_controle.py:178 · "e o hook grava" no nome do teste de bwrap é verdade trivial; já provado na Estrutura. Não bloqueia.
- A3 (recomendado, aberto) .github/workflows/ci.yml:1 · o CI não sonda bubblewrap; os 2 testes de sandbox pulam aqui (Operation not permitted) e só valem com o check-run `bateria` do mesmo sha sem pulo (no CI, exigir reprova). Não bloqueia; cite o run no PR.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A3 modelo nega os caminhos de controle | Estrutura.test_modelo_de_projeto_nega_os_quatro_caminhos_de_controle | permissão (denyWrite) | passou; prova (asserção) |
| A3 Forge via patch, arquivo versionado fora | Estrutura (3 testes) | permissão, limite | passou |
| 0 byte não afrouxa; soltura grava null | ControleVazio (6 testes) | vazio, temporário plantado | passou; 6 provas (asserção) |
| forge-init e início de sessão criam os arquivos | ControleVazio (2 testes) | arquivo ausente | passou; prova |
| recusa por find -delete, tar e chmod | SandboxNegaEscrita (2) | permissão | pulado (bwrap sem namespace); sem veredito local |
| sonda falta_bwrap | Sondas.test_bwrap_ausente... | vazio, erro, timeout | passou; roda agora |

## Provas
Vermelho (`forge-testes --vermelho 03448b3d --modulos test_apoio_sandbox,test_sandbox_controle --prazo 300`), rc=0:
```
contagem: não prova (passa na base)=28; prova (asserção)=7; pulado=2
```
Mutantes (`forge-mutante tests/mutantes/v0479-sandbox-controle.json --base 03448b3d`), rc=0:
```
base=03448b3d8050 mb=03448b3d8050 rev=64fca89083f7
M1 M2 M4 M5 M6 M7 M8 M9 M10 M11 M12 M13 M14 · morreu (13 de 13; M3 não aparece na saída)
```
CI: não há run para o sha (sem PR); a prova da suíte inteira é o check-run `bateria` do PR.
