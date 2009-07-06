import htmltidy

import parser
from tags import tags

invalid_attributes = ('width', 'border', 'align', 'valign', 'size', 'style',
  'face', 'color')

def shuck(html, allow=('text',), _invalid_attributes=()):
  global invalid_attributes
  if _invalid_attributes:
    invalid_attributes = _invalid_attributes
  
  valid_tags = [tag for tag, info in tags.items() if info.get('type') in allow]
  
  html = htmltidy.tidy(html)
  
  html = parser.parse(html, valid_tags, invalid_attributes)
  
  return html