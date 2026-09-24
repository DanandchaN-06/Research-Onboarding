import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "notion_sync.py"
SPEC = importlib.util.spec_from_file_location("notion_sync", SCRIPT_PATH)
notion_sync = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = notion_sync
SPEC.loader.exec_module(notion_sync)


class NormalizeMarkdownTests(unittest.TestCase):
    def test_converts_notion_table_to_github_markdown(self):
        source = """<table header-row="true">
<tr>
<td>命令</td>
<td>说明</td>
</tr>
<tr>
<td>`git status`</td>
<td>查看状态</td>
</tr>
</table>"""

        normalized = notion_sync.normalize_markdown(source, title="Git 基础")

        self.assertIn(
            "| 命令 | 说明 |\n"
            "| --- | --- |\n"
            "| `git status` | 查看状态 |",
            normalized,
        )
        self.assertNotIn("<table", normalized)
        self.assertTrue(normalized.startswith("# Git 基础\n\n"))

    def test_converts_toggles_and_callouts_to_quotes(self):
        source = """<details>
<summary>基础拾遗</summary>
第一条
第二条
</details>

<callout icon="💡">
记住这一点
</callout>"""

        normalized = notion_sync.normalize_markdown(source)

        self.assertIn(
            "> **基础拾遗**\n>\n> 第一条\n> 第二条",
            normalized,
        )
        self.assertIn("> 💡 记住这一点", normalized)
        self.assertNotIn("<details>", normalized)
        self.assertNotIn("<callout", normalized)

    def test_normalizes_shell_fences_and_block_spacing(self):
        source = """# 标题
段落
lua
```lua
git status
```
## 下一节
正文"""

        normalized = notion_sync.normalize_markdown(source)

        self.assertEqual(
            "# 标题\n\n"
            "段落\n\n"
            "```bash\n"
            "git status\n"
            "```\n\n"
            "## 下一节\n\n"
            "正文\n",
            normalized,
        )


class ValidateMarkdownTests(unittest.TestCase):
    def test_rejects_temporary_notion_images_and_unbalanced_fences(self):
        markdown = """# 标题

![](https://prod-files-secure.s3.us-west-2.amazonaws.com/image.png)

```bash
echo hello
"""

        issues = notion_sync.validate_markdown(markdown)
        codes = {issue.code for issue in issues}

        self.assertIn("temporary-image-url", codes)
        self.assertIn("unbalanced-fence", codes)

    def test_accepts_existing_relative_image(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            note_dir = root / "Notes" / "基础"
            image_dir = note_dir / "assets" / "Git基础"
            image_dir.mkdir(parents=True)
            (image_dir / "图.png").write_bytes(b"png")
            note_path = note_dir / "Git基础.md"
            markdown = (
                "# Git 基础\n\n"
                "![示意图](assets/Git基础/图.png)\n"
            )
            note_path.write_text(markdown, encoding="utf-8")

            issues = notion_sync.validate_markdown(
                markdown,
                document_path=note_path,
                repo_root=root,
            )

        self.assertEqual([], issues)


class UpdateReadmeTests(unittest.TestCase):
    def test_replaces_only_generated_note_index_and_is_idempotent(self):
        readme = """# Research Onboarding

介绍。

<!-- NOTES_INDEX:START -->
旧内容
<!-- NOTES_INDEX:END -->

## 路线图

保持不变。
"""
        entries = [
            {
                "section": "开发环境与服务器",
                "title": "Linux 基础",
                "path": "Notes/基础/Linux基础.md",
            },
            {
                "section": "开发环境与服务器",
                "title": "Git 基础",
                "path": "Notes/基础/Git基础.md",
            },
        ]

        updated = notion_sync.update_readme_index(readme, entries)
        updated_again = notion_sync.update_readme_index(updated, entries)

        self.assertIn(
            "### 开发环境与服务器\n\n"
            "- [Linux 基础](Notes/基础/Linux基础.md)\n"
            "- [Git 基础](Notes/基础/Git基础.md)",
            updated,
        )
        self.assertIn("## 路线图\n\n保持不变。", updated)
        self.assertEqual(updated, updated_again)

    def test_requires_both_readme_markers(self):
        with self.assertRaisesRegex(ValueError, "README markers"):
            notion_sync.update_readme_index(
                "# README\n",
                [{"section": "基础", "title": "Git", "path": "Git.md"}],
            )


class CliTests(unittest.TestCase):
    def test_load_entries_accepts_json_object_with_notes_key(self):
        payload = json.dumps(
            {
                "notes": [
                    {"section": "基础", "title": "Git", "path": "Git.md"}
                ]
            },
            ensure_ascii=False,
        )

        self.assertEqual(
            [{"section": "基础", "title": "Git", "path": "Git.md"}],
            notion_sync.load_entries(payload),
        )

    def test_normalizes_notion_link_in_repository_path_property(self):
        self.assertEqual(
            "Notes/基础/Linux基础.md",
            notion_sync.normalize_repo_path(
                "Notes/基础/[Linux基础.md](http://Linux基础.md)"
            ),
        )
        self.assertEqual(
            "Notes/基础/Git基础.md",
            notion_sync.normalize_repo_path("Notes/基础/Git基础.md"),
        )

    def test_rejects_repository_path_traversal(self):
        with self.assertRaisesRegex(ValueError, "relative"):
            notion_sync.normalize_repo_path("../README.md")


if __name__ == "__main__":
    unittest.main()
