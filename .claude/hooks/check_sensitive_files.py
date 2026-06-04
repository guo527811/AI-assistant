"""
PreToolUse Hook：拦截对敏感文件的编辑/写入操作

受保护的文件模式：
  - *.env（环境变量文件，含密钥）
  - *.pem（私钥文件）
  - *.key（密钥文件）
  - credentials.*（凭证文件）
  - secrets.*（秘密文件）

使用方式：在 settings.json 的 PreToolUse hook 中配置
"""

import sys
import json
import os

# 敏感文件黑名单（glob 模式匹配后缀）
SENSITIVE_PATTERNS = [
    '.env',
    '.pem',
    '.key',
    'credentials.json',
    'secrets.json',
    'id_rsa',
    'id_ed25519',
    '.npmrc',
    '.pypirc',
]


def is_sensitive(file_path: str) -> bool:
    """检查文件路径是否匹配敏感模式"""
    basename = os.path.basename(file_path)
    for pattern in SENSITIVE_PATTERNS:
        if basename.endswith(pattern) or basename == pattern:
            return True
    return False


def main():
    try:
        # Hook 输入：JSON 格式的工具调用信息
        input_data = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        # 无法解析，放行
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # 只拦截编辑和写入类工具
    if tool_name not in ("Edit", "Write"):
        sys.exit(0)

    # 获取目标文件路径
    file_path = tool_input.get("file_path", "")

    if not file_path:
        sys.exit(0)

    if is_sensitive(file_path):
        print(
            f"\n[Hook: check_sensitive_files] 操作已拦截！\n"
            f"  文件: {file_path}\n"
            f"  原因: 该文件属于敏感文件（密钥/凭证/环境变量），不允许编辑或覆盖。\n"
            f"  建议: 如果确实需要修改，请手动操作。\n",
            file=sys.stderr,
        )
        sys.exit(1)  # 非零退出码 = 拦截

    sys.exit(0)  # 零退出码 = 放行


if __name__ == "__main__":
    main()
