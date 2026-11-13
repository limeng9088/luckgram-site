#!/usr/bin/env python3
"""Render the static pages of luckgram.cc in Chinese (default, at /) and English (at /en/).
Every piece of copy is written as t("English", "中文"). Edit the page bodies here, then run:
    python3 scripts/build.py
"""
import hashlib
import json
import re
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIKI_HOST = "https://wiki.luckgram.cc"
IOS_REPO = "https://github.com/limeng9088/luckgram-ios"
ANDROID_REPO = "https://github.com/limeng9088/luckgram-android"
# Downloads come from dl.luckgram.cc (Cloudflare in front of S3), never from GitHub.
# The buttons get the newest file from download/latest.json at page load; these
# build-time links are the fallback when that file can't be loaded.
def _latest():
    import json as _j
    try:
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "download", "latest.json"), encoding="utf-8") as f:
            return _j.load(f)
    except (OSError, ValueError):
        return {}
_L = _latest()
IOS_LATEST = _L.get("ios", {}).get("url", "/download/")
ANDROID_LATEST = _L.get("android", {}).get("arm64", {}).get("url", "/download/")
ANDROID_X86_LATEST = _L.get("android", {}).get("x86_64", {}).get("url", ANDROID_LATEST)
WIN_LATEST = _L.get("windows", {}).get("setup", {}).get("url", "/download/")
WIN_PORTABLE_LATEST = _L.get("windows", {}).get("portable", {}).get("url", WIN_LATEST)
# Signed iOS build: installs straight from Safari, no computer. The signing service rotates its
# install domain, so the button asks IOS_INSTALL_API for the current address on click and falls
# back to IOS_INSTALL when that request fails.
IOS_INSTALL_API = "https://api.owcywmpr.com/api/mdm/link/yx6sv23c"
IOS_INSTALL = "https://luckgram.evztet.cn/yx6sv23c"
UPDATED = ("October 24, 2026", "2026 年 10 月 24 日")
PRIVACY_UPDATED = ("November 4, 2026", "2026 年 11 月 4 日")
LANGS = ("zh", "en")
LANG = "zh"  # the language currently being rendered
# Changes whenever site.css changes, so browsers and Cloudflare never pair new pages with an old stylesheet.
MEDIA_VERSION = "4"   # bump when the feature videos are re-rendered, so cached copies are skipped
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
ICON_WINDOWS = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M3 5.1l7.4-1v7.2H3V5.1zm8.3-1.2L21 2.5v8.8h-9.7V3.9zM3 12.7h7.4v7.2L3 18.9v-6.2zm8.3 0H21v8.8l-9.7-1.4v-7.4z"/></svg>'
ICON_ANDROID = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.6 9.5l1.6-2.8a.4.4 0 0 0-.7-.4l-1.6 2.8a9.9 9.9 0 0 0-7.8 0L7.5 6.3a.4.4 0 1 0-.7.4l1.6 2.8A9.2 9.2 0 0 0 3.5 17h17a9.2 9.2 0 0 0-2.9-7.5zM8 14.4a1 1 0 1 1 0-2 1 1 0 0 1 0 2zm8 0a1 1 0 1 1 0-2 1 1 0 0 1 0 2z"/></svg>'
ICON_GITHUB = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 1.5a10.5 10.5 0 0 0-3.3 20.5c.5.1.7-.2.7-.5v-1.8c-2.9.6-3.5-1.4-3.5-1.4-.5-1.2-1.2-1.5-1.2-1.5-.9-.7.1-.6.1-.6 1 .1 1.6 1.1 1.6 1.1.9 1.6 2.5 1.1 3.1.9.1-.7.4-1.1.7-1.4-2.3-.3-4.8-1.2-4.8-5.2 0-1.1.4-2.1 1.1-2.8-.1-.3-.5-1.4.1-2.8 0 0 .9-.3 2.9 1.1a10 10 0 0 1 5.2 0c2-1.4 2.9-1.1 2.9-1.1.6 1.4.2 2.5.1 2.8.7.8 1.1 1.7 1.1 2.8 0 4-2.5 4.9-4.8 5.2.4.3.7 1 .7 2v2.9c0 .3.2.6.7.5A10.5 10.5 0 0 0 12 1.5z"/></svg>'


def header(current, here):
    def link(href, label, key, cls="", new_tab=False):
        cur = ' aria-current="page"' if key == current else ""
        c = f' class="{cls}"' if cls else ""
        nt = ' target="_blank" rel="noopener"' if new_tab else ""
        return f'<a href="{href}"{c}{cur}{nt}>{label}</a>'
    other = ("/en" + here) if LANG == "zh" else here
    switch = f'<a class="lang" href="{other}" hreflang="{"en" if LANG == "zh" else "zh-CN"}" lang="{"en" if LANG == "zh" else "zh-CN"}">{"EN" if LANG == "zh" else "中文"}</a>'
    return f'''<header class="site-header">
  <div class="wrap">
    <a class="logo" href="{u("/")}"><img src="/assets/logo-white-144.png" alt="" width="30" height="25">Luckgram</a>
    <nav class="nav" aria-label="{t("Main", "主导航")}">
      {link(u("/features/"), t("Features", "功能"), "features")}
      {link("https://web.luckgram.cc/", t("Web", "网页版"), "web", new_tab=True)}
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
        <li><a href="https://web.luckgram.cc/" target="_blank" rel="noopener">{t("Web version", "网页版")}</a></li>
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
// Download buttons: /download/latest.json is written by the app CI after each master release
// (luckgram-specs#100). Buttons keep their build-time link if the file cannot be loaded.
(function () {{
  var zh = document.documentElement.lang.indexOf("zh") === 0;
  function mb(n) {{ return (n / 1048576).toFixed(1) + " MB"; }}
  function day(s) {{ return (s || "").slice(0, 10); }}
  function meta(el, r, f) {{
    if (!el || !f) return;
    var line = (zh ? "版本 " : "Version ") + r.version + (zh ? " · 构建号 " : " · build ") + r.build +
      " · " + day(r.published_at) + " · " + mb(f.size);
    el.textContent = "";
    var p = document.createElement("p"); p.textContent = line; el.appendChild(p);
    var d = document.createElement("details"), s = document.createElement("summary"), c = document.createElement("code");
    s.textContent = "SHA-256"; c.textContent = f.sha256; d.appendChild(s); d.appendChild(c); el.appendChild(d);
    el.hidden = false;
  }}
  // Mirror (specs#160): on lg-www.cat158.com, or when dl.luckgram.cc can't be reached from this
  // network, the buttons use lg-dl.cat158.com, which serves the same files.
  var DL = "https://dl.luckgram.cc/", ALT = "https://lg-dl.cat158.com/";
  var dlBase = location.hostname === "lg-www.cat158.com" ? ALT : DL;
  function dlURL(u) {{ return u.indexOf(DL) === 0 ? dlBase + u.slice(DL.length) : u; }}
  function useAlt() {{
    dlBase = ALT;
    document.querySelectorAll("[data-dl]").forEach(function (a) {{ a.href = dlURL(a.href); }});
  }}
  if (window.fetch && dlBase === DL && document.querySelector("[data-dl]")) {{
    var probe = setTimeout(useAlt, 6000);
    fetch(DL + "ping", {{method: "HEAD", mode: "no-cors", cache: "no-store"}})
      .then(function () {{ clearTimeout(probe); }}, function () {{ clearTimeout(probe); useAlt(); }});
  }}
  function set(key, r, f) {{
    if (!f || f.url.indexOf(DL) !== 0) return false;
    document.querySelectorAll('[data-dl="' + key + '"]').forEach(function (a) {{ a.href = dlURL(f.url); }});
    meta(document.querySelector('[data-dl-meta="' + key + '"]'), r, f);
    return true;
  }}
  // Signed iOS install: the service's install domain changes, so ask for the current one on click.
  document.querySelectorAll("[data-ios-install]").forEach(function (a) {{
    a.addEventListener("click", function (e) {{
      if (!window.fetch || e.metaKey || e.ctrlKey) return;
      e.preventDefault();
      var done = false, go = function (url) {{ if (!done) {{ done = true; location.href = url; }} }};
      setTimeout(function () {{ go(a.href); }}, 4000);
      fetch("{IOS_INSTALL_API}").then(function (r) {{ return r.json(); }}).then(function (j) {{
        go(j && String(j.link_jump || "").indexOf("https://") === 0 ? j.link_jump : a.href);
      }}).catch(function () {{ go(a.href); }});
    }});
  }});
  if (!window.fetch || !document.querySelector("[data-dl]")) return;
  fetch("/download/latest.json", {{cache: "no-cache"}}).then(function (r) {{ return r.ok ? r.json() : null; }}).then(function (j) {{
    if (!j) return;
    if (j.ios) set("ios", j.ios, j.ios);
    if (j.android) {{
      set("android", j.android, j.android.arm64);
      if (set("android-x86_64", j.android, j.android.x86_64)) {{
        var o = document.querySelector('[data-dl-other="android"]'); if (o) o.hidden = false;
      }}
    }}
    if (j.windows) {{
      set("windows", j.windows, j.windows.setup);
      set("windows-portable", j.windows, j.windows.portable);
    }}
  }}).catch(function () {{}});
}})();

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
        (t("Several accounts", "多个账号"), t("Switch between Telegram accounts in one app: 10 for free, unlimited with Luckgram Pro (Telegram itself allows 3).",
                                          "在一个应用里切换多个 Telegram 账号：免费 10 个，开通 Luckgram Pro 后不限数量（Telegram 官方是 3 个）。")),
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
         t("Yes. Every feature not marked Pro is free. Luckgram Pro is an optional membership with more AI, unlimited accounts, cloud backup and no sponsored messages. Telegram Premium and Telegram Stars are Telegram's own services and are sold and managed by Telegram.",
           "免费。没有标注“Pro 专享”的功能都免费使用。Luckgram Pro 是可选的会员，提供更多 AI、不限数量的账号、云备份和去除赞助消息。Telegram Premium 和 Telegram Stars 是 Telegram 自己的服务，由 Telegram 销售和管理。")),
        (t("Why isn't Luckgram on the App Store or Google Play?", "为什么 App Store 和 Google Play 上找不到 Luckgram？"),
         t("Luckgram is currently distributed through GitHub Releases. The Download page always links to the latest build.",
           "Luckgram 目前通过 GitHub Releases 发布。下载页上的链接始终指向最新版本。")),
        (t("How do I install Luckgram on an iPhone?", "怎么在 iPhone 上安装 Luckgram？"),
         t("The iOS build is an unsigned IPA. Sign it with a tool such as Sideloadly or AltStore, or with your own Apple developer certificate, then install it. The install guide walks through each step.",
           "iOS 版是未签名的 IPA。先用 Sideloadly、AltStore 等工具或你自己的 Apple 开发者证书签名，再安装。安装指南里有每一步的说明。")),
        (t("Which Android phones are supported?", "支持哪些 Android 手机？"),
         t("Android 6.0 or later on a 64-bit ARM phone (arm64-v8a), which covers almost every phone sold in recent years. Allow installs from your browser or file manager when asked.",
           "Android 6.0 及以上、64 位 ARM 处理器（arm64-v8a）的手机，近几年卖的手机基本都支持。安装时如有提示，请允许浏览器或文件管理器安装应用。")),
        (t("Which extra features can I use?", "哪些新增功能现在能用？"),
         t(f'The <a href="{u("/features/")}">features page</a> lists every feature Luckgram adds. Those marked Available work in the current version, and those marked Pro need Luckgram Pro.',
           f'<a href="{u("/features/")}">功能页</a>列出了 Luckgram 新增的全部功能。标注“已上线”的在当前版本里就能用，标注“Pro 专享”的需要开通 Luckgram Pro。')),
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
    return f'''<a class="{cls}" href="{IOS_LATEST}" data-dl="ios">{ICON_APPLE}<span><small>{t("iPhone and iPad · sign it yourself", "iPhone 和 iPad · 需自行签名")}</small>{t("Download IPA", "下载 IPA")}</span></a>
        <a class="btn platform" href="{IOS_INSTALL}" data-ios-install rel="noopener">{ICON_APPLE}<span><small>{t("iPhone and iPad · no computer needed", "iPhone 和 iPad · 无需电脑")}</small>{t("Install on iPhone", "直接安装 iOS 版")}</span></a>
        <a class="btn platform" href="{ANDROID_LATEST}" data-dl="android">{ICON_ANDROID}<span><small>{t("Android 6.0 or later", "Android 6.0 及以上")}</small>{t("Download APK", "下载 APK")}</span></a>
        <a class="btn platform" href="{WIN_LATEST}" data-dl="windows">{ICON_WINDOWS}<span><small>{t("Windows 10/11 · beta", "Windows 10/11 · 测试版")}</small>{t("Download for Windows", "下载 Windows 版")}</span></a>'''


def feature_by_slug():
    return {slug: (short, title, status, body) for _, items in feature_groups() for slug, short, title, status, body, _, _ in items}


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
      <p class="lede">{t("Luckgram is an independent, open-source Telegram client for iOS, Android and Windows. Sign in with your Telegram account and your chats, channels and calls are all there, plus more accounts, hidden chats, free translation and AI tools.",
                         "Luckgram 是独立、开源的 iOS、Android 和 Windows Telegram 客户端。用你的 Telegram 账号登录，聊天、频道和通话都在，还有多账号、隐藏聊天、免费翻译和 AI 等功能。")}</p>
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
    <div class="head"><h2>{t("Everything you use in Telegram", "你在 Telegram 里用的，这里都有")}</h2>
      <p>{t("Luckgram connects to the Telegram network, so the features you rely on work from the first sign-in.", "Luckgram 连接的是 Telegram 网络，你常用的功能从第一次登录起就能用。")}</p></div>
    <div class="today">
{today}
    </div>
  </div>
</section>

<section class="block">
  <div class="wrap">
    <div class="head"><h2>{t("What Luckgram adds", "Luckgram 的新功能")}</h2>
      <p>{t("Each feature is marked with where it stands: available to everyone, or part of Luckgram Pro.", "每个功能都标明了状态：所有人可用，或属于 Luckgram Pro。")}</p></div>
    <div class="wall">
{"".join(cells)}
    </div>
    <div class="wall-foot"><span>{t(f"{n} features in all.", f"共 {n} 个功能。")}</span><a class="btn" href="{u("/features/")}">{t("See all features", "查看全部功能")}</a></div>
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
    <p>{t("Free for iPhone, iPad, Android and Windows. Sign in with the account you already have.", "iPhone、iPad、Android 和 Windows 均可免费使用，用你现有的账号登录。")}</p>
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
    page("/", t("Luckgram – an independent Telegram client for iOS, Android and Windows", "Luckgram – 独立的 iOS、Android 和 Windows Telegram 客户端"),
         t("Luckgram is an independent, open-source Telegram client for iOS, Android and Windows. Sign in with your Telegram account and keep everything you use today.",
           "Luckgram 是独立、开源的 iOS、Android 和 Windows Telegram 客户端。用你的 Telegram 账号登录，现在用的一切都还在。"),
         body)


def download():
    body = f'''<section class="page-head">
  <div class="wrap">
    <h1>{t("Get Luckgram", "下载 Luckgram")}</h1>
    <p>{t("The buttons download the newest build directly. Links update automatically after each release.",
          "点按钮直接下载最新版本。每次发布后链接自动更新。")}</p>
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
      <div class="btns"><a class="btn primary" href="{ANDROID_LATEST}" data-dl="android">{t("Download APK", "下载 APK")}</a></div>
      <div class="dl-meta" data-dl-meta="android" hidden></div>
      <details class="dl-more" data-dl-other="android" hidden>
        <summary>{t("Other builds", "其他版本")}</summary>
        <p>{t("x86_64 APK for Android emulators on x86 computers (Windows, Intel Mac). Not for phones.",
              "x86_64 APK，给 x86 电脑（Windows、Intel Mac）上的 Android 模拟器用，手机请下载上面的版本。")}</p>
        <p><a class="btn" href="{ANDROID_X86_LATEST}" data-dl="android-x86_64">{t("Download x86_64 APK", "下载 x86_64 APK")}</a></p>
        <div class="dl-meta" data-dl-meta="android-x86_64"></div>
      </details>
    </div>
    <div class="dl-card">
      <svg class="os" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">{ICON_APPLE[ICON_APPLE.index("<path"):ICON_APPLE.index("</svg>")]}</svg>
      <h2>{t("iPhone and iPad", "iPhone 和 iPad")}</h2>
      <ul>
        <li>{t("Unsigned IPA", "未签名的 IPA")}</li>
        <li>{t("Sign it with Sideloadly, AltStore or your own certificate before installing", "安装前先用 Sideloadly、AltStore 或你自己的证书签名")}</li>
        <li>{t("iOS 15 or later", "iOS 15 及以上")}</li>
      </ul>
      <div class="btns"><a class="btn primary" href="{IOS_LATEST}" data-dl="ios">{t("Download IPA", "下载 IPA")}</a><a class="btn" href="{IOS_INSTALL}" data-ios-install rel="noopener">{t("Install on iPhone", "直接安装")}</a><a class="btn" href="{wiki("/getting-started/install.html")}">{t("Install guide", "安装指南")}</a></div>
      <p class="dl-sign">{t("The IPA must be signed by you before it can be installed. “Install on iPhone” is a signed build: open this page in Safari on the device and follow the steps.", "IPA 需要自行签名后才能安装。「直接安装」是已签名的版本：在 iPhone 的 Safari 里打开本页，按提示操作即可。")}</p>
      <div class="dl-meta" data-dl-meta="ios" hidden></div>
    </div>
    <div class="dl-card">
      <svg class="os" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">{ICON_WINDOWS[ICON_WINDOWS.index("<path"):ICON_WINDOWS.index("</svg>")]}</svg>
      <h2>{t("Windows (beta)", "Windows（测试版）")}</h2>
      <ul>
        <li>{t("Windows 10 or 11, 64-bit", "Windows 10 或 11，64 位")}</li>
        <li>{t("Installs for your user only, no administrator rights needed", "只装给当前用户，不需要管理员权限")}</li>
        <li>{t("Not code-signed yet: if SmartScreen warns, click More info → Run anyway", "暂未做代码签名：如果 SmartScreen 拦截，点「更多信息 → 仍要运行」")}</li>
      </ul>
      <div class="btns"><a class="btn primary" href="{WIN_LATEST}" data-dl="windows">{t("Download installer", "下载安装包")}</a></div>
      <div class="dl-meta" data-dl-meta="windows" hidden></div>
      <details class="dl-more">
        <summary>{t("Other builds", "其他版本")}</summary>
        <p>{t("Portable ZIP: unzip and run Luckgram.exe, data stays in that folder.", "便携版 ZIP：解压后直接运行 Luckgram.exe，数据保存在同一个文件夹里。")}</p>
        <p><a class="btn" href="{WIN_PORTABLE_LATEST}" data-dl="windows-portable">{t("Download portable ZIP", "下载便携版 ZIP")}</a></p>
        <div class="dl-meta" data-dl-meta="windows-portable"></div>
      </details>
    </div>
  </div>
  <p class="note">{t("If you previously installed a test build of Luckgram on Android, uninstall it first: builds signed with a different key cannot update each other. Only download Luckgram from this page or the GitHub repositories it links to.",
                     "如果你之前在 Android 上装过 Luckgram 的测试版，请先卸载：签名密钥不同的版本不能相互覆盖升级。请只从本页或本页链接的 GitHub 仓库下载 Luckgram。")}</p>
</div>'''
    page("/download/", t("Download Luckgram for Android, iOS and Windows", "下载 Luckgram（Android、iOS 和 Windows）"),
         t("Download the latest Luckgram builds for Android (APK), iOS (IPA) and Windows.", "下载最新版 Luckgram：Android（APK）、iOS（IPA）和 Windows。"), body, "download")



def privacy():
    body = f'''<article class="prose">
<h1>{t("Privacy Policy", "隐私政策")}</h1>
<p class="meta">{t("Last updated", "最后更新：")}{" " if LANG == "en" else ""}{t(*PRIVACY_UPDATED)}</p>

<p>{t("This policy explains what happens to your information when you use the Luckgram apps for iOS and Android and the luckgram.cc websites. Luckgram is an independent app built from the open-source Telegram apps.",
      "本政策说明你使用 Luckgram iOS 和 Android 应用以及 luckgram.cc 网站时，你的信息会如何处理。Luckgram 是基于开源 Telegram 应用开发的独立应用。")}</p>

<h2>{t("Your Telegram data", "你的 Telegram 数据")}</h2>
<p>{t('Luckgram is a client for the Telegram network. When you sign in, send messages, make calls or sync contacts, the app exchanges that data directly with Telegram\'s servers. That data is processed by Telegram under the <a href="https://telegram.org/privacy">Telegram Privacy Policy</a>, not by Luckgram.',
      'Luckgram 是 Telegram 网络的客户端。你登录、发消息、打电话或同步联系人时，应用直接与 Telegram 的服务器交换这些数据。这些数据由 Telegram 依据 <a href="https://telegram.org/privacy">Telegram 隐私政策</a>处理，而不是由 Luckgram 处理。')}</p>
<p>{t("Luckgram does not run its own servers for your messages, calls, contacts or media, and does not receive copies of them. The exceptions are the Luckgram features described in the next section, which only send data when you use them.",
      "Luckgram 没有为你的消息、通话、联系人或媒体设立自己的服务器，也不会收到它们的副本。例外是下一节列出的 Luckgram 功能，只有在你使用这些功能时才会发送数据。")}</p>

<h2>{t("Luckgram features that use our servers", "使用 Luckgram 服务器的功能")}</h2>
<p>{t("Some Luckgram features run on servers operated by Luckgram on Amazon Web Services in Singapore. Each feature can be turned off in Settings → Luckgram Features.",
      "部分 Luckgram 功能运行在 Luckgram 运营的服务器上，服务器位于新加坡的 Amazon Web Services。每个功能都可以在「设置 → Luckgram 功能」里关闭。")}</p>
<ul>
<li>{t("<b>Device registration.</b> On first use the app registers an anonymous device token together with the platform, app version and language. We store only a hash of the token. A device that has not connected for 180 days is deleted.",
      "<b>设备登记。</b>首次使用时，应用会登记一个匿名设备令牌，以及系统平台、应用版本和语言。我们只保存令牌的哈希值。180 天没有连接的设备会被删除。")}</li>
<li>{t("<b>Account link.</b> Features that need an account (AI quotas, People Nearby, Square, Luckgram Pro) link your device to your Telegram user ID through the Luckgram bot. We store only the numeric user ID, not your phone number. You can unlink in Settings → Luckgram Features → Account.",
      "<b>账号关联。</b>需要账号的功能（AI 额度、附近的人、广场、Luckgram Pro）会通过 Luckgram 机器人，把你的设备和 Telegram 用户 ID 关联起来。我们只保存数字用户 ID，不保存手机号。你可以在「设置 → Luckgram 功能 → 账号」里解除关联。")}</li>
<li>{t("<b>AI features</b> (assistant, summaries, writing help, reply suggestions, images, posts, voice-to-text and call transcripts). The text, audio or prompt you choose to process is sent through our server to OpenAI to produce the result, and is then returned to you. We do not store or log this content; we keep only usage records (feature, amount, time) for 90 days to enforce quotas. Generated images are kept for 24 hours so you can download them. OpenAI processes the content under its own terms. AI chat history is stored only on your device.",
      "<b>AI 功能</b>（助手、总结、写作、回复建议、图片、帖子、语音转文字和通话文字稿）。你选择处理的文字、音频或提示词会经由我们的服务器发给 OpenAI 生成结果，再返回给你。我们不保存、也不记录这些内容；只为执行额度保留用量记录（功能、用量、时间）90 天。生成的图片保留 24 小时，供你下载。OpenAI 依据其自身条款处理这些内容。AI 对话历史只保存在你的设备上。")}</li>
<li>{t("<b>People Nearby</b> (only when you turn on “Visible nearby”). The app rounds your location to a grid of about 1 km on the device before sending it; your exact position never leaves the device. Your card (display name, bio, optional photo and public username) and that rounded location are deleted automatically after 24 hours, or immediately when you turn visibility off, sign out or unlink. Other users see only a distance range, never your coordinates.",
      "<b>附近的人</b>（仅在你打开「在附近可见」时）。应用会先在设备上把你的位置粗化到约 1 公里的网格再发送，精确位置不会离开设备。你的名片（显示名、简介、可选头像和公开用户名）和粗化后的位置在 24 小时后自动删除；你关闭可见、退出登录或解除关联时立即删除。其他用户只能看到距离范围，看不到你的坐标。")}</li>
<li>{t("<b>Square.</b> Posts, comments and likes are public to all Luckgram users. Before upload the app resizes photos and removes their metadata, including GPS; videos are re-encoded without metadata. You can delete any post or comment, or remove all your Square data at once in Settings → Luckgram Features → Account. Media from deleted posts is removed within 24 hours, and all copies of deleted data within 30 days. Reported content may be reviewed and hidden.",
      "<b>广场。</b>帖子、评论和点赞对所有 Luckgram 用户公开。上传前，应用会压缩图片并去掉包括 GPS 在内的元数据；视频会重新编码并去掉元数据。你可以删除任何一条自己的帖子或评论，也可以在「设置 → Luckgram 功能 → 账号」里一键删除全部广场数据。已删除帖子的图片和视频在 24 小时内删除，被删除数据的所有副本在 30 天内清除。被举报的内容可能会被审核和隐藏。")}</li>
<li>{t("<b>Square recommendations.</b> To recommend Square posts you may like, Luckgram records how you browse and interact in Square: which posts you saw, how long you stayed, and when you open, like, comment on, share, report or mark a post “Not interested”. These records are linked only to an opaque device or user identifier, contain no post text and none of your chats, are used only to recommend and rank Square posts (including improving those recommendations), are not used anywhere else and are never combined with data from other apps or websites (no cross-app tracking). They are deleted automatically after 90 days.",
      "<b>广场推荐。</b>为了在广场里给你推荐可能感兴趣的帖子，Luckgram 会记录你在广场里的浏览和互动：看到了哪些帖子、停留多久、点开、点赞、评论、分享、举报和「不感兴趣」。这些记录只和一个不透明的设备或用户标识关联，不包含帖子文字或你的聊天内容，只用于广场的推荐和排序（包括改进推荐效果），不会用于广场以外的地方，也不会和其他 App 或网站的数据关联（不做跨 App 追踪），90 天后自动删除。")}</li>
<li>{t("<b>Luckgram Pro.</b> Payments are made with Telegram Stars and processed by Telegram. We store your Telegram user ID and subscription period, not payment details.",
      "<b>Luckgram Pro。</b>使用 Telegram Stars 付款，由 Telegram 处理。我们只保存你的 Telegram 用户 ID 和会员有效期，不保存付款信息。")}</li>
<li>{t("<b>Settings, announcements and updates.</b> The app downloads feature settings, in-app announcements and version information from our server. These requests carry only the device token and app version.",
      "<b>配置、公告和更新。</b>应用会从我们的服务器下载功能配置、应用内公告和版本信息。这些请求只带设备令牌和应用版本。")}</li>
</ul>
<p>{t("Server logs record technical details such as the request type, result and timing, never message, post or AI content, and are kept for 30 days. We do not sell your data or use it for advertising.",
      "服务器日志只记录请求类型、结果和耗时等技术信息，不记录消息、帖子或 AI 内容，保留 30 天。我们不出售你的数据，也不将其用于广告。")}</p>

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
<p>{t("App builds are downloaded from dl.luckgram.cc. The files are stored with Amazon Web Services and delivered through Cloudflare, which may process technical data such as your IP address to deliver them. We don't keep download logs of our own.",
      "应用安装包从 dl.luckgram.cc 下载，文件存放在 Amazon Web Services，经由 Cloudflare 分发。分发过程中 Cloudflare 可能会处理 IP 地址等技术数据。我们自己不记录下载日志。")}</p>

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




# Feature page: (slug, short name, title, status, body, help path); text pairs are (English, Chinese)
FEATURES_JSON = os.path.join(ROOT, "data", "features.json")
STATUS_CLASS = {"live": "ok", "telegram": "ok", "pro": "pro", "wip": "wip"}


def load_features():
    """data/features.json is the single feature list shared with wiki.luckgram.cc (issue specs#103)."""
    with open(FEATURES_JSON, encoding="utf-8") as f:
        return json.load(f)


def feature_groups():
    """[((group en, zh), [(slug, short, title, (css class, label), body, wiki path, has video)])] from features.json."""
    data = load_features()
    pair = lambda d: (d["en"], d["zh"])
    out = []
    for g in data["groups"]:
        items = [(f["id"], pair(f["name"]), pair(f["title"]), (STATUS_CLASS[f["status"]], pair(data["statuses"][f["status"]])),
                  pair(f["description"]), f["wiki"], f["video"])
                 for f in data["features"] if f["group"] == g["id"]]
        out.append((pair(g["name"]), items))
    return out


def features():
    toc, sections = [], []
    for group, items in feature_groups():
        toc.append(f'<li class="toc-group">{t(*group)}</li>')
        for slug, short, title, (key, label), body, help_path, has_video in items:
            title = t(*title)
            toc.append(f'<li><a href="#{slug}">{t(*short)}</a></li>')
            demo = video(slug, title) if has_video else ""
            sections.append(f'''<section class="feat{"" if has_video else " novid"}" id="{slug}">
  {demo}
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
    <p>{t("Everything you use in Telegram already works in Luckgram. Below are the extras we add, each marked with its status: Available for everyone, or Pro for Luckgram Pro members. Each one links to its Help Center page.",
          "你在 Telegram 里用的一切，Luckgram 里都能用。下面是我们额外增加的功能，每项都标明了状态：“已上线”所有人可用，“Pro 专享”需要 Luckgram Pro。每项都能点进帮助中心的对应页面。")}</p>
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
    page("/features/", t("Luckgram features", "Luckgram 功能"),
         t("Every feature Luckgram adds to Telegram, with its status: available for everyone or part of Luckgram Pro.",
           "Luckgram 在 Telegram 之上增加的全部功能及状态：所有人可用，或属于 Luckgram Pro。"),
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
