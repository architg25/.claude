#!/usr/bin/env python3
"""
Google Docs Operations Script

This script provides full CRUD operations on Google Documents:
- Create new docs from markdown with automatic diagram rendering
- Read existing docs (structure, content, tabs)
- Update docs with text, formatting, and structural changes
- Append markdown content to existing documents

Requirements:
- Pandoc (installed via: brew install pandoc)
- Python packages: google-auth google-auth-httplib2 google-api-python-client
- gcloud CLI configured with application default credentials

Make sure Google Drive API and Google Docs API are enabled:
    gcloud services enable drive.googleapis.com docs.googleapis.com
"""

import sys
import subprocess
import argparse
import tempfile
import json
from pathlib import Path

import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError


def upload_image_to_drive(image_data, filename, credentials):
    """
    Uploads an image to Google Drive with domain-restricted access.

    Args:
        image_data: Image bytes
        filename: Name for the file
        credentials: Google credentials

    Returns:
        str: URL of the uploaded image accessible to domain users
    """
    drive_service = build('drive', 'v3', credentials=credentials)

    # Save image data to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
        temp_file.write(image_data)
        temp_path = temp_file.name

    try:
        # Upload to Drive
        file_metadata = {'name': filename}
        media = MediaFileUpload(temp_path, mimetype='image/png')

        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        file_id = file.get('id')

        # Restrict access to Spotify domain only
        permission = {
            'type': 'domain',
            'role': 'reader',
            'domain': 'spotify.com'
        }

        drive_service.permissions().create(
            fileId=file_id,
            body=permission
        ).execute()

        # Return URL that works with Google Docs
        public_url = f"https://drive.google.com/uc?export=view&id={file_id}"

        return public_url

    finally:
        # Clean up temp file
        Path(temp_path).unlink()


def convert_markdown_to_docx(markdown_file, output_docx=None):
    """Converts a markdown file to .docx using Pandoc with improved formatting."""
    markdown_path = Path(markdown_file)

    if not markdown_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {markdown_file}")

    if output_docx is None:
        output_docx = markdown_path.with_suffix('.docx')
    else:
        output_docx = Path(output_docx)

    print(f"Converting {markdown_path.name} to .docx...")

    try:
        # Use Pandoc with options for better table and formatting preservation
        pandoc_cmd = [
            'pandoc',
            str(markdown_path),
            '-o', str(output_docx),
            '--standalone',
            '--columns=1000'  # Prevent line wrapping in tables
        ]

        subprocess.run(
            pandoc_cmd,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"Created {output_docx}")
        return output_docx
    except subprocess.CalledProcessError as e:
        print(f"Error running Pandoc: {e.stderr}")
        raise
    except FileNotFoundError:
        print("Error: Pandoc not found. Please install it:")
        print("  brew install pandoc")
        raise


def apply_font_formatting(document_id, credentials, text_font='Proxima Nova', code_font='Consolas'):
    """Applies font formatting to the document - Proxima Nova for text, Consolas for code."""
    docs_service = build('docs', 'v1', credentials=credentials)

    print(f"\nApplying font formatting ({text_font} for text, {code_font} for code)...")

    try:
        # Get the document to analyze its structure
        doc = docs_service.documents().get(documentId=document_id).execute()
        content = doc.get('body').get('content')

        # Find the last index in the document
        end_index = 1
        for element in content:
            if 'endIndex' in element:
                end_index = max(end_index, element['endIndex'])

        requests = []

        # First, apply Proxima Nova to entire document
        requests.append({
            'updateTextStyle': {
                'range': {
                    'startIndex': 1,
                    'endIndex': end_index - 1
                },
                'textStyle': {
                    'weightedFontFamily': {
                        'fontFamily': text_font
                    }
                },
                'fields': 'weightedFontFamily'
            }
        })

        # Process document elements
        for element in content:
            if 'paragraph' in element:
                paragraph = element['paragraph']
                paragraph_style = paragraph.get('paragraphStyle', {})

                # Check if this is a blockquote (identified by named style or indentation)
                is_blockquote = paragraph_style.get('namedStyleType') == 'NORMAL_TEXT' and \
                               paragraph_style.get('indentFirstLine', {}).get('magnitude', 0) > 0

                for paragraph_element in paragraph.get('elements', []):
                    if 'textRun' in paragraph_element:
                        text_run = paragraph_element['textRun']
                        text_style = text_run.get('textStyle', {})
                        start_idx = paragraph_element['startIndex']
                        end_idx = paragraph_element['endIndex']

                        # Check if this is a code block (monospace font from conversion)
                        if text_style.get('weightedFontFamily', {}).get('fontFamily') in ['Courier New', 'Consolas', 'Monaco', 'Courier']:
                            requests.append({
                                'updateTextStyle': {
                                    'range': {
                                        'startIndex': start_idx,
                                        'endIndex': end_idx
                                    },
                                    'textStyle': {
                                        'weightedFontFamily': {
                                            'fontFamily': code_font
                                        }
                                    },
                                    'fields': 'weightedFontFamily'
                                }
                            })

                        # Make blockquote text italic
                        elif is_blockquote:
                            requests.append({
                                'updateTextStyle': {
                                    'range': {
                                        'startIndex': start_idx,
                                        'endIndex': end_idx
                                    },
                                    'textStyle': {
                                        'italic': True
                                    },
                                    'fields': 'italic'
                                }
                            })

            # Handle tables
            elif 'table' in element:
                table = element['table']
                table_start_index = element.get('startIndex')

                # Process each table cell individually with all styling
                for row_idx, row in enumerate(table.get('tableRows', [])):
                    is_header_row = (row_idx == 0)  # First row is header

                    for col_idx, cell in enumerate(row.get('tableCells', [])):
                        # Build the table cell style
                        cell_style = {
                            'borderTop': {
                                'width': {'magnitude': 1, 'unit': 'PT'},
                                'dashStyle': 'SOLID',
                                'color': {'color': {'rgbColor': {'red': 0, 'green': 0, 'blue': 0}}}
                            },
                            'borderBottom': {
                                'width': {'magnitude': 1, 'unit': 'PT'},
                                'dashStyle': 'SOLID',
                                'color': {'color': {'rgbColor': {'red': 0, 'green': 0, 'blue': 0}}}
                            },
                            'borderLeft': {
                                'width': {'magnitude': 1, 'unit': 'PT'},
                                'dashStyle': 'SOLID',
                                'color': {'color': {'rgbColor': {'red': 0, 'green': 0, 'blue': 0}}}
                            },
                            'borderRight': {
                                'width': {'magnitude': 1, 'unit': 'PT'},
                                'dashStyle': 'SOLID',
                                'color': {'color': {'rgbColor': {'red': 0, 'green': 0, 'blue': 0}}}
                            }
                        }

                        fields = 'borderTop,borderBottom,borderLeft,borderRight'

                        # Add grey background for header cells
                        if is_header_row:
                            cell_style['backgroundColor'] = {
                                'color': {
                                    'rgbColor': {
                                        'red': 0.9,
                                        'green': 0.9,
                                        'blue': 0.9
                                    }
                                }
                            }
                            fields += ',backgroundColor'

                        # Apply cell styling
                        requests.append({
                            'updateTableCellStyle': {
                                'tableRange': {
                                    'tableCellLocation': {
                                        'tableStartLocation': {
                                            'index': table_start_index
                                        },
                                        'rowIndex': row_idx,
                                        'columnIndex': col_idx
                                    },
                                    'rowSpan': 1,
                                    'columnSpan': 1
                                },
                                'tableCellStyle': cell_style,
                                'fields': fields
                            }
                        })

                        for cell_content in cell.get('content', []):
                            if 'paragraph' in cell_content:
                                paragraph = cell_content['paragraph']
                                for paragraph_element in paragraph.get('elements', []):
                                    if 'textRun' in paragraph_element:
                                        start_idx = paragraph_element['startIndex']
                                        end_idx = paragraph_element['endIndex']

                                        # Apply font to table text
                                        requests.append({
                                            'updateTextStyle': {
                                                'range': {
                                                    'startIndex': start_idx,
                                                    'endIndex': end_idx
                                                },
                                                'textStyle': {
                                                    'weightedFontFamily': {
                                                        'fontFamily': text_font
                                                    },
                                                    'bold': is_header_row  # Make header text bold
                                                },
                                                'fields': 'weightedFontFamily,bold' if is_header_row else 'weightedFontFamily'
                                            }
                                        })

        # Apply all formatting requests
        if requests:
            docs_service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
            print(f"Applied custom font formatting")
    except HttpError as e:
        print(f"Warning: Could not apply font formatting: {e}")
        print(f"  The document was created successfully, but font may be default.")


def upload_to_google_drive(docx_file, doc_name=None, convert_to_gdoc=True, folder_id=None, apply_font=True):
    """Uploads a .docx file to Google Drive using application default credentials."""
    docx_path = Path(docx_file)

    if not docx_path.exists():
        raise FileNotFoundError(f"DOCX file not found: {docx_file}")

    if doc_name is None:
        doc_name = docx_path.stem

    print("\nUploading to Google Drive...")

    try:
        # Use application default credentials
        credentials, project = google.auth.default(
            scopes=[
                'https://www.googleapis.com/auth/drive.file',
                'https://www.googleapis.com/auth/documents'
            ]
        )

        service = build('drive', 'v3', credentials=credentials)

        # Prepare file metadata
        file_metadata = {'name': doc_name}

        if folder_id:
            file_metadata['parents'] = [folder_id]

        if convert_to_gdoc:
            # Convert to native Google Doc format
            file_metadata['mimeType'] = 'application/vnd.google-apps.document'

        # Upload the file
        media = MediaFileUpload(
            str(docx_path),
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            resumable=True
        )

        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink, mimeType'
        ).execute()

        print(f"Successfully uploaded: {file.get('name')}")
        print(f"  Document ID: {file.get('id')}")
        print(f"  Link: {file.get('webViewLink')}")

        # Apply Proxima Nova font if converting to Google Doc
        if convert_to_gdoc and apply_font:
            apply_font_formatting(file.get('id'), credentials)

        return file

    except google.auth.exceptions.DefaultCredentialsError:
        print("\nError: Google Cloud credentials not found!")
        print("\nPlease run:")
        print("  gcloud auth application-default login")
        print("\nThen make sure Google Drive API is enabled:")
        print("  gcloud services enable drive.googleapis.com --project=YOUR_PROJECT_ID")
        raise
    except HttpError as error:
        print(f"An error occurred: {error}")
        if error.resp.status == 403:
            print("\nThis might be because:")
            print("1. Google Drive API is not enabled. Run:")
            print("   gcloud services enable drive.googleapis.com --project=YOUR_PROJECT_ID")
            print("2. Your credentials don't have the necessary permissions")
        raise


# ============================================================================
# NEW FUNCTIONS: Read, Edit, Append, Replace, Insert operations
# ============================================================================

def get_docs_service(credentials=None):
    """Build Google Docs API service."""
    if credentials is None:
        credentials, _ = google.auth.default(
            scopes=[
                'https://www.googleapis.com/auth/drive.file',
                'https://www.googleapis.com/auth/documents'
            ]
        )
    return build('docs', 'v1', credentials=credentials)


def read_document(doc_id, tab_id=None, include_tabs=True):
    """Read a Google Doc and return its content."""
    credentials, _ = google.auth.default(
        scopes=['https://www.googleapis.com/auth/documents']
    )
    docs_service = get_docs_service(credentials)

    doc = docs_service.documents().get(
        documentId=doc_id,
        includeTabsContent=include_tabs
    ).execute()

    return doc


def list_document_tabs(doc_id):
    """List all tabs in a document."""
    doc = read_document(doc_id, include_tabs=True)

    tabs = []

    def extract_tabs(tab_list, level=0):
        for tab in tab_list:
            props = tab.get('tabProperties', {})
            tabs.append({
                'tabId': props.get('tabId'),
                'title': props.get('title', 'Untitled'),
                'level': level
            })
            if 'childTabs' in tab:
                extract_tabs(tab['childTabs'], level + 1)

    extract_tabs(doc.get('tabs', []))
    return tabs


def create_empty_document(title):
    """Create a new empty Google Doc."""
    credentials, _ = google.auth.default(
        scopes=['https://www.googleapis.com/auth/documents']
    )
    docs_service = get_docs_service(credentials)

    doc = docs_service.documents().create(
        body={'title': title}
    ).execute()

    print(f"Created empty document: {title}")
    print(f"  Document ID: {doc.get('documentId')}")
    print(f"  Link: https://docs.google.com/document/d/{doc.get('documentId')}/edit")

    return doc


def replace_text_in_doc(doc_id, find_text, replace_text, tab_id=None):
    """Replace all occurrences of text in a document."""
    credentials, _ = google.auth.default(
        scopes=['https://www.googleapis.com/auth/documents']
    )
    docs_service = get_docs_service(credentials)

    request = {
        'replaceAllText': {
            'containsText': {'text': find_text, 'matchCase': True},
            'replaceText': replace_text
        }
    }

    if tab_id:
        request['replaceAllText']['tabsCriteria'] = {'tabIds': [tab_id]}

    result = docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={'requests': [request]}
    ).execute()

    occurrences = result.get('replies', [{}])[0].get('replaceAllText', {}).get('occurrencesChanged', 0)
    print(f"Replaced {occurrences} occurrence(s) of '{find_text}' with '{replace_text}'")

    return result


def insert_text_in_doc(doc_id, text, index=None, tab_id=None):
    """Insert text at a specific position or end of document."""
    credentials, _ = google.auth.default(
        scopes=['https://www.googleapis.com/auth/documents']
    )
    docs_service = get_docs_service(credentials)

    if index is not None:
        location = {'index': index}
        if tab_id:
            location['tabId'] = tab_id
        request = {'insertText': {'location': location, 'text': text}}
    else:
        location = {'endOfSegmentLocation': {'segmentId': ''}}
        if tab_id:
            location['endOfSegmentLocation']['tabId'] = tab_id
        request = {'insertText': location, 'text': text}

    result = docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={'requests': [request]}
    ).execute()

    position = f"index {index}" if index else "end of document"
    print(f"Inserted text at {position}")

    return result


def apply_batch_update(doc_id, requests_file):
    """Apply a batch update from a JSON file."""
    credentials, _ = google.auth.default(
        scopes=['https://www.googleapis.com/auth/documents']
    )
    docs_service = get_docs_service(credentials)

    with open(requests_file, 'r') as f:
        body = json.load(f)

    result = docs_service.documents().batchUpdate(
        documentId=doc_id,
        body=body
    ).execute()

    num_requests = len(body.get('requests', []))
    print(f"Applied {num_requests} request(s) from {requests_file}")

    return result


def get_document_end_index(doc_id, tab_id=None):
    """Get the end index of a document or tab for appending."""
    doc = read_document(doc_id, include_tabs=True)

    if tab_id:
        # Find the specific tab
        def find_tab(tabs, target_id):
            for tab in tabs:
                if tab.get('tabProperties', {}).get('tabId') == target_id:
                    return tab.get('documentTab', {})
                if 'childTabs' in tab:
                    result = find_tab(tab['childTabs'], target_id)
                    if result:
                        return result
            return None

        doc_tab = find_tab(doc.get('tabs', []), tab_id)
        if not doc_tab:
            raise ValueError(f"Tab {tab_id} not found")
        content = doc_tab.get('body', {}).get('content', [])
    else:
        # Use first tab or main body
        tabs = doc.get('tabs', [])
        if tabs:
            content = tabs[0].get('documentTab', {}).get('body', {}).get('content', [])
        else:
            content = doc.get('body', {}).get('content', [])

    # Find the last index
    end_index = 1
    for element in content:
        if 'endIndex' in element:
            end_index = max(end_index, element['endIndex'])

    return end_index - 1  # Subtract 1 to insert before final newline


def append_markdown_to_doc(doc_id, markdown_file, tab_id=None):
    """Append markdown content to an existing Google Doc."""
    print(f"Appending {markdown_file} to document {doc_id}...")

    # Read the markdown content
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Get current end index
    end_index = get_document_end_index(doc_id, tab_id)

    # Insert the content as plain text
    insert_text_in_doc(doc_id, "\n\n" + content, index=end_index, tab_id=tab_id)

    print(f"Appended content from {markdown_file}")
    print(f"  Link: https://docs.google.com/document/d/{doc_id}/edit")


def main():
    parser = argparse.ArgumentParser(
        description='Google Docs operations: create, read, edit, append',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  create <file.md>              Create new doc from markdown
  create-empty <title>          Create empty document
  read <doc_id>                 Read document content (JSON)
  list-tabs <doc_id>            List all tabs in document
  append <doc_id> <file.md>     Append markdown to existing doc
  replace <doc_id> <find> <rep> Replace all occurrences of text
  insert <doc_id> <text>        Insert text at position
  update <doc_id> <json_file>   Apply batchUpdate from JSON

Examples:
  python gdocs.py create my_doc.md --name "My Document"
  python gdocs.py append 1abc...xyz section.md --tab t.appendix
  python gdocs.py replace 1abc...xyz "{{DATE}}" "2025-01-15"
  python gdocs.py list-tabs 1abc...xyz
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Create command (from markdown)
    create_parser = subparsers.add_parser('create', help='Create doc from markdown')
    create_parser.add_argument('markdown_file', help='Path to markdown file')
    create_parser.add_argument('--name', help='Document name')
    create_parser.add_argument('--folder', help='Google Drive folder ID')
    create_parser.add_argument('--no-convert', action='store_true', help='Keep as .docx')
    create_parser.add_argument('--convert-only', action='store_true', help='Only convert, no upload')
    create_parser.add_argument('--output', help='Output path for .docx')
    create_parser.add_argument('--keep-docx', action='store_true', help='Keep .docx after upload')

    # Create-empty command
    create_empty_parser = subparsers.add_parser('create-empty', help='Create empty document')
    create_empty_parser.add_argument('title', help='Document title')

    # Read command
    read_parser = subparsers.add_parser('read', help='Read document content')
    read_parser.add_argument('doc_id', help='Document ID')
    read_parser.add_argument('--tab', help='Specific tab ID')
    read_parser.add_argument('--tabs', action='store_true', help='Include all tabs')

    # List-tabs command
    list_tabs_parser = subparsers.add_parser('list-tabs', help='List document tabs')
    list_tabs_parser.add_argument('doc_id', help='Document ID')

    # Append command
    append_parser = subparsers.add_parser('append', help='Append markdown to doc')
    append_parser.add_argument('doc_id', help='Document ID')
    append_parser.add_argument('markdown_file', help='Path to markdown file')
    append_parser.add_argument('--tab', help='Target tab ID')

    # Replace command
    replace_parser = subparsers.add_parser('replace', help='Replace text in doc')
    replace_parser.add_argument('doc_id', help='Document ID')
    replace_parser.add_argument('find', help='Text to find')
    replace_parser.add_argument('replace_text', help='Replacement text')
    replace_parser.add_argument('--tab', help='Target tab ID')

    # Insert command
    insert_parser = subparsers.add_parser('insert', help='Insert text in doc')
    insert_parser.add_argument('doc_id', help='Document ID')
    insert_parser.add_argument('text', help='Text to insert')
    insert_parser.add_argument('--index', type=int, help='Position index')
    insert_parser.add_argument('--tab', help='Target tab ID')

    # Update command
    update_parser = subparsers.add_parser('update', help='Apply batchUpdate from JSON')
    update_parser.add_argument('doc_id', help='Document ID')
    update_parser.add_argument('json_file', help='Path to JSON file with requests')

    args = parser.parse_args()

    try:
        if args.command == 'create':
            # Existing create logic (unchanged)
            if not args.convert_only:
                try:
                    google.auth.default(
                        scopes=[
                            'https://www.googleapis.com/auth/drive.file',
                            'https://www.googleapis.com/auth/documents'
                        ]
                    )
                except google.auth.exceptions.DefaultCredentialsError:
                    print("Warning: No Google credentials.")

            print("Converting markdown file...")
            docx_file = convert_markdown_to_docx(args.markdown_file, args.output)

            if args.convert_only:
                print(f"\nConversion complete: {docx_file}")
                return

            file_info = upload_to_google_drive(
                docx_file,
                doc_name=args.name,
                convert_to_gdoc=not args.no_convert,
                folder_id=args.folder
            )

            if not args.keep_docx and not args.output:
                docx_file.unlink()
                print(f"\nCleaned up: {docx_file.name}")

            print(f"\nDone! Open at: {file_info.get('webViewLink')}")

        elif args.command == 'create-empty':
            create_empty_document(args.title)

        elif args.command == 'read':
            doc = read_document(args.doc_id, tab_id=args.tab, include_tabs=args.tabs)
            print(json.dumps(doc, indent=2))

        elif args.command == 'list-tabs':
            tabs = list_document_tabs(args.doc_id)
            print(f"{'Tab ID':<20} {'Title':<20} {'Level'}")
            print("-" * 50)
            for tab in tabs:
                indent = "  " * tab['level']
                print(f"{tab['tabId']:<20} {indent}{tab['title']:<20} {tab['level']}")

        elif args.command == 'append':
            append_markdown_to_doc(args.doc_id, args.markdown_file, tab_id=args.tab)

        elif args.command == 'replace':
            replace_text_in_doc(args.doc_id, args.find, args.replace_text, tab_id=args.tab)

        elif args.command == 'insert':
            insert_text_in_doc(args.doc_id, args.text, index=args.index, tab_id=args.tab)

        elif args.command == 'update':
            apply_batch_update(args.doc_id, args.json_file)

        else:
            parser.print_help()

    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
