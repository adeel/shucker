__version__ = '0.1'

import re
import htmlentitydefs

from BeautifulSoup import BeautifulSoup

valid_tags = ['a', 'abbr', 'acronym', 'address', 'b', 'big', 'blockquote',
    'br', 'cite', 'code', 'dd', 'del', 'div', 'dl', 'dt', 'em', 'h1', 'h2',
    'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'ins', 'li', 'p', 'pre', 'q', 's',
    'strike', 'strong', 'sub', 'sup', 'tt', 'ul', 'ol', 'var']
  
invalid_attributes = ['id', 'class', 'style', 'align', 'onclick',
    'ondblclick', 'onmousedown', 'onmouseup', 'onmouseover', 'onmousemove',
    'onmouseout', 'onkeypress', 'onkeydown', 'onkeyup', 'width', 'height']
  
def shuck(html):
    soup = BeautifulSoup(html, fromEncoding='utf-8')
    
    soup = _get_body(soup)
    soup = _strip_context(soup)
    soup = _strip_extra(soup)

    html = HTMLStripper().strip(unicode(soup), valid_tags, invalid_attributes)
    
    html = html.replace('&nbsp;', ' ')
    html = re.compile('<(div|span|p)>\s*</\\1>').sub('', html)
    html = re.compile('(<br />)+').sub('<br />', html)

    return unicode(BeautifulSoup(html)).strip()

def _get_body(soup):
    """If soup is a complete HTML document, return the body.  Otherwise
    return the whole thing."""
    body = soup.body
    if not body:
        return soup
    return body

def _strip_extra(soup):
    """Strip extra elements from the page, including presentational elements
    and comments.  Replace tables with divs."""
    html = unicode(soup)
    html = _strip_presentation(html)
    html = _strip_comments(html)
    html = _strip_tables(html)
    return BeautifulSoup(unicode(html))

def _strip_context(soup):
    """Attempt to strip `context' from the page-- header, footer, navigation,
    and so on."""
    for div in soup.findAll('div'):
        if 'id' not in div:
            continue
        id = div['id'].lower()
        context_blocks = ['header', 'menu', 'sidebar', 'footer']
        if id in context_blocks or id.startswith('nav'):
            div.extract()
    return soup

def _strip_presentation(html):
    """Strip styles, scripts and forms."""
    html = _strip_tags(html, ['script', 'style', 'input', 'label', 'fieldset',
        'select', 'option'], True)
    html = re.compile('\s*href\s*=\s*\"\s*(java|vb)script:[^\"]*\"',
        re.IGNORECASE | re.DOTALL).sub('', html)
    html = re.compile('\s*href\s*=\s*\'\s*(java|vb)script:[^\']*\'',
        re.IGNORECASE | re.DOTALL).sub('', html)
    html = re.compile('\s*href\s*=\s*(java|vb)script:(.*)',
        re.IGNORECASE | re.DOTALL).sub('', html)
    return html

def _strip_comments(html):
    """Strip comments and processor instructions."""
    html = re.compile('<![\s\S]*?--[ \t\n\r]*>').sub('', html)
    html = html.replace('<!--', '')
    html = html.replace('<![CDATA[', '')
    html = html.replace('<?', '')
    return html

def _strip_tables(html):
    """Replace tables with divs."""
    html = re.compile('<\s*(tr|td)[^>]*>', re.IGNORECASE).sub('<div>', html)
    html = re.compile('<\s*/\s*(tr|td)\s*>', re.IGNORECASE).sub('</div>', html)
    html = _strip_tags(html, ['table', 'tbody', 'tr', 'th'], False)
    return html

def _strip_tags(html, tags, strip_contents=False):
    """Strip the specified tags from the page."""
    all_tags = re.compile('<([^>]+)>').findall(html)
    for tag in all_tags:
        el = tag.partition(' ')[0]
        if el in tags:
            if strip_contents:
                html = re.compile('<%s[^>]*>.*</%s>' % (el, el),
                    re.DOTALL).sub('', html)
            html = re.compile('</?%s[^>]*>' % el).sub('', html)
    return html

import sgmllib
class HTMLStripper(sgmllib.SGMLParser):
    """Strip all `invalid' tags and attributes."""
    def __init__(self):
        sgmllib.SGMLParser.__init__(self)
        self.safe_tags = []
        self.current_start_tag = ''
        self.current_end_tag = ''
        self.filter_attrs = False
        self.self_closers = ['br', 'hr']
    
    def strip(self, html, safe_tags=[], filter_attrs=False):
        self.safe_tags = safe_tags
        self.filter_attrs = filter_attrs
        self.html_buffer = ''
        self.feed(html)
        self.close()
        return self.html_buffer
    
    def unknown_starttag(self, tag, attrs):
        if tag in self.safe_tags:
            if self.filter_attrs:
                attrs = [x for x in attrs if x[0] not in self.filter_attrs]
            attr_str = ''.join([' %s="%s"' % (k, v) for k, v in attrs])
            if tag in self.self_closers:
                start_tag = '<%s%s />' % (tag, attr_str)
            else:
                start_tag = '<%s%s>' % (tag, attr_str)
            self.html_buffer += start_tag
    
    def handle_data(self, data):
        data = self._standardize_whitespace(data)
        data = data.encode('utf-8', 'xmlcharrefreplace')
        self.html_buffer += data
    
    def handle_charref(self, ref):
        self.html_buffer += '&#%s;' % ref
    
    def handle_entityref(self, ref):
        self.html_buffer += '&%s' % ref
        if ref in htmlentitydefs.entitydefs:
            self.html_buffer += ';'
    
    def unknown_endtag(self, tag):
        if tag in self.safe_tags:
            self.html_buffer += '</%s>' % tag
    
    def _standardize_whitespace(self, html):
        html = html.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        html = re.compile('(\s)\s*').sub(' ', html)
        return html
    

if __name__ == '__main__':
    import sys
    print shuck(sys.stdin).encode('utf-8')