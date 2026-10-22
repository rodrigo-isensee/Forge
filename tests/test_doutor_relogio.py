"""RELOGIO-WSL: o aviso do relógio contra o `Date` do GitHub (hook `doutor` e `forge doutor` completo) e `desvio_do_relogio`
(CR-1 a CR-6 do modelo de ameaças). Sem rede: `FORGE_RELOGIO_REMOTO` (só com FORGE_PERMITE_LOCAL) e conexão falsa.

Arquivo próprio do item, para o commit dele se reverter sozinho. A `RelogioNoHook` repete o ambiente de `DoutorVersao` (do `test_doutor`)
em vez de herdar dele, para não rodar de novo os testes de versão.
"""
import datetime
import email.utils
import json
import os
import ssl
import subprocess
import sys
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import remoto_sem_manutencao  # noqa: E402
import apoio_versao_defasada as ap  # noqa: E402
import test_doutor as td  # noqa: E402

# Os caminhos vêm do `test_doutor`: o mapa do `bin/forge-testes` aciona um módulo pelos arquivos que ele cita com `RAIZ / "..."`
DOUTOR, HOOK, HOJE, VERSAO = td.DOUTOR, td.HOOK, td.HOJE, td.VERSAO
BIN = td.RAIZ / "bin"


class RelogioNoHook(ap.Base):
    """O aviso do relógio no mesmo cache `versao-nova`, uma vez por dia."""

    def setUp(self):
        super().setUp()
        self.publicado = self.tmp / "publicado.git"
        self.g("init", "-q", "--bare", "-b", "main", str(self.publicado), cwd=self.tmp)
        remoto_sem_manutencao(self.publicado)
        semente = self.tmp / "semente"
        self.g("clone", "-q", str(self.publicado), str(semente), cwd=self.tmp)
        (semente / "a").write_text("1\n", encoding="utf-8")
        self.g("add", "-A", cwd=semente)
        self.g("commit", "-q", "-m", "a", cwd=semente)
        self.g("push", "-q", "origin", "main", cwd=semente)
        self.semente = semente
        self.proj = self.tmp / "proj"
        self.g("init", "-q", "-b", "main", str(self.proj), cwd=self.tmp)
        (self.proj / ".forge").mkdir()
        (self.proj / ".forge/versao").write_text("0.1.0\n", encoding="utf-8")
        self.env.update(FORGE_HOJE=HOJE, FORGE_PERMITE_LOCAL="1", FORGE_REPO_URL=str(self.publicado))
        self.versao = VERSAO

    def tag(self, nome):
        self.g("tag", nome, cwd=self.semente)
        self.g("push", "-q", "origin", f"refs/tags/{nome}", cwd=self.semente)

    def stop(self):
        entrada = {"hook_event_name": "Stop", "session_id": "s1", "cwd": str(self.proj)}
        r = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(entrada), env=self.env, cwd=self.proj,
                           capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r

    def cache(self):
        arq = self.proj / ".forge/run/versao-nova"
        return json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else None

    def mais_nova(self):
        a, b, c = (int(n) for n in self.versao.split("."))
        return f"{a}.{b}.{c + 1}"

    def desvio(self, segundos):
        self.env["FORGE_RELOGIO_REMOTO"] = repr(time.time() + segundos)

    def test_relogio_atrasado_avisa_no_primeiro_stop_do_dia_e_o_segundo_fica_em_silencio(self):
        self.desvio(6840)
        r = self.stop()
        self.assertIn("O relógio deste computador está 114 min atrasado", r.stdout)
        self.assertIn("wsl --shutdown", r.stdout)
        self.assertEqual(list(json.loads(r.stdout)), ["systemMessage"])
        self.assertEqual(self.stop().stdout, "")
        self.assertEqual(self.cache()["relogio"]["data"], HOJE)

    def test_relogio_adiantado_diz_adiantado(self):
        self.desvio(-3600)
        self.assertIn("60 min adiantado", self.stop().stdout)

    def test_desvio_pequeno_nao_diz_nada(self):
        self.desvio(60)
        self.assertNotIn("relógio", self.stop().stdout)
        self.assertEqual(self.cache()["relogio"]["texto"], "")

    def test_relogio_junta_o_aviso_de_versao_nova_na_mesma_linha(self):
        self.tag(f"v{self.mais_nova()}")
        self.desvio(6840)
        saida = json.loads(self.stop().stdout)["systemMessage"]
        self.assertIn("Saiu a versão", saida)
        self.assertIn("O relógio deste computador", saida)

    def test_consulta_do_relogio_que_falha_nao_marca_o_dia_e_tenta_de_novo_depois_da_espera(self):
        self.env["FORGE_RELOGIO_REMOTO"] = "lixo"
        self.assertNotIn("relógio", self.stop().stdout)
        cache = self.cache()
        self.assertNotIn("relogio", cache)
        self.assertIn("relogio_falhou_em", cache)
        self.desvio(6840)
        self.assertNotIn("relógio", self.stop().stdout, "dentro da espera depois da falha: não consulta")
        cache["relogio_falhou_em"] = time.time() - 3600
        (self.proj / ".forge/run/versao-nova").write_text(json.dumps(cache), encoding="utf-8")
        self.assertIn("O relógio deste computador", self.stop().stdout)

    def test_com_a_consulta_de_versao_que_falhou_o_relogio_nem_e_consultado(self):
        self.env["FORGE_REPO_URL"] = str(self.tmp / "nao-existe.git")
        self.desvio(6840)
        self.assertNotIn("relógio", self.stop().stdout)
        self.assertNotIn("relogio", self.cache())

    def test_consulta_desligada_nao_consulta_o_relogio(self):
        self.env["FORGE_VERIFICAR_VERSAO"] = "0"
        self.desvio(6840)
        self.assertNotIn("relógio", self.stop().stdout)
        self.assertNotIn("relogio", self.cache())

    def test_o_ponto_de_injecao_so_vale_com_o_marcador_de_teste(self):
        sys.path.insert(0, str(BIN))
        self.addCleanup(sys.path.remove, str(BIN))
        import forge_versoes
        env = {"FORGE_REPO_URL": "https://github.com/exemplo/Forge", "FORGE_RELOGIO_REMOTO": repr(time.time() + 6840)}
        with mock.patch.dict(os.environ, env), mock.patch.object(forge_versoes.http.client, "HTTPSConnection") as conexao:
            os.environ.pop("FORGE_PERMITE_LOCAL", None)
            os.environ.pop("FORGE_VERIFICAR_VERSAO", None)
            conexao.return_value.getresponse.return_value.getheader.return_value = email.utils.formatdate(time.time() + 20, usegmt=True)
            desvio = forge_versoes.desvio_do_relogio(forge_versoes.url_do_forge(), 3)
        self.assertTrue(conexao.called, "sem o marcador, a variável é ignorada e a consulta é a de verdade")
        self.assertLess(abs(desvio - 20), 5)

    def test_o_doutor_completo_mostra_o_aviso_e_o_rapido_nao(self):
        self.proj = self.tmp / "proj-completo"
        self.g("init", "-q", "-b", "main", str(self.proj), cwd=self.tmp)
        sem_gh = self.tmp / "sem-gh"
        sem_gh.mkdir()
        (sem_gh / "gh").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        (sem_gh / "gh").chmod(0o755)
        (self.proj / ".forge").mkdir()
        (self.proj / ".forge/versao").write_text(self.versao + "\n", encoding="utf-8")
        self.env.update(PATH=f"{sem_gh}:{self.env['PATH']}")
        self.desvio(6840)
        completo = subprocess.run([sys.executable, str(DOUTOR), str(self.proj)], env=self.env, cwd=self.proj, capture_output=True,
                                  text=True, timeout=60, stdin=subprocess.DEVNULL)
        self.assertIn("O relógio deste computador está 114 min atrasado", completo.stdout)
        rapido = subprocess.run([sys.executable, str(DOUTOR), "--rapido", str(self.proj)], env=self.env, cwd=self.proj,
                                capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
        self.assertNotIn("relógio", rapido.stdout)


class DesvioDoRelogio(ap.Base):
    """`desvio_do_relogio` (CR-1 a CR-6 do modelo de ameaças): só `HEAD` em https, sem redirecionamento, host público, prazo total, `Date` defensivo."""

    def setUp(self):
        super().setUp()
        sys.path.insert(0, str(BIN))
        self.addCleanup(sys.path.remove, str(BIN))
        import forge_versoes
        self.v = forge_versoes
        patcher = mock.patch.dict(os.environ, {"FORGE_REPO_URL": "https://github.com/exemplo/Forge"})
        patcher.start()
        self.addCleanup(patcher.stop)
        for nome in ("FORGE_PERMITE_LOCAL", "FORGE_VERIFICAR_VERSAO", "FORGE_RELOGIO_REMOTO"):
            os.environ.pop(nome, None)

    def consultar(self, cabecalho, url="https://github.com/exemplo/Forge", limite=3, status=200):
        """O desvio e o mock da conexão, com a resposta falsa (`cabecalho` None = sem `Date`)."""
        with mock.patch.object(self.v.http.client, "HTTPSConnection") as conexao:
            resposta = conexao.return_value.getresponse.return_value
            resposta.status = status
            resposta.getheader.return_value = cabecalho
            return self.v.desvio_do_relogio(url, limite), conexao

    def test_le_o_date_com_fuso_e_devolve_remoto_menos_local(self):
        desvio, conexao = self.consultar(email.utils.formatdate(time.time() + 7200, usegmt=True))
        self.assertLess(abs(desvio - 7200), 5)
        conexao.return_value.request.assert_called_once()
        self.assertEqual(conexao.return_value.request.call_args.args[0], "HEAD")

    def test_aceita_deslocamento_explicito(self):
        agora = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3)))
        desvio, _ = self.consultar(email.utils.format_datetime(agora + datetime.timedelta(seconds=90)))
        self.assertLess(abs(desvio - 90), 5)

    def test_cabecalho_ausente_ilegivel_sem_fuso_ou_absurdo_da_none_sem_excecao(self):
        ruins = (None, "", "garbage", "Wed, 21 Oct 12345 07:52:36 GMT", "Wed, 21 Oct 2026 07:52:36", "x" * 1_000_000,
                 "Wed, 21 Oct 2026 07:52:36 -0000")
        for valor in ruins:
            with self.subTest(valor=str(valor)[:30]):
                desvio, _ = self.consultar(valor)
                self.assertIsNone(desvio)

    def test_desvio_de_dez_anos_vira_nao_consegui_conferir(self):
        desvio, _ = self.consultar(email.utils.formatdate(time.time() + 10 * 365 * 86400, usegmt=True))
        self.assertIsNone(desvio)

    def test_redirecionamento_nao_e_seguido_e_so_ha_uma_conexao(self):
        desvio, conexao = self.consultar(email.utils.formatdate(time.time() + 600, usegmt=True), status=302)
        self.assertEqual(conexao.call_count, 1)
        self.assertEqual(conexao.return_value.request.call_count, 1)
        self.assertLess(abs(desvio - 600), 5)

    def test_host_local_sem_ponto_ip_ou_porta_diferente_da_none_sem_abrir_conexao(self):
        for url in ("https://127.0.0.1/x", "https://localhost/x", "https://10.0.0.1/x", "https://intranet/x", "https://127.1/x",
                    "https://2130706433/x", "https://github.com:8443/x", "https://[::1]/x", "http://github.com/x",
                    "https://usuario:senha@github.com/x", "https://a..b.com/x", "/tmp/repositorio-local"):
            with self.subTest(url=url):
                desvio, conexao = self.consultar(email.utils.formatdate(time.time() + 600, usegmt=True), url=url)
                self.assertIsNone(desvio)
                self.assertFalse(conexao.called)

    def test_consulta_desligada_nao_abre_conexao(self):
        os.environ["FORGE_VERIFICAR_VERSAO"] = "0"
        desvio, conexao = self.consultar(email.utils.formatdate(time.time() + 600, usegmt=True), url=self.v.url_do_forge())
        self.assertIsNone(desvio)
        self.assertFalse(conexao.called)

    def test_conexao_que_nunca_responde_estoura_no_prazo_total(self):
        def pendurar(*_):
            time.sleep(3)
            raise OSError("cortada depois do prazo do teste")  # a thread do pedido termina limpa, sem ruído no fim da suíte
        with mock.patch.object(self.v.http.client, "HTTPSConnection") as conexao:
            conexao.return_value.getresponse.side_effect = pendurar
            inicio = time.monotonic()
            desvio = self.v.desvio_do_relogio("https://github.com/exemplo/Forge", 0.3)
        self.assertIsNone(desvio)
        self.assertLess(time.monotonic() - inicio, 2)

    def test_erro_de_rede_da_none(self):
        with mock.patch.object(self.v.http.client, "HTTPSConnection", side_effect=OSError("sem rede")):
            self.assertIsNone(self.v.desvio_do_relogio("https://github.com/exemplo/Forge", 3))

    def test_o_pedido_nao_leva_credencial_nem_cookie_e_valida_o_certificado(self):
        _, conexao = self.consultar(email.utils.formatdate(time.time(), usegmt=True))
        cabecalhos = {k.lower() for k in conexao.return_value.request.call_args.kwargs.get("headers", {})}
        self.assertFalse(cabecalhos & {"authorization", "cookie", "proxy-authorization"})
        self.assertEqual(conexao.call_args.args[0], "github.com")
        self.assertEqual(conexao.call_args.kwargs["context"].verify_mode, ssl.CERT_REQUIRED)

    def test_texto_so_acima_de_300_segundos_e_sem_eco_do_cabecalho(self):
        self.assertEqual(self.v.texto_de_relogio(300), "")
        self.assertEqual(self.v.texto_de_relogio(-300), "")
        self.assertEqual(self.v.texto_de_relogio(None), "")
        self.assertIn("5 min atrasado", self.v.texto_de_relogio(301))
        self.assertIn("120 min adiantado", self.v.texto_de_relogio(-7200))


if __name__ == "__main__":
    unittest.main()
