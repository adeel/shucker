import re
import htmlentitydefs
from HTMLParser import HTMLParser
import taginfo
import htmltidy

tags_to_empty = ('forms', 'flash', 'java', 'meta')
tags_to_divize = ('tables', 'container')

def shuck(html, allow=('core',)):
  html = htmltidy.tidy(html)
  html = Parser(allow).read(html)
  
  return html


class Parser(HTMLParser):
  
  # queue of trees that are being removed
  removing_trees = []
  
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
    if self.removing_trees:
      return
    
    if name not in self.valid_tags:
      if name in taginfo.tags and taginfo.type(name) in tags_to_empty:
        self.removing_trees.append(name)
      
      if (name in taginfo.tags and taginfo.type(name) not in tags_to_divize):
        return
      
      name = 'div'
    
    attrs = [(k, v) for k, v in attrs if self.is_attr_allowed(k)]
    
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
    
    attrs = [(k, v) for k, v in attrs if self.is_attr_allowed(k)]
    
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
  
  def is_attr_allowed(self, attr):
    allowed_attrs = taginfo.attributes['core']
    
    for group in self.allow:
      allowed_attrs += taginfo.attributes.get(group)
    
    return attr in allowed_attrs
  

def attrs_to_html(attrs):
  return ''.join([' %s="%s"' % (k, v.replace(r'"', r'\"'))
                  for k, v in attrs])
