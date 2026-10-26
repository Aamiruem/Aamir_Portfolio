"""Daily AI/ML + automation video generator for Aamir Hussain Azad.

Usage:  python3 generator.py [YYYY-MM-DD] [out_dir]
Picks the day's topic from TOPICS (rotates by date), renders a 1080x1080 MP4
(about 19 s, no audio) plus a LinkedIn caption .txt, and prints both paths.
Needs: playwright (chromium) and ffmpeg.
"""
import datetime, os, subprocess, sys, tempfile, html

PORTFOLIO = "aamir-hussain-azad.vercel.app"
GITHUB = "github.com/Aamiruem"
NAME = "Aamir Hussain Azad"
ROLE = "AI/ML Engineer & MERN Developer"

ICONS = {
 "leaf": '<path d="M5 19c0-8 6-14 15-14 0 9-6 15-14 15"/><path d="M5 19c3-4 6-7 10-9"/>',
 "chart": '<path d="M4 20V10"/><path d="M10 20V4"/><path d="M16 20v-7"/><path d="M22 20H2"/>',
 "heart": '<path d="M12 20s-7-4.5-7-10a4 4 0 0 1 7-2.5A4 4 0 0 1 19 10c0 5.5-7 10-7 10z"/><path d="M8 11h2l1-2 2 4 1-2h2"/>',
 "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/><path d="M15 17l2 2 4-4"/>',
 "trend": '<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
 "video": '<rect x="3" y="6" width="13" height="12" rx="2"/><path d="M16 10l5-3v10l-5-3"/>',
 "home": '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/>',
 "gear": '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1L7 17M17 7l2.1-2.1"/>',
 "broom": '<path d="M19 3l-7 7"/><path d="M12 10l-6 2-3 9 9-3 2-6z"/><path d="M7 15l2 2"/>',
 "app": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18"/><path d="M7 13h5M7 16h8"/>',
 "target": '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4"/><circle cx="12" cy="12" r="1"/>',
 "dots": '<circle cx="6" cy="7" r="2"/><circle cx="9" cy="16" r="2"/><circle cx="17" cy="8" r="2"/><circle cx="18" cy="17" r="2"/><circle cx="13" cy="12" r="2"/>',
 "api": '<path d="M8 8l-5 4 5 4"/><path d="M16 8l5 4-5 4"/><path d="M14 5l-4 14"/>',
 "eye": '<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/><path d="M4 4h4M4 4v4M20 4h-4M20 4v4M4 20h4M4 20v-4M20 20h-4M20 20v-4"/>',
}

# Facts here come from Aamir's own GitHub repos and LinkedIn profile.
TOPICS = [
 dict(slug="india-crop-intelligence", tag="AI/ML Project", icon="leaf", c=("#0f5132","#16a34a"),
      title="I built a crop advisor for all of India",
      points=["Covers 28 states, 8 UTs and 45 crops", "Compares regression models, leakage-safe features", "Seasonal crop ranking + live weather in Streamlit"],
      link="github.com/Aamiruem/Indian-Crop-Optimization-Production",
      caption="Farmers decide what to sow with limited data. I built an end-to-end ML + Streamlit system that covers all 28 states and 8 union territories, 45 crops and 11 soil systems, with regression model comparison, seasonal crop ranking and optional live weather.",
      tags="#MachineLearning #AgriTech #Python #Streamlit #DataScience"),
 dict(slug="retail-analytics-pipeline", tag="Automation + Analytics", icon="chart", c=("#3b0f6b","#7c3aed"),
      title="An automated pipeline for retail insights",
      points=["Merges CSV, Excel and SQLite sources", "Rule-based cleaning: 4,180 validated order lines", "RFM + K-Means segments, Power BI and Streamlit"],
      link="github.com/Aamiruem/Retail-sales-customer",
      caption="Manual reporting is slow and error-prone. In this project an automated pipeline pulls CSV, Excel and SQLite data, cleans it with auditable rules, builds a SQL star schema and segments customers with RFM and K-Means, then feeds Power BI and Streamlit dashboards. (Synthetic data.)",
      tags="#DataAnalytics #Automation #PowerBI #SQL #Python"),
 dict(slug="mansik-santulan", tag="ML for Good", icon="heart", c=("#7f1d3a","#e11d48"),
      title="Can ML spot social media's effect on students?",
      points=["Trained on a student survey dataset", "Scikit-learn model saved and served on the web", "Deployed live on Render"],
      link="mansik-santulan-scores-1.onrender.com",
      caption="Mansik Santulan Score is my machine learning app that estimates the impact of social media use on student mental health, trained on a survey dataset and deployed live on Render. Try it from the link.",
      tags="#MachineLearning #MentalHealth #Python #AIForGood"),
 dict(slug="email-validator-automation", tag="Python Automation", icon="mail", c=("#0c4a6e","#0284c7"),
      title="Stop checking emails by hand",
      points=["Regex + email-validator syntax checks", "Automatic DNS and MX record lookup", "One-click Streamlit app, mobile friendly"],
      link="github.com/Aamiruem/Professional-Email-Checker",
      caption="Bad email lists cost time and bounce rates. I automated validation in Python: syntax checks, then DNS and MX lookups, all in a one-click Streamlit app.",
      tags="#Automation #Python #Streamlit #Productivity"),
 dict(slug="zerodha-clone-mern", tag="MERN Stack", icon="trend", c=("#0b3b2e","#0f766e"),
      title="Rebuilding a trading platform with MERN",
      points=["React frontend + trading dashboard", "Node.js / Express API with MongoDB", "User login with Passport.js"],
      link="github.com/Aamiruem/Apna-College-Zerodha-Clone",
      caption="To sharpen my full-stack skills I built a Zerodha-style trading platform: React frontend and dashboard, Node.js/Express backend, MongoDB with Mongoose and Passport.js authentication.",
      tags="#MERN #ReactJS #NodeJS #MongoDB #WebDevelopment"),
 dict(slug="video-meet-socketio", tag="MERN · Real-time", icon="video", c=("#7c2d12","#ea580c"),
      title="Real-time video calls with Socket.io",
      points=["React client, Node/Express server", "Socket.io for real-time signalling", "MongoDB users + bcrypt password hashing"],
      link="github.com/Aamiruem/ApnaCollegeZoomClone",
      caption="Real-time apps are a different challenge from CRUD. This Zoom-style app uses React, Node.js/Express, Socket.io for real-time communication, MongoDB and bcrypt for secure passwords.",
      tags="#SocketIO #MERN #RealTime #JavaScript"),
 dict(slug="ci-for-ml-projects", tag="Automation Tip", icon="gear", c=("#1e1b4b","#4338ca"),
      title="Automate your ML repo with GitHub Actions",
      points=["Run tests and data checks on every push", "Catch broken notebooks and scripts early", "I use workflows in my crop + retail projects"],
      link=GITHUB,
      caption="Automation tip: add a GitHub Actions workflow to your ML repos so tests and data checks run on every push. Broken scripts get caught before anyone else sees them. My crop and retail analytics projects both use workflows.",
      tags="#GitHubActions #MLOps #Automation #MachineLearning"),
 dict(slug="automate-data-cleaning", tag="Automation Tip", icon="broom", c=("#134e4a","#0d9488"),
      title="Write your data cleaning once, run it forever",
      points=["Turn manual Excel fixes into Python rules", "Log every rejected row so results are auditable", "Re-run the whole pipeline with one command"],
      link="github.com/Aamiruem/Retail-sales-customer",
      caption="Automation tip: if you clean data by hand every week, write the rules once in Python and log what gets rejected. My retail project rejects defective rows with clear reasons, so every KPI can be reconciled.",
      tags="#DataCleaning #Python #Pandas #Automation"),
 dict(slug="notebook-to-app", tag="AI Productivity", icon="app", c=("#701a75","#c026d3"),
      title="Turn a notebook into an app in an afternoon",
      points=["Wrap your model in a Streamlit UI", "Add inputs, charts and batch scoring", "Share one link instead of a .ipynb file"],
      link=PORTFOLIO,
      caption="Recruiters and clients rarely open notebooks. Wrapping a model in Streamlit gives them inputs, charts and predictions behind one link. I do this for most of my ML projects.",
      tags="#Streamlit #MachineLearning #Python #Portfolio"),
 dict(slug="regression-metrics", tag="ML Concept", icon="target", c=("#78350f","#d97706"),
      title="MAE, RMSE or R²? Pick the right one",
      points=["MAE: average error, easy to explain", "RMSE: punishes big misses harder", "R²: share of variance the model explains"],
      link=PORTFOLIO,
      caption="Quick ML refresher from my crop yield work: MAE tells you the typical error, RMSE punishes large misses, and R² shows how much variance the model explains. Report more than one.",
      tags="#MachineLearning #DataScience #Regression #Statistics"),
 dict(slug="kmeans-rfm", tag="ML Concept", icon="dots", c=("#164e63","#0891b2"),
      title="Segment customers with RFM + K-Means",
      points=["Recency, Frequency, Monetary per customer", "Scale features, then cluster with K-Means", "Name clusters: Champions, Loyal, At Risk"],
      link="github.com/Aamiruem/Retail-sales-customer",
      caption="How I segment customers: compute Recency, Frequency and Monetary value, scale them, cluster with K-Means, then give each cluster a business name like Champions, Loyal or At Risk.",
      tags="#KMeans #CustomerAnalytics #MachineLearning #DataAnalytics"),
 dict(slug="rest-api-structure", tag="MERN Tip", icon="api", c=("#1e3a8a","#2563eb"),
      title="A clean folder layout for Express APIs",
      points=["routes → controllers → models", "Keep secrets in .env, never in code", "Validate input before it reaches MongoDB"],
      link=GITHUB,
      caption="MERN tip: split Express apps into routes, controllers and models, keep secrets in .env, and validate input before it hits MongoDB. Small habits, much easier debugging.",
      tags="#ExpressJS #NodeJS #MERN #BackendDevelopment"),
 dict(slug="object-detection-work", tag="Computer Vision", icon="eye", c=("#312e81","#7c3aed"),
      title="What I'm building as an AI/ML Engineer",
      points=["Object detection models with TensorFlow", "Crop yield prediction for agriculture", "ML models shipped inside full-stack apps"],
      link=PORTFOLIO,
      caption="At Root Developers in Gurugram I work on object detection, image generation and crop yield prediction models, and integrate them into full-stack web apps.",
      tags="#ComputerVision #TensorFlow #AIML #DeepLearning"),
 dict(slug="wanderlust-fullstack", tag="Full Stack", icon="home", c=("#831843","#db2777"),
      title="WanderLust: an Airbnb-style listing app",
      points=["Node.js + Express server", "MongoDB for listings and users", "Full CRUD web app from scratch"],
      link="github.com/Aamiruem/Airbnb-Clone-main",
      caption="WanderLust is my Airbnb-style property listing app built with Node.js, Express and MongoDB, one of the projects where I practised full-stack CRUD end to end.",
      tags="#FullStack #NodeJS #MongoDB #WebDevelopment"),
]

CSS = """*{box-sizing:border-box}html,body{margin:0}
body{width:1080px;height:1080px;overflow:hidden;font-family:'Inter',sans-serif;color:#fff;position:relative;
 background:linear-gradient(140deg,%(c1)s 0%%,%(c2)s 75%%,%(c2)s 100%%)}
.dots{position:absolute;inset:0;background-image:radial-gradient(rgba(255,255,255,.10) 1.5px,transparent 1.5px);background-size:30px 30px}
.glow{position:absolute;right:-180px;top:-180px;width:700px;height:700px;border-radius:50%%;background:radial-gradient(circle,rgba(255,255,255,.20),transparent 62%%)}
.top{position:absolute;left:80px;right:80px;top:70px;display:flex;justify-content:space-between;align-items:center;font-weight:700;font-size:26px;letter-spacing:2px;text-transform:uppercase}
.pill{background:rgba(255,255,255,.16);border:1.5px solid rgba(255,255,255,.35);padding:10px 22px;border-radius:999px;font-size:22px}
.foot{position:absolute;left:80px;right:80px;bottom:64px;display:flex;justify-content:space-between;font-size:24px;font-weight:600;opacity:.9}
.bar{position:absolute;left:0;bottom:0;height:10px;background:rgba(255,255,255,.85)}
.mid{position:absolute;left:80px;right:80px;top:210px;bottom:170px;display:flex;flex-direction:column;justify-content:center}
h1{font-family:'Inter Display','Inter';font-size:84px;line-height:1.04;margin:0;font-weight:800;letter-spacing:-2px}
.num{font-size:150px;font-weight:800;line-height:1;opacity:.35;font-family:'Inter Display','Inter'}
.pt{font-family:'Inter Display','Inter';font-size:70px;font-weight:800;line-height:1.08;letter-spacing:-1.5px;margin-top:10px}
.badge{width:200px;height:200px;border-radius:52px;background:rgba(255,255,255,.14);border:2px solid rgba(255,255,255,.4);display:flex;align-items:center;justify-content:center;margin-bottom:46px}
.cta h1{font-size:72px}.link{margin-top:34px;font-size:40px;font-weight:700;background:rgba(255,255,255,.95);color:%(c1)s;padding:18px 30px;border-radius:22px;display:inline-block}
.small{margin-top:26px;font-size:30px;opacity:.9;font-weight:500}
"""

def icon(name, size):
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>'

def page(t, body, progress):
    css = CSS % {"c1": t["c"][0], "c2": t["c"][1]}
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>'
            f'<div class="dots"></div><div class="glow"></div>'
            f'<div class="top"><span>{html.escape(NAME)}</span><span class="pill">{html.escape(t["tag"])}</span></div>'
            f'{body}<div class="foot"><span>{html.escape(ROLE)}</span><span>{PORTFOLIO}</span></div>'
            f'<div class="bar" style="width:{progress}%"></div></body></html>')

def scenes(t):
    out = [page(t, f'<div class="mid"><div class="badge">{icon(t["icon"],120)}</div><h1>{html.escape(t["title"])}</h1></div>', 20)]
    for i, p in enumerate(t["points"], 1):
        out.append(page(t, f'<div class="mid"><div class="num">0{i}</div><div class="pt">{html.escape(p)}</div></div>', 20 + 20 * i))
    out.append(page(t, f'<div class="mid cta"><h1>See the code and more projects</h1>'
                       f'<div><span class="link">{PORTFOLIO}</span></div>'
                       f'<div class="small">{html.escape(t["link"])}</div></div>', 100))
    return out

def render(date, out_dir):
    t = TOPICS[date.toordinal() % len(TOPICS)]
    os.makedirs(out_dir, exist_ok=True)
    base = os.path.join(out_dir, f"{date.isoformat()}_{t['slug']}")
    from playwright.sync_api import sync_playwright
    tmp = tempfile.mkdtemp()
    pngs = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1080})
        for i, h in enumerate(scenes(t)):
            pg.set_content(h); pg.wait_for_timeout(150)
            p = os.path.join(tmp, f"s{i}.png"); pg.screenshot(path=p); pngs.append(p)
        b.close()
    durs = [4.0, 3.5, 3.5, 3.5, 4.5]; fade = 0.5
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    for p, d in zip(pngs, durs):
        cmd += ["-loop", "1", "-framerate", "30", "-t", str(d), "-i", p]
    # gentle zoom on each scene, then cross-fade between them
    parts = [f"[{i}:v]scale=1188:1188,zoompan=z='min(zoom+0.0006,1.06)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1080:fps=30,setsar=1[v{i}]" for i in range(len(pngs))]
    chain, last, off = [], "v0", 0.0
    for i in range(1, len(pngs)):
        off += durs[i - 1] - fade
        chain.append(f"[{last}][v{i}]xfade=transition=fade:duration={fade}:offset={off:.2f}[x{i}]")
        last = f"x{i}"
    cmd += ["-filter_complex", ";".join(parts + chain), "-map", f"[{last}]",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", "-movflags", "+faststart", base + ".mp4"]
    subprocess.run(cmd, check=True)
    caption = (f"{t['caption']}\n\n"
               + "\n".join(f"✅ {p}" for p in t["points"]) +
               f"\n\n🔗 Code: https://{t['link']}\n🌐 Portfolio: https://{PORTFOLIO}\n\n"
               f"I'm open to AI/ML Engineer and MERN Developer roles. Happy to connect!\n\n{t['tags']} #AIML #OpenToWork")
    with open(base + "_caption.txt", "w", encoding="utf-8") as f:
        f.write(caption)
    return base + ".mp4", base + "_caption.txt", t

if __name__ == "__main__":
    d = datetime.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime.date.today()
    out = sys.argv[2] if len(sys.argv) > 2 else "."
    v, c, t = render(d, out)
    print(v); print(c); print("topic:", t["slug"])
