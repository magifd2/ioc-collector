import pytest
from ioc_collector.defang import refang, defang
from ioc_collector.models import IoCType


class TestRefang:
    """デファング解除のテスト。"""

    @pytest.mark.parametrize("defanged, expected", [
        # [.] 形式
        ("192.0.2[.]1", "192.0.2.1"),
        ("evil[.]example[.]com", "evil.example.com"),
        # [dot] 形式
        ("evil[dot]example[dot]com", "evil.example.com"),
        ("evil[DOT]example.com", "evil.example.com"),
        # (dot) 形式
        ("evil(dot)example(dot)com", "evil.example.com"),
        # hxxp/hxxps 形式
        ("hxxp://evil.com/path", "http://evil.com/path"),
        ("hxxps://evil.com/path", "https://evil.com/path"),
        ("HXXP://evil.com/path", "http://evil.com/path"),
        # [at] / [@] 形式（メールアドレス）
        ("user[at]evil.com", "user@evil.com"),
        ("user[@]evil.com", "user@evil.com"),
        # [:] 形式（ポート番号）
        ("192.0.2.1[:]8080", "192.0.2.1:8080"),
        # 複合パターン
        ("hxxp://evil[.]example[.]com[:]8080/path", "http://evil.example.com:8080/path"),
        ("hxxps://192.0.2[.]1/payload[.]exe", "https://192.0.2.1/payload.exe"),
        # すでにデファングされていない値は変更なし
        ("192.0.2.1", "192.0.2.1"),
        ("evil.example.com", "evil.example.com"),
        ("http://evil.com", "http://evil.com"),
        # ハッシュ値は変更なし
        ("d41d8cd98f00b204e9800998ecf8427e", "d41d8cd98f00b204e9800998ecf8427e"),
    ])
    def test_refang(self, defanged, expected):
        assert refang(defanged) == expected

    def test_idempotent(self):
        """refang は冪等であること。"""
        value = "hxxp://evil[.]com"
        assert refang(refang(value)) == refang(value)


class TestDefang:
    """デファング化のテスト（Markdown 安全表示用）。"""

    @pytest.mark.parametrize("value, ioc_type, expected", [
        # IP アドレス（全ドット置換）
        ("192.0.2.1", IoCType.IPV4_ADDR, "192[.]0[.]2[.]1"),
        # ドメイン（全ドット置換）
        ("evil.example.com", IoCType.DOMAIN_NAME, "evil[.]example[.]com"),
        # URL（スキーム置換 + 全ドット置換）
        ("http://evil.example.com/path", IoCType.URL, "hxxp://evil[.]example[.]com/path"),
        ("https://evil.example.com/path", IoCType.URL, "hxxps://evil[.]example[.]com/path"),
        # ファイルハッシュ（デファング不要）
        ("d41d8cd98f00b204e9800998ecf8427e", IoCType.FILE_HASH_MD5, "d41d8cd98f00b204e9800998ecf8427e"),
        ("da39a3ee5e6b4b0d3255bfef95601890afd80709", IoCType.FILE_HASH_SHA1, "da39a3ee5e6b4b0d3255bfef95601890afd80709"),
        ("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", IoCType.FILE_HASH_SHA256, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
        # ファイル名（デファング不要）
        ("malware.exe", IoCType.FILE_NAME, "malware.exe"),
        # プロセス名（デファング不要）
        ("svchost_fake.exe", IoCType.PROCESS_NAME, "svchost_fake.exe"),
        # OTHER（全ドット置換）
        ("some.evil.domain.example", IoCType.OTHER, "some[.]evil[.]domain[.]example"),
    ])
    def test_defang(self, value, ioc_type, expected):
        assert defang(value, ioc_type) == expected

    def test_already_defanged_input_is_normalized(self):
        """すでにデファング済みの値を渡しても二重デファングにならないこと。"""
        # hxxp://evil[.]com → refang → http://evil.com → defang → hxxp://evil[.]com
        result = defang("hxxp://evil[.]com", IoCType.URL)
        assert result == "hxxp://evil[.]com"
        # ドットが二重に置換されないこと
        assert "[.][.]" not in result

    def test_already_defanged_ip_is_normalized(self):
        # refang → 192.0.2.1 → defang → 192[.]0[.]2[.]1（二重デファングにならない）
        result = defang("192.0.2[.]1", IoCType.IPV4_ADDR)
        assert result == "192[.]0[.]2[.]1"
        assert "[.][.]" not in result

    def test_idempotent(self):
        """defang(refang(x)) が idempotent であること。"""
        url = "hxxp://evil[.]example[.]com"
        result1 = defang(refang(url), IoCType.URL)
        result2 = defang(refang(result1), IoCType.URL)
        assert result1 == result2
