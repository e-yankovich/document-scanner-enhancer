import os
import uuid

from flask import Flask, request, render_template_string, url_for, redirect
from werkzeug.utils import secure_filename

from pipeline import run_pipeline

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
RESULTS_DIR = os.path.join(BASE_DIR, "static", "results")
ALLOWED = (".jpg", ".jpeg", ".png")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

app = Flask(__name__)

ORIGINAL_FILE = "01_original.jpg"
SCAN_FILE = "07_scan.jpg"
STAGES = [
    ("02_enhanced.jpg", "1. Enhance"),
    ("03_mask.jpg", "2. Segment (mask)"),
    ("04_clean.jpg", "3. Clean (silhouette)"),
    ("05_detection.jpg", "4. Detect (corners)"),
    ("06_warped.jpg", "5. Perspective corrected"),
]

PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Document Scanner &amp; Enhancer</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #0b1020; --panel: rgba(30,41,59,.55); --line: rgba(148,163,184,.18);
      --txt: #e6edf6; --muted: #93a4bd; --accent: #6366f1; --accent2: #22d3ee;
    }
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
      font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
      margin: 0; color: var(--txt); background: var(--bg);
      background-image:
        radial-gradient(60rem 60rem at 85% -10%, rgba(99,102,241,.20), transparent 60%),
        radial-gradient(50rem 50rem at -10% 10%, rgba(34,211,238,.14), transparent 55%);
      background-attachment: fixed; min-height: 100vh;
    }
    main { max-width: 1120px; margin: 0 auto; padding: 0 22px 72px; }

    header { text-align: center; padding: 54px 20px 30px; }
    .logo {
      width: 56px; height: 56px; margin: 0 auto 16px; border-radius: 16px;
      display: grid; place-items: center;
      background: linear-gradient(135deg, var(--accent), var(--accent2));
      box-shadow: 0 12px 30px -8px rgba(99,102,241,.6);
    }
    .logo svg { width: 30px; height: 30px; stroke: #fff; }
    h1 {
      margin: 0 0 10px; font-size: 32px; font-weight: 800; letter-spacing: -.02em;
      background: linear-gradient(90deg, #fff, #b9c6ff 60%, #8be9ff);
      -webkit-background-clip: text; background-clip: text; color: transparent;
    }
    .chips { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; margin-top: 14px; }
    .chip {
      font-size: 12px; font-weight: 600; color: var(--muted);
      padding: 6px 12px; border: 1px solid var(--line); border-radius: 999px;
      background: rgba(255,255,255,.03);
    }
    .chip b { color: var(--txt); font-weight: 700; }

    .glass {
      background: var(--panel); border: 1px solid var(--line); border-radius: 20px;
      backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
      box-shadow: 0 24px 60px -28px rgba(0,0,0,.7);
    }

    /* upload */
    .upload { padding: 30px; margin-bottom: 30px; }
    .dropzone {
      display: block; border: 1.5px dashed rgba(148,163,184,.4); border-radius: 16px;
      padding: 34px 22px; text-align: center; transition: .2s; cursor: pointer;
      background: rgba(255,255,255,.02);
    }
    .dropzone.drag { border-color: var(--accent2); background: rgba(34,211,238,.08); }
    .dropzone .ico { font-size: 30px; }
    .dropzone p { margin: 10px 0 4px; font-weight: 600; }
    .dropzone small { display: block; color: var(--muted); }
    #fname { display: block; margin-top: 10px; color: var(--accent2); font-weight: 600;
             font-size: 13px; min-height: 16px; }
    .row { display: flex; justify-content: center; margin-top: 22px; }
    button {
      font: inherit; font-weight: 700; color: #fff; border: 0; cursor: pointer;
      padding: 13px 30px; border-radius: 12px;
      background: linear-gradient(135deg, var(--accent), #4f46e5);
      box-shadow: 0 12px 26px -10px rgba(99,102,241,.8); transition: .15s;
    }
    button:hover { transform: translateY(-1px); filter: brightness(1.08); }
    button:active { transform: translateY(0); }
    button:disabled { opacity: .6; cursor: progress; }

    /* banner */
    .banner {
      display: flex; align-items: center; gap: 12px; padding: 16px 20px;
      border-radius: 14px; font-weight: 600; margin-bottom: 26px;
    }
    .banner .dot { width: 26px; height: 26px; border-radius: 50%; display: grid;
                   place-items: center; font-size: 15px; flex: none; }
    .ok { background: rgba(16,185,129,.12); border: 1px solid rgba(16,185,129,.45); color: #6ee7b7; }
    .ok .dot { background: #10b981; color: #04130d; }
    .fail { background: rgba(244,63,94,.12); border: 1px solid rgba(244,63,94,.45); color: #fda4af; }
    .fail .dot { background: #f43f5e; color: #2a0510; }

    .back {
      display: inline-flex; align-items: center; gap: 7px; margin-bottom: 18px;
      color: var(--muted); text-decoration: none; font-weight: 600; font-size: 14px;
      padding: 8px 14px; border: 1px solid var(--line); border-radius: 10px;
      background: rgba(255,255,255,.03); transition: .15s;
    }
    .back:hover { color: var(--txt); border-color: rgba(148,163,184,.4); }

    /* hero before/after */
    .hero { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 20px; margin-bottom: 38px; }
    .tile { border-radius: 16px; overflow: hidden; position: relative;
            border: 1px solid var(--line); background: #060912; }
    .tile .tag {
      position: absolute; top: 12px; left: 12px; z-index: 2;
      font-size: 11px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase;
      padding: 5px 11px; border-radius: 999px; backdrop-filter: blur(6px);
    }
    .tag.before { background: rgba(15,23,42,.7); color: #cbd5e1; border: 1px solid var(--line); }
    .tag.after  { background: linear-gradient(135deg, var(--accent), var(--accent2)); color: #fff; }
    .tile img { width: 100%; display: block; background: #fff; }

    .section-title { display: flex; align-items: baseline; gap: 10px; margin: 0 0 18px; }
    .section-title h2 { font-size: 18px; font-weight: 700; margin: 0; }
    .section-title span { color: var(--muted); font-size: 13px; }

    /* stages grid */
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 18px; }
    .stage {
      border: 1px solid var(--line); border-radius: 16px; overflow: hidden;
      background: #060912; transition: .18s;
    }
    .stage:hover { transform: translateY(-4px); border-color: rgba(99,102,241,.5);
                   box-shadow: 0 18px 40px -22px rgba(99,102,241,.8); }
    .stage h3 {
      display: flex; align-items: center; gap: 10px; margin: 0; padding: 12px 14px;
      font-size: 13px; font-weight: 600; border-bottom: 1px solid var(--line);
      background: rgba(255,255,255,.02);
    }
    .stage .num {
      width: 22px; height: 22px; flex: none; border-radius: 7px; font-size: 12px;
      font-weight: 700; display: grid; place-items: center; color: #fff;
      background: linear-gradient(135deg, var(--accent), var(--accent2));
    }
    .stage img { width: 100%; display: block; background: #fff; }

    footer { text-align: center; color: var(--muted); font-size: 12px; padding-top: 8px; }

    @keyframes rise { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: none; } }
    .anim { animation: rise .45s ease both; }
  </style>
</head>
<body>
  <header>
    <div class="logo">
      <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M4 7V5a1 1 0 0 1 1-1h2M17 4h2a1 1 0 0 1 1 1v2M20 17v2a1 1 0 0 1-1 1h-2M7 20H5a1 1 0 0 1-1-1v-2"/>
        <path d="M4 12h16"/>
      </svg>
    </div>
    <h1>Document Scanner &amp; Enhancer</h1>
  </header>

  <main>
    <form class="glass upload anim" method="post" action="{{ url_for('process') }}" enctype="multipart/form-data">
      <label class="dropzone" id="dz" for="file">
        <div class="ico">📄</div>
        <p>Drop a document photo here, or click to browse</p>
        <small>JPG · JPEG · PNG</small>
        <span id="fname">No file chosen</span>
        <input type="file" id="file" name="image" accept=".jpg,.jpeg,.png" required hidden>
      </label>
      <div class="row">
        <button type="submit" id="go">Scan document</button>
      </div>
    </form>

    {% if error %}
      <div class="banner fail anim"><span class="dot">!</span>{{ error }}</div>
    {% endif %}

    {% if result %}
      <a class="back" href="{{ url_for('index') }}">&larr; Scan another</a>
      <div class="banner {{ 'ok' if result.success else 'fail' }} anim">
        <span class="dot">{{ '✓' if result.success else '✕' }}</span>
        {{ result.message }}{% if result.success %} — {{ result.corners }} corners detected{% endif %}
      </div>

      <div class="hero anim">
        <div class="tile">
          <span class="tag before">Input</span>
          <img src="{{ original_src }}" alt="Input">
        </div>
        {% if scan_src %}
        <div class="tile">
          <span class="tag after">Scanned</span>
          <img src="{{ scan_src }}" alt="Scanned result">
        </div>
        {% endif %}
      </div>

      <div class="section-title">
        <h2>Processing stages</h2>
        <span>{{ stages|length }} steps</span>
      </div>
      <div class="grid">
        {% for src, label in stages %}
          <div class="stage anim" style="animation-delay: {{ loop.index0 * 60 }}ms">
            <h3><span class="num">{{ loop.index }}</span>{{ label.split('. ')[-1] }}</h3>
            <img src="{{ src }}" alt="{{ label }}">
          </div>
        {% endfor %}
      </div>
    {% endif %}

    <footer>Computer Vision team project · enhance → segment → clean → detect → decide</footer>
  </main>

  <script>
    const fi = document.getElementById('file');
    const nm = document.getElementById('fname');
    const dz = document.getElementById('dz');
    const form = dz.closest('form');
    const go = document.getElementById('go');
    if (fi) {
      fi.addEventListener('change', () => {
        nm.textContent = fi.files.length ? fi.files[0].name : 'No file chosen';
      });
      ['dragover', 'dragenter'].forEach(e => dz.addEventListener(e, ev => {
        ev.preventDefault(); dz.classList.add('drag');
      }));
      ['dragleave', 'drop'].forEach(e => dz.addEventListener(e, ev => {
        ev.preventDefault(); dz.classList.remove('drag');
      }));
      dz.addEventListener('drop', ev => {
        if (ev.dataTransfer.files.length) {
          fi.files = ev.dataTransfer.files;
          nm.textContent = fi.files[0].name;
        }
      });
      form.addEventListener('submit', () => {
        if (fi.files.length) { go.disabled = true; go.textContent = 'Scanning…'; }
      });
    }
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(PAGE, result=None, error=None, stages=None,
                                  original_src=None, scan_src=None)

@app.route("/process", methods=["POST"])
def process():
    file = request.files.get("image")
    if file is None or file.filename == "":
        return render_template_string(PAGE, result=None, stages=None,
                                      original_src=None, scan_src=None,
                                      error="No file selected.")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED:
        return render_template_string(PAGE, result=None, stages=None,
                                      original_src=None, scan_src=None,
                                      error="Unsupported file type. Use JPG or PNG.")

    job_id = uuid.uuid4().hex[:12]
    upload_path = os.path.join(UPLOAD_DIR, secure_filename(f"{job_id}{ext}"))
    file.save(upload_path)

    out_dir = os.path.join(RESULTS_DIR, job_id)
    result = run_pipeline(upload_path, out_dir)

    def static_src(fname):
        return url_for("static", filename=f"results/{job_id}/{fname}")

    stages = [
        (static_src(fname), label)
        for fname, label in STAGES
        if os.path.exists(os.path.join(out_dir, fname))
    ]
    original_src = static_src(ORIGINAL_FILE)
    scan_src = (static_src(SCAN_FILE)
                if os.path.exists(os.path.join(out_dir, SCAN_FILE)) else None)

    return render_template_string(PAGE, result=result, stages=stages, error=None,
                                  original_src=original_src, scan_src=scan_src)


if __name__ == "__main__":
    from werkzeug.serving import make_server

    host, port = "127.0.0.1", 5001
    print(f"Document Scanner & Enhancer — open http://{host}:{port}  (Ctrl+C to stop)",
          flush=True)
    make_server(host, port, app, threaded=True).serve_forever()
