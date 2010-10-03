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
  
  valid_tags = [tag for tag, info in taginfo.tags.items()
                    if info.get('type') in allow]
  html = Parser(valid_tags).read(html)
  
  html = extract_contents(html)
  
  return html

def extract_contents(html):
  """
  Attempts to extract the contents out of the HTML document.
  
  The algorithm is simple.  First we find elements that are 'text wrappers',
  i.e. they are the minimal elements that contain text.  For example, p, h1,
  li are text wrappers, but div is not.  If a text wrapper contains more than
  three words, we add it to our list of 'text elements'.  Then we go through
  all the elements in the document and give each a 'score' based on how many
  of the text elements it contains.  Finally, we take the list of elements with
  score at least 60 and define a second metric on them: the ratio of lines of
  text that have more than three words.  We call this 'density'.  We return the
  contents of the most dense element.
  """
    
  soup = BeautifulSoup(html)
  
  text_wrappers = ('p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'address',
                   'dd', 'dt', 'pre')  
  text_els = []
  for el in soup.findAll(text_wrappers):
    text = ''.join(el.findAll(text=True))
    if len(text.strip().split()) > 3:
      text_els.append(el['shucker'])
  
  scores = {}
  for el in soup.findAll():
    if el.name not in text_wrappers:
      score = (100 * len(el.findAll(lambda tag: tag['shucker'] in text_els))
                   / len(text_els))
      if score >= 60:
        scores[score] = el['shucker']
  
  if len(scores.keys()) and scores.keys()[0] == 100:
    el_uid = scores[100]
  else:
    densities = {}
    for s, el in scores.iteritems():
      text = ''.join(soup.find(shucker=el).findAll(text=True))
      lines = text.strip().split('\n')
      density = (100 * len([line for line in lines if len(line.split()) > 3])
                     / len(lines))
      densities[density] = el
    
    el_uid = densities[max(densities.keys())]
  
  html = soup.find(shucker=el_uid).renderContents()
  
  return html

class Parser(HTMLParser):
  """
  Parses the document using HTMLParser, removing unknown elements, stripping
  elements in tags_to_empty, and converting tags_to_divize into div elements.
  """
  
  counter = 1
  
  # queue of trees that are being removed
  removing_trees = []
  
  def __init__(self, valid_tags):
    "Takes one argument, valid_tags: a list of tags to be allowed."
    
    self.valid_tags = valid_tags
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
    
    attrs = dict(attrs)
    if 'href' in attrs:
      attrs['href'] = re.compile('(java|vb)script:.*', re.I).sub('#',
        attrs['href'])
    attrs = attrs.items()
    
    attrs.append(('shucker', self.get_uid()))
    
    self.buffer += '<%s%s>' % (name, attrs_to_html(attrs))
  
  def handle_startendtag(self, name, attrs):
    if self.removing_trees:
      return
    
    if name not in self.valid_tags:
      if (name in taginfo.tags and taginfo.type(name) not in tags_to_divize):
        return
      
      name = 'div'
    
    attrs = [(k, v) for k, v in attrs if self.is_attr_allowed(name, k)]
    attrs.append(('shucker', self.get_uid()))
    
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
  
  def get_uid(self):
    uid = str(self.counter)
    self.counter += 1
    return uid

def attrs_to_html(attrs):
  "Takes a list of tuples of attributes and converts it to HTML."
  
  return ''.join([' %s="%s"' % (k, v.replace(r'"', r'\"'))
                  for k, v in attrs])
