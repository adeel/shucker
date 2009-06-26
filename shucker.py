from parser import *

tags_core = {
  'default': ('html', 'head', 'title', 'base', 'link', 'meta', 'body', 'div',
    'p', 'ul', 'ol', 'li', 'dl', 'dt', 'dd', 'address', 'hr', 'pre',
    'blockquote', 'ins', 'del', 'a', 'span', 'bdo', 'br', 'em', 'strong',
    'dfn', 'code', 'samp', 'kbd', 'var', 'cite', 'abbr', 'acronym', 'q', 'sub',
    'sup', 'tt', 'i', 'b', 'big', 'small', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'),
  
  'minimal': ('div', 'p', 'ul', 'ol', 'li', 'dl', 'dt', 'dd', 'address', 'hr',
    'pre', 'blockquote', 'ins', 'del', 'a', 'span', 'bdo', 'br', 'em',
    'strong', 'dfn', 'code', 'samp', 'kbd', 'var', 'cite', 'abbr', 'acronym',
    'q', 'sub', 'sup', 'tt', 'i', 'b',  'h1', 'h2', 'h3', 'h4', 'h5', 'h6'),  
}

tags_extra = {
  'scripts': ('script', 'noscript'),
  'styles': ('style', ),
  'forms': ('form', 'fieldset', 'label', 'input', 'button', 'textarea',
    'select', 'optgroup', 'option', 'legend'),
  'tables': ('table', 'tr', 'th', 'td', 'caption', 'colgroup', 'col',
    'thead', 'tfoot', 'tbody'),
  'flash': ('object', 'param', 'embed'),
  'images': ('img', 'map', 'area')
}

attrs_extra = {
  'scripts': ('onclick', 'ondblclick',
    'onmousedown', 'onmouseup', 'onmouseover', 'onmousemove', 'onmouseout',
    'onkeypress', 'onkeydown', 'onkeyup',
    'onfocus', 'onblur',
    'onsubmit', 'onreset'),
  'styles': ('class', 'style', 'align', 'valign', 'width', 'height')
}

def tidy(html):
  return parse(html).to_html()

def shuck(html, **options):
  
  tags = tags_core['default']
  if options.get('allow_styles'):
    tags += tags_extra['styles']
  if options.get('allow_scripts'):
    tags += tags_extra['scripts']
  if options.get('allow_forms'):
    tags += tags_extra['forms']
  if options.get('allow_tables'):
    tags += tags_extra['tables']
  if options.get('allow_flash'):
    tags += tags_extra['flash']
  if options.get('allow_images'):
    tags += tags_extra['images']
  
  doc = _shuck(parse(html), tags, **options)
  body = doc.children[0]
  
  return body.to_html()

def _shuck(element, tags, **options):
  children = []
  for child in element.children:
    if child.type == 'element':
      if child.name not in tags:
        if child.name in ('html', 'body', 'table', 'tr', 'th', 'td',
                          'form', 'fieldset'):
          child.name = 'div'
      if child.name in tags:
        if (not options.get('allow_styles')
            and child.name == 'link'
            and child.attrs.get('rel') == 'stylesheet'):
          continue
        child = _shuck(child, tags, **options)
        children.append(child)
    elif child.type in ('text', 'entity_ref', 'char_ref'):
      children.append(child)
  element.children = children
  return element

def parse(html):
  return Parser().parse(html)
