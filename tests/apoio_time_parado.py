"""O `reason` do time parado do `vigia` (emenda da ADR 0003, item 7; F4, v0481 E34.6): as partes cartões, PR sem agente e
preso, nesta ordem, separadas por `; `, e o sufixo fixo; o teto de 280 caracteres o teste confere à parte. Lido pelo laço das
fixtures (`test_hooks`) e pelos testes do F4 (`test_hook_vigia_f4`)."""
_CARTOES = r"(\d+ cartões disponíveis(, primeiro [A-Za-z0-9.-]{1,16})?)"
_PRS = r"(PR sem agente: #\d+ [A-Za-zçã/]+(, #\d+ [A-Za-zçã/]+){0,2}( e mais \d+)?)"
_PRESO = r"(preso há mais de 10 min: [a-z][a-z0-9:-]{0,23} a[0-9a-f]{16} há \d+ min( e mais \d+)?)"
REASON_DO_TIME_PARADO = (f"time parado: ({_CARTOES}(; {_PRS})?(; {_PRESO})?|{_PRS}(; {_PRESO})?|{_PRESO}); "
                         "retome sem esperar o dono")
TETO_DO_REASON = 280
