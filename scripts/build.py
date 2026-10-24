#!/usr/bin/env python3
"""Render the static pages of luckgram.cc. Edit the page bodies here, then run:
    python3 scripts/build.py
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIKI = "https://wiki.luckgram.cc"
IOS_REPO = "https://github.com/limeng9088/luckgram-ios"
ANDROID_REPO = "https://github.com/limeng9088/luckgram-android"
IOS_LATEST = IOS_REPO + "/releases/latest"
ANDROID_LATEST = ANDROID_REPO + "/releases/latest"
INSTALL = WIKI + "/getting-started/install.html"
UPDATED = "October 24, 2026"


def header(current):
    def link(href, label, key, cls=""):
        cur = ' aria-current="page"' if key == current else ""
        c = f' class="{cls}"' if cls else ""
        return f'<a href="{href}"{c}{cur}>{label}</a>'
    return f'''<header class="site-header">
  <div class="wrap">
    <a class="logo" href="/"><img src="/assets/icon-512.png" alt="" width="30" height="30">Luckgram</a>
    <nav class="nav">
      {link("/#features", "Features", "features", "opt")}
      {link("/download/", "Download", "download")}
      {link(WIKI, "Help", "help")}
      {link("/#faq", "FAQ", "faq", "opt")}
    </nav>
  </div>
</header>'''


FOOTER = f'''<footer class="site-footer">
  <div class="wrap">
    <div class="cols">
      <div><h4>Luckgram</h4><ul>
        <li><a href="/download/">Download</a></li>
        <li><a href="{WIKI}/features/">Features</a></li>
        <li><a href="{WIKI}">Help Center</a></li>
      </ul></div>
      <div><h4>Source code</h4><ul>
        <li><a href="{IOS_REPO}">Luckgram for iOS</a></li>
        <li><a href="{ANDROID_REPO}">Luckgram for Android</a></li>
      </ul></div>
      <div><h4>Legal</h4><ul>
        <li><a href="/privacy-policy/">Privacy Policy</a></li>
        <li><a href="/terms-of-use/">Terms of Use</a></li>
      </ul></div>
      <div><h4>Contact</h4><ul>
        <li><a href="mailto:support@luckgram.cc">support@luckgram.cc</a></li>
        <li><a href="mailto:contact@luckgram.cc">contact@luckgram.cc</a></li>
        <li><a href="mailto:ads@luckgram.cc">ads@luckgram.cc</a></li>
      </ul></div>
    </div>
    <p class="disclaimer">Luckgram is an independent app based on the open-source Telegram apps. It is not made by,
    affiliated with, or endorsed by Telegram. Telegram is a trademark of Telegram FZ-LLC.</p>
    <p>&copy; 2026 Luckgram</p>
  </div>
</footer>'''


def page(path, title, description, body, current=""):
    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="https://luckgram.cc/assets/icon-512.png">
<link rel="icon" href="/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
{header(current)}
<main>
{body}
</main>
{FOOTER}
</body>
</html>
'''
    out = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)


def redirect(path, target):
    out = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Luckgram</title>
<meta http-equiv="refresh" content="0; url={target}">
<link rel="canonical" href="{target}">
</head><body><p><a href="{target}">Continue to {target}</a></p></body></html>
''')


AVAILABLE = [
    ("Chats and groups", "Cloud chats that sync across your devices, groups of up to 200,000 members, replies, reactions and polls."),
    ("Channels", "Follow and run channels, with comments, scheduled posts and statistics where Telegram offers them."),
    ("Voice and video calls", "End-to-end encrypted one-on-one calls, plus group calls and live streams."),
    ("Secret Chats", "Device-to-device encrypted chats with self-destructing messages."),
    ("Stories, bots and mini apps", "Everything that runs on the Telegram platform works in Luckgram."),
    ("Several accounts", "Switch between Telegram accounts in one app, up to Telegram's standard limit."),
]

IN_DEVELOPMENT = [
    "More accounts in one app",
    "Account backup and transfer",
    "Double Bottom",
    "Hidden chats",
    "Quick replies",
    "Outgoing translation",
    "Free speech-to-text",
    "Call recording",
    "Gallery video as round message",
    "Keyword folders",
    "Show Telegram ID",
    "AI Assistant",
]

FAQ = [
    ("Is Luckgram an official Telegram app?",
     "No. Luckgram is an independent app built from the open-source Telegram apps for iOS and Android. It is not made by, affiliated with, or endorsed by Telegram."),
    ("Can I use my existing Telegram account?",
     "Yes. Sign in with your phone number. Your cloud chats, contacts and channels load from Telegram as they do in any Telegram app."),
    ("Is Luckgram free?",
     "Yes. Telegram Premium and Telegram Stars are Telegram's own services and are sold and managed by Telegram."),
    ("Why isn't Luckgram on the App Store or Google Play?",
     "Luckgram is currently distributed through GitHub Releases. The Download page always links to the latest build."),
    ("How do I install Luckgram on an iPhone?",
     "The iOS build is an unsigned IPA. Sign it with a tool such as Sideloadly or AltStore, or with your own Apple developer certificate, then install it. The install guide walks through each step."),
    ("Which Android phones are supported?",
     "Android 6.0 or later on a 64-bit ARM phone (arm64-v8a), which covers almost every phone sold in recent years. Allow installs from your browser or file manager when asked."),
    ("Where are the extra features?",
     "The features listed under In development are being built. Until they ship, Luckgram works like the Telegram app it is based on. No release dates are promised."),
    ("How do I get help?",
     f'Start with the <a href="{WIKI}">Help Center</a>. If it does not answer your question, write to <a href="mailto:support@luckgram.cc">support@luckgram.cc</a>.'),
]


def home():
    cards = "\n".join(
        f'<div class="card"><span class="tag ok">Available</span><h3>{t}</h3><p>{d}</p></div>'
        for t, d in AVAILABLE)
    wip = "\n".join(f'<li>{t}<span class="tag wip">In development</span></li>' for t in IN_DEVELOPMENT)
    faq = "\n".join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in FAQ)
    body = f'''<section class="hero">
  <div class="wrap">
    <div>
      <p class="eyebrow">Independent Telegram client</p>
      <h1>Luckgram: your Telegram, in a new app</h1>
      <p class="lede">Luckgram is built on the open-source Telegram apps for iOS and Android. Sign in with your
      Telegram account and everything works as you know it. More tools are on the way.</p>
      <div class="btns">
        <a class="btn primary" href="/download/">Download Luckgram</a>
        <a class="btn" href="{IOS_REPO}">View the source</a>
      </div>
    </div>
    <div class="hero-art"><img src="/assets/icon-512.png" alt="Luckgram app icon" width="512" height="512"></div>
  </div>
</section>

<section class="block" id="features">
  <div class="wrap">
    <h2>What works today</h2>
    <p class="sub">Luckgram connects to the Telegram network, so the Telegram features you already use are all here.</p>
    <div class="grid">
{cards}
    </div>
  </div>
</section>

<section class="block">
  <div class="wrap">
    <h2>In development</h2>
    <p class="sub">These Luckgram additions are being built. They are not in the app yet, and no release dates are promised.</p>
    <ul class="list-wip">
{wip}
    </ul>
    <p class="more"><a href="{WIKI}/features/">See the full feature status in the Help Center &rarr;</a></p>
  </div>
</section>

<section class="block">
  <div class="wrap">
    <h2>Open source and transparent</h2>
    <p class="sub">The complete source code for both apps is public, and every release is built by GitHub Actions from that code.</p>
    <div class="grid">
      <div class="card"><h3>Public source code</h3><p>Read the code for <a href="{IOS_REPO}">iOS</a> and <a href="{ANDROID_REPO}">Android</a> on GitHub.</p></div>
      <div class="card"><h3>No Luckgram message servers</h3><p>Your messages go to Telegram's servers, as they would from any Telegram app. Luckgram does not run its own servers for them.</p></div>
      <div class="card"><h3>No added trackers</h3><p>Luckgram does not add analytics or advertising SDKs to the apps.</p></div>
    </div>
  </div>
</section>

<section class="block" id="download">
  <div class="wrap">
    <h2>Get Luckgram</h2>
    <p class="sub">Free for iOS and Android.</p>
    <div class="btns">
      <a class="btn primary" href="/download/">Go to downloads</a>
      <a class="btn" href="{INSTALL}">Install guide</a>
    </div>
  </div>
</section>

<section class="block" id="faq">
  <div class="wrap">
    <h2>Frequently asked questions</h2>
    <p class="sub">More answers in the <a href="{WIKI}">Help Center</a>.</p>
{faq}
  </div>
</section>'''
    page("index.html", "Luckgram – an independent Telegram client for iOS and Android",
         "Luckgram is an independent, open-source Telegram client for iOS and Android. Sign in with your Telegram account and keep everything you use today.",
         body)


def download():
    body = f'''<section class="hero" style="padding-bottom:32px">
  <div class="wrap" style="grid-template-columns:1fr">
    <div>
      <p class="eyebrow">Download</p>
      <h1>Get Luckgram</h1>
      <p class="lede">Luckgram is distributed through GitHub Releases. These links always open the latest build.</p>
    </div>
  </div>
</section>
<section class="block" style="border-top:0;padding-top:0">
  <div class="wrap">
    <div class="dl">
      <div class="card">
        <h3>Android</h3>
        <ul>
          <li>Signed APK for 64-bit ARM phones (arm64-v8a)</li>
          <li>Android 6.0 or later</li>
          <li>Allow installs from your browser or file manager when asked</li>
        </ul>
        <div class="btns"><a class="btn primary" href="{ANDROID_LATEST}">Download APK</a></div>
      </div>
      <div class="card">
        <h3>iPhone and iPad</h3>
        <ul>
          <li>Unsigned IPA</li>
          <li>Sign it with Sideloadly, AltStore or your own certificate before installing</li>
          <li>iOS 15 or later</li>
        </ul>
        <div class="btns"><a class="btn primary" href="{IOS_LATEST}">Download IPA</a><a class="btn" href="{INSTALL}">Install guide</a></div>
      </div>
    </div>
    <p class="note" style="margin-top:24px">If you previously installed a test build of Luckgram on Android, uninstall it first:
    builds signed with a different key cannot update each other. Only download Luckgram from this page or the
    GitHub repositories it links to.</p>
  </div>
</section>'''
    page("download/index.html", "Download Luckgram for Android and iOS",
         "Download the latest Luckgram builds for Android (APK) and iOS (IPA).", body, "download")


def privacy():
    body = f'''<article class="prose">
<h1>Privacy Policy</h1>
<p class="meta">Last updated {UPDATED}</p>

<p>This policy explains what happens to your information when you use the Luckgram apps for iOS and Android and
the luckgram.cc websites. Luckgram is an independent app built from the open-source Telegram apps.</p>

<h2>Your Telegram data</h2>
<p>Luckgram is a client for the Telegram network. When you sign in, send messages, make calls or sync contacts,
the app exchanges that data directly with Telegram's servers. That data is processed by Telegram under the
<a href="https://telegram.org/privacy">Telegram Privacy Policy</a>, not by Luckgram.</p>
<p>Luckgram does not run its own servers for your messages, calls, contacts or media, and does not receive copies
of them.</p>

<h2>Data stored on your device</h2>
<p>Like other Telegram apps, Luckgram keeps a local cache of your chats and media on your device so the app works
quickly and offline. You can clear it in the app's storage settings, or remove it by uninstalling the app.</p>

<h2>Analytics and advertising</h2>
<p>Luckgram does not add analytics, advertising or tracking SDKs to the apps. Sponsored messages that Telegram
shows in some public channels come from Telegram and follow Telegram's policies.</p>

<h2>Services from Apple and Google</h2>
<p>The apps use services built into the operating system or the Telegram code. Push notifications are delivered
through Apple Push Notification service on iOS and Firebase Cloud Messaging on Android. On Android, maps and
location features may use Google Play services. These providers process data under their own privacy policies.</p>

<h2>Downloads</h2>
<p>App builds are hosted on GitHub. When you download one, GitHub processes your request under the
<a href="https://docs.github.com/site-policy/privacy-policies/github-general-privacy-statement">GitHub Privacy Statement</a>.</p>

<h2>Our websites</h2>
<p>luckgram.cc and wiki.luckgram.cc are static websites hosted on GitHub Pages and served through Cloudflare. These
providers may process technical data such as your IP address and browser type to deliver and protect the sites.
The sites do not use cookies or analytics of their own.</p>

<h2>Email</h2>
<p>If you write to a luckgram.cc address, we receive your email address and message and use them only to reply to
you. Mail to these addresses is forwarded through Cloudflare Email Routing.</p>

<h2>Children</h2>
<p>Luckgram is not intended for children under the minimum age that Telegram requires in their country.</p>

<h2>Changes</h2>
<p>We may update this policy. The date at the top of this page shows when it last changed.</p>

<h2>Contact</h2>
<p>Questions about privacy: <a href="mailto:support@luckgram.cc">support@luckgram.cc</a>.</p>
</article>'''
    page("privacy-policy/index.html", "Privacy Policy – Luckgram",
         "How Luckgram handles your information.", body)


def terms():
    body = f'''<article class="prose">
<h1>Terms of Use</h1>
<p class="meta">Last updated {UPDATED}</p>

<p>These terms apply to your use of the Luckgram apps and the luckgram.cc websites. By using Luckgram you agree to
them.</p>

<h2>What Luckgram is</h2>
<p>Luckgram is an independent app built from the open-source Telegram apps. It is not made by, affiliated with,
or endorsed by Telegram. Telegram is a trademark of Telegram FZ-LLC.</p>

<h2>Telegram's terms still apply</h2>
<p>Luckgram connects you to the Telegram network. Your Telegram account, and everything you do with it, is
subject to <a href="https://telegram.org/tos">Telegram's Terms of Service</a>. Telegram may limit or close
accounts under its own rules, and Luckgram cannot reverse those decisions.</p>

<h2>Acceptable use</h2>
<p>Do not use Luckgram to send spam, to scam or harass people, to spread illegal content, or to break the law
where you live.</p>

<h2>Telegram Premium and Stars</h2>
<p>Telegram Premium, Telegram Stars and other paid Telegram services are sold and managed by Telegram. Luckgram is
free and does not sell them.</p>

<h2>Open-source licence</h2>
<p>Luckgram is built from the Telegram apps, which Telegram publishes under the GNU General Public License.
The complete Luckgram source code is available on GitHub for <a href="{IOS_REPO}">iOS</a> and
<a href="{ANDROID_REPO}">Android</a>.</p>

<h2>Installing builds</h2>
<p>Luckgram is distributed through GitHub Releases. Download it only from the links on luckgram.cc or from the
GitHub repositories above. You are responsible for how you sign and install the iOS build.</p>

<h2>No warranty</h2>
<p>Luckgram is provided "as is", without warranty of any kind. Features listed as in development may change or
may not ship. To the extent the law allows, Luckgram is not liable for any loss arising from your use of the
apps or websites.</p>

<h2>Changes</h2>
<p>We may update these terms. The date at the top of this page shows when they last changed.</p>

<h2>Contact</h2>
<p><a href="mailto:contact@luckgram.cc">contact@luckgram.cc</a></p>
</article>'''
    page("terms-of-use/index.html", "Terms of Use – Luckgram",
         "The terms for using Luckgram.", body)


def not_found():
    body = '''<article class="prose">
<h1>Page not found</h1>
<p>This page does not exist. Go to the <a href="/">home page</a> or the <a href="/download/">downloads</a>.</p>
</article>'''
    page("404.html", "Page not found – Luckgram", "Page not found.", body)


if __name__ == "__main__":
    home()
    download()
    privacy()
    terms()
    not_found()
    # Paths referenced by the Help Center.
    redirect("features/index.html", WIKI + "/features/")
    redirect("faq/index.html", WIKI + "/help/")
    redirect("hub/index.html", WIKI + "/features/ai.html")
    print("built")
