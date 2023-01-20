from html import escape

def html_as_iframe(html, frame_size, style='background: white;'):
  # srcdoc based iframes never get useragent stylesheets, which GPT seems to rely on
  html = html.replace('<head>', '<head><style>html { box-sizing: border-box; }\n*, *:before, *:after { box-sizing: inherit; }</style>')

  return f'<div id="lmtk-frame" style="display: inline-block; width: {frame_size[0]}px; height: {frame_size[1]}px;\n{style}"><iframe srcdoc="{escape(html)}" style="height: 100%; width: 100%; border: 0px;"></iframe></div>'

# Uh, obviously this is because I want to be light-weight or something?
# It really does need to be a self-contained html file.
def render_display_page(
    language='javascript',
    code='',
    html='',
    frame_size=(700, 800),
    bg_color='#444654',
):
  escaped_code = escape(code)
  iframe = html_as_iframe(html, frame_size)

  # download = '<a href="/" target="_blank" class="button" download>Download</a>'
  download = ''
  fullscreen = ''

  return f"""
<html style="height: 100%">
  <head>
    <style>
      html {{
        height: 100%;
        box-sizing: border-box;
      }}
      *,
      *:before,
      *:after {{
        box-sizing: inherit;
      }}
      body {{
        display: flex;
        flex-direction: row;
        background: { bg_color };
      }}
      .row {{
        flex: 1;
        margin: 10px;
        margin-top: 15px;
      }}
      #lmtk-frame {{
        box-shadow: 0px 0px 20px #000 !important;
      }}
      pre {{
        display: inline-block;
        margin-top: 0px;
        text-align: left;
      }}
      code {{
        width: {frame_size[0]}px;
        height: {frame_size[1]}px;
        box-shadow: 0px 0px 20px #000;
        white-space: pre-wrap;
      }}
      buttons {{
        position: fixed;
        bottom: 1.4rem;
        right: 0.8rem;
      }}
      .button {{
        color: rgb(217,217,227);
        background-color: rgba(52,53,65);
        border-color: rgba(86,88,105);
        font-family: Helvetica;
        padding: 10px;
        box-shadow: 0px 0px 3px #000;
        text-decoration: none;
        margin-left: 10px;
      }}
    </style>
    <link  rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/monokai.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js"></script>
  </head>
  <body>
    <div class="row" style="text-align: right">
      { iframe }
    </div>
    <div class="row" style="text-align: left">
      <pre><code class="language-{language}" id="code">{escaped_code}</code></pre>
      <script>
        hljs.highlightAll();
      </script>
    </div>
    <buttons>
      { download }
      { fullscreen }
    </buttons>
  </body>
</html>
"""
