import re
import htmlentitydefs
from HTMLParser import HTMLParser

import htmltidy
from BeautifulSoup import BeautifulSoup

import taginfo

tags_to_empty = ('forms', 'flash', 'java', 'meta', 'scripts')
tags_to_divize = ('tables', 'container')

def shuck(html, allow=('core',)):
  html = htmltidy.tidy(html)
  html = Parser(allow).read(html)
  html = extract_contents(html)
  
  return html

def extract_contents(html):
  "Attempts to extract the contents out of the HTML document."
  
  soup = BeautifulSoup(html)
  for header in soup.findAll(id='header') + soup.findAll({'class': 'header'}):
    header.extract()
  
  for id in ('wrapper', 'container', 'content', 'article'):
    div = soup.find(id=id)
    if div:
      soup = div
    div = soup.find({'class': id})
    if div:
      soup = div
  
  return soup.renderContents()

class Parser(HTMLParser):
  """
  Parses the document using HTMLParser, removing unknown elements, stripping
  elements in tags_to_empty, and converting tags_to_divize into div elements.
  """
  
  # queue of trees that are being removed
  removing_trees = []
  
  def __init__(self, allow):
    "Takes one argument, allow: the type of tags to be allowed."
    
    self.allow = allow
    self.valid_tags = [tag for tag, info in taginfo.tags.items()
                           if info.get('type') in self.allow]
    HTMLParser.__init__(self)
  
  def read(self, html):
    "Reads the HTML and feeds it to the parser."
    
    self.buffer = ''
    self.feed(html)
    self.close()
    
    return self.buffer
  
  def handle_starttag(self, name, attrs):
    if self.removing_trees:
      return
    
    if name not in self.valid_tags:
      if name in taginfo.tags and taginfo.type(name) in tags_to_empty:
        self.removing_trees.append(name)
      
      if (name in taginfo.tags and taginfo.type(name) not in tags_to_divize):
        return
      
      name = 'div'
    
    attrs = [(k, v) for k, v in attrs if self.is_attr_allowed(name, k)]
    
    if 'scripts' not in self.allow:
      attrs = dict(attrs)
      
      if 'href' in attrs:
        attrs['href'] = re.compile('(java|vb)script:.*', re.I).sub('#',
          attrs['href'])
      
      attrs = attrs.items()
    
    self.buffer += '<%s%s>' % (name, attrs_to_html(attrs))
  
  def handle_startendtag(self, name, attrs):
    if self.removing_trees:
      return
    
    if name not in self.valid_tags:
      if (name in taginfo.tags and taginfo.type(name) not in tags_to_divize):
        return
      
      name = 'div'
    
    attrs = [(k, v) for k, v in attrs if self.is_attr_allowed(name, k)]
    
    self.buffer += '<%s%s/>' % (name, attrs_to_html(attrs))
  
  def handle_data(self, text):
    if self.removing_trees:
      return
    
    text = text.replace('\r', '\n')
    text = re.compile('\n( )+').sub('\n', text)
    
    self.buffer += text
  
  def handle_charref(self, ref):
    if self.removing_trees:
      return
    
    self.buffer += '&#%s;' % ref
  
  def handle_entityref(self, ref):
    if self.removing_trees:
      return
    
    if ref in htmlentitydefs.entitydefs:
      if ref == 'nbsp':
        self.buffer += ' '
      else:
        self.buffer += '&%s;' % ref
    else:
      self.buffer += '&amp;#%s;' % ref
  
  def handle_endtag(self, name):
    if self.removing_trees:
      if name == self.removing_trees[-1]:
        self.removing_trees.pop()
      return
    
    if name not in self.valid_tags:
      if (name in taginfo.tags and taginfo.type(name) not in tags_to_divize):
        return
      
      name = 'div'
    self.buffer += '</%s>' % name
  
  def is_attr_allowed(self, tag, attr):
    "Checks whether a tag is allowed to have the given attribute."
    
    if tag not in taginfo.tags:
      return False
    
    return attr in taginfo.attributes[taginfo.tags[tag]['type']]
  

def attrs_to_html(attrs):
  "Takes a list of tuples of attributes and converts it to HTML."
  
  return ''.join([' %s="%s"' % (k, v.replace(r'"', r'\"'))
                  for k, v in attrs])
