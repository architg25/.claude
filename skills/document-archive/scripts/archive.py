#!/usr/bin/env python3
"""Save documents (Excalidraw diagrams, Google Docs, etc.) into a local git archive."""

import argparse
import base64
import json
import struct
import sys
import urllib.request
import zlib
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ARCHIVE_ROOT = Path.home() / "Git" / "documents-archive"


# --- Excalidraw decryption ---


def split_buffers(data: bytes) -> list[bytes]:
    """Parse Excalidraw's concat-buffers format: [4B version][4B len][data]..."""
    cursor = 0
    version = struct.unpack_from(">I", data, cursor)[0]
    cursor += 4
    if version > 1:
        raise ValueError(f"Unsupported buffer version: {version}")
    chunks = []
    while cursor < len(data):
        chunk_size = struct.unpack_from(">I", data, cursor)[0]
        cursor += 4
        chunks.append(data[cursor : cursor + chunk_size])
        cursor += chunk_size
    return chunks


def _decode_key(key_b64url: str) -> bytes:
    padded = key_b64url + "=" * (-len(key_b64url) % 4)
    return base64.urlsafe_b64decode(padded)


def _decrypt_modern(encrypted_blob: bytes, key_b64url: str) -> dict:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    chunks = split_buffers(encrypted_blob)
    raw_key = _decode_key(key_b64url)
    aesgcm = AESGCM(raw_key)
    compressed = aesgcm.decrypt(chunks[1], chunks[2], None)
    inner_chunks = split_buffers(zlib.decompress(compressed))
    return json.loads(inner_chunks[1].decode("utf-8"))


def _decrypt_legacy(encrypted_blob: bytes, key_b64url: str) -> dict:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    raw_key = _decode_key(key_b64url)
    aesgcm = AESGCM(raw_key)
    plaintext = aesgcm.decrypt(encrypted_blob[:12], encrypted_blob[12:], None)
    return json.loads(plaintext.decode("utf-8"))


def decrypt_excalidraw_url(url: str) -> dict:
    """Fetch and decrypt an Excalidraw shared link."""
    fragment = urlparse(url).fragment
    if not fragment.startswith("json="):
        raise ValueError(f"Not a valid Excalidraw share link: {url}")
    parts = fragment[len("json=") :].split(",", 1)
    if len(parts) != 2:
        raise ValueError(f"Expected #json=<docId>,<key> format")
    doc_id, key_b64url = parts

    api_url = f"https://json.excalidraw.com/api/v2/{doc_id}"
    req = urllib.request.Request(
        api_url, headers={"User-Agent": "document-archive/1.0"}
    )
    with urllib.request.urlopen(req) as resp:
        blob = resp.read()

    try:
        return _decrypt_modern(blob, key_b64url)
    except Exception:
        return _decrypt_legacy(blob, key_b64url)


def analyze_excalidraw(scene: dict) -> dict:
    """Extract text content and element metadata for title/description generation."""
    elements = [e for e in scene.get("elements", []) if not e.get("isDeleted")]
    text_els = [
        e for e in elements if e.get("type") == "text" and e.get("text", "").strip()
    ]
    text_els.sort(key=lambda e: e.get("fontSize", 20), reverse=True)

    type_counts = Counter(e.get("type", "unknown") for e in elements)

    return {
        "text_elements": [e["text"].strip() for e in text_els],
        "frame_labels": [
            e.get("name", "").strip()
            for e in elements
            if e.get("type") == "frame" and e.get("name", "").strip()
        ],
        "element_counts": dict(type_counts),
        "total_elements": len(elements),
    }


# --- Generic save ---


def write_meta(meta_path: Path, meta: dict):
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")


def build_meta(
    title: str,
    description: str,
    source: str,
    doc_type: str,
    tags: list[str],
    initiative: str,
) -> dict:
    return {
        "title": title,
        "description": description,
        "source": source,
        "type": doc_type,
        "saved": date.today().isoformat(),
        "tags": tags,
        "initiative": initiative,
    }


# --- Subcommands ---


def cmd_save_excalidraw(args):
    inp = args.input.strip()

    if inp.startswith("http"):
        scene = decrypt_excalidraw_url(inp)
        source = inp
        default_name = urlparse(inp).fragment.split("=", 1)[1].split(",")[0][:20]
    else:
        path = Path(inp).expanduser().resolve()
        with open(path) as f:
            scene = json.load(f)
        source = str(path)
        default_name = path.stem.replace(".excalidraw", "")

    if args.analyze:
        analysis = analyze_excalidraw(scene)
        analysis["source"] = source
        print(json.dumps(analysis, indent=2))
        return

    name = args.name or default_name
    tags = [t.strip() for t in args.tags.split(",")] if args.tags else []

    out_dir = ARCHIVE_ROOT / "excalidraw"
    out_dir.mkdir(parents=True, exist_ok=True)

    scene_path = out_dir / f"{name}.excalidraw"
    meta_path = out_dir / f"{name}.meta.json"

    if scene_path.exists():
        print(f"Warning: {scene_path} already exists, overwriting.", file=sys.stderr)

    scene_path.write_text(json.dumps(scene, indent=2), encoding="utf-8")
    write_meta(
        meta_path,
        build_meta(
            title=name.replace("-", " ").title(),
            description=args.description or "",
            source=source,
            doc_type="excalidraw",
            tags=tags,
            initiative=args.initiative or "",
        ),
    )

    print(f"Saved: {scene_path}")
    print(f"Meta:  {meta_path}")


def cmd_save_google_doc(args):
    content_path = Path(args.content_file).expanduser().resolve()
    if not content_path.exists():
        print(f"Error: Content file not found: {content_path}", file=sys.stderr)
        sys.exit(1)

    content = content_path.read_text(encoding="utf-8")
    name = args.name
    tags = [t.strip() for t in args.tags.split(",")] if args.tags else []

    out_dir = ARCHIVE_ROOT / "google-docs"
    out_dir.mkdir(parents=True, exist_ok=True)

    doc_path = out_dir / f"{name}.md"
    meta_path = out_dir / f"{name}.meta.json"

    if doc_path.exists():
        print(f"Warning: {doc_path} already exists, overwriting.", file=sys.stderr)

    doc_path.write_text(content, encoding="utf-8")
    write_meta(
        meta_path,
        build_meta(
            title=args.title or name.replace("-", " ").title(),
            description=args.description or "",
            source=args.source or "",
            doc_type="google-doc",
            tags=tags,
            initiative=args.initiative or "",
        ),
    )

    print(f"Saved: {doc_path}")
    print(f"Meta:  {meta_path}")


def main():
    parser = argparse.ArgumentParser(description="Save documents to local archive")
    sub = parser.add_subparsers(dest="command", required=True)

    # excalidraw subcommand
    exc = sub.add_parser("excalidraw", help="Save an Excalidraw diagram")
    exc.add_argument("input", help="Excalidraw share URL or .excalidraw file path")
    exc.add_argument("name", nargs="?", help="Name for the diagram (without extension)")
    exc.add_argument(
        "--analyze", action="store_true", help="Print analysis JSON instead of saving"
    )
    exc.add_argument("--description", help="Description for metadata")
    exc.add_argument("--tags", help="Comma-separated tags")
    exc.add_argument("--initiative", help="Initiative or project name")

    # google-doc subcommand
    gdoc = sub.add_parser("google-doc", help="Save a Google Doc")
    gdoc.add_argument("name", help="Name for the document (without extension)")
    gdoc.add_argument(
        "--content-file", required=True, help="Path to markdown content file"
    )
    gdoc.add_argument("--source", help="Original Google Doc URL")
    gdoc.add_argument("--title", help="Document title (defaults to name)")
    gdoc.add_argument("--description", help="Description for metadata")
    gdoc.add_argument("--tags", help="Comma-separated tags")
    gdoc.add_argument("--initiative", help="Initiative or project name")

    args = parser.parse_args()

    if args.command == "excalidraw":
        cmd_save_excalidraw(args)
    elif args.command == "google-doc":
        cmd_save_google_doc(args)


if __name__ == "__main__":
    main()
