---
tipo: revisao-seguranca
contrato: 1
pedido: teto-bloqueia-carga-alta
branch: melhoria/teto-bloqueia-carga-alta
commit: 345da10
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-15
---
# Review de segurança: hook `agentes` bloqueia qualquer disparo com carga alta

Escopo: `git diff origin/develop..origin/melhoria/teto-bloqueia-carga-alta -- hooks/ tests/hooks/agentes/` (HEAD do remoto 1330688; o código revisado é o de 345da10, e 1330688 só acrescenta o parecer independente). Defensivo e estático; as sondas rodaram numa cópia descartável (`git archive` de `hooks/`, `bin/`, `templates/projeto/.forge/` em `$TMPDIR/probe`), com `/proc` simulado em `FORGE_PROC` como as fixtures fazem. Nenhum código tocado. **Parecer: aprovado**, sem bloqueante; três recomendações.

## Gatilhos
`R-SEGURANCA`: mudança em hook de controle do Forge (`hooks/agentes.py`, aplica `R-TETO`). O controle endurece (barra mais), não afrouxa; sem segredo, rede, dado pessoal ou dependência nova.

## Sondas (rc do hook; 0 = deixa passar, 2 = barra)
Projeto sintético com `.git` e `.forge/versao`, zero agentes ativos, base `loadavg 1.0`, `MemAvailable 8 GB`.

| Sonda | rc | Leitura |
|---|---|---|
| base sã | 0 | libera |
| load 7.0 | 2 | barra (a trava funciona) |
| `loadavg` ausente / vazio / texto / `nan` / negativo | 0 | **falha aberta** |
| `meminfo` ausente / vazio / sem a linha `MemAvailable` / texto / bytes inválidos | 0 | **falha aberta** |
| só uma medida ausente, a outra extrema (load 99 sem meminfo; 100 kB sem loadavg) | 0 | **falha aberta** (exige as duas medidas) |
| `loadavg` `inf` | 2 | barra |
| `MemAvailable` 0 kB ou -5 kB | 2 | barra |
| config `teto_agentes:-1, teto_maximo:-3` com load 7 | 2 | barra; valor inválido cai no modelo e não desliga a trava |
| config `teto_agentes:"abc", teto_maximo:"x"` com load 1 | 0 | ignora o texto, libera como o normal |
| config `teto_agentes:999, teto_maximo:999` com load 7 | 2 | teto alto não desliga a trava |
| config `teto_agentes:0, teto_maximo:0` com load 1 | 0 | ignora |
| config JSON quebrado ou `[]` | 0 | **falha aberta**; `erros.log` registra `JSONDecodeError`/`ValueError` (ADR 0003) |

## Respostas às perguntas
1. **`/proc` ilegível ou malformado: falha aberta.** `medir()` devolve `None` para `OSError`, `ValueError`, `IndexError` e `StopIteration`, e `carga_alta` exige as duas medidas (`hooks/agentes.py`, `medir`, `carga_alta`). Aceitável: é o critério da `R-TETO` ("sem leitura, piso de 3") e do ADR 0003 (erro interno libera); o hook é guarda de disciplina, não fronteira de segurança. Quem poderia forçar a falta de leitura precisaria controlar `FORGE_PROC` do processo do hook (só o dono) ou o `/proc` do sistema; sem caminho realista de ataque. Os valores `nan` (falha aberta, porque toda comparação é falsa) e negativos de load não saem do kernel; informativo.
2. **`teto_agentes` e `teto_maximo` adulterados:** valor negativo, zero ou texto é descartado por `inteiro()` em `hooks/_comum.py` (`Hook.config`, `v >= 1`, sem bool) e vira padrão do modelo; valor alto não desliga a trava (a checagem vem antes de `calcular_teto`). Config corrompida (JSON ou tipo) falha aberta e fica em `erros.log`: pré-existente, não é efeito desta mudança. Sem novo vetor.
3. **Negação de serviço por carga externa: real, não malicioso.** A própria máquina de desenvolvimento do dono, medida durante este review (`/proc/loadavg` 7.40 com 8 CPUs; `MemAvailable` 1,93 GB), já estaria barrada com 0 ou 1 agente ativo. Em WSL2 e em contêiner, `loadavg` e `meminfo` podem refletir o hospedeiro e não só o Forge; carga de fora ou de uma compilação do dono bloqueia o time por tempo indefinido, e a trava vale até para o primeiro agente. Quem ataca: ninguém precisa; quem perde: o fluxo, que só se destrava esperando ou com `hooks_desligados` (desliga o hook todo, inclusive o teto e a deduplicação). Severidade **média** (disponibilidade; é o comportamento exigido pela `R-TETO`, por isso não bloqueia o merge).

## Achados
1. **Média, disponibilidade.** Sem saída graduada para carga externa persistente (acima). Evidência: `hooks/agentes.py`, em `lancar`, bloqueio após `medir()`; sonda load 7.0 rc 2 com zero ativos. Correção mínima, sem implementar aqui (decisão do dono, `R-DECISAO`, porque mexe em regra com ID): (a) mensagem do bloqueio dizer como o dono proceder (já cita "espere a carga baixar"; acrescentar o próprio load e a opção abaixo); (b) escape só do dono, no padrão de `FORGE_GUARDA_ABERTA` (variável no ambiente do processo, que o agente não define), por exemplo `FORGE_CARGA_LIVRE=1`, que pula só a trava de carga e deixa teto e deduplicação; registrar o uso no log do hook; (c) alternativa mais pesada: considerar `loadavg` por CPU (`load/nproc`), o que muda o limite da regra e exige emenda da `R-TETO`. Esforço P (b). Dono: `software-architect` e `tech-lead` (regra), com o usuário decidindo.
2. **Baixa, robustez.** `carga_alta` não distingue "sem leitura" de "leitura sã": carga e memória ausentes juntas ou separadas liberam. Aceito pela regra; sugestão opcional: se só uma medida faltar e a outra já ultrapassar o limite, barrar (sonda: load 99 sem `meminfo` rc 0). Esforço P. Dono: `backend-engineer`. Registrado também no review independente.
3. **Informativa.** `hooks_desligados` na config do projeto desliga o hook e, com ele, a trava de carga; é pré-existente e já está sob a guarda do `conformidade`. Sem ação nesta entrega.

Casos de abuso para o `qa-engineer` (já cobertos pelas fixtures da mudança, exceto o último): load 6,5 com zero ativos barra; memória 1,5 GB com um ativo barra; teto fixo 5 com load 7 barra; load 5 libera; sem `/proc` libera. Sugestão de teste novo, se o achado 2 for adotado: uma medida ausente com a outra acima do limite.

## Riscos aceitos e ferramentas
Nenhum risco aceito gravado: o parecer é `aprovado`; os achados 1 e 2 são recomendações para o dono decidir. Ferramentas: nenhuma varredura automática aplicável (Python do hook sem dependência nova; sem segredo, workflow nem imagem no diff). Sondas manuais com `python3` e o shell; `gitleaks`, `semgrep` e `zizmor` não foram usados (não se aplicam a este diff).
