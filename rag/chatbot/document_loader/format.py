from enum import Enum


class Format(Enum):
    MARKDOWN = "markdown"
    JSON = "json"  # JSON 형식을 추가합니다.


SUPPORTED_FORMATS = {
    Format.MARKDOWN.value: [
        # Markdown을 위한 분리자들
        "\n#{1,6} ",
        "```\n",
        "\n\\*\\*\\*+\n",
        "\n---+\n",
        "\n___+\n",
        "\n\n",
        "\n",
        " ",
        "",
    ],
    Format.JSON.value: [
        # JSON은 일반적으로 전체를 하나의 문서로 처리하므로,
        # 분리자가 필요없습니다. 빈 문자열을 사용하여 전체 내용을 하나로 반환합니다.
        ""
    ]
}


def get_separators(format: str):
    """
    지정한 포맷에 대한 분리자 리스트를 반환합니다.

    Args:
        format (str): 분리자를 가져올 포맷.

    Returns:
        list[str]: 지정한 포맷에 대한 분리자 리스트.

    Raises:
        KeyError: 지원되지 않는 포맷인 경우.
    """
    separators = SUPPORTED_FORMATS.get(format)
    if separators is None:
        raise KeyError(format + " is a not supported format")
    return separators
