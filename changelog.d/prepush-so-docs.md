### Alterado
- O pre-push do modelo de projeto pula o pre-push.local (lint e typecheck) quando todo arquivo enviado é de docs/** ou termina em .md; qualquer outro arquivo, branch nova, tag, apagar ref ou falha do git roda tudo, e o CI segue completo (PREPUSH-SO-DOCS, afrouxa)
