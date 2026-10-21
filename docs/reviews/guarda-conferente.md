---
tipo: review
contrato: 1
pedido: guarda-conferente
branch: melhoria/guarda-conferente
commit: b050d634b5e34cd4844ac80e0e21f3ed98df8906
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-21
---
# Review: GUARDA-CONFERENTE (M6, hook recusa o conferente sem o cabeçalho da mensagem)

Escopo: `f911dfa...b050d63` (base f911dfa0b2ebd9692d45c374f9ff4bab8523ed6b), 3 arquivos em 3 commits (`hooks/agentes.py`, `tests/test_guarda_conferente.py`, `changelog.d/guarda-conferente.md`). Quem revisa não é o autor (instância distinta, D-ETAPAS-INST). Comparei o diff com E1 e E2 do pedido e com a seção M6 de `docs/propostas/aq/m1-m11.md`.

Veredito sobre `b050d63`: **REPROVADO**, 1 achado bloqueante e 3 recomendados. Volta ao autor; este revisor não corrige o diff.

## Ferramentas (saída citada, não refeita)
- `python3 -m unittest tests.test_guarda_conferente`: `Ran 14 tests in 0.929s` / `OK`.
- A suíte completa e o `scripts/validar-plugin.sh` ficam com o pre-push, o QA e o CI; esta revisão não os rodou.
- Segurança (hook de bloqueio, R-SEGURANCA): parecer próprio do `security-engineer` em `docs/security/`, em paralelo; não refeito aqui.

## O que está conforme
- A guarda só vale para `forge:conferente` (mesmo nome de `hooks/conformidade.json:11`); outro agente segue o caminho antigo (teste `test_outro_agente_passa_sem_cabecalho`).
- Só forma: nenhum acesso ao arquivo nem cálculo de hash; a recusa usa `bloquear("R-BRIEF", ...)` e manda gerar a mensagem com `forge-check brief mensagem`, como pede E1.
- A recusa vem antes do teste de relançamento e da reserva de vaga em `lancar`, então um lançamento recusado não ocupa o teto (R-TETO).
- Primeira linha exata `modo: brief|entrega` (com `fullmatch`), coerente com `agents/conferente.md:13-16`; mensagem com dois blocos passa (o `Arquivo:` e o `Brief-sha256:` são procurados em qualquer linha); hash exige 64 hex minúsculos sem continuação, igual à saída do `forge-check`; CRLF passa (sonda local).
- Testes: 9 recusas (sem modo, modo fora da primeira linha, modo desconhecido, sem Arquivo, Arquivo fora de docs/briefs/, sem hash, hash curto, hash não hexadecimal, prompt vazio) e 5 passagens (saída real do `brief mensagem`, Arquivo relativo, modo entrega, vários blocos, outro agente). Cobre o que E2 pede.
- Fragmento `changelog.d/guarda-conferente.md` corresponde à branch; docstring do hook atualizada; nada específico de projeto (R-NEUTRO); nada com custo (R-CUSTO); endurece, sem afrouxar regra.

## Achados
- A1 (bloqueante) hooks/agentes.py:103 · `\S*docs/briefs/\S+` recusa Arquivo absoluto com espaço (sonda: `/mnt/c/Users/R/Meus Projetos/docs/briefs/p-x-1.md`), saída real do `brief mensagem` nesse caso: conferente inalcançável. Aceitar o caminho com espaço e testar.

## Recomendações (fora do bloco de achados)
1. `tests/test_guarda_conferente.py:74` · O teste da saída real usa um diretório temporário sem espaço, por isso o A1 não apareceu. Junto da correção, um caso com a raiz do cenário num diretório com espaço (ou o caminho absoluto com espaço substituído na saída real), como pede a regra de teste novo para bug corrigido.
2. Commits: `b6da56c` removeu a leitura de `description` em `lancar` e `fc3a1a9` a devolveu; o commit intermediário não passa nos testes do relançamento. Sem efeito se a integração for por squash; se não for, vale juntar os dois na volta (sem `--amend` nem `--force` na branch já enviada, então só registro).
3. `agents/jarvis.md:64` descreve a mensagem ao conferente, mas não diz que o hook agora a recusa sem o cabeçalho. Uma frase ali evita que o Jarvis descubra a guarda só pelo bloqueio.
