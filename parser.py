import re
from HTMLParser import HTMLParser
import htmlentitydefs

# <div id="wrapper">
# <h1>
# <span>
# Header
# </span>
# </h1>
# <br/>
# <div id="content">
# <p>
# Welcome.
# </p>
# </div>
# </div>

class Parser(object):
  
  def __init__(self):
    pass
  
  def parse(self, html):
    nodelist = FlatParser().parse(html)
    path = [Element('container')]
    root = path[0]
    for node in nodelist.nodes:
      if node.type == 'start_tag':
        element = Element(node.name, node.attrs.to_dict(), [])
        path[-1].children.append(element)
        path.append(element)
      elif node.type == 'start_end_tag':
        element = Element(node.name, node.attrs.to_dict(), [])
        path[-1].children.append(element)
      elif node.type == 'end_tag':
        path.pop()
      elif node.type == 'text':
        if node.text and not node.text.isspace():
          path[-1].children.append(node)
      elif node.type in ('char_ref', 'entity_ref'):
        path[-1].children.append(node)
    
    return root
  

class Node(object):
  
  def __repr__(self):
    return self.to_html()
  

class Element(Node):
  
  def __init__(self, name, attrs={}, children=[]):
    self.type = 'element'
    self.name = name
    self.attrs = attrs
    self.children = children
  
  def find(self, name, attrs={}):
    results = []
    
    children = self.get_children()
    for child in children:
      if (child.name == name
          and all([attrs[key] == child.attrs[key] for key in attrs.keys()])):
        results.append(child)
    
    return results
  
  def get_children(self):
    children = []
    for child in self.children:
      if child.type == 'element':
        children.append(child)
        children += child.get_children()
    return children
  
  def to_html(self):
    return (StartTag(self.name, self.attrs).to_html()
          + ''.join([c.to_html() for c in self.children])
          + EndTag(self.name).to_html())
  

class FlatParser(HTMLParser):
  
  def __init__(self):
    HTMLParser.__init__(self)
  
  def parse(self, html):
    self.nodes = []
    self.feed(html)
    self.close()
    return NodeList(self.nodes)
  
  def handle_starttag(self, tag, attrs):
    self.nodes.append(StartTag(tag, attrs))
  
  def handle_startendtag(self, tag, attrs):
    self.nodes.append(StartEndTag(tag, attrs))
  
  def handle_endtag(self, tag):
    self.nodes.append(EndTag(tag))
  
  def handle_data(self, data):
    self.nodes.append(Text(data))
  
  def handle_charref(self, ref):
    self.nodes.append(CharRef(ref))
  
  def handle_entityref(self, ref):
    self.nodes.append(EntityRef(ref))
  

class StartTag(Node):
  type = 'start_tag'
  
  def __init__(self, name, attrs={}):
    self.name = name
    self.attrs = Attributes(attrs)
  
  def to_html(self):
    return '<%s%s>' % (self.name, self.attrs)
  

class StartEndTag(Node):
  type = 'start_end_tag'
  
  def __init__(self, name, attrs={}):
    self.name = name
    self.attrs = Attributes(attrs)
  
  def to_html(self):
    return '<%s%s/>' % (self.name, self.attrs)
  

class EndTag(Node):
  type = 'end_tag'
  
  def __init__(self, name):
    self.name = name
  
  def to_html(self):
    return '</%s>' % self.name
  

class Text(Node):
  type = 'text'
  
  def __init__(self, text):
    self.text = text
  
  def to_html(self):
    text = self.text.replace('\r', '\n')
    text = re.compile('\n( )+').sub('\n', text)
    text = text.encode('utf-8', 'xmlcharrefreplace')
    return text
  

class CharRef(Node):
  type = 'char_ref'
  
  def __init__(self, ref):
    self.ref = ref
  
  def to_html(self):
    return '&#%s;' % self.ref
  

class EntityRef(Node):
  type = 'entity_ref'
  
  def __init__(self, ref):
    self.ref = ref
  
  def to_html(self):
    if self.ref in htmlentitydefs.entitydefs:
      return '&%s;' % self.ref
    else:
      return '&#%s' % self.ref
  

class EmptyNode(Node):
  type = 'empty'
  
  def to_html(self):
    return ''
  

class NodeList(list):
  
  def __init__(self, nodes=[]):
    self.nodes = nodes
  
  def to_html(self):
    return ''.join([n.to_html() for n in self.nodes])
  
  def append(self, node):
    self.nodes.append(node)
  
  def __repr__(self):
    return self.to_html()
  

class Attributes(object):
  
  def __init__(self, attrs):
    if type(attrs) == dict:
      attrs = attrs.items()
    self.attrs = attrs
  
  def to_dict(self):
    return dict(self.attrs)
  
  def to_html(self):
    return ''.join([' %s="%s"' % (k, v.replace(r'"', r'\"'))
                      for k, v in self.attrs])
  
  def get(self, key):
    attrs = dict(self.attrs)
    if key in attrs:
      return attrs[key]
  
  def __repr__(self):
    return ''.join([' %s="%s"' % (k, v.replace(r'"', r'\"'))
                      for k, v in self.attrs])
  
