"""Semantic HTML assertions for presentation contracts; no production authority."""
from html.parser import HTMLParser


class Document(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.nodes=[]; self.hrefs=[]; self.headings=[]; self.buttons=[]; self._text=[]; self._stack=[]
        self.feed(html)
        self.text=' '.join(' '.join(self._text).split())

    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        self.nodes.append((tag, attrs))
        if tag=='a' and attrs.get('href'): self.hrefs.append(attrs['href'])
        if tag in ('area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'): return
        hidden=tag in ('script','style','head') or 'hidden' in attrs or bool(self._stack and self._stack[-1][1])
        self._stack.append((tag, hidden, []))

    def handle_endtag(self, tag):
        index=next((i for i in range(len(self._stack)-1,-1,-1) if self._stack[i][0]==tag),None)
        if index is None: return
        name, hidden, chunks=self._stack[index]
        text=' '.join(' '.join(chunks).split())
        if not hidden:
            if name in ('h1','h2','h3','h4'): self.headings.append(text)
            if name=='button': self.buttons.append(text)
        del self._stack[index:]

    def handle_data(self, value):
        if self._stack and self._stack[-1][1]: return
        self._text.append(value)
        for _,_,chunks in self._stack: chunks.append(value)
