#!/usr/bin/env python3
"""Render the static pages of luckgram.cc in Chinese (default, at /) and English (at /en/).
Every piece of copy is written as t("English", "中文"). Edit the page bodies here, then run:
    python3 scripts/build.py
"""
import hashlib
import re
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIKI_HOST = "https://wiki.luckgram.cc"
IOS_REPO = "https://github.com/limeng9088/luckgram-ios"
ANDROID_REPO = "https://github.com/limeng9088/luckgram-android"
IOS_LATEST = IOS_REPO + "/releases/latest"
ANDROID_LATEST = ANDROID_REPO + "/releases/latest"
UPDATED = ("October 24, 2026", "2026 年 10 月 24 日")
LANGS = ("zh", "en")
LANG = "zh"  # the language currently being rendered
# Changes whenever site.css changes, so browsers and Cloudflare never pair new pages with an old stylesheet.
MEDIA_VERSION = "3"   # bump when the feature videos are re-rendered, so cached copies are skipped
CSS_VERSION = hashlib.sha1(open(os.path.join(ROOT, "assets", "site.css"), "rb").read()).hexdigest()[:10]


def t(en, zh):
    return zh if LANG == "zh" else en


def u(path):
    """Site path in the current language: /download/ -> /en/download/ for English."""
    return path if LANG == "zh" else "/en" + path


def wiki(path="/"):
    """Help Center link in the current language (Chinese at /, English at /en/)."""
    return WIKI_HOST + (path if LANG == "zh" else "/en" + path)


ICON_APPLE = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M16.4 12.6c0-2.4 2-3.6 2.1-3.6-1.1-1.7-2.9-1.9-3.5-1.9-1.5-.2-2.9.9-3.7.9-.8 0-1.9-.9-3.2-.8-1.6 0-3.1 1-4 2.4-1.7 3-.4 7.4 1.2 9.8.8 1.2 1.8 2.5 3 2.4 1.2 0 1.7-.8 3.1-.8 1.5 0 1.9.8 3.2.8 1.3 0 2.2-1.2 3-2.4.9-1.4 1.3-2.7 1.3-2.8 0 0-2.5-1-2.5-4zM14 5.4c.7-.8 1.1-1.9 1-3-1 0-2.1.7-2.8 1.5-.6.7-1.2 1.8-1 2.9 1.1.1 2.1-.6 2.8-1.4z"/></svg>'
ICON_ANDROID = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.6 9.5l1.6-2.8a.4.4 0 0 0-.7-.4l-1.6 2.8a9.9 9.9 0 0 0-7.8 0L7.5 6.3a.4.4 0 1 0-.7.4l1.6 2.8A9.2 9.2 0 0 0 3.5 17h17a9.2 9.2 0 0 0-2.9-7.5zM8 14.4a1 1 0 1 1 0-2 1 1 0 0 1 0 2zm8 0a1 1 0 1 1 0-2 1 1 0 0 1 0 2z"/></svg>'
ICON_GITHUB = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 1.5a10.5 10.5 0 0 0-3.3 20.5c.5.1.7-.2.7-.5v-1.8c-2.9.6-3.5-1.4-3.5-1.4-.5-1.2-1.2-1.5-1.2-1.5-.9-.7.1-.6.1-.6 1 .1 1.6 1.1 1.6 1.1.9 1.6 2.5 1.1 3.1.9.1-.7.4-1.1.7-1.4-2.3-.3-4.8-1.2-4.8-5.2 0-1.1.4-2.1 1.1-2.8-.1-.3-.5-1.4.1-2.8 0 0 .9-.3 2.9 1.1a10 10 0 0 1 5.2 0c2-1.4 2.9-1.1 2.9-1.1.6 1.4.2 2.5.1 2.8.7.8 1.1 1.7 1.1 2.8 0 4-2.5 4.9-4.8 5.2.4.3.7 1 .7 2v2.9c0 .3.2.6.7.5A10.5 10.5 0 0 0 12 1.5z"/></svg>'


def header(current, here):
    def link(href, label, key, cls=""):
        cur = ' aria-current="page"' if key == current else ""
        c = f' class="{cls}"' if cls else ""
        return f'<a href="{href}"{c}{cur}>{label}</a>'
    other = ("/en" + here) if LANG == "zh" else here
    switch = f'<a class="lang" href="{other}" hreflang="{"en" if LANG == "zh" else "zh-CN"}" lang="{"en" if LANG == "zh" else "zh-CN"}">{"EN" if LANG == "zh" else "中文"}</a>'
    return f'''<header class="site-header">
  <div class="wrap">
    <a class="logo" href="{u("/")}"><img src="/assets/logo-white-144.png" alt="" width="30" height="25">Luckgram</a>
    <nav class="nav" aria-label="{t("Main", "主导航")}">
      {link(u("/features/"), t("Features", "功能"), "features")}
      {link(wiki(), t("Help", "帮助"), "help")}
      {link(u("/#faq"), t("FAQ", "常见问题"), "faq", "opt")}
      {switch}
      {link(u("/download/"), t("Download", "下载"), "download", "get")}
    </nav>
  </div>
</header>'''


def footer():
    return f'''<footer class="site-footer">
  <div class="wrap">
    <div class="top">
      <div><a class="logo" href="{u("/")}"><img src="/assets/logo-white-144.png" alt="" width="30" height="25">Luckgram</a>
        <p>{t("An independent, open-source Telegram client.", "独立、开源的 Telegram 客户端。")}</p></div>
      <div><h4>{t("Product", "产品")}</h4><ul>
        <li><a href="{u("/download/")}">{t("Download", "下载")}</a></li>
        <li><a href="{u("/features/")}">{t("Features", "功能")}</a></li>
        <li><a href="{wiki()}">{t("Help Center", "帮助中心")}</a></li>
      </ul></div>
      <div><h4>{t("Source code", "源代码")}</h4><ul>
        <li><a href="{IOS_REPO}">{t("Luckgram for iOS", "iOS 版")}</a></li>
        <li><a href="{ANDROID_REPO}">{t("Luckgram for Android", "Android 版")}</a></li>
      </ul></div>
      <div><h4>{t("Legal", "法律")}</h4><ul>
        <li><a href="{u("/privacy-policy/")}">{t("Privacy Policy", "隐私政策")}</a></li>
        <li><a href="{u("/terms-of-use/")}">{t("Terms of Use", "使用条款")}</a></li>
      </ul></div>
      <div><h4>{t("Contact", "联系我们")}</h4><ul>
        <li><a href="mailto:support@luckgram.cc">support@luckgram.cc</a></li>
        <li><a href="mailto:contact@luckgram.cc">contact@luckgram.cc</a></li>
        <li><a href="mailto:ads@luckgram.cc">ads@luckgram.cc</a></li>
      </ul></div>
    </div>
    <div class="legal">
      <p>{t("Luckgram is an independent app based on the open-source Telegram apps. It is not made by, affiliated with, or endorsed by Telegram. Telegram is a trademark of Telegram FZ-LLC.",
            "Luckgram 是基于开源 Telegram 应用开发的独立应用，并非由 Telegram 制作，与 Telegram 没有关联，也未获其认可。Telegram 是 Telegram FZ-LLC 的商标。")}</p>
      <p>&copy; 2026 Luckgram</p>
    </div>
  </div>
</footer>
<script>
// Feature videos load and play only while they are on screen.
(function () {{
  var vids = document.querySelectorAll('video[data-lazy]');
  function load(v) {{ if (v.dataset.loaded) return; v.querySelectorAll('source').forEach(function (s) {{ s.src = s.dataset.src; }}); v.load(); v.dataset.loaded = 1; }}
  if (!('IntersectionObserver' in window)) {{ vids.forEach(load); return; }}
  var io = new IntersectionObserver(function (es) {{
    es.forEach(function (e) {{ var v = e.target; if (e.isIntersecting) {{ load(v); var p = v.play(); if (p) p.catch(function () {{}}); }} else v.pause(); }});
  }}, {{rootMargin: '200px 0px'}});
  vids.forEach(function (v) {{ io.observe(v); }});
}})();
</script>'''



def page(here, title, description, body, current=""):
    """here: the page's path without the language prefix, e.g. "/download/" or "/404.html"."""
    file = here + "index.html" if here.endswith("/") else here
    path = file.lstrip("/") if LANG == "zh" else "en" + file
    alt_zh, alt_en = "https://luckgram.cc" + here, "https://luckgram.cc/en" + here
    html = f'''<!doctype html>
<html lang="{"zh-CN" if LANG == "zh" else "en"}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="https://luckgram.cc/assets/icon-512.png">
<link rel="alternate" hreflang="zh-CN" href="{alt_zh}">
<link rel="alternate" hreflang="en" href="{alt_en}">
<link rel="alternate" hreflang="x-default" href="{alt_zh}">
<meta name="heleket" content="16ef8c76" />
<link rel="icon" href="/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="stylesheet" href="/assets/site.css?v={CSS_VERSION}">
</head>
<body>
{header(current, here)}
<main>
{body}
</main>
{footer()}
</body>
</html>
'''
    out = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)


# 24px line icons for the works-today list, in the same order as available()
TODAY_ICONS = [
    '<path d="M4 5h16v11H9l-5 4z"/>',
    '<path d="M3 10v4l4 1 8 4V5L7 9zM18 9a4 4 0 0 1 0 6"/>',
    '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a1 1 0 0 1-1 1A16 16 0 0 1 4 5a1 1 0 0 1 1-1z"/>',
    '<rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
    '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3.5"/>',
    '<circle cx="9" cy="9" r="3.5"/><path d="M3 20a6 6 0 0 1 12 0M16 6.5a3 3 0 0 1 0 5.5M18 14.5a5.5 5.5 0 0 1 3 5"/>',
]


def available():
    return [
        (t("Chats and groups", "聊天和群组"), t("Cloud chats that sync across your devices, groups of up to 200,000 members, replies, reactions and polls.",
                                          "在所有设备间同步的云端聊天，最多 20 万人的群组，支持回复、表情回应和投票。")),
        (t("Channels", "频道"), t("Follow and run channels, with comments, scheduled posts and statistics where Telegram offers them.",
                                "关注和运营频道，支持评论、定时发布，以及 Telegram 提供的数据统计。")),
        (t("Voice and video calls", "语音和视频通话"), t("End-to-end encrypted one-on-one calls, plus group calls and live streams.",
                                                  "端到端加密的一对一通话，还有群组通话和直播。")),
        (t("Secret Chats", "私密聊天"), t("Device-to-device encrypted chats with self-destructing messages.",
                                      "设备之间端到端加密的聊天，支持阅后即焚。")),
        (t("Stories, bots and mini apps", "动态、机器人和小程序"), t("Everything that runs on the Telegram platform works in Luckgram.",
                                                         "Telegram 平台上的一切都能在 Luckgram 中使用。")),
        (t("Several accounts", "多个账号"), t("Switch between Telegram accounts in one app, up to Telegram's standard limit.",
                                          "在一个应用里切换多个 Telegram 账号，上限与 Telegram 官方一致。")),
    ]


def faq():
    return [
        (t("Is Luckgram an official Telegram app?", "Luckgram 是 Telegram 官方应用吗？"),
         t("No. Luckgram is an independent app built from the open-source Telegram apps for iOS and Android. It is not made by, affiliated with, or endorsed by Telegram.",
           "不是。Luckgram 是基于开源的 Telegram iOS 和 Android 应用开发的独立应用，并非由 Telegram 制作，与 Telegram 没有关联，也未获其认可。")),
        (t("Can I use my existing Telegram account?", "可以用我现有的 Telegram 账号吗？"),
         t("Yes. Sign in with your phone number. Your cloud chats, contacts and channels load from Telegram as they do in any Telegram app.",
           "可以。用手机号登录即可，云端聊天、联系人和频道会像在任何 Telegram 应用里一样从 Telegram 加载。")),
        (t("Is Luckgram free?", "Luckgram 免费吗？"),
         t("Yes. Telegram Premium and Telegram Stars are Telegram's own services and are sold and managed by Telegram.",
           "免费。Telegram Premium 和 Telegram Stars 是 Telegram 自己的服务，由 Telegram 销售和管理。")),
        (t("Why isn't Luckgram on the App Store or Google Play?", "为什么 App Store 和 Google Play 上找不到 Luckgram？"),
         t("Luckgram is currently distributed through GitHub Releases. The Download page always links to the latest build.",
           "Luckgram 目前通过 GitHub Releases 发布。下载页上的链接始终指向最新版本。")),
        (t("How do I install Luckgram on an iPhone?", "怎么在 iPhone 上安装 Luckgram？"),
         t("The iOS build is an unsigned IPA. Sign it with a tool such as Sideloadly or AltStore, or with your own Apple developer certificate, then install it. The install guide walks through each step.",
           "iOS 版是未签名的 IPA。先用 Sideloadly、AltStore 等工具或你自己的 Apple 开发者证书签名，再安装。安装指南里有每一步的说明。")),
        (t("Which Android phones are supported?", "支持哪些 Android 手机？"),
         t("Android 6.0 or later on a 64-bit ARM phone (arm64-v8a), which covers almost every phone sold in recent years. Allow installs from your browser or file manager when asked.",
           "Android 6.0 及以上、64 位 ARM 处理器（arm64-v8a）的手机，近几年卖的手机基本都支持。安装时如有提示，请允许浏览器或文件管理器安装应用。")),
        (t("Where are the extra features?", "额外的功能在哪里？"),
         t("The features listed under In development are being built. Until they ship, Luckgram works like the Telegram app it is based on. No release dates are promised.",
           "标注为“开发中”的功能正在开发。上线之前，Luckgram 的用法和它所基于的 Telegram 应用一样。我们不承诺上线时间。")),
        (t("How do I get help?", "遇到问题怎么办？"),
         t(f'Start with the <a href="{wiki()}">Help Center</a>. If it does not answer your question, write to <a href="mailto:support@luckgram.cc">support@luckgram.cc</a>.',
           f'先看看<a href="{wiki()}">帮助中心</a>。如果没有找到答案，请发邮件到 <a href="mailto:support@luckgram.cc">support@luckgram.cc</a>。')),
    ]


def video(slug, label, lazy=True):
    # The website cut of each demo (luckgram-promo render-web.sh): just the phone, faded into black, no baked-in title.
    sfx = "" if LANG == "en" else "-zh"   # Chinese pages use the videos with the Chinese phone UI
    src = "data-src" if lazy else "src"
    attrs = 'preload="none" data-lazy' if lazy else 'autoplay preload="auto"'
    base = f"/media/web/{slug}{sfx}"
    return (f'<video class="demo" muted loop playsinline {attrs} poster="{base}.jpg?v={MEDIA_VERSION}" width="576" height="768" aria-label="{t("Animation", "演示动画")}: {label}">'
            f'<source {src}="{base}.webm?v={MEDIA_VERSION}" type="video/webm"><source {src}="{base}.mp4?v={MEDIA_VERSION}" type="video/mp4"></video>')


def download_buttons(primary=True):
    cls = "btn platform primary" if primary else "btn platform"
    return f'''<a class="{cls}" href="{IOS_LATEST}">{ICON_APPLE}<span><small>{t("iPhone and iPad", "iPhone 和 iPad")}</small>{t("Download for iOS", "下载 iOS 版")}</span></a>
        <a class="btn platform" href="{ANDROID_LATEST}">{ICON_ANDROID}<span><small>{t("Android 6.0 or later", "Android 6.0 及以上")}</small>{t("Download APK", "下载 APK")}</span></a>'''


def feature_by_slug():
    return {slug: (short, title, status, body) for _, items in feature_groups() for slug, short, title, status, body, _ in items}


def home():
    feats = feature_by_slug()
    n = len(feats)
    today = "\n".join(
        f'<div><svg class="ic" viewBox="0 0 24 24" aria-hidden="true">{ic}</svg><h3>{a}</h3><p>{d}</p></div>'
        for ic, (a, d) in zip(TODAY_ICONS, available()))
    cells = []
    for slug in ("accounts", "double-bottom", "translate-out", "voice-text", "round-video", "ai-summary"):
        short, title, (key, label), body = feats[slug]
        # subtitle: the full title, minus a leading "Name: " that would repeat the heading
        sub = re.sub(r"^.{1,24}?[:：]\s*", "", t(*title)) if t(*title).startswith(t(*short)) else t(*title)
        sub = sub[:1].upper() + sub[1:]
        cells.append(f'''<a class="cell" href="{u("/features/")}#{slug}">{video(slug, t(*title))}
        <span class="tag {key}">{t(*label)}</span><h3>{t(*short)}</h3><p>{sub}</p></a>''')
    qa = "\n".join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in faq())
    body = f'''<section class="hero">
  <div class="wrap">
    <div class="hero-text">
      <h1>{t("Telegram,<br>flying further", "Telegram，<br>飞得更远")}</h1>
      <p class="lede">{t("Luckgram is an independent, open-source Telegram client for iOS and Android. Sign in with your Telegram account and your chats, channels and calls are all there. More accounts, hidden chats, translation and AI tools are on the way.",
                         "Luckgram 是独立、开源的 iOS 和 Android Telegram 客户端。用你的 Telegram 账号登录，聊天、频道和通话都在；多账号、隐藏聊天、翻译和 AI 等功能正在陆续加入。")}</p>
      <div class="btns">
        {download_buttons()}
      </div>
      <p class="fine">{t(f'Free. Installing on iPhone? Read the <a href="{wiki("/getting-started/install.html")}">install guide</a>.', f'免费使用。在 iPhone 上安装，请先看<a href="{wiki("/getting-started/install.html")}">安装指南</a>。')}</p>
    </div>
    <figure class="stage" style="margin:0">
      {video("translate-in", t("Translate messages", "翻译消息"), lazy=False)}
      <figcaption><span class="tag ok">{t("Available now: translate incoming messages", "现已可用：翻译收到的消息")}</span></figcaption>
    </figure>
    <svg class="route" aria-hidden="true"><path id="route"/></svg>
    <div class="plane" id="plane" aria-hidden="true"></div>
  </div>
</section>

<section class="block">
  <div class="wrap">
    <div class="head"><h2>{t("Everything you use in Telegram", "你在 Telegram 里用的，<br>这里都有")}</h2>
      <p>{t("Luckgram connects to the Telegram network, so the features you rely on work from the first sign-in.", "Luckgram 连接的是 Telegram 网络，你常用的功能从第一次登录起就能用。")}</p></div>
    <div class="today">
{today}
    </div>
  </div>
</section>

<section class="block">
  <div class="wrap">
    <div class="head"><h2>{t("What Luckgram adds", "Luckgram 的新功能")}</h2>
      <p>{t("Each feature is marked with where it stands. Features in development are not in the app yet, and we don't promise release dates.", "每个功能都标明了目前的状态。标注“开发中”的功能还没有加入应用，我们也不承诺上线时间。")}</p></div>
    <div class="wall">
{"".join(cells)}
    </div>
    <div class="wall-foot"><span>{t(f"{n} features, each with a short demo.", f"共 {n} 个功能，每个都有演示动画。")}</span><a class="btn" href="{u("/features/")}">{t("See all features", "查看全部功能")}</a></div>
  </div>
</section>

<section class="block">
  <div class="wrap">
    <div class="head"><h2>{t("Open source, start to finish", "从头到尾都开源")}</h2>
      <p>{t("The complete code for both apps is public, and every release is built from it by GitHub Actions.", "两个应用的完整代码都已公开，每个版本都由 GitHub Actions 从这些代码构建。")}</p></div>
    <div class="open">
      <div><h3>{t("Your messages stay with Telegram", "消息只经过 Telegram")}</h3><p>{t("Messages go to Telegram's servers, as they would from any Telegram app. Luckgram runs no message servers of its own.", "你的消息和在任何 Telegram 应用里一样，发送到 Telegram 的服务器。Luckgram 没有自己的消息服务器。")}</p></div>
      <div><h3>{t("No added trackers", "不加追踪")}</h3><p>{t("Luckgram does not add analytics or advertising SDKs to the apps.", "Luckgram 没有在应用里加入任何统计或广告 SDK。")}</p></div>
      <div><h3>{t("Follows Telegram's updates", "跟进 Telegram 更新")}</h3><p>{t("Luckgram is built on the official open-source apps, so new Telegram features arrive with each update.", "Luckgram 基于官方开源应用构建，Telegram 的新功能会随更新一起到来。")}</p></div>
    </div>
    <div class="repos">
      <a class="repo" href="{IOS_REPO}">{ICON_GITHUB}<span><b>limeng9088/luckgram-ios</b>{t("Source code for iPhone and iPad", "iPhone 和 iPad 版源代码")}</span></a>
      <a class="repo" href="{ANDROID_REPO}">{ICON_GITHUB}<span><b>limeng9088/luckgram-android</b>{t("Source code for Android", "Android 版源代码")}</span></a>
    </div>
  </div>
</section>

<section class="cta" id="download">
  <div class="wrap">
    <div class="mark" aria-hidden="true"></div>
    <h2>{t("Take your Telegram with you", "带上你的 Telegram，出发")}</h2>
    <p>{t("Free for iPhone, iPad and Android. Sign in with the account you already have.", "iPhone、iPad 和 Android 均可免费使用，用你现有的账号登录。")}</p>
    <div class="btns">
      {download_buttons()}
    </div>
  </div>
</section>

<section class="block" id="faq">
  <div class="wrap faq">
    <div class="head solo"><h2>{t("Questions", "常见问题")}</h2>
      <p>{t(f'More answers in the <a href="{wiki()}">Help Center</a>.', f'更多解答请看<a href="{wiki()}">帮助中心</a>。')}</p></div>
    <div class="qa">
{qa}
    </div>
  </div>
</section>
<script>
// Draw the paper plane's route from under the buttons to the corner of the demo, then fly it once.
(function () {{
  var hero = document.querySelector('.hero .wrap'), path = document.getElementById('route'), plane = document.getElementById('plane');
  function draw() {{
    if (window.innerWidth < 980) {{ path.setAttribute('d', ''); plane.style.display = 'none'; return; }}
    var h = hero.getBoundingClientRect(), b = hero.querySelector('.fine').getBoundingClientRect(), s = hero.querySelector('.stage video').getBoundingClientRect();
    var x0 = b.left - h.left + 4, y0 = b.bottom - h.top + 44, x1 = s.left - h.left + 18, y1 = s.top - h.top + 6, dx = x1 - x0;
    var d = 'M' + x0 + ' ' + y0 + ' C' + (x0 + dx * .55) + ' ' + (y0 + 70) + ' ' + (x1 - dx * .5) + ' ' + (y1 + 40) + ' ' + x1 + ' ' + y1;
    path.setAttribute('d', d); plane.style.display = ''; plane.style.offsetPath = "path('" + d + "')";
  }}
  draw(); window.addEventListener('resize', draw);
}})();
</script>'''
    page("/", t("Luckgram – an independent Telegram client for iOS and Android", "Luckgram – 独立的 iOS 和 Android Telegram 客户端"),
         t("Luckgram is an independent, open-source Telegram client for iOS and Android. Sign in with your Telegram account and keep everything you use today.",
           "Luckgram 是独立、开源的 iOS 和 Android Telegram 客户端。用你的 Telegram 账号登录，现在用的一切都还在。"),
         body)


def download():
    body = f'''<section class="page-head">
  <div class="wrap">
    <h1>{t("Get Luckgram", "下载 Luckgram")}</h1>
    <p>{t("Luckgram is distributed through GitHub Releases. These links always open the latest build.",
          "Luckgram 通过 GitHub Releases 发布，下面的链接始终指向最新版本。")}</p>
  </div>
</section>
<div class="wrap">
  <div class="dl">
    <div class="dl-card">
      <svg class="os" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">{ICON_ANDROID[ICON_ANDROID.index("<path"):ICON_ANDROID.index("</svg>")]}</svg>
      <h2>Android</h2>
      <ul>
        <li>{t("Signed APK for 64-bit ARM phones (arm64-v8a)", "已签名的 APK，适用于 64 位 ARM 手机（arm64-v8a）")}</li>
        <li>{t("Android 6.0 or later", "Android 6.0 及以上")}</li>
        <li>{t("Allow installs from your browser or file manager when asked", "安装时如有提示，请允许浏览器或文件管理器安装应用")}</li>
      </ul>
      <div class="btns"><a class="btn primary" href="{ANDROID_LATEST}">{t("Download APK", "下载 APK")}</a></div>
    </div>
    <div class="dl-card">
      <svg class="os" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">{ICON_APPLE[ICON_APPLE.index("<path"):ICON_APPLE.index("</svg>")]}</svg>
      <h2>{t("iPhone and iPad", "iPhone 和 iPad")}</h2>
      <ul>
        <li>{t("Unsigned IPA", "未签名的 IPA")}</li>
        <li>{t("Sign it with Sideloadly, AltStore or your own certificate before installing", "安装前先用 Sideloadly、AltStore 或你自己的证书签名")}</li>
        <li>{t("iOS 15 or later", "iOS 15 及以上")}</li>
      </ul>
      <div class="btns"><a class="btn primary" href="{IOS_LATEST}">{t("Download IPA", "下载 IPA")}</a><a class="btn" href="{wiki("/getting-started/install.html")}">{t("Install guide", "安装指南")}</a></div>
    </div>
  </div>
  <p class="note">{t("If you previously installed a test build of Luckgram on Android, uninstall it first: builds signed with a different key cannot update each other. Only download Luckgram from this page or the GitHub repositories it links to.",
                     "如果你之前在 Android 上装过 Luckgram 的测试版，请先卸载：签名密钥不同的版本不能相互覆盖升级。请只从本页或本页链接的 GitHub 仓库下载 Luckgram。")}</p>
</div>'''
    page("/download/", t("Download Luckgram for Android and iOS", "下载 Luckgram（Android 和 iOS）"),
         t("Download the latest Luckgram builds for Android (APK) and iOS (IPA).", "下载最新版 Luckgram：Android（APK）和 iOS（IPA）。"), body, "download")



def privacy():
    body = f'''<article class="prose">
<h1>{t("Privacy Policy", "隐私政策")}</h1>
<p class="meta">{t("Last updated", "最后更新：")}{" " if LANG == "en" else ""}{t(*UPDATED)}</p>

<p>{t("This policy explains what happens to your information when you use the Luckgram apps for iOS and Android and the luckgram.cc websites. Luckgram is an independent app built from the open-source Telegram apps.",
      "本政策说明你使用 Luckgram iOS 和 Android 应用以及 luckgram.cc 网站时，你的信息会如何处理。Luckgram 是基于开源 Telegram 应用开发的独立应用。")}</p>

<h2>{t("Your Telegram data", "你的 Telegram 数据")}</h2>
<p>{t('Luckgram is a client for the Telegram network. When you sign in, send messages, make calls or sync contacts, the app exchanges that data directly with Telegram\'s servers. That data is processed by Telegram under the <a href="https://telegram.org/privacy">Telegram Privacy Policy</a>, not by Luckgram.',
      'Luckgram 是 Telegram 网络的客户端。你登录、发消息、打电话或同步联系人时，应用直接与 Telegram 的服务器交换这些数据。这些数据由 Telegram 依据 <a href="https://telegram.org/privacy">Telegram 隐私政策</a>处理，而不是由 Luckgram 处理。')}</p>
<p>{t("Luckgram does not run its own servers for your messages, calls, contacts or media, and does not receive copies of them.",
      "Luckgram 没有为你的消息、通话、联系人或媒体设立自己的服务器，也不会收到它们的副本。")}</p>

<h2>{t("Data stored on your device", "存储在你设备上的数据")}</h2>
<p>{t("Like other Telegram apps, Luckgram keeps a local cache of your chats and media on your device so the app works quickly and offline. You can clear it in the app's storage settings, or remove it by uninstalling the app.",
      "和其他 Telegram 应用一样，Luckgram 会在你的设备上缓存聊天和媒体，让应用运行更快、离线也能查看。你可以在应用的存储设置里清除缓存，卸载应用也会将其删除。")}</p>

<h2>{t("Analytics and advertising", "统计和广告")}</h2>
<p>{t("Luckgram does not add analytics, advertising or tracking SDKs to the apps. Sponsored messages that Telegram shows in some public channels come from Telegram and follow Telegram's policies.",
      "Luckgram 没有在应用中加入统计、广告或追踪 SDK。部分公开频道里由 Telegram 展示的赞助消息来自 Telegram，并遵循 Telegram 的政策。")}</p>

<h2>{t("Services from Apple and Google", "Apple 和 Google 的服务")}</h2>
<p>{t("The apps use services built into the operating system or the Telegram code. Push notifications are delivered through Apple Push Notification service on iOS and Firebase Cloud Messaging on Android. On Android, maps and location features may use Google Play services. These providers process data under their own privacy policies.",
      "应用会使用操作系统或 Telegram 代码中内置的服务：iOS 上的推送通知通过 Apple 推送通知服务送达，Android 上通过 Firebase Cloud Messaging 送达；Android 上的地图和定位功能可能使用 Google Play 服务。这些服务商依据各自的隐私政策处理数据。")}</p>

<h2>{t("Downloads", "下载")}</h2>
<p>{t('App builds are hosted on GitHub. When you download one, GitHub processes your request under the <a href="https://docs.github.com/site-policy/privacy-policies/github-general-privacy-statement">GitHub Privacy Statement</a>.',
      '应用安装包托管在 GitHub 上。你下载时，GitHub 依据 <a href="https://docs.github.com/site-policy/privacy-policies/github-general-privacy-statement">GitHub 隐私声明</a>处理你的请求。')}</p>

<h2>{t("Our websites", "我们的网站")}</h2>
<p>{t("luckgram.cc and wiki.luckgram.cc are static websites hosted on GitHub Pages and served through Cloudflare. These providers may process technical data such as your IP address and browser type to deliver and protect the sites. The sites do not use cookies or analytics of their own.",
      "luckgram.cc 和 wiki.luckgram.cc 是托管在 GitHub Pages、经由 Cloudflare 提供访问的静态网站。这些服务商可能会处理 IP 地址、浏览器类型等技术数据，用于提供和保护网站。网站本身不使用 Cookie，也没有自己的统计。")}</p>

<h2>{t("Email", "电子邮件")}</h2>
<p>{t("If you write to a luckgram.cc address, we receive your email address and message and use them only to reply to you. Mail to these addresses is forwarded through Cloudflare Email Routing.",
      "如果你给 luckgram.cc 的邮箱写信，我们会收到你的邮箱地址和邮件内容，只用于回复你。发往这些地址的邮件经由 Cloudflare Email Routing 转发。")}</p>

<h2>{t("Children", "儿童")}</h2>
<p>{t("Luckgram is not intended for children under the minimum age that Telegram requires in their country.",
      "Luckgram 不面向未达到其所在国家 Telegram 最低使用年龄的儿童。")}</p>

<h2>{t("Changes", "政策变更")}</h2>
<p>{t("We may update this policy. The date at the top of this page shows when it last changed.",
      "我们可能会更新本政策，页面顶部的日期是最后一次修改的时间。")}</p>

<h2>{t("Contact", "联系我们")}</h2>
<p>{t("Questions about privacy:", "隐私相关问题请联系：")} <a href="mailto:support@luckgram.cc">support@luckgram.cc</a></p>
{t("", '<p class="note">本政策以中文和英文发布。两种版本如有不一致，以英文版为准。</p>')}
</article>'''
    page("/privacy-policy/", t("Privacy Policy – Luckgram", "隐私政策 – Luckgram"),
         t("How Luckgram handles your information.", "Luckgram 如何处理你的信息。"), body)


def terms():
    body = f'''<article class="prose">
<h1>{t("Terms of Use", "使用条款")}</h1>
<p class="meta">{t("Last updated", "最后更新：")}{" " if LANG == "en" else ""}{t(*UPDATED)}</p>

<p>{t("These terms apply to your use of the Luckgram apps and the luckgram.cc websites. By using Luckgram you agree to them.",
      "本条款适用于你对 Luckgram 应用和 luckgram.cc 网站的使用。使用 Luckgram 即表示你同意本条款。")}</p>

<h2>{t("What Luckgram is", "Luckgram 是什么")}</h2>
<p>{t("Luckgram is an independent app built from the open-source Telegram apps. It is not made by, affiliated with, or endorsed by Telegram. Telegram is a trademark of Telegram FZ-LLC.",
      "Luckgram 是基于开源 Telegram 应用开发的独立应用，并非由 Telegram 制作，与 Telegram 没有关联，也未获其认可。Telegram 是 Telegram FZ-LLC 的商标。")}</p>

<h2>{t("Telegram's terms still apply", "Telegram 的条款依然适用")}</h2>
<p>{t('Luckgram connects you to the Telegram network. Your Telegram account, and everything you do with it, is subject to <a href="https://telegram.org/tos">Telegram\'s Terms of Service</a>. Telegram may limit or close accounts under its own rules, and Luckgram cannot reverse those decisions.',
      'Luckgram 将你连接到 Telegram 网络。你的 Telegram 账号及你用它进行的一切活动，均受 <a href="https://telegram.org/tos">Telegram 服务条款</a>约束。Telegram 可能依据自身规则限制或封禁账号，Luckgram 无法撤销这些决定。')}</p>

<h2>{t("Acceptable use", "合理使用")}</h2>
<p>{t("Do not use Luckgram to send spam, to scam or harass people, to spread illegal content, or to break the law where you live.",
      "不得使用 Luckgram 发送垃圾信息、诈骗或骚扰他人、传播违法内容，或违反你所在地的法律。")}</p>

<h2>{t("Telegram Premium and Stars", "Telegram Premium 和 Stars")}</h2>
<p>{t("Telegram Premium, Telegram Stars and other paid Telegram services are sold and managed by Telegram. Luckgram is free and does not sell them.",
      "Telegram Premium、Telegram Stars 及其他 Telegram 付费服务由 Telegram 销售和管理。Luckgram 免费，不出售这些服务。")}</p>

<h2>{t("Open-source licence", "开源许可")}</h2>
<p>{t(f'Luckgram is built from the Telegram apps, which Telegram publishes under the GNU General Public License. The complete Luckgram source code is available on GitHub for <a href="{IOS_REPO}">iOS</a> and <a href="{ANDROID_REPO}">Android</a>.',
      f'Luckgram 基于 Telegram 应用开发，Telegram 以 GNU 通用公共许可证（GPL）发布这些应用。Luckgram 的完整源代码在 GitHub 上公开：<a href="{IOS_REPO}">iOS</a> 和 <a href="{ANDROID_REPO}">Android</a>。')}</p>

<h2>{t("Installing builds", "安装包")}</h2>
<p>{t("Luckgram is distributed through GitHub Releases. Download it only from the links on luckgram.cc or from the GitHub repositories above. You are responsible for how you sign and install the iOS build.",
      "Luckgram 通过 GitHub Releases 发布。请只从 luckgram.cc 上的链接或上面的 GitHub 仓库下载。iOS 版如何签名和安装由你自行负责。")}</p>

<h2>{t("No warranty", "免责声明")}</h2>
<p>{t('Luckgram is provided "as is", without warranty of any kind. Features listed as in development may change or may not ship. To the extent the law allows, Luckgram is not liable for any loss arising from your use of the apps or websites.',
      "Luckgram 按“现状”提供，不作任何形式的保证。标注为开发中的功能可能会变更，也可能不会上线。在法律允许的范围内，Luckgram 不对你使用应用或网站造成的任何损失承担责任。")}</p>

<h2>{t("Changes", "条款变更")}</h2>
<p>{t("We may update these terms. The date at the top of this page shows when they last changed.",
      "我们可能会更新本条款，页面顶部的日期是最后一次修改的时间。")}</p>

<h2>{t("Contact", "联系我们")}</h2>
<p><a href="mailto:contact@luckgram.cc">contact@luckgram.cc</a></p>
{t("", '<p class="note">本条款以中文和英文发布。两种版本如有不一致，以英文版为准。</p>')}
</article>'''
    page("/terms-of-use/", t("Terms of Use – Luckgram", "使用条款 – Luckgram"),
         t("The terms for using Luckgram.", "使用 Luckgram 的条款。"), body)


WIP = ("wip", ("In development", "开发中"))
OK_TG = ("ok", ("Available (Telegram feature)", "已上线（Telegram 功能）"))


# Feature page: (slug, short name, title, status, body, help path); text pairs are (English, Chinese)
def feature_groups():
    return [
    (("Accounts and privacy", "账号与隐私"), [
        ("accounts", ("More accounts", "更多账号"), ("More accounts in one app", "一个应用登录更多账号"), WIP,
         ("Today Luckgram follows Telegram's standard limit of 3 accounts on one device. We are removing the cap on both "
          "iOS and Android, so personal, work, client and channel-admin accounts sit side by side, each with its own "
          "notifications, and you switch between them in a tap.",
          "目前 Luckgram 在一台设备上可登录的账号数与 Telegram 官方一致（3 个）。我们正在 iOS 和 Android 上取消这个上限，"
          "个人、工作、客户和频道管理账号可以并排放着，各自的通知互不干扰，一点就能切换。"),
         "/getting-started/accounts.html"),
        ("backup", ("Account backup", "账号备份"), ("Back up your accounts and move them to a new phone", "备份账号，换手机时一起带走"), WIP,
         ("Choose the accounts you want and save them to one backup file locked with your own password. Restore it on a "
          "new phone or after reinstalling, without signing in to each account again, and move between iPhone and "
          "Android with the same file.",
          "选择要备份的账号，保存成一个用你自己的密码加密的备份文件。换新手机或重装应用后用它恢复，不用再逐个登录；"
          "同一个文件在 iPhone 和 Android 之间也能互相迁移。"),
         "/features/privacy.html"),
        ("double-bottom", ("Double Bottom", "双重空间"), ("Double Bottom: a second passcode with its own view", "双重空间：第二个密码，打开另一套视图"), WIP,
         ("Set a second passcode that opens Luckgram with only the accounts you pick. Your usual passcode still opens "
          "everything, so you decide what shows up when someone else is looking.",
          "设置第二个密码，用它打开 Luckgram 时只显示你挑选的账号；用平时的密码则打开全部。别人在看你手机时显示什么，由你决定。"),
         "/features/privacy.html"),
        ("hidden-chats", ("Hidden chats", "隐藏聊天"), ("Hide chats without deleting them", "隐藏聊天，不用删除"), WIP,
         ("Swipe a chat out of your list without deleting it or leaving the group. Hidden chats stay one gesture away "
          "whenever you need them.",
          "滑动一下就能把聊天从列表里隐藏，既不删除，也不用退群。需要时一个手势就能找回。"),
         "/features/privacy.html"),
        ("unblock", ("Restricted channels", "受限频道"), ("Open channels the store apps hide, for free", "免费打开商店版隐藏的频道"), WIP,
         ("Some channels and groups are hidden only in the App Store and Google Play builds of Telegram. Turn on one "
          "switch in Settings and Luckgram opens them, free and permanently, with no website login. Channels that "
          "Telegram blocks for everyone, or that are blocked where you live, stay blocked.",
          "有些频道和群组只在 App Store 和 Google Play 版的 Telegram 里被隐藏。在设置里打开一个开关，Luckgram 就能打开它们："
          "免费、永久有效，也不用登录任何网站。Telegram 对所有人封禁的频道，以及你所在地区依法屏蔽的频道，仍然打不开。"),
         "/features/privacy.html"),
    ]),
    (("Messages and language", "消息与语言"), [
        ("translate-in", ("Translate messages", "翻译消息"), ("Read messages in your language", "用你的语言阅读消息"), OK_TG,
         ("Tap Translate and messages in another language switch to yours, right in the chat. This is Telegram's own "
          "translation: single messages are free, and translating a whole chat at once needs Telegram Premium.",
          "点“翻译”，外语消息就直接在聊天里变成你的语言。这是 Telegram 自带的翻译：翻译单条消息免费，一次翻译整个聊天需要 Telegram Premium。"),
         "/features/translation-and-voice.html"),
        ("translate-out", ("Translate before sending", "发送前翻译"), ("Translate what you write before you send it", "发送前先翻译你写的内容"), WIP,
         ("Write in the language you think in, then translate the text in the input bar and send it in your contact's "
          "language. You see the result before anything is sent.",
          "用你习惯的语言写，在输入框里翻译成对方的语言再发出去。发送前你能先看到翻译结果。"),
         "/features/translation-and-voice.html"),
        ("voice-text", ("Voice to text", "语音转文字"), ("Read voice messages, dictate your replies", "语音消息直接看，回复直接说"),
         ("part", ("Telegram Premium; free version in development", "Telegram Premium 功能，免费版开发中")),
         ("Turn voice messages and round videos of any length into text with one tap, handy in a meeting or on a noisy "
          "train. Dictate instead of typing and watch the words appear as you speak; optional AI cleanup removes filler "
          "words and fixes punctuation. Telegram offers transcription with Premium; a free version for Luckgram is being built.",
          "一点就把任意长度的语音消息和圆形视频转成文字，开会时、在嘈杂的地铁上都方便。也可以直接说话代替打字，边说边出字；"
          "可选的 AI 整理会去掉口头禅、补好标点。Telegram 的转写功能需要 Premium，Luckgram 正在开发免费版。"),
         "/features/translation-and-voice.html"),
        ("quick-replies", ("Quick replies", "快捷回复"), ("Answer with saved quick replies", "用保存好的快捷回复作答"), WIP,
         ("Keep the answers you send all the time, such as running late or I will call you back, and send them with "
          "one tap from the input bar.",
          "把常用的回复存起来，比如“我晚点到”“稍后回电”，在输入框一点就能发出。"),
         "/features/messaging.html"),
        ("forward-anon", ("Forward without name", "隐藏来源转发"), ("Forward without the sender's name", "转发时隐藏原发送者"), OK_TG,
         ("When you forward a message, turn on Hide sender's name and it arrives as if you wrote it, without the "
          "original author attached.",
          "转发消息时打开“隐藏发送者名字”，消息就像是你自己发的，不会带上原作者。"),
         "/features/messaging.html"),
        ("select-all", ("Select all", "全选"), ("Select every message from one person", "一键选中某人的全部消息"), WIP,
         ("Long-press a message and select everything that person wrote in the chat at once, not just the last hundred, "
          "ready to copy, forward, save or delete.",
          "长按一条消息，就能一次选中这个人在聊天里发的所有消息（不限 100 条），方便复制、转发、收藏或删除。"),
         "/features/messaging.html"),
        ("save-direct", ("Save in one tap", "一键收藏"), ("Save to Saved Messages in one tap", "一键存到收藏夹"), WIP,
         ("Keep a post or message for later straight from the message menu, without opening the forward screen and "
          "looking for Saved Messages.",
          "直接在消息菜单里把帖子或消息存起来，不用打开转发页面再去找“收藏夹”。"),
         "/features/messaging.html"),
    ]),
    (("Media, calls and storage", "媒体、通话与存储"), [
        ("round-video", ("Round videos", "圆形视频"), ("Send gallery videos as round video messages", "把相册视频发成圆形视频消息"), WIP,
         ("Pick a video you already recorded and send it as a round video message, the same way as one you film in "
          "the chat.",
          "选一段相册里已有的视频，像在聊天里现拍的一样，发成圆形视频消息。"),
         "/features/media-and-calls.html"),
        ("call-rec", ("Call recording", "通话录音"), ("Record calls, with a transcript and AI summary", "通话录音，附文字稿和 AI 总结"), WIP,
         ("Record a call with one tap, on iPhone and Android. When you hang up, the recording lands in Saved Messages or "
          "any chat you choose, with a searchable transcript and an AI summary of what was agreed. Recording laws "
          "differ by country; let the other person know before you record.",
          "一点就能录下通话，iPhone 和 Android 都支持。挂断后录音会存到收藏夹或你指定的聊天，附带可搜索的文字稿和 AI 总结，"
          "谈好了什么一目了然。各国对录音的法律规定不同，录音前请先告知对方。"),
         "/features/media-and-calls.html"),
        ("cache", ("Storage", "存储空间"), ("See what takes up space and clear it", "看清空间被谁占用，按需清理"),
         ("part", ("Available; extra controls in development", "已上线，更多设置开发中")),
         ("Storage Usage shows how much space videos, photos, files and music take on your phone, and you clear the "
          "types you choose. Coming next: pick any cache size from 1 GB to no limit, keep media from one hour to "
          "forever, and set different rules for each chat.",
          "“存储空间”会显示视频、照片、文件和音乐各占多少空间，你可以按类型清理。即将加入：缓存上限可在 1 GB 到不限之间任选，"
          "媒体保留时间从 1 小时到永久，还能给每个聊天单独设置。"),
         "/features/media-and-calls.html"),
    ]),
    (("Profiles and organizing", "资料与整理"), [
        ("profile-info", ("Profile details", "资料详情"), ("Telegram ID, sign-up date and clickable bio links", "Telegram ID、注册时间和可点击的简介链接"), WIP,
         ("Profiles show the account's Telegram ID, which you can copy in a tap, an estimate of when the account was "
          "created, and links in bios that open when you tap them.",
          "个人资料页会显示账号的 Telegram ID（一点即可复制）、账号大致的注册时间，简介里的链接也能直接点开。"),
         "/features/profiles-and-folders.html"),
        ("keyword-folders", ("Keyword folders", "关键词文件夹"), ("Keyword folders that find chats for you", "关键词文件夹，帮你找出相关聊天"), WIP,
         ("Create a folder from a word, such as invoice or flight, and it gathers every chat that mentions it, with the "
          "word highlighted.",
          "用一个词建文件夹，比如“发票”或“航班”，所有提到这个词的聊天都会归进来，关键词会高亮显示。"),
         "/features/profiles-and-folders.html"),
        ("user-notes", ("Private notes", "私人备注"), ("Private notes on any contact", "给任何联系人写私人备注"), WIP,
         ("Write a note on someone's profile, such as where you met or what they ordered. Only you can see it, it shows "
          "at the top of your chat with them, and you can search all your notes at once.",
          "在对方的资料页写一条备注，比如在哪认识、订过什么。只有你能看到，打开和对方的聊天时会显示在顶部，所有备注还能一起搜索。"),
         "/features/profiles-and-folders.html"),
        ("shared-activity", ("Activity", "共同群动态"), ("See what a contact said in groups you share", "查看联系人在共同群里说了什么"), WIP,
         ("Open a profile and the Activity tab lists that person's latest messages in the groups you are both in, "
          "with a tap to jump to each one. It only shows messages you could already read in those groups.",
          "打开资料页的“动态”标签，就能看到对方最近在你们共同所在的群里发的消息，点一下就跳到原处。只显示你在这些群里本来就能看到的消息。"),
         "/features/profiles-and-folders.html"),
    ]),
    (("AI", "AI"), [
        ("ai-chat", ("AI assistant", "AI 助手"), ("An AI assistant inside your chats", "聊天里的 AI 助手"), WIP,
         ("Ask a question, get a topic explained with an example, have a long text summarized or rewritten, or a math "
          "problem worked through step by step, in a chat like any other. Share a message, a link or a file with it "
          "straight from any chat.",
          "像平常聊天一样提问：让它举例讲解一个话题、总结或改写一段长文，或者一步步解一道数学题。"
          "任何聊天里的消息、链接和文件都能直接转给它处理。"),
         "/features/ai.html"),
        ("ai-summary", ("Chat summary", "聊天总结"), ("Catch up on a busy chat with a summary", "用总结快速跟上热闹的群聊"), WIP,
         ("Coming back to hundreds of unread messages? Get the decisions, dates and open questions in a few lines "
          "before you scroll. Ask your own question, such as what the client agreed to, and tap any point to jump to "
          "the messages behind it.",
          "回来发现几百条未读？先用几行字看清结论、日期和待解决的问题，再决定要不要往上翻。"
          "也可以直接问，比如“客户最后答应了什么”，点任意一条就能跳到对应的原消息。"),
         "/features/ai.html"),
        ("ai-reply", ("Reply drafts", "AI 回复"), ("Turn rough notes into a reply", "把随手写的几个字变成得体的回复"), WIP,
         ("Type what you mean, however quickly, and choose from polished replies that fit the conversation. Edit "
          "the one you pick before you send it.",
          "随手打下你想说的意思，从几条贴合对话的润色回复里挑一条，发送前还可以再改。"),
         "/features/ai.html"),
        ("ai-writing", ("AI writing", "AI 写作"), ("Polish any message before you send it", "发送前一键润色任何消息"), WIP,
         ("Type in any chat, tap the AI button in the input bar and choose what you want: better wording, more formal, "
          "friendlier, shorter or just fixed grammar. The text is rewritten in place, in your language.",
          "在任何聊天里打完字，点输入框里的 AI 按钮，选你想要的效果：表达更好、更正式、更亲切、更简短，或者只改语法。"
          "文字会在输入框里直接改好，语言保持不变。"),
         "/features/ai.html"),
        ("ai-agents", ("AI agents", "AI 智能体"), ("AI agents for every task, or build your own", "各种任务的 AI 智能体，也能自己做一个"), WIP,
         ("Pick an agent made for the job, such as a travel planner, copywriter, language tutor or researcher, and chat "
          "with it like with anyone else. Need something specific? Create your own agent with your own instructions.",
          "挑一个专做这件事的智能体，比如旅行规划、文案、语言陪练或资料查询，像和普通联系人一样聊天。"
          "有特别的需求？用你自己的指令做一个专属智能体。"),
         "/features/ai.html"),
        ("ai-image", ("AI images", "AI 画图"), ("Create images from a sentence", "一句话生成图片"), WIP,
         ("Describe the picture you want and it appears in the chat. Send it to any chat or channel, save it, or ask "
          "for another version.",
          "描述你想要的画面，图片就出现在聊天里。可以直接发到任何聊天或频道、保存下来，或者再生成一版。"),
         "/features/ai.html"),
        ("ai-post", ("AI posts", "AI 写帖子"), ("Channel posts written in your channel's style", "按你频道的风格写帖子"), WIP,
         ("Give a topic and get a ready-to-edit post that matches the tone of your earlier posts. Make it shorter, add "
          "emoji or translate it, then publish from the same screen.",
          "给一个主题，就能得到一篇可以直接修改的帖子，语气和你以前发的保持一致。可以改短、加表情或翻译，在同一个页面直接发布。"),
         "/features/ai.html"),
    ]),
    ]


def features():
    toc, sections = [], []
    for group, items in feature_groups():
        toc.append(f'<li class="toc-group">{t(*group)}</li>')
        for slug, short, title, (key, label), body, help_path in items:
            title = t(*title)
            toc.append(f'<li><a href="#{slug}">{t(*short)}</a></li>')
            sections.append(f'''<section class="feat" id="{slug}">
  {video(slug, title)}
  <div class="feat-text">
    <span class="tag {key}">{t(*label)}</span>
    <h2>{title}</h2>
    <p>{t(*body)}</p>
    <p class="feat-more"><a href="{wiki(help_path)}">{t("Read more in the Help Center", "在帮助中心了解更多")}</a></p>
  </div>
</section>''')
    body = f'''<section class="page-head">
  <div class="wrap">
    <h1>{t("Luckgram features", "Luckgram 功能")}</h1>
    <p>{t("Everything you use in Telegram already works in Luckgram. Below are the extras we add, each marked with where it stands today. Features in development are not in the app yet, and no release dates are promised.",
          "你在 Telegram 里用的一切，Luckgram 里都能用。下面是我们额外增加的功能，每项都标明了目前的状态。标注“开发中”的功能还没有加入应用，我们也不承诺上线时间。")}</p>
  </div>
</section>
<div class="wrap feat-layout">
  <nav class="feat-toc" aria-label="{t("Features", "功能")}"><ul>
    {"".join(toc)}
  </ul></nav>
  <div class="feat-list">
{"".join(sections)}
  </div>
</div>
<section class="cta">
  <div class="wrap">
    <div class="mark" aria-hidden="true"></div>
    <h2>{t("Start with what works today", "先从现在能用的开始")}</h2>
    <p>{t("Sign in with your Telegram account. New features arrive with updates.", "用你的 Telegram 账号登录，新功能会随更新到来。")}</p>
    <div class="btns">
      {download_buttons()}
    </div>
  </div>
</section>
<script>
// Highlight the feature being read in the list.
(function () {{
  var links = {{}}; document.querySelectorAll('.feat-toc a').forEach(function (a) {{ links[a.getAttribute('href').slice(1)] = a; }});
  if (!('IntersectionObserver' in window)) return;
  var io = new IntersectionObserver(function (es) {{
    es.forEach(function (e) {{ if (!e.isIntersecting) return; var a = links[e.target.id]; if (!a) return;
      document.querySelectorAll('.feat-toc a.on').forEach(function (x) {{ x.classList.remove('on'); }}); a.classList.add('on');
      // keep the current item centred in the list without moving the page
      var toc = document.querySelector('.feat-toc'), wide = window.innerWidth >= 980;
      toc.scrollTo(wide ? {{top: a.offsetTop - toc.clientHeight / 2 + a.offsetHeight / 2, behavior: 'smooth'}}
                        : {{left: a.offsetLeft - toc.clientWidth / 2 + a.offsetWidth / 2, behavior: 'smooth'}}); }});
  }}, {{rootMargin: '-45% 0px -50% 0px'}});
  document.querySelectorAll('.feat').forEach(function (s) {{ io.observe(s); }});
}})();
</script>'''
    page("/features/", t("Luckgram features – what works today and what is coming", "Luckgram 功能 – 现在能用的和即将推出的"),
         t("Every Luckgram feature with its current status: Telegram features available today and Luckgram additions in development.",
           "Luckgram 全部功能及当前状态：现在可用的 Telegram 功能，以及正在开发的 Luckgram 新功能。"),
         body, "features")


def not_found():
    body = f'''<article class="prose">
<h1>{t("Page not found", "页面不存在")}</h1>
<p>{t(f'This page does not exist. Go to the <a href="{u("/")}">home page</a> or the <a href="{u("/download/")}">downloads</a>.',
      f'这个页面不存在。去<a href="{u("/")}">首页</a>或<a href="{u("/download/")}">下载页</a>看看吧。')}</p>
<p><a href="/en/">English</a> · <a href="/">中文</a></p>
</article>'''
    page("/404.html", t("Page not found – Luckgram", "页面不存在 – Luckgram"), t("Page not found.", "页面不存在。"), body)


def redirect(path, target):
    out = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>Luckgram</title>
<meta http-equiv="refresh" content="0; url={target}">
<link rel="canonical" href="{target}">
</head><body><p><a href="{target}">{target}</a></p></body></html>
''')


if __name__ == "__main__":
    for LANG in LANGS:
        home()
        download()
        privacy()
        terms()
        features()
        if LANG == "zh":
            not_found()   # GitHub Pages serves one 404 page for the whole site
        # Paths referenced by the Help Center.
        redirect(("" if LANG == "zh" else "en/") + "faq/index.html", wiki("/help/"))
        redirect(("" if LANG == "zh" else "en/") + "hub/index.html", wiki("/features/ai.html"))
    print("built")
