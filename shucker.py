"""
Shucker
=======

Shucker takes any (X)HTML and gives you back a stripped down version. You
can give it any web page and it will find the actual content of the page,
minus styling, scripts, headers, footers, navigation elements and so on.
Or you can just give it a bit of (X)HTML (like a blog comment) and it will
remove anything `bad'. Shucker always returns valid markup, even if you
give it invalid markup.

  Usage
  -----
  
  Standard usage:
  
    import shucker
    html = '''
    <html>
      <head>
        <title>Someone's Webpage</title>
      </head>
      <body>
        <div id="header">
          <h1>Someone's Website</h1>
        </div>
        <div id="content">
          <h2>Someone's Webpage!</h2>
      
          <p style="color: #f00;" align=CENTER>This is a paragraph.</p>
      
          <!-- This comment will be stripped. -->
      
          <table><tr><td>
            <p>Click this <a href="javascript:alert('evil');">innocent</a>
            link.</td></p>
          </td></tr></table>
        </div>
        <div id="footer">
          <p>This web page was created by Nyoob Ekid on 1 Feb 2003.</p>
        </div>
      </body>
    </html>'''
    html = shucker.shuck(html)
  
  This example will result in this:
  
    <div> <h2>Someone's Webpage!</h2> <p>This is a paragraph.</p> <div>
    <p>Click this <a>innocent</a> link.</p></div> </div>
  
  Limitations
  -----------
  
  Shucker will usually do a pretty good job, but it may have trouble with
  some pages:
  
    * Shucker does best with semantic markup. Table-based layouts, for
      example, are harder to work with (it still does a fairly good job,
      though).
  
    * Shucker looks for non-text content (headers, footers and navigation
      elements) by looking for `suspicious' <div> elements. It often misses
      things, and it may even mistakenly remove something that is actually
      part of the page.

Enjoy. GPL:

Copyright (c) 2007-2008 Adeel Ahmad Khan

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import sys
import re

from BeautifulSoup import BeautifulSoup

valid_tags = ['address', 'a', 'abbr', 'acronym', 'b', 'big',
  'blockquote', 'br', 'cite', 'code', 'dd', 'del', 'div',
  'dl', 'dt', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
  'hr', 'i', 'ins', 'li', 'p', 'pre', 'q', 's', 'strike',
  'strong', 'sub', 'sup', 'tt', 'ul', 'ol', 'var']
  
invalid_attributes = ['id', 'class', 'style', 'align',
  'onclick', 'ondblclick', 'onmousedown', 'onmouseup',
  'onmouseover', 'onmousemove', 'onmouseout',
  'onkeypress', 'onkeydown', 'onkeyup', 'width',
  'height']
  
def shuck(html):
  
  import chardet
  enc = chardet.detect(html)['encoding']
  
  soup = BeautifulSoup(html, fromEncoding=enc)
  
  soup = _get_body(soup)
  soup = _strip_context_blocks(soup)
  soup = _strip_extra(soup)

  html = HTMLStripper().strip(unicode(soup), valid_tags, invalid_attributes)
  
  html = re.compile('<(div|span|p)>\s*</\\1>').sub('', html)
  
  return unicode(BeautifulSoup(html)).strip()

def _get_body(soup):
  body = soup.body
  if not body: body = unicode(soup)
  return BeautifulSoup(unicode(body))

def _strip_extra(soup):
  html = unicode(soup)
  html = _strip_presentation(html)
  html = _strip_comments(html)
  html = _strip_tables(html)
  html = _strip_selected_tags(html, ['title'], True)
  return BeautifulSoup(unicode(html))

def _strip_presentation(html):
  html = re.compile('<(script|style|input|label|fieldset|select|option)[^>]*?>.*?</\\1>', re.IGNORECASE | re.DOTALL).sub('', html)
  html = re.compile('\s*href\s*=\s*\"\s*(java|vb)script:[^\"]*\"', re.IGNORECASE | re.DOTALL).sub('', html)
  html = re.compile('\s*href\s*=\s*\'\s*(java|vb)script:[^\']*\'', re.IGNORECASE | re.DOTALL).sub('', html)
  html = re.compile('\s*href\s*=\s*(java|vb)script:(.*)', re.IGNORECASE | re.DOTALL).sub('', html)
  return html

def _strip_comments(html):
  html = re.compile('<![\s\S]*?--[ \t\n\r]*>').sub('', html)
  html = html.replace('<!--', '')
  html = html.replace('<![CDATA[', '')
  html = html.replace('<?', '')
  return html

def _strip_tables(html):
  html = re.compile('<\s*td[^>]*>', re.IGNORECASE).sub('<div>', html)
  html = re.compile('<\s*/\s*td\s*>', re.IGNORECASE).sub('</div>', html)
  html = _strip_selected_tags(html, ['table', 'tbody', 'tr', 'th'], False)
  return html

def _strip_selected_tags(html, tags=None, strip_contents=False):
  all_tags = re.compile('<([^>]+)>').findall(html)
  for tag in all_tags:
    el = tag.partition(' ')[0]
    if el in tags:
      if strip_contents:
        html = re.compile('<%s[^>]*>.*</%s>' % (el, el), re.DOTALL).sub('', html)
      html = re.compile('</?%s[^>]*>' % el).sub('', html)
  return html

def _strip_context_blocks(soup):
  for div in soup.findAll('div'):
    try: id = div['id'].lower()
    except KeyError: id = ''
    if id in ['header', 'menu', 'footer'] or id.startswith('nav'):
      div.extract()
  return soup


# Strip `invalid' tags and attributes.
from sgmllib import SGMLParser
class HTMLStripper(SGMLParser):
  def __init__(self):
    SGMLParser.__init__(self)
    self.safe_tags = []
    self.current_start_tag = ''
    self.current_end_tag = ''
    self.filter_attrs = False
    self.self_closing_elements = ['br', 'hr']
  
  def strip(self, html, safe_tags=[], filter_attrs=False):
    self.safe_tags = safe_tags
    self.filter_attrs = filter_attrs
    self.html_buffer = ''
    self.feed(html)
    self.close()
    return self.html_buffer
  
  def unknown_starttag(self, tag, attributes):
    if tag in self.safe_tags:
      if self.filter_attrs:
        attributes = filter(lambda x: x[0] not in self.filter_attrs, attributes)
      attr_str = ''.join([' %s="%s"' % (key, value) for key, value in attributes])
      if tag not in self.self_closing_elements:
        self.current_start_tag = '<%s%s>' % (tag, attr_str)
      else:
        self.current_start_tag = '<%s%s />' % (tag, attr_str)
    else:
      self.current_start_tag = ''
    self.html_buffer += self.current_start_tag
  
  def handle_data(self, data):
    data = self.whitespace(data)
    self.html_buffer += data
    self.current_start_tag = ''
  
  def handle_charref(self, ref):
    self.html_buffer += '&#%s;' % ref
  
  def handle_entityref(self, ref):
    import htmlentitydefs
    self.html_buffer += '&%s' % ref
    if htmlentitydefs.entitydefs.has_key(ref):
      self.html_buffer += ';'
  
  def unknown_endtag(self, tag):
    if tag in self.safe_tags:
      self.current_end_tag = '</%s>' % tag
    else:
      self.current_end_tag = ''
    self.html_buffer += self.current_end_tag    
    self.current_end_tag = ''
  
  def whitespace(self, html):
    html = html.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    html = re.compile('\s\s*').sub(' ', html)
    return html

if __name__ == '__main__':
  print 'Shucker 0.1'