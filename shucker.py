import re
import htmlentitydefs
from HTMLParser import HTMLParser
import taginfo
import htmltidy

def shuck(html, allow=('core',)):
  html = htmltidy.tidy(html)
  html = Parser(allow).read(html)
  
  return html


class Parser(HTMLParser):
  
  elements_to_clear = []
  
  def __init__(self, allow):
    self.allow = allow
    
    self.valid_tags = [tag for tag, info in taginfo.tags.items()
                           if info.get('type') in self.allow]
    
    HTMLParser.__init__(self)
  
  def read(self, html):
    self.buffer = ''
    self.feed(html)
    self.close()
    return self.buffer
  
  def handle_starttag(self, name, attrs):
    if self.elements_to_clear:
      return
    
    if name not in self.valid_tags:
      if name in taginfo.tags and taginfo.tags[name].get('type') in ('forms',
        'flash', 'java', 'meta'):
        self.elements_to_clear.append(name)
      
      if (name in taginfo.tags
      and taginfo.tags[name].get('type') not in ('tables', 'container')):
        return
      
      name = 'div'
    
    attrs = [(k, v) for k, v in attrs if self.is_attr_allowed(k)]
    
    if 'scripts' not in self.allow:
      attrs = dict(attrs)
      
      if name == 'a' and 'href' in attrs:
        attrs['href'] = re.compile('(java|vb)script:.*', re.I).sub('#',
          attrs['href'])
      
      attrs = attrs.items()
    
    self.buffer += '<%s%s>' % (name, attrs_to_html(attrs))
  
  def handle_startendtag(self, name, attrs):
    if self.elements_to_clear:
      return
    
    if name not in self.valid_tags:
      if (name in taginfo.tags
      and taginfo.tags[name].get('type') not in ('tables', 'container')):
        return
      name = 'div'
    
    attrs = [(k, v) for k, v in attrs if self.is_attr_allowed(k)]
    
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
      
      if (name in taginfo.tags
      and taginfo.tags[name].get('type') not in ('tables', 'container')):
        return
      
      name = 'div'
    self.buffer += '</%s>' % name
  
  def is_attr_allowed(self, attr):
    allowed_attrs = taginfo.attributes['core']
    
    for group in self.allow:
      allowed_attrs += taginfo.attributes.get(group)
    
    return attr in allowed_attrs
  

def attrs_to_html(attrs):
  return ''.join([' %s="%s"' % (k, v.replace(r'"', r'\"'))
                  for k, v in attrs])
