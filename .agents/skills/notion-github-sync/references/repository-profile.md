# Repository profile and state

Read this reference when creating, repairing, or validating a repository's
Notion sync configuration.

## Profile

The repository root file `.notion-github-sync.json` uses this shape:

```json
{
  "version": 1,
  "repository": "owner/name",
  "branch": "main",
  "notion": {
    "data_source": "collection://...",
    "title_property": "笔记",
    "path_property": "GitHub 路径",
    "category_property": "分类",
    "status_property": "状态",
    "ready_values": ["已掌握"],
    "sync_property": "同步到 GitHub",
    "last_edited_property": "最后编辑"
  },
  "paths": {
    "state": ".notion-sync-state.json",
    "readme": "README.md",
    "assets_template": "{note_dir}/assets/{note_stem}"
  },
  "readme": {
    "start_marker": "<!-- NOTES_INDEX:START -->",
    "end_marker": "<!-- NOTES_INDEX:END -->",
    "section_by_category": {
      "服务器与 Linux": "开发环境与服务器"
    }
  }
}
```

Unknown categories may use their category name as the README section. Missing
or blank paths are not publishable. A Notion rich-text path such as
`Notes/基础/[Linux基础.md](http://Linux基础.md)` is normalized to
`Notes/基础/Linux基础.md`; the URL is not used.

## State

The state file is versioned with the notes:

```json
{
  "version": 1,
  "notes": [
    {
      "page_url": "https://app.notion.com/p/...",
      "title": "Linux 基础",
      "section": "开发环境与服务器",
      "path": "Notes/基础/Linux基础.md",
      "notion_last_edited": "2026-09-23T16:47:10.189Z",
      "content_sha": "git-blob-sha"
    }
  ]
}
```

The state file is an audit and conflict-detection aid, not the source of note
content. Git history records which commit changed each state entry.

## Conflict test

For an existing entry:

1. `notion_changed = fetched_last_edited != recorded_last_edited`
2. `github_changed = current_blob_sha != recorded_content_sha`
3. If both are true, require a user choice.
4. If only Notion changed, publish the new Notion version.
5. If only GitHub changed, preserve GitHub and report the divergence.
6. If neither changed, skip the note.

For a new entry, require an explicit user request or a configured ready state.

## Script commands

```bash
python scripts/notion_sync.py normalize raw.md --output note.md --title "标题"
python scripts/notion_sync.py validate note.md --repo-root .
python scripts/notion_sync.py update-readme README.md \
  --entries note-index.json --output README.md
python -m unittest discover -s tests -v
```
