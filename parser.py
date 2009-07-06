import re
import htmlentitydefs
from HTMLParser import HTMLParser
from tags import tags

def parse(html, valid_tags=(), invalid_attributes=()):
  return Parser(valid_tags, invalid_attributes).parse(html)

class Parser(HTMLParser):
  
  elements_to_clear = []
  
  def __init__(self, valid_tags, invalid_attributes):
    self.valid_tags = valid_tags
    self.invalid_attributes = invalid_attributes
    
    HTMLParser.__init__(self)
  
  def parse(self, html):
    self.buffer = ''
    self.feed(html)
    self.close()
    return self.buffer
  
  def handle_starttag(self, name, attrs):
    if self.elements_to_clear:
      return
    
    if name not in self.valid_tags:
      if name in tags and tags[name].get('type') in ('forms',
        'flash', 'java', 'meta'):
        self.elements_to_clear.append(name)

      if name in tags and tags[name].get('type') not in ('tables',
        'container'):
        return
      
      name = 'div'
    
    attrs = [(k, v) for k, v in attrs if k not in self.invalid_attributes]
    
    self.buffer += '<%s%s>' % (name, attrs_to_html(attrs))
  
  def handle_startendtag(self, name, attrs):
    if self.elements_to_clear:
      return
    
    if name not in self.valid_tags:
      if name in tags and tags[name].get('type') not in ('tables',
        'container'):
        return
      name = 'div'
    
    attrs = [(k, v) for k, v in attrs if k not in self.invalid_attributes]
    
    self.buffer += '<%s%s/>' % (name, attrs_to_html(attrs))
  
  def handle_data(self, text):
    if self.elements_to_clear:
      return
    
    text = text.replace('\r', '\n')
    text = re.compile('\n( )+').sub('\n', text)
    text = text.encode('utf-8', 'xmlcharrefreplace')
    
    self.buffer += text
  
  def handle_charref(self, ref):
    if self.elements_to_clear:
      return
    
    self.buffer += '&#%s;' % ref
  
  def handle_entityref(self, ref):
    if self.elements_to_clear:
      return
    
    if ref in htmlentitydefs.entitydefs:
      if ref == 'nbsp':
        self.buffer += ' '
      else:
        self.buffer += '&%s;' % ref
    else:
      self.buffer += '&amp;#%s;' % ref
  
  def handle_endtag(self, name):
    if name not in self.valid_tags:
      if self.elements_to_clear and name == self.elements_to_clear[-1]:
        self.elements_to_clear.pop()
        return
      
      if name in tags and tags[name].get('type') not in ('tables',
        'container'):
        return
      
      name = 'div'
    self.buffer += '</%s>' % name
  

def attrs_to_html(attrs):
  return ''.join([' %s="%s"' % (k, v.replace(r'"', r'\"'))
                  for k, v in attrs])
