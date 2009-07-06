'Attempts to use <http://countergram.com/software/pytidylib>.'

try:
  import tidylib

  def tidy(html):
    html, errors = tidylib.tidy_document(html, options={'force-output': True,
      'drop-empty-paras': True, 'output-xhtml': True, 'tidy-mark': False})
    return html
  
except ImportError:
  def tidy(html):
    return html
  