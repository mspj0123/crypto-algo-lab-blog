"""
Notionの開発ログDBからJekyllブログ記事を自動生成するスクリプト。

必要な環境変数:
  NOTION_TOKEN      : Notion Integration Token
  NOTION_DATABASE_ID: 対象DBのID（デフォルト: 3518f0b7-804f-8052-be43-c3881a470443）

使用方法:
  python scripts/sync_notion.py
"""

import os
import re
import sys
from datetime import datetime, timezone

import requests

NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")
NOTION_DATABASE_ID = os.environ.get(
    "NOTION_DATABASE_ID", "3518f0b7-804f-8052-be43-c3881a470443"
)
POSTS_DIR = os.path.join(os.path.dirname(__file__), "..", "_posts")

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}


def get_db_properties() -> dict:
    """Notion DBのプロパティ一覧を取得する。"""
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json().get("properties", {})


def get_pages() -> list[dict]:
    """Notion DBからページ一覧を取得する。「ブログ公開」チェックボックスがあればフィルタリングする。"""
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"

    # DBに「ブログ公開」プロパティがあればフィルター適用
    try:
        db_props = get_db_properties()
        has_publish_flag = "ブログ公開" in db_props and db_props["ブログ公開"].get("type") == "checkbox"
    except Exception:
        has_publish_flag = False

    payload: dict = {
        "sorts": [{"property": "日付", "direction": "descending"}],
    }
    if has_publish_flag:
        payload["filter"] = {
            "property": "ブログ公開",
            "checkbox": {"equals": True},
        }
        print("「ブログ公開」フィルターを適用します")
    else:
        print("「ブログ公開」プロパティなし — 全ページを取得します")

    resp = requests.post(url, headers=HEADERS, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json().get("results", [])


def get_page_blocks(page_id: str) -> list[dict]:
    """ページのブロック（本文）を取得する。"""
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json().get("results", [])


def extract_text(rich_text: list[dict]) -> str:
    """rich_text配列からプレーンテキストを抽出する。"""
    return "".join(t.get("plain_text", "") for t in rich_text)


def block_to_markdown(block: dict) -> str:
    """NotionブロックをMarkdown文字列に変換する。"""
    btype = block.get("type", "")
    data = block.get(btype, {})
    text = extract_text(data.get("rich_text", []))

    if btype == "paragraph":
        return f"{text}\n\n" if text else "\n"
    elif btype == "heading_1":
        return f"# {text}\n\n"
    elif btype == "heading_2":
        return f"## {text}\n\n"
    elif btype == "heading_3":
        return f"### {text}\n\n"
    elif btype == "bulleted_list_item":
        return f"- {text}\n"
    elif btype == "numbered_list_item":
        return f"1. {text}\n"
    elif btype == "code":
        lang = data.get("language", "")
        return f"```{lang}\n{text}\n```\n\n"
    elif btype == "quote":
        return f"> {text}\n\n"
    elif btype == "divider":
        return "---\n\n"
    else:
        return f"{text}\n\n" if text else ""


def slugify(title: str) -> str:
    """タイトルをファイル名用スラグに変換する（英数字・ハイフンのみ）。"""
    slug = re.sub(r"[^\w\s-]", "", title.lower())
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug or "post"


def get_prop(props: dict, key: str) -> str:
    """プロパティから値を安全に取得する。"""
    prop = props.get(key, {})
    ptype = prop.get("type", "")
    if ptype == "title":
        return extract_text(prop.get("title", []))
    elif ptype == "rich_text":
        return extract_text(prop.get("rich_text", []))
    elif ptype == "date":
        date_obj = prop.get("date") or {}
        return (date_obj.get("start") or "")[:10]
    elif ptype == "multi_select":
        return ",".join(s["name"] for s in prop.get("multi_select", []))
    elif ptype == "select":
        sel = prop.get("select") or {}
        return sel.get("name", "")
    return ""


def page_to_post(page: dict) -> tuple[str, str] | None:
    """
    Notionページをファイル名とMarkdownコンテンツのタプルに変換する。
    スキップすべき場合はNoneを返す。
    """
    props = page.get("properties", {})

    title = get_prop(props, "タイトル") or get_prop(props, "Name")
    if not title:
        return None

    date_str = get_prop(props, "日付")
    if not date_str:
        created = page.get("created_time", "")
        date_str = created[:10] if created else datetime.now(timezone.utc).strftime("%Y-%m-%d")

    categories = get_prop(props, "カテゴリ") or "開発ログ"
    tags = get_prop(props, "タグ") or ""
    summary = get_prop(props, "概要") or ""

    # Front matter
    cat_list = "[" + ", ".join(c.strip() for c in categories.split(",")) + "]"
    tag_list = "[" + ", ".join(t.strip() for t in tags.split(",") if t.strip()) + "]" if tags else "[]"

    front_matter = f"""---
layout: post
title: "{title}"
date: {date_str}
categories: {cat_list}
tags: {tag_list}
---

"""

    # ページ本文
    blocks = get_page_blocks(page["id"])
    body = "".join(block_to_markdown(b) for b in blocks)

    if not body.strip() and summary:
        body = f"{summary}\n\n"

    content = front_matter + body + "\n---\n\n*本記事は技術的な実装紹介を目的としており、投資を推奨するものではありません。*\n"

    filename = f"{date_str}-{slugify(title)}.md"
    return filename, content


def main():
    if not NOTION_TOKEN:
        print("ERROR: NOTION_TOKEN が設定されていません", file=sys.stderr)
        sys.exit(1)

    os.makedirs(POSTS_DIR, exist_ok=True)

    print(f"Notion DB ({NOTION_DATABASE_ID}) からページを取得中...")
    pages = get_pages()
    print(f"{len(pages)} 件のページを取得しました")

    created = 0
    for page in pages:
        result = page_to_post(page)
        if result is None:
            continue
        filename, content = result
        filepath = os.path.join(POSTS_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  作成: {filename}")
        created += 1

    print(f"\n完了: {created} 件の記事を生成しました")


if __name__ == "__main__":
    main()
