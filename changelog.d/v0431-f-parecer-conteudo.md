### Mudado
- O parecer fica preso ao conteúdo do seu domínio, não ao commit (PARECER-CONTEUDO, P3 da 0.43.1, decisão do dono de 08/11): o `forge-check pr` (e o hook `parecer`, o `forge-fechar` e a catraca `--modo pareceres`, que o chamam) só dá o parecer por desatualizado quando o delta desde o `commit:` toca arquivo do domínio do tipo dele (review e QA: tudo; segurança: tudo menos documentação e testes; devops: pipeline, contêiner, IaC, hooks do git, `bin/`, `scripts/` e dependências), e diz qual arquivo do domínio mudou. O teste do QA aprovado (commits só de teste, mesmo blob do `commit:` do QA) não derruba o review. `dominio_mais: [caminho, pasta/]` no parecer alarga o domínio.
- O rótulo `afrouxa-regra` fica preso aos arquivos protegidos (P9): a catraca o mantém enquanto os arquivos protegidos (e os de configuração que as regras leem) têm o mesmo blob e modo do head rotulado e os testes não pioram mais do que pioravam nele; push que não muda arquivo protegido não o derruba.

### Adicionado
- `forge-check parecer delta <parecer> [--ate REF]`: o diff desde o `commit:` do parecer só nos arquivos do domínio do tipo dele, para a revalidação ler só o que mudou; só leitura.
