"""IoC 値のデファング・リファング処理。

- refang(): デファング表記を解除し、実際の IoC 値に戻す（STIX 保存用）
- defang(): IoC 値をデファング表記に変換する（Markdown レポート等の安全表示用）

両関数は冪等であり、defang(refang(x)) の形で正規化できる。
"""

import re

from ioc_collector.models import IoCType

# デファング表記のパターン（refang 対象）
_REFANG_PATTERNS: list[tuple[str, str]] = [
    # hxxp/hxxps → http/https（大文字小文字不問）
    (r"(?i)\bhxxps://", "https://"),
    (r"(?i)\bhxxp://", "http://"),
    # [.] / [dot] / (dot) → .
    (r"\[\.\]", "."),
    (r"(?i)\[dot\]", "."),
    (r"(?i)\(dot\)", "."),
    # [@] / [at] → @
    (r"\[@\]", "@"),
    (r"(?i)\[at\]", "@"),
    # [:] → :
    (r"\[:\]", ":"),
]

# デファング不要な IoCType（そのまま表示して安全なもの）
_NO_DEFANG_TYPES = frozenset({
    IoCType.FILE_HASH_MD5,
    IoCType.FILE_HASH_SHA1,
    IoCType.FILE_HASH_SHA256,
    IoCType.FILE_NAME,
    IoCType.PROCESS_NAME,
})


def refang(value: str) -> str:
    """デファング表記を解除し、実際の IoC 値を返す。

    ネット上の記事ではドット置換・スキーム置換等でデファングされていることが多い。
    STIX パターンに使用する前にこの関数で正規化する。

    冪等: refang(refang(x)) == refang(x)
    """
    result = value
    for pattern, replacement in _REFANG_PATTERNS:
        result = re.sub(pattern, replacement, result)
    return result


def defang(value: str, ioc_type: IoCType) -> str:
    """IoC 値をデファング表記に変換する（Markdown レポートへの安全な記載用）。

    入力値がすでにデファング済みでも二重デファングにならないよう、
    内部で refang() による正規化を行ってからデファングする。

    ハッシュ値・ファイル名・プロセス名はそのまま返す（デファング不要）。
    """
    # 正規化（二重デファング防止）
    normalized = refang(value)

    if ioc_type in _NO_DEFANG_TYPES:
        return normalized

    if ioc_type == IoCType.URL:
        # スキームを置換してからドットを置換
        result = re.sub(r"^https://", "hxxps://", normalized, flags=re.IGNORECASE)
        result = re.sub(r"^http://", "hxxp://", result, flags=re.IGNORECASE)
        result = result.replace(".", "[.]")
        return result

    # IPV4_ADDR, DOMAIN_NAME, OTHER, その他: ドットを置換
    return normalized.replace(".", "[.]")
