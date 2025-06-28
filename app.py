
import gradio as gr, requests, ast, traceback, logging, os, contextlib, io, json, time, re, sys, importlib.util, subprocess

LOG_FILE = "ai_diagnostics.log"
FEEDBACK_FILE = "user_feedback.jsonl"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# --- Self-modifying helper ------------------------------------------------
def append_to_self(new_code:str):
    """Append validated code to this file for self-programming."""
    fname = sys.argv[0] if '__file__' not in globals() else __file__
    with open(fname, 'a') as f:
        f.write('\n# --- auto-learned at ' + time.strftime('%Y-%m-%d %H:%M:%S') + '\n')
        f.write(new_code + '\n')
    logging.info('Appended new code block to self.')
    return 'Code appended to app.py; reload space to apply.'

# --- Sandboxed execution --------------------------------------------------
def safe_exec(code):
    try:
        ast.parse(code)
    except SyntaxError as e:
        logging.error('SyntaxError: ' + str(e))
        return 'Syntax error: ' + str(e)
    safe_globals = {'__builtins__': {'print': print, 'range': range, 'len': len, 'int': int, 'float': float, 'str': str, 'bool': bool, 'list': list, 'dict': dict, 'set': set, 'sum': sum}}
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            exec(code, safe_globals)
        except Exception as e:
            logging.error('Runtime error: ' + traceback.format_exc())
            return 'Runtime error: ' + str(e)
    return buf.getvalue() or 'Code executed without output'

# --- Web search -----------------------------------------------------------
def web_search(query, k=5):
    try:
        url = 'https://html.duckduckgo.com/html/?q=' + requests.utils.quote(query)
        html = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10).text
        links = re.findall(r'/l/\?uddg=(.*?)"', html)[:k]
        logging.info('Search for ' + query)
        return '\n'.join([requests.utils.unquote(l) for l in links]) or 'No links found.'
    except Exception as e:
        logging.error('Search error: ' + str(e))
        return 'Search error: ' + str(e)

# --- Diagnostics ----------------------------------------------------------
def show_logs():
    if not os.path.exists(LOG_FILE):
        return 'No logs yet.'
    with open(LOG_FILE) as f:
        return ''.join(f.readlines()[-250:])

# --- Feedback -------------------------------------------------------------
def save_feedback(text, rating):
    with open(FEEDBACK_FILE, 'a') as f:
        f.write(json.dumps({'time': time.time(), 'fb': text, 'rating': rating}) + '\n')
    logging.info('Feedback stored')
    return 'Thanks for the feedback!'

# --- Self-debugger (very minimal) ----------------------------------------
def self_diagnose():
    try:
        import py_compile, pathlib
        py_compile.compile(__file__, doraise=True)
        return 'No syntax errors in current code.'
    except py_compile.PyCompileError as e:
        return 'Self-diagnose found syntax issue: ' + str(e)

# --- GUI ------------------------------------------------------------------
with gr.Blocks(css='body{max-width:900px;margin:auto}') as demo:
    gr.Markdown('# Autonomous AI Space')
    with gr.Tab('Run Code'):
        code_in = gr.Code(label='Python code', language='python')
        run_btn = gr.Button('Run')
        code_out = gr.Textbox(label='Output')
        run_btn.click(fn=safe_exec, inputs=code_in, outputs=code_out)

    with gr.Tab('Teach Me'):
        teach_code = gr.Code(label='New function code', language='python')
        teach_btn = gr.Button('Add to brain')
        teach_resp = gr.Textbox()
        teach_btn.click(fn=append_to_self, inputs=teach_code, outputs=teach_resp)

    with gr.Tab('Web Search'):
        q = gr.Textbox(label='Query')
        s_btn = gr.Button('Search')
        res = gr.Textbox(label='Links', lines=8)
        s_btn.click(fn=web_search, inputs=q, outputs=res)

    with gr.Tab('Diagnostics'):
        diag_btn = gr.Button('Run self-diagnostics')
        diag_out = gr.Textbox(lines=6, label='Diagnostics')
        log_btn = gr.Button('Show recent logs')
        log_out = gr.Textbox(lines=10, label='Logs')
        diag_btn.click(fn=self_diagnose, outputs=diag_out)
        log_btn.click(fn=show_logs, outputs=log_out)

    with gr.Tab('Feedback'):
        fb = gr.Textbox(label='Your feedback')
        rating = gr.Slider(1,5,1,label='Rating')
        fb_btn = gr.Button('Submit')
        fb_resp = gr.Textbox()
        fb_btn.click(fn=save_feedback, inputs=[fb, rating], outputs=fb_resp)

if __name__ == '__main__':
    demo.launch()
