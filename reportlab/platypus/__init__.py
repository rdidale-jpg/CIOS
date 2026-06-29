from __future__ import annotations
from html import unescape
from pathlib import Path
from typing import Any

class Paragraph:
    def __init__(self, text: str, style: Any = None):
        self.text = unescape(text.replace('<br/>', '\n'))
        self.style = style

class Spacer:
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

class PageBreak:
    pass

class Table:
    def __init__(self, data, colWidths=None, repeatRows=0):
        self.data = data
        self.colWidths = colWidths
        self.repeatRows = repeatRows
    def setStyle(self, style):
        self.style = style

class TableStyle:
    def __init__(self, commands):
        self.commands = commands

class _Canvas:
    def saveState(self): pass
    def restoreState(self): pass
    def setStrokeColor(self, *_): pass
    def line(self, *_): pass
    def setFont(self, *_): pass
    def setFillColor(self, *_): pass
    def drawString(self, *_): pass
    def drawCentredString(self, *_): pass
    def drawRightString(self, *_): pass

class SimpleDocTemplate:
    def __init__(self, filename: str, pagesize=None, **kwargs):
        self.filename = filename
        self.pagesize = pagesize
        self.kwargs = kwargs
        self.page = 1
    def build(self, story, onFirstPage=None, onLaterPages=None):
        pages = [[]]
        for item in story:
            if isinstance(item, PageBreak):
                pages.append([])
            else:
                pages[-1].append(item)
        page_texts = []
        for idx, page in enumerate(pages, start=1):
            lines = []
            self.page = idx
            if idx == 1 and onFirstPage:
                onFirstPage(_Canvas(), self)
            elif idx > 1 and onLaterPages:
                onLaterPages(_Canvas(), self)
            lines.append(f'FLORA PDF PAGE {idx}')
            for item in page:
                if isinstance(item, Paragraph):
                    lines.extend(_wrap(item.text))
                elif isinstance(item, Table):
                    for row in item.data:
                        lines.extend(_wrap(' | '.join(str(cell) for cell in row)))
            lines.append(f'Page {idx}')
            page_texts.append('\n'.join(lines))
        Path(self.filename).write_bytes(_pdf_bytes(page_texts))

def _wrap(text: str, width: int = 92):
    words = str(text).split()
    if not words: return ['']
    out=[]; line=''
    for w in words:
        if len(line)+len(w)+1 > width:
            out.append(line); line=w
        else:
            line = f'{line} {w}'.strip()
    out.append(line)
    return out

def _pdf_escape(s: str) -> str:
    return s.replace('\\', r'\\').replace('(', r'\(').replace(')', r'\)')

def _pdf_bytes(page_texts: list[str]) -> bytes:
    objects = [
        b'1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n',
        b'2 0 obj << /Type /Pages /Kids [' + b' '.join(f'{3 + i*2} 0 R'.encode() for i in range(len(page_texts))) + b'] /Count ' + str(len(page_texts)).encode() + b' >> endobj\n',
    ]
    for i, text in enumerate(page_texts):
        page_obj = 3 + i * 2
        content_obj = page_obj + 1
        content_lines = ['BT', '/F1 9 Tf', '50 800 Td']
        for line in text.splitlines():
            content_lines.append(f'({_pdf_escape(line[:110])}) Tj')
            content_lines.append('0 -12 Td')
        content_lines.append('ET')
        stream = '\n'.join(content_lines).encode('latin-1', 'replace')
        objects.append(f'{page_obj} 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 {3 + len(page_texts)*2} 0 R >> >> /Contents {content_obj} 0 R >> endobj\n'.encode())
        objects.append(f'{content_obj} 0 obj << /Length {len(stream)} >> stream\n'.encode() + stream + b'\nendstream endobj\n')
    objects.append(f'{3 + len(page_texts)*2} 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n'.encode())
    out = bytearray(b'%PDF-1.4\n')
    offsets = [0]
    for obj in objects:
        offsets.append(len(out)); out.extend(obj)
    xref = len(out)
    out.extend(f'xref\n0 {len(objects)+1}\n0000000000 65535 f \n'.encode())
    for off in offsets[1:]:
        out.extend(f'{off:010d} 00000 n \n'.encode())
    out.extend(f'trailer << /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode())
    return bytes(out)
