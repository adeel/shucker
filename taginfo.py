def type(name):
  if name in tags:
    return tags[name].get('type')

tags = {
  'a': {'type': 'core'},
  'abbr': {'type': 'core'},
  'acronym': {'type': 'core'},
  'address': {'type': 'core'},
  'applet': {'type': 'java'},
  'area': {'type': 'images'},
  'b': {'type': 'core'},
  'bdo': {'type': 'core'},
  'big': {'type': 'core'},
  'blockquote': {'type': 'core'},
  'body': {'type': 'container'},
  'br': {'type': 'core'},
  'button': {'type': 'forms'},
  'caption': {'type': 'tables'},
  'cite': {'type': 'core'},
  'code': {'type': 'core'},
  'col': {'type': 'tables'},
  'colgroup': {'type': 'tables'},
  'dd': {'type': 'core'},
  'del': {'type': 'core'},
  'dfn': {'type': 'core'},
  'div': {'type': 'core'},
  'dl': {'type': 'core'},
  'dt': {'type': 'core'},
  'em': {'type': 'core'},
  'fieldset': {'type': 'forms'},
  'form': {'type': 'core'},
  'h1': {'type': 'core'},
  'h2': {'type': 'core'},
  'h3': {'type': 'core'},
  'h4': {'type': 'core'},
  'h5': {'type': 'core'},
  'h6': {'type': 'core'},
  'head': {'type': 'meta'},
  'hr': {'type': 'core'},
  'html': {'type': 'container'},
  'i': {'type': 'core'},
  'iframe': {'type': 'iframes'},
  'img': {'type': 'images'},
  'input': {'type': 'forms'},
  'ins': {'type': 'core'},
  'kbd': {'type': 'core'},
  'label': {'type': 'forms'},
  'legend': {'type': 'forms'},
  'li': {'type': 'core'},
  'link': {'type': 'meta'},
  'map': {'type': 'images'},
  'meta': {'type': 'meta'},
  'noscript': {'type': 'scripts'},
  'object': {'type': 'flash'},
  'ol': {'type': 'core'},
  'optgroup': {'type': 'forms'},
  'option': {'type': 'form'},
  'p': {'type': 'core'},
  'param': {'type': 'flash'},
  'pre': {'type': 'core'},
  'q': {'type': 'core'},
  's': {'type': 'core'},
  'samp': {'type': 'core'},
  'script': {'type': 'scripts'},
  'select': {'type': 'forms'},
  'small': {'type': 'core'},
  'span': {'type': 'core'},
  'strike': {'type': 'core'},
  'strong': {'type': 'core'},
  'style': {'type': 'styles'},
  'sub': {'type': 'core'},
  'sup': {'type': 'core'},
  'table': {'type': 'tables'},
  'tbody': {'type': 'tables'},
  'td': {'type': 'tables'},
  'textarea': {'type': 'forms'},
  'tfoot': {'type': 'tables'},
  'th': {'type': 'tables'},
  'thead': {'type': 'tables'},
  'title': {'type': 'meta'},
  'tr': {'type': 'tables'},
  'tt': {'type': 'core'},
  'u': {'type': 'core'},
  'ul': {'type': 'core'},
  'var': {'type': 'core'},
}

attributes = {
  'core': ('id', 'class', 'title', 'lang', 'xml:lang', 'dir', 'href',
           'hreflang', 'rel', 'rev', 'charset', 'type', 'cite', 'datetime'),
  'styles': ('style', 'media', 'xml:space'),
  'scripts': ('src', 'defer', 'xml:space',
              'onload', 'onunload', 'onclick', 'ondblclick', 'onmousedown',
              'onmouseup', 'onmouseover', 'onmousemove', 'onmouseout',
              'onkeypress', 'onkeydown', 'onkeyup', 'onfocus', 'onblur',
              'onsubmit', 'onreset'),
  'tables': ('summary', 'width', 'border', 'frame', 'rules', 'cellspacing',
             'cellpadding', 'align', 'valign', 'char', 'charoff', 'span',
             'abbr', 'axis', 'headers', 'scope', 'rowspan', 'colspan'),
  'forms': ('accesskey', 'tabindex', 'action', 'method', 'enctype', 'accept',
            'for', 'name', 'value', 'checked', 'disabled', 'readonly', 'size',
            'maxlength', 'src', 'alt', 'multiple', 'label',
            'rows', 'cols'),
  'images': ('src', 'alt', 'shape', 'coords', 'usemap', 'ismap', 'nohref',
             'longdesc', 'height', 'width'),
  'flash': ('declare', 'classid', 'codebase', 'data', 'codetype',
            'name', 'archive', 'standby', 'height', 'width', 'usemap',
            'tabindex', 'value', 'valuetype'),
}