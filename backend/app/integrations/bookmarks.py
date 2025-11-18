"""
Bookmark import from various browsers (HTML/JSON formats)
"""
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path
from loguru import logger
import json
from html.parser import HTMLParser


class BookmarkHTMLParser(HTMLParser):
    """Parser for Netscape Bookmark File Format (used by Chrome, Firefox, Edge)"""

    def __init__(self):
        super().__init__()
        self.bookmarks = []
        self.current_folder = []
        self.in_dt = False
        self.current_link = None

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        if tag == "h3":
            # Folder/category
            self.in_dt = True
        elif tag == "a":
            # Bookmark link
            self.current_link = {
                "url": attrs_dict.get("href", ""),
                "title": "",
                "add_date": attrs_dict.get("add_date"),
                "icon": attrs_dict.get("icon"),
                "folder": "/".join(self.current_folder) if self.current_folder else "Bookmarks",
                "tags": []
            }
        elif tag == "dl":
            # Start of folder contents
            pass

    def handle_endtag(self, tag):
        if tag == "h3":
            self.in_dt = False
        elif tag == "a" and self.current_link:
            self.bookmarks.append(self.current_link)
            self.current_link = None
        elif tag == "dl" and self.current_folder:
            self.current_folder.pop()

    def handle_data(self, data):
        data = data.strip()
        if not data:
            return

        if self.in_dt:
            # This is a folder name
            self.current_folder.append(data)
        elif self.current_link is not None:
            # This is a bookmark title
            self.current_link["title"] = data


def parse_html_bookmarks(file_path: str) -> List[Dict[str, Any]]:
    """
    Parse bookmarks from HTML file (Netscape Bookmark File Format)

    Supports:
    - Chrome bookmark export
    - Firefox bookmark export
    - Edge bookmark export
    - Safari bookmark export (with some variations)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        parser = BookmarkHTMLParser()
        parser.feed(html_content)

        logger.info(f"Parsed {len(parser.bookmarks)} bookmarks from HTML file")
        return parser.bookmarks

    except Exception as e:
        logger.error(f"Failed to parse HTML bookmarks: {e}")
        return []


def parse_json_bookmarks(file_path: str, browser: str = "chrome") -> List[Dict[str, Any]]:
    """
    Parse bookmarks from JSON file

    Args:
        file_path: Path to JSON file
        browser: Browser type (chrome, firefox, edge)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        bookmarks = []

        if browser in ["chrome", "edge"]:
            # Chrome/Edge JSON format
            bookmarks = _parse_chrome_json(data)
        elif browser == "firefox":
            # Firefox JSON format
            bookmarks = _parse_firefox_json(data)

        logger.info(f"Parsed {len(bookmarks)} bookmarks from JSON file")
        return bookmarks

    except Exception as e:
        logger.error(f"Failed to parse JSON bookmarks: {e}")
        return []


def _parse_chrome_json(data: Dict, folder_path: str = "Bookmarks") -> List[Dict[str, Any]]:
    """Parse Chrome/Edge JSON bookmark format"""
    bookmarks = []

    def traverse(node, path):
        if node.get("type") == "url":
            # This is a bookmark
            add_date = node.get("date_added")
            if add_date:
                # Chrome stores timestamps in microseconds since epoch
                add_date = str(int(add_date) // 1000000)

            bookmarks.append({
                "url": node.get("url", ""),
                "title": node.get("name", ""),
                "add_date": add_date,
                "folder": path,
                "tags": [],
                "metadata": {
                    "id": node.get("id"),
                    "guid": node.get("guid")
                }
            })
        elif node.get("type") == "folder":
            # This is a folder, recurse into children
            folder_name = node.get("name", "")
            new_path = f"{path}/{folder_name}" if path else folder_name

            for child in node.get("children", []):
                traverse(child, new_path)

    # Chrome bookmarks have roots: bookmark_bar, other, synced
    roots = data.get("roots", {})
    for root_name, root_node in roots.items():
        if root_name not in ["sync_transaction_version", "version"]:
            traverse(root_node, root_name.replace("_", " ").title())

    return bookmarks


def _parse_firefox_json(data: Dict) -> List[Dict[str, Any]]:
    """Parse Firefox JSON bookmark format"""
    bookmarks = []

    def traverse(node, path="Bookmarks"):
        if node.get("type") == "text/x-moz-place":
            # This is a bookmark
            add_date = node.get("dateAdded")
            if add_date:
                # Firefox stores timestamps in microseconds
                add_date = str(int(add_date) // 1000000)

            bookmarks.append({
                "url": node.get("uri", ""),
                "title": node.get("title", ""),
                "add_date": add_date,
                "folder": path,
                "tags": node.get("tags", "").split(",") if node.get("tags") else [],
                "metadata": {
                    "id": node.get("id"),
                    "guid": node.get("guid"),
                    "keyword": node.get("keyword")
                }
            })
        elif node.get("type") == "text/x-moz-place-container":
            # This is a folder
            folder_name = node.get("title", "")
            new_path = f"{path}/{folder_name}" if folder_name else path

            for child in node.get("children", []):
                traverse(child, new_path)

    traverse(data)
    return bookmarks


def normalize_bookmark(bookmark: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize bookmark data into standard format for the knowledge graph

    Returns:
        Dictionary suitable for creating a Node
    """
    # Convert Unix timestamp to datetime
    created_at = datetime.utcnow()
    if bookmark.get("add_date"):
        try:
            timestamp = int(bookmark["add_date"])
            created_at = datetime.fromtimestamp(timestamp)
        except (ValueError, OverflowError):
            pass

    # Extract domain from URL for categorization
    domain = ""
    if bookmark.get("url"):
        from urllib.parse import urlparse
        try:
            parsed = urlparse(bookmark["url"])
            domain = parsed.netloc
        except:
            pass

    # Generate tags from folder path
    folder_tags = []
    if bookmark.get("folder"):
        folder_tags = [
            tag.strip().lower()
            for tag in bookmark["folder"].split("/")
            if tag.strip() and tag.strip().lower() != "bookmarks"
        ]

    # Combine with existing tags
    all_tags = list(set(folder_tags + bookmark.get("tags", [])))

    return {
        "title": bookmark.get("title") or bookmark.get("url", "Untitled"),
        "content": f"Bookmark: {bookmark.get('title', '')}\nURL: {bookmark.get('url', '')}\nFolder: {bookmark.get('folder', '')}",
        "url": bookmark.get("url"),
        "node_type": "bookmark",
        "source": "bookmark_import",
        "created_at": created_at,
        "tags": all_tags,
        "metadata": {
            "domain": domain,
            "folder": bookmark.get("folder", ""),
            "icon": bookmark.get("icon"),
            **(bookmark.get("metadata", {}))
        }
    }


async def import_bookmarks_file(file_path: str, browser: str = "auto") -> Dict[str, Any]:
    """
    Import bookmarks from a file

    Args:
        file_path: Path to bookmark file
        browser: Browser type (auto, chrome, firefox, edge) or file format (html, json)

    Returns:
        Dictionary with import results
    """
    path = Path(file_path)

    if not path.exists():
        return {
            "success": False,
            "error": f"File not found: {file_path}",
            "bookmarks": []
        }

    # Detect file format
    file_extension = path.suffix.lower()

    try:
        if file_extension == ".html" or browser == "html":
            bookmarks = parse_html_bookmarks(file_path)
        elif file_extension == ".json" or browser == "json":
            # Try to detect browser from JSON structure
            with open(file_path, 'r') as f:
                data = json.load(f)

            if "roots" in data:
                browser_type = "chrome"
            elif "type" in data and data.get("type") == "text/x-moz-place-container":
                browser_type = "firefox"
            else:
                browser_type = browser if browser != "auto" else "chrome"

            bookmarks = parse_json_bookmarks(file_path, browser_type)
        else:
            return {
                "success": False,
                "error": f"Unsupported file format: {file_extension}",
                "bookmarks": []
            }

        # Normalize bookmarks
        normalized = [normalize_bookmark(bm) for bm in bookmarks]

        return {
            "success": True,
            "bookmarks": normalized,
            "count": len(normalized),
            "source_file": file_path
        }

    except Exception as e:
        logger.error(f"Failed to import bookmarks: {e}")
        return {
            "success": False,
            "error": str(e),
            "bookmarks": []
        }


async def categorize_bookmarks(bookmarks: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Categorize bookmarks by domain, folder, or topic

    Returns:
        Dictionary of categories with bookmark lists
    """
    categories = {
        "by_domain": {},
        "by_folder": {},
        "uncategorized": []
    }

    for bookmark in bookmarks:
        # Categorize by domain
        domain = bookmark.get("metadata", {}).get("domain", "unknown")
        if domain not in categories["by_domain"]:
            categories["by_domain"][domain] = []
        categories["by_domain"][domain].append(bookmark)

        # Categorize by folder
        folder = bookmark.get("metadata", {}).get("folder", "uncategorized")
        if folder not in categories["by_folder"]:
            categories["by_folder"][folder] = []
        categories["by_folder"][folder].append(bookmark)

    return categories
