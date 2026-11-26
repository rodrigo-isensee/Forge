---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-s5-cabecalho
commit: e216aa71cd0e5e720ce00da880a6e4adfd8464fd
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 E25.4 (S5, cabeçalho dos pareceres na autorização)

Rodada 1, completa. Diff lido: `3c833f3f..e216aa71` (merge-base com a develop): `bin/forge_autorizacao.py` (`frente`), `tests/test_autorizacao.py` (4 testes), `tests/mutantes/v0481-s5-cabecalho.json` (M1 a M4), fragmento do changelog. CI do head (runs 45856837729 e 45856837897) vermelho; causas lidas no log em A1 e A2. Sem linha `ci:`.

## Gatilhos
Gatilhos: autenticação ou autorização (`frente` é o leitor do veredito dos pareceres em `fora_do_revisado` e `commit_do_ramo`, `bin/forge_autorizacao.py:214`, `:218`, `:387`).

## Achados
- A1 (bloqueante) tests/mutantes/v0479-pv-a2-concessao-3.json:16 · Suíte parte 4/5 vermelha no CI (3.12 e 3.14): M18 desta spec e M27 de v0479-pv-a2-concessao-4.json:26 têm o `de` fora da fonte; as guardas PV-A2 da autorização ficam sem mutante. Alinhar as duas specs no mesmo commit.
- A2 (bloqueante) bin/forge_autorizacao.py:232 · Catraca vermelha no head (mesmo achado A1 do QA): a guarda da base `texto.startswith('---\n')` (base:230) sai sem mutante declarado que a cubra; declare-o (ou a isenção da spec) como a catraca pede.
- A3 (recomendado) bin/forge_autorizacao.py:221 · Parecer sem fecho agora some da lista em vez de contar: um parecer reprovado velho, anterior ao Commit e sem o `---` final, deixa de barrar (base: inativa; head: ativa). Falhar fechado quando o arquivo achado pelo grep não tem cabeçalho legível.

## Sondas
- S1 · python3 -m unittest tests.test_forge_mutante.ConferirTodas.test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes · espera: OK · obtido: FAIL, v0479-pv-a2-concessao-3.json: M18 e v0479-pv-a2-concessao-4.json: M27 com o `de` fora da fonte
- S2 · catraca do CI no head e216aa71 (run 45856837897) · espera: verde · obtido: R-QA guarda de bin/forge_autorizacao.py mudada sem mutante declarado, apagada, base:230 texto.startswith('---\n')

## Detalhe dos achados
**A1** · evidência: `tests/mutantes/v0479-pv-a2-concessao-3.json:16` (M18, `de` = `if texto.startswith("---\n") else ""`) e `tests/mutantes/v0479-pv-a2-concessao-4.json:26` (M27, `de` = `if ": " in linha)`); as duas linhas sumiram de `frente`. Caminho: não é ataque; as guardas "parecer sem frontmatter não conta" e "campo vazio não derruba a leitura" da autorização ficam sem prova de que um teste as segura, e o CI barra o merge. Severidade: média (controle de autorização sem a rede de mutantes). Correção mínima: no mesmo commit, M18 passa a mirar `if linhas[0] != "---":` e M27 `if ": " in campo)` (ou remover os dois, já cobertos por M1 e M4 da spec nova, com a pendência registrada como o teste aceita). Esforço P. Dono: o autor (E25.1).

**A2** · evidência: log da catraca no head; a condição nova é coberta por M1, mas a catraca casa o texto da base. Correção mínima e dono: os do A1 do QA; não repito.

**A3** · evidência: `bin/forge_autorizacao.py:221` filtra `p.get("branch") == ramo`, e `frente` sem fecho agora devolve `{}` (`:237`). Sonda local (arquivo no scratchpad, biblioteca padrão, fixture do `ItemPresoAoCommit`): `docs/devops/velho.md` com `tipo: revisao-devops`, `branch: <ramo>`, `parecer: reprovado`, sem o `---` final, commitado antes do Commit revisado; head: `ativa`, base: `inativa`. O mesmo vale para um segundo parecer de um tipo exigido. Caminho de ataque: fraco, porque apagar o arquivo dá o mesmo efeito na base e a escrita em `docs/` é por pasta (hook `conformidade`); o parecer escrito depois do Commit já falha fechado em `:214`, e o `forge-check docs` acusa "frontmatter sem fechamento". Fica como perda de falha fechada por engano: um parecer quebrado deixa de barrar e ninguém é avisado. Severidade: baixa. Correção mínima: em `fora_do_revisado`, arquivo achado pelo grep em `PARECERES` com `frente(...) == {}` devolve um motivo ("Parecer sem cabeçalho legível"); cobre também o CRLF no topo, que a base já ignorava. Esforço P. Dono: o autor.

**Aperta, neutro e afrouxa (o pedido do brief):**
- Aperta: sem fecho, o corpo não vale como cabeçalho (`:237`): na base, `parecer: aprovado` no corpo sobrescrevia o `reprovado` do topo (teste `Frente.test_sem_fecho_ou_sem_tracos_no_topo_e_vazio`, M3). Linha ` ---` ou `\t--- ` fecha (`:235`); na base não fechava e o corpo entrava (teste `Frente.test_fecho_com_espaco_vale_e_o_corpo_nao_entra` e o `ItemPresoAoCommit` novo).
- Strip no fecho em vez da comparação exata: confere, é o mais estrito. Com a exata, ` ---` não fecharia, o corpo voltaria a contar até o próximo `---` e mais pareceres cairiam no "sem fecho" do A3. É o fecho do `ler_frontmatter` (`bin/forge-check:265`), então autorização e validador concordam onde o cabeçalho acaba.
- Neutro: o topo exige `---` exato (`:232`), como a base (`startswith("---\n")`); o validador aceita `---` com espaço (A3 do QA): só disponibilidade, nunca aprovação a mais. CRLF, valor com espaço no fim, `chave:valor` sem espaço, chave repetida (a última vale): iguais na base e no head.
- Afrouxa: o pretendido, `---8<---`, `----`, `---x` não cortam mais o cabeçalho (o defeito de disponibilidade do S5); quem escreve isso é o dono do parecer, que já decide o veredito, e o `forge-check docs` recusa a linha. O não pretendido é o A3.

Provas locais: `tests.test_autorizacao` 25 OK no head; na base (`3c833f3f` com o teste do head), os 4 testes novos falham. `bin/forge-mutante tests/mutantes/v0481-s5-cabecalho.json`: M1 a M4 morrem (M4 por erro do teste sob o mutante). CI do head: suíte parte 4/5 (A1), catraca (A2), `bateria (pareceres)` à espera do parecer de review (processual, não é defeito); o resto verde.

Fora do domínio: `tests/test_autorizacao.py:374` `FIXA ={` (estilo; A2 do QA, tech-lead).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, o módulo tocado, o executor de mutantes do Forge, os logs do CI e uma sonda comparativa local (biblioteca padrão). Sem varredura de segredo ou dependência: o diff não traz dependência, configuração nem segredo.
