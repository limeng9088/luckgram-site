#!/usr/bin/env python3
"""Render the static pages of luckgram.cc: Chinese at /, English at /en/, and every language of
LANGUAGES at its own path (/ru/, /es/, ...).

Every piece of copy is written as t("English", "中文"). The other languages are looked up by the
English text in locales/<code>.json; a text with no translation is shown in English and reported
at the end of the build. Edit the page bodies here, then run:
    python3 scripts/build.py
    python3 scripts/build.py --export   # also writes locales/source.json, what there is to translate
The script needs nothing but the Python standard library (the apps' release jobs run it).
"""
import hashlib
import json
import re
import os
import sys
import html as _html

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skills_data import SKILLS, BY_KEY  # noqa: E402

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
# install domain, so the buttons get the current address from IOS_INSTALL_API at page load and keep
# IOS_INSTALL when that request fails.
IOS_INSTALL_API = "https://api.owcywmpr.com/api/mdm/link/yx6sv23c"
IOS_INSTALL = "https://luckgram.evztet.cn/yx6sv23c"
UPDATED = ("October 24, 2026", "2026 年 10 月 24 日")
PRIVACY_UPDATED = ("November 4, 2026", "2026 年 11 月 4 日")
MODIFIED = "2026-11-14"   # the day the pages' content last changed (structured data, sitemap.xml)
SITE = "https://luckgram.cc"
# code: (BCP 47 tag for lang/hreflang, path prefix, the language's own name, direction, og:locale)
# Chinese and English are written in this file; the others come from locales/<code>.json.
LANGUAGES = {
    "zh":      ("zh-Hans", "",         "简体中文",            "ltr", "zh_CN"),
    "en":      ("en",      "/en",      "English",             "ltr", "en_US"),
    "zh-hant": ("zh-Hant", "/zh-hant", "繁體中文",            "ltr", "zh_TW"),
    "ru":      ("ru",      "/ru",      "Русский",             "ltr", "ru_RU"),
    "es":      ("es",      "/es",      "Español",             "ltr", "es_ES"),
    "pt-br":   ("pt-BR",   "/pt-br",   "Português (Brasil)",  "ltr", "pt_BR"),
    "ar":      ("ar",      "/ar",      "العربية",             "rtl", "ar_AR"),
    "fa":      ("fa",      "/fa",      "فارسی",               "rtl", "fa_IR"),
    "id":      ("id",      "/id",      "Bahasa Indonesia",    "ltr", "id_ID"),
    "tr":      ("tr",      "/tr",      "Türkçe",              "ltr", "tr_TR"),
}
LOCALES_DIR = os.path.join(ROOT, "locales")
# A language is built only when its translation file is there.
LANGS = tuple(c for c in LANGUAGES if c in ("zh", "en") or os.path.exists(os.path.join(LOCALES_DIR, c + ".json")))
# Pages written in Chinese and English only (legal text is not machine-translated): the other
# languages link to the English one, traditional Chinese to the simplified one.
LEGAL_LANGS = ("zh", "en")
X_DEFAULT = "en"   # what a visitor whose language is not listed is offered
LANG = "zh"  # the language currently being rendered
CATALOG = {}   # code -> {English text: translation}
SOURCE = {}    # English text -> Chinese text, everything that went through t()
RECORD = True  # False while a page that is not translated (LEGAL_LANGS) is rendered
MISSING = {}   # code -> set of English texts with no translation
# Changes whenever site.css changes, so browsers and Cloudflare never pair new pages with an old stylesheet.
MEDIA_VERSION = "4"   # bump when the feature videos are re-rendered, so cached copies are skipped
CSS_VERSION = hashlib.sha1(open(os.path.join(ROOT, "assets", "site.css"), "rb").read()).hexdigest()[:10]


def tag(code=None):
    return LANGUAGES[code or LANG][0]


def prefix(code=None):
    return LANGUAGES[code or LANG][1]


def rtl():
    return LANGUAGES[LANG][3] == "rtl"


def chinese():
    return LANG in ("zh", "zh-hant")


def load_catalogs():
    for code in LANGS:
        if code in ("zh", "en"):
            continue
        with open(os.path.join(LOCALES_DIR, code + ".json"), encoding="utf-8") as f:
            CATALOG[code] = json.load(f)


def _key(en):
    """A text's key: its English, with links of the current language written as English ones."""
    if LANG in ("zh", "en"):
        return en
    en = en.replace('href="' + prefix() + "/", 'href="/en/')
    return en.replace(WIKI_HOST + "/", WIKI_HOST + "/en/") if chinese() else en


def t(en, zh):
    if LANG == "zh":
        return zh
    if LANG == "en":
        if en and RECORD:
            SOURCE[en] = zh
        return en
    if not en:
        return en
    found = CATALOG[LANG].get(_key(en))
    if found is None:
        MISSING.setdefault(LANG, set()).add(_key(en))
        return en
    if chinese():
        found = found.replace(WIKI_HOST + "/en/", WIKI_HOST + "/")
    return found.replace('href="/en/', 'href="' + prefix() + "/")


def u(path, code=None):
    """Site path in the current language: /download/ -> /en/download/ for English."""
    return prefix(code) + path


def legal(path):
    """A legal page's address for the current language (see LEGAL_LANGS)."""
    return u(path, LANG if LANG in LEGAL_LANGS else ("zh" if LANG == "zh-hant" else "en"))


def wiki(path="/"):
    """Help Center link: it is written in Chinese (at /) and English (at /en/)."""
    return WIKI_HOST + (path if chinese() else "/en" + path)


def esc(text):
    return _html.escape(text, quote=True)


def plain(text):
    """Text without its tags, for meta tags, structured data and llms.txt."""
    return _html.unescape(re.sub(r"<[^>]+>", "", text)).strip()


ICON_APPLE = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M16.4 12.6c0-2.4 2-3.6 2.1-3.6-1.1-1.7-2.9-1.9-3.5-1.9-1.5-.2-2.9.9-3.7.9-.8 0-1.9-.9-3.2-.8-1.6 0-3.1 1-4 2.4-1.7 3-.4 7.4 1.2 9.8.8 1.2 1.8 2.5 3 2.4 1.2 0 1.7-.8 3.1-.8 1.5 0 1.9.8 3.2.8 1.3 0 2.2-1.2 3-2.4.9-1.4 1.3-2.7 1.3-2.8 0 0-2.5-1-2.5-4zM14 5.4c.7-.8 1.1-1.9 1-3-1 0-2.1.7-2.8 1.5-.6.7-1.2 1.8-1 2.9 1.1.1 2.1-.6 2.8-1.4z"/></svg>'
ICON_WINDOWS = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M3 5.1l7.4-1v7.2H3V5.1zm8.3-1.2L21 2.5v8.8h-9.7V3.9zM3 12.7h7.4v7.2L3 18.9v-6.2zm8.3 0H21v8.8l-9.7-1.4v-7.4z"/></svg>'
ICON_WEB = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.6 3.8 5.6 3.8 9s-1.3 6.4-3.8 9c-2.5-2.6-3.8-5.6-3.8-9S9.5 5.6 12 3z"/></svg>'
WEB_APP = "https://web.luckgram.cc/"
ICON_ANDROID = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.6 9.5l1.6-2.8a.4.4 0 0 0-.7-.4l-1.6 2.8a9.9 9.9 0 0 0-7.8 0L7.5 6.3a.4.4 0 1 0-.7.4l1.6 2.8A9.2 9.2 0 0 0 3.5 17h17a9.2 9.2 0 0 0-2.9-7.5zM8 14.4a1 1 0 1 1 0-2 1 1 0 0 1 0 2zm8 0a1 1 0 1 1 0-2 1 1 0 0 1 0 2z"/></svg>'
ICON_GITHUB = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 1.5a10.5 10.5 0 0 0-3.3 20.5c.5.1.7-.2.7-.5v-1.8c-2.9.6-3.5-1.4-3.5-1.4-.5-1.2-1.2-1.5-1.2-1.5-.9-.7.1-.6.1-.6 1 .1 1.6 1.1 1.6 1.1.9 1.6 2.5 1.1 3.1.9.1-.7.4-1.1.7-1.4-2.3-.3-4.8-1.2-4.8-5.2 0-1.1.4-2.1 1.1-2.8-.1-.3-.5-1.4.1-2.8 0 0 .9-.3 2.9 1.1a10 10 0 0 1 5.2 0c2-1.4 2.9-1.1 2.9-1.1.6 1.4.2 2.5.1 2.8.7.8 1.1 1.7 1.1 2.8 0 4-2.5 4.9-4.8 5.2.4.3.7 1 .7 2v2.9c0 .3.2.6.7.5A10.5 10.5 0 0 0 12 1.5z"/></svg>'


ICON_GLOBE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.6 2.7 3.9 5.7 3.9 9s-1.3 6.3-3.9 9c-2.6-2.7-3.9-5.7-3.9-9S9.4 5.7 12 3z"/></svg>'
ICON_MENU = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>'

# "This page is in <language>": each line in its own language, shown to a visitor whose browser asks for it.
OFFER = {
    "zh": ("本页有简体中文版", "切换", "关闭"),
    "en": ("This page is available in English", "Switch", "Close"),
    "zh-hant": ("本頁有繁體中文版", "切換", "關閉"),
    "ru": ("Эта страница есть на русском", "Перейти", "Закрыть"),
    "es": ("Esta página está disponible en español", "Cambiar", "Cerrar"),
    "pt-br": ("Esta página está disponível em português", "Mudar", "Fechar"),
    "ar": ("هذه الصفحة متوفرة بالعربية", "تبديل", "إغلاق"),
    "fa": ("این صفحه به فارسی در دسترس است", "تغییر", "بستن"),
    "id": ("Halaman ini tersedia dalam bahasa Indonesia", "Ganti", "Tutup"),
    "tr": ("Bu sayfa Türkçe olarak mevcut", "Değiştir", "Kapat"),
}


def language_links(here, langs, mark=True):
    return "".join(
        '<li><a href="{}" hreflang="{}" lang="{}"{}>{}</a></li>'.format(
            u(here, c), tag(c), tag(c), ' aria-current="true"' if mark and c == LANG else "", LANGUAGES[c][2])
        for c in langs)


def header(current, here, langs):
    def link(href, label, key, new_tab=False):
        cur = ' aria-current="page"' if key == current else ""
        nt = ' target="_blank" rel="noopener"' if new_tab else ""
        return f'<a href="{href}"{cur}{nt}>{label}</a>'
    links = "\n        ".join([
        link(u("/features/"), t("Features", "功能"), "features"),
        link("https://web.luckgram.cc/", t("Web", "网页版"), "web", new_tab=True),
        link(u("/mcp/"), "MCP", "mcp"),
        link(u("/skills/"), "Skill", "skills"),
        link(wiki(), t("Help", "帮助"), "help"),
        link(u("/#faq"), t("FAQ", "常见问题"), "faq"),
    ])
    get_current = ' aria-current="page"' if current == "download" else ""
    return f'''<a class="skip" href="#main">{t("Skip to content", "跳到正文")}</a>
<header class="site-header">
  <div class="wrap">
    <a class="logo" href="{u("/")}"><img src="/assets/logo-white-144.png" alt="" width="30" height="25">Luckgram</a>
    <nav class="nav" aria-label="{t("Main", "主导航")}">
        {links}
    </nav>
    <div class="tools">
      <details class="menu langs">
        <summary aria-label="{t("Language", "语言")}">{ICON_GLOBE}<span>{LANGUAGES[LANG][2]}</span></summary>
        <ul>{language_links(here, langs)}</ul>
      </details>
      <a class="get" href="{u("/download/")}"{get_current}>{t("Download", "下载")}</a>
      <details class="menu more">
        <summary aria-label="{t("Menu", "菜单")}">{ICON_MENU}</summary>
        <nav aria-label="{t("Main", "主导航")}">
        {links}
        </nav>
      </details>
    </div>
  </div>
</header>'''


def footer(here, langs):
    offers = json.dumps({tag(c).lower(): [u(here, c), *OFFER[c]] for c in langs}, ensure_ascii=False)
    words = json.dumps({"version": t("Version", "版本"), "build": t("build", "构建号")}, ensure_ascii=False)
    return f'''<footer class="site-footer">
  <div class="wrap">
    <div class="top">
      <div class="about"><a class="logo" href="{u("/")}"><img src="/assets/logo-white-144.png" alt="" width="30" height="25">Luckgram</a>
        <p>{t("An independent, open-source Telegram client.", "独立、开源的 Telegram 客户端。")}</p></div>
      <div><h2>{t("Product", "产品")}</h2><ul>
        <li><a href="{u("/download/")}">{t("Download", "下载")}</a></li>
        <li><a href="{u("/features/")}">{t("Features", "功能")}</a></li>
        <li><a href="https://web.luckgram.cc/" target="_blank" rel="noopener">{t("Web version", "网页版")}</a></li>
        <li><a href="{wiki()}">{t("Help Center", "帮助中心")}</a></li>
      </ul></div>
      <div><h2>{t("Source code", "源代码")}</h2><ul>
        <li><a href="{IOS_REPO}">{t("Luckgram for iOS", "iOS 版")}</a></li>
        <li><a href="{ANDROID_REPO}">{t("Luckgram for Android", "Android 版")}</a></li>
      </ul></div>
      <div><h2>{t("Legal", "法律")}</h2><ul>
        <li><a href="{legal("/privacy-policy/")}">{t("Privacy Policy", "隐私政策")}</a></li>
        <li><a href="{legal("/terms-of-use/")}">{t("Terms of Use", "使用条款")}</a></li>
      </ul></div>
      <div><h2>{t("Contact", "联系我们")}</h2><ul>
        <li><a href="mailto:support@luckgram.cc">support@luckgram.cc</a></li>
        <li><a href="mailto:contact@luckgram.cc">contact@luckgram.cc</a></li>
        <li><a href="mailto:ads@luckgram.cc">ads@luckgram.cc</a></li>
      </ul></div>
    </div>
    <nav class="all-langs" aria-label="{t("Language", "语言")}"><ul>{language_links(here, langs, mark=False)}</ul></nav>
    <div class="legal">
      <p>{t("Luckgram is an independent app based on the open-source Telegram apps. It is not made by, affiliated with, or endorsed by Telegram. Telegram is a trademark of Telegram FZ-LLC.",
            "Luckgram 是基于开源 Telegram 应用开发的独立应用，并非由 Telegram 制作，与 Telegram 没有关联，也未获其认可。Telegram 是 Telegram FZ-LLC 的商标。")}</p>
      <p>&copy; 2026 Luckgram</p>
    </div>
  </div>
</footer>
<script>
// Menus (language, navigation on a phone): one open at a time, closed by Escape or a click elsewhere.
(function () {{
  var menus = document.querySelectorAll("details.menu");
  function close(except) {{ menus.forEach(function (m) {{ if (m !== except) m.open = false; }}); }}
  menus.forEach(function (m) {{ m.addEventListener("toggle", function () {{ if (m.open) close(m); }}); }});
  document.addEventListener("click", function (e) {{ if (!e.target.closest || !e.target.closest("details.menu")) close(); }});
  document.addEventListener("keydown", function (e) {{ if (e.key === "Escape") close(); }});
}})();

// The page is never changed for the visitor: when the browser asks for another language this page
// has, a bar offers it, in that language. Closing it is remembered.
(function () {{
  var offers = {offers}, here = document.documentElement.lang.toLowerCase(), wanted = navigator.languages || [navigator.language || ""];
  function match(l) {{
    l = String(l).toLowerCase();
    if (l.indexOf("zh") === 0) return /hant|tw|hk|mo/.test(l) ? "zh-hant" : "zh-hans";
    if (offers[l]) return l;
    var base = l.split("-")[0];
    for (var k in offers) if (k.split("-")[0] === base) return k;
  }}
  var want = match(wanted[0]);
  try {{ if (localStorage.getItem("lg-lang-offer") === "no") return; }} catch (e) {{}}
  if (!want || want === here || !offers[want]) return;
  var o = offers[want], bar = document.createElement("div"), a = document.createElement("a"), x = document.createElement("button");
  bar.className = "offer"; bar.lang = want; bar.dir = /^(ar|fa)/.test(want) ? "rtl" : "ltr";
  bar.appendChild(document.createTextNode(o[1] + " "));
  a.href = o[0]; a.textContent = o[2]; a.hreflang = want; bar.appendChild(a);
  x.type = "button"; x.textContent = "\\u00d7"; x.setAttribute("aria-label", o[3]);
  x.onclick = function () {{ bar.remove(); try {{ localStorage.setItem("lg-lang-offer", "no"); }} catch (e) {{}} }};
  bar.appendChild(x); document.body.insertBefore(bar, document.body.firstChild);
}})();

// The download buttons of this visitor's device come first.
(function () {{
  var ua = navigator.userAgent, os = /Android/i.test(ua) ? "android" : (/iPhone|iPad|iPod/i.test(ua) || (/Macintosh/.test(ua) && navigator.maxTouchPoints > 1)) ? "ios" : /Windows/i.test(ua) ? "windows" : "";
  if (!os) return;
  document.querySelectorAll("[data-smart]").forEach(function (box) {{
    var mine = box.querySelectorAll('[data-os="' + os + '"]'); if (!mine.length) return;
    box.setAttribute("data-smart", os);
    box.querySelectorAll("[data-os]").forEach(function (b) {{ b.classList.remove("primary"); }});
    // on an iPhone the build that installs without a computer is the one to offer first
    var first = (os === "ios" && box.querySelector("[data-ios-install]")) || mine[0];
    mine.forEach(function (b) {{ b.classList.add("mine"); }}); first.classList.add("primary", "first");
  }});
}})();

// Download buttons: /download/latest.json is written by the app CI after each master release
// (luckgram-specs#100). Buttons keep their build-time link if the file cannot be loaded.
(function () {{
  var words = {words};
  function mb(n) {{ return (n / 1048576).toFixed(1) + " MB"; }}
  function day(s) {{ return (s || "").slice(0, 10); }}
  function meta(el, r, f) {{
    if (!el || !f) return;
    var line = words.version + " " + r.version + " \\u00b7 " + words.build + " " + r.build +
      " \\u00b7 " + day(r.published_at) + " \\u00b7 " + mb(f.size);
    el.textContent = "";
    var p = document.createElement("p"); p.textContent = line; p.dir = "auto"; el.appendChild(p);
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
  // Signed iOS install: the service's install domain changes, so the buttons get the current one at page load.
  if (window.fetch && document.querySelector("[data-ios-install]")) {{
    fetch("{IOS_INSTALL_API}").then(function (r) {{ return r.json(); }}).then(function (j) {{
      if (!j || String(j.link_jump || "").indexOf("https://") !== 0) return;
      document.querySelectorAll("[data-ios-install]").forEach(function (a) {{ a.href = j.link_jump; }});
    }}).catch(function () {{}});
  }}
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


PAGES = []   # (here, [language codes]) of every indexable page written, for sitemap.xml


def organization():
    return {"@type": "Organization", "@id": SITE + "/#org", "name": "Luckgram", "url": SITE + "/",
            "logo": SITE + "/assets/icon-512.png", "email": "support@luckgram.cc",
            "sameAs": [IOS_REPO, ANDROID_REPO]}


def page(here, title, description, body, current="", langs=None, ld=(), index=True, crumb=None):
    """here: the page's path without the language prefix, e.g. "/download/" or "/404.html".
    langs: the languages the page exists in; ld: schema.org objects of the page;
    crumb: its name in the breadcrumb; index=False keeps it out of search engines and the sitemap."""
    langs = [c for c in LANGS if c in (langs or LANGS)]
    file = here + "index.html" if here.endswith("/") else here
    path = (prefix() + file).lstrip("/")
    url = SITE + u(here)
    alternates = "\n".join(f'<link rel="alternate" hreflang="{tag(c)}" href="{SITE}{u(here, c)}">' for c in langs)
    alternates += f'\n<link rel="alternate" hreflang="x-default" href="{SITE}{u(here, X_DEFAULT)}">'
    og_alt = "\n".join(f'<meta property="og:locale:alternate" content="{LANGUAGES[c][4]}">' for c in langs if c != LANG)
    graph = [organization(),
             {"@type": "WebSite", "@id": SITE + "/#site", "url": SITE + "/", "name": "Luckgram",
              "publisher": {"@id": SITE + "/#org"}, "inLanguage": [tag(c) for c in LANGS]},
             {"@type": "WebPage", "@id": url + "#page", "url": url, "name": plain(title), "description": plain(description),
              "inLanguage": tag(), "isPartOf": {"@id": SITE + "/#site"}, "dateModified": MODIFIED}]
    if crumb:
        graph.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Luckgram", "item": SITE + u("/")},
            {"@type": "ListItem", "position": 2, "name": crumb, "item": url}]})
    graph.extend(ld)
    data = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    seo = f'<link rel="canonical" href="{url}">\n{alternates}' if index else '<meta name="robots" content="noindex">'
    html = f'''<!doctype html>
<html lang="{tag()}" dir="{LANGUAGES[LANG][3]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(plain(title))}</title>
<meta name="description" content="{esc(plain(description))}">
{seo}
<meta property="og:type" content="website">
<meta property="og:site_name" content="Luckgram">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{esc(plain(title))}">
<meta property="og:description" content="{esc(plain(description))}">
<meta property="og:image" content="{SITE}/assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="{LANGUAGES[LANG][4]}">
{og_alt}
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#000000">
<meta name="heleket" content="16ef8c76" />
<link rel="icon" href="/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="preload" href="/assets/fonts/InterVariable.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/site.css?v={CSS_VERSION}">
<script type="application/ld+json">{data}</script>
</head>
<body>
{header(current, here, langs)}
<main id="main">
{body}
</main>
{footer(here, langs)}
</body>
</html>
'''
    out = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    if index and LANG == langs[0]:
        PAGES.append((here, langs))


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
        (t("What is Luckgram?", "Luckgram 是什么？"),
         t("Luckgram is an independent, open-source Telegram client for iPhone, iPad, Android and Windows. You sign in with your existing Telegram account and get everything Telegram has, plus extras such as more accounts in one app, hidden chats, free translation and AI tools.",
           "Luckgram 是独立、开源的 Telegram 客户端，支持 iPhone、iPad、Android 和 Windows。用你现有的 Telegram 账号登录，Telegram 有的功能都在，另外还有一个应用登录更多账号、隐藏聊天、免费翻译和 AI 等功能。")),
        (t("Is Luckgram an official Telegram app?", "Luckgram 是 Telegram 官方应用吗？"),
         t("No. Luckgram is an independent app built from the open-source Telegram apps for iOS and Android. It is not made by, affiliated with, or endorsed by Telegram.",
           "不是。Luckgram 是基于开源的 Telegram iOS 和 Android 应用开发的独立应用，并非由 Telegram 制作，与 Telegram 没有关联，也未获其认可。")),
        (t("Can I use my existing Telegram account?", "可以用我现有的 Telegram 账号吗？"),
         t("Yes. Sign in with your phone number. Your cloud chats, contacts and channels load from Telegram as they do in any Telegram app.",
           "可以。用手机号登录即可，云端聊天、联系人和频道会像在任何 Telegram 应用里一样从 Telegram 加载。")),
        (t("Can Luckgram read my messages?", "Luckgram 能看到我的消息吗？"),
         t("No. Your messages go to Telegram's servers, as they would from any Telegram app, and Luckgram runs no message servers of its own. Features that use Luckgram's servers, such as AI, only send what you choose to process. The source code of the apps is public.",
           "不能。你的消息和在任何 Telegram 应用里一样，发送到 Telegram 的服务器，Luckgram 没有自己的消息服务器。AI 等用到 Luckgram 服务器的功能，只发送你选择处理的内容。应用的源代码是公开的。")),
        (t("Is Luckgram free?", "Luckgram 免费吗？"),
         t("Yes. Every feature not marked Pro is free. Luckgram Pro is an optional membership with more AI, unlimited accounts, cloud backup and no sponsored messages. Telegram Premium and Telegram Stars are Telegram's own services and are sold and managed by Telegram.",
           "免费。没有标注“Pro 专享”的功能都免费使用。Luckgram Pro 是可选的会员，提供更多 AI、不限数量的账号、云备份和去除赞助消息。Telegram Premium 和 Telegram Stars 是 Telegram 自己的服务，由 Telegram 销售和管理。")),
        (t("Why isn't Luckgram on the App Store or Google Play?", "为什么 App Store 和 Google Play 上找不到 Luckgram？"),
         t(f'Luckgram is currently distributed from luckgram.cc. The <a href="{u("/download/")}">Download page</a> always links to the latest build.',
           f'Luckgram 目前直接在 luckgram.cc 发布。<a href="{u("/download/")}">下载页</a>上的链接始终指向最新版本。')),
        (t("How do I install Luckgram on an iPhone?", "怎么在 iPhone 上安装 Luckgram？"),
         t(f'There are two ways. “Install on iPhone” on the Download page is a signed build: open the page in Safari on the device and follow the steps, no computer needed. The IPA is unsigned: sign it with a tool such as Sideloadly or AltStore, or with your own Apple developer certificate, then install it. The <a href="{wiki("/getting-started/install.html")}">install guide</a> walks through each step.',
           f'有两种方式。下载页的「直接安装」是已签名的版本：在 iPhone 的 Safari 里打开下载页，按提示操作即可，不需要电脑。IPA 是未签名的：先用 Sideloadly、AltStore 等工具或你自己的 Apple 开发者证书签名，再安装。<a href="{wiki("/getting-started/install.html")}">安装指南</a>里有每一步的说明。')),
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
    sfx = "-zh" if chinese() else ""   # Chinese pages use the videos with the Chinese phone UI
    src = "data-src" if lazy else "src"
    attrs = 'preload="none" data-lazy' if lazy else 'autoplay preload="auto"'
    base = f"/media/web/{slug}{sfx}"
    return (f'<video class="demo" muted loop playsinline {attrs} poster="{base}.jpg?v={MEDIA_VERSION}" width="576" height="768" aria-label="{t("Animation", "演示动画")}: {label}">'
            f'<source {src}="{base}.webm?v={MEDIA_VERSION}" type="video/webm"><source {src}="{base}.mp4?v={MEDIA_VERSION}" type="video/mp4"></video>')


def download_buttons():
    """The four downloads and the web app. The script in footer() puts the visitor's own system first (data-smart)."""
    return f'''<a class="btn platform primary" href="{IOS_LATEST}" data-dl="ios" data-os="ios" target="_blank" rel="noopener">{ICON_APPLE}<span><small>{t("iPhone and iPad · sign it yourself", "iPhone 和 iPad · 需自行签名")}</small>{t("Download IPA", "下载 IPA")}</span></a>
        <a class="btn platform" href="{IOS_INSTALL}" data-ios-install data-os="ios" target="_blank" rel="noopener">{ICON_APPLE}<span><small>{t("iPhone and iPad · no computer needed", "iPhone 和 iPad · 无需电脑")}</small>{t("Install on iPhone", "直接安装 iOS 版")}</span></a>
        <a class="btn platform" href="{ANDROID_LATEST}" data-dl="android" data-os="android" target="_blank" rel="noopener">{ICON_ANDROID}<span><small>{t("Android 6.0 or later", "Android 6.0 及以上")}</small>{t("Download APK", "下载 APK")}</span></a>
        <a class="btn platform" href="{WIN_LATEST}" data-dl="windows" data-os="windows" target="_blank" rel="noopener">{ICON_WINDOWS}<span><small>{t("Windows 10/11 · beta", "Windows 10/11 · 测试版")}</small>{t("Download for Windows", "下载 Windows 版")}</span></a>
        <a class="btn platform" href="{WEB_APP}" target="_blank" rel="noopener">{ICON_WEB}<span><small>{t("In your browser · nothing to install", "浏览器直接用 · 无需安装")}</small>{t("Open the web app", "打开网页版")}</span></a>'''


def feature_by_slug():
    return {slug: (short, title, status, body) for _, items in feature_groups() for slug, short, title, status, body, _, _, _ in items}


def software(description):
    """schema.org description of the app, the same on every page that carries it."""
    return {"@type": "SoftwareApplication", "@id": SITE + "/#app", "name": "Luckgram",
            "description": plain(description), "url": SITE + u("/"), "downloadUrl": SITE + u("/download/"),
            "applicationCategory": "CommunicationApplication", "operatingSystem": "iOS, Android, Windows",
            "isAccessibleForFree": True, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
            "publisher": {"@id": SITE + "/#org"}, "inLanguage": tag()}


def facts():
    """What Luckgram is, in the plainest words: the answers people (and the search and AI tools they ask) look for."""
    return [
        (t("What it is", "是什么"), t("An independent Telegram client: an app that connects to the Telegram network with your own Telegram account.",
                                   "独立的 Telegram 客户端：用你自己的 Telegram 账号连接 Telegram 网络的应用。")),
        (t("Who makes it", "谁做的"), t("The Luckgram team. It is not made by, affiliated with, or endorsed by Telegram.",
                                     "Luckgram 团队。并非由 Telegram 制作，与 Telegram 没有关联，也未获其认可。")),
        (t("Where it runs", "支持的平台"), t("iPhone and iPad, Android, Windows (beta), and in a browser at web.luckgram.cc.",
                                         "iPhone 和 iPad、Android、Windows（测试版），以及浏览器里的 web.luckgram.cc。")),
        (t("Price", "价格"), t("Free. Luckgram Pro is an optional membership.", "免费。Luckgram Pro 是可选的会员。")),
        (t("Accounts", "账号数量"), t("10 Telegram accounts in one app for free, unlimited with Luckgram Pro.",
                                   "一个应用里免费登录 10 个 Telegram 账号，开通 Luckgram Pro 后不限数量。")),
        (t("Source code", "源代码"), t("Public on GitHub for iOS and Android.", "iOS 和 Android 版的代码在 GitHub 上公开。")),
    ]


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
        sub = re.sub(r"^.{1,40}?[:：]\s*", "", t(*title)) if t(*title).startswith(t(*short)) else t(*title)
        sub = sub[:1].upper() + sub[1:]
        cells.append(f'''<a class="cell" href="{u("/features/")}#{slug}">{video(slug, t(*title))}
        <span class="tag {key}">{t(*label)}</span><h3>{t(*short)}</h3><p>{sub}</p></a>''')
    qa = "\n".join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in faq())
    glance = "\n".join(f'<div><dt>{k}</dt><dd>{v}</dd></div>' for k, v in facts())
    lede = t("Luckgram is an independent, open-source Telegram client for iOS, Android and Windows. Sign in with your Telegram account and your chats, channels and calls are all there, plus more accounts, hidden chats, free translation and AI tools.",
             "Luckgram 是独立、开源的 iOS、Android 和 Windows Telegram 客户端。用你的 Telegram 账号登录，聊天、频道和通话都在，还有多账号、隐藏聊天、免费翻译和 AI 等功能。")
    count = t("{n} features in all.", "共 {n} 个功能。").replace("{n}", str(n))
    body = f'''<section class="hero">
  <div class="wrap">
    <h1>{t("Telegram,<br>flying further", "Telegram，<br>飞得更远")}</h1>
    <p class="lede">{lede}</p>
    <div class="btns" data-smart>
        {download_buttons()}
    </div>
    <p class="fine">{t(f'Free. Installing on iPhone? Read the <a href="{wiki("/getting-started/install.html")}">install guide</a>.', f'免费使用。在 iPhone 上安装，请先看<a href="{wiki("/getting-started/install.html")}">安装指南</a>。')}</p>
  </div>
  <div class="horizon">
    <div class="side">{video("accounts", t(*feats["accounts"][1]))}</div>
    <figure class="stage">
      {video("translate-in", t("Translate messages", "翻译消息"), lazy=False)}
      <figcaption><span class="tag ok">{t("Available now: translate incoming messages", "现已可用：翻译收到的消息")}</span></figcaption>
    </figure>
    <div class="side">{video("ai-summary", t(*feats["ai-summary"][1]))}</div>
  </div>
</section>

<section class="block glance">
  <div class="wrap">
    <h2>{t("Luckgram at a glance", "一眼看懂 Luckgram")}</h2>
    <dl>
{glance}
    </dl>
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
    <div class="wall-foot"><span>{count}</span><a class="btn" href="{u("/features/")}">{t("See all features", "查看全部功能")}</a></div>
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

<section class="block" id="faq">
  <div class="wrap faq">
    <div class="head solo"><h2>{t("Questions", "常见问题")}</h2>
      <p>{t(f'More answers in the <a href="{wiki()}">Help Center</a>.', f'更多解答请看<a href="{wiki()}">帮助中心</a>。')}</p></div>
    <div class="qa">
{qa}
    </div>
  </div>
</section>

<section class="cta" id="download">
  <div class="wrap">
    <div class="mark" aria-hidden="true"></div>
    <h2>{t("Take your Telegram with you", "带上你的 Telegram，出发")}</h2>
    <p>{t("Free for iPhone, iPad, Android and Windows. Sign in with the account you already have.", "iPhone、iPad、Android 和 Windows 均可免费使用，用你现有的账号登录。")}</p>
    <div class="btns" data-smart>
      {download_buttons()}
    </div>
  </div>
</section>'''
    description = t("Luckgram is an independent, open-source Telegram client for iOS, Android and Windows. Sign in with your Telegram account and keep everything you use today.",
                    "Luckgram 是独立、开源的 iOS、Android 和 Windows Telegram 客户端。用你的 Telegram 账号登录，现在用的一切都还在。")
    questions = {"@type": "FAQPage", "@id": SITE + u("/") + "#faq", "inLanguage": tag(), "mainEntity": [
        {"@type": "Question", "name": plain(q), "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq()]}
    page("/", t("Luckgram – an independent Telegram client for iOS, Android and Windows", "Luckgram – 独立的 iOS、Android 和 Windows Telegram 客户端"),
         description, body, ld=[software(description), questions])


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
      <div class="btns"><a class="btn primary" href="{ANDROID_LATEST}" data-dl="android" target="_blank" rel="noopener">{t("Download APK", "下载 APK")}</a></div>
      <div class="dl-meta" data-dl-meta="android" hidden></div>
      <details class="dl-more" data-dl-other="android" hidden>
        <summary>{t("Other builds", "其他版本")}</summary>
        <p>{t("x86_64 APK for Android emulators on x86 computers (Windows, Intel Mac). Not for phones.",
              "x86_64 APK，给 x86 电脑（Windows、Intel Mac）上的 Android 模拟器用，手机请下载上面的版本。")}</p>
        <p><a class="btn" href="{ANDROID_X86_LATEST}" data-dl="android-x86_64" target="_blank" rel="noopener">{t("Download x86_64 APK", "下载 x86_64 APK")}</a></p>
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
      <div class="btns"><a class="btn primary" href="{IOS_LATEST}" data-dl="ios" target="_blank" rel="noopener">{t("Download IPA", "下载 IPA")}</a><a class="btn" href="{IOS_INSTALL}" data-ios-install target="_blank" rel="noopener">{t("Install on iPhone", "直接安装")}</a><a class="btn" href="{wiki("/getting-started/install.html")}">{t("Install guide", "安装指南")}</a></div>
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
      <div class="btns"><a class="btn primary" href="{WIN_LATEST}" data-dl="windows" target="_blank" rel="noopener">{t("Download installer", "下载安装包")}</a></div>
      <div class="dl-meta" data-dl-meta="windows" hidden></div>
      <details class="dl-more">
        <summary>{t("Other builds", "其他版本")}</summary>
        <p>{t("Portable ZIP: unzip and run Luckgram.exe, data stays in that folder.", "便携版 ZIP：解压后直接运行 Luckgram.exe，数据保存在同一个文件夹里。")}</p>
        <p><a class="btn" href="{WIN_PORTABLE_LATEST}" data-dl="windows-portable" target="_blank" rel="noopener">{t("Download portable ZIP", "下载便携版 ZIP")}</a></p>
        <div class="dl-meta" data-dl-meta="windows-portable"></div>
      </details>
    </div>
    <div class="dl-card">
      <svg class="os" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true">{ICON_WEB[ICON_WEB.index("<circle"):ICON_WEB.index("</svg>")]}</svg>
      <h2>{t("Web app", "网页版")}</h2>
      <ul>
        <li>{t("Runs in the browser on any computer or phone, nothing to download", "在电脑或手机的浏览器里直接使用，不用下载")}</li>
        <li>{t("Up to 20 accounts", "最多登录 20 个账号")}</li>
        <li>{t("Chrome, Edge or Safari can install it as a desktop app", "Chrome、Edge、Safari 可以把它安装成桌面应用")}</li>
      </ul>
      <div class="btns"><a class="btn primary" href="{WEB_APP}" target="_blank" rel="noopener">{t("Open the web app", "打开网页版")}</a><a class="btn" href="{wiki("/getting-started/web.html")}">{t("About the web app", "网页版说明")}</a></div>
    </div>
  </div>
  <p class="note">{t("If you previously installed a test build of Luckgram on Android, uninstall it first: builds signed with a different key cannot update each other. Only download Luckgram from this page or the GitHub repositories it links to.",
                     "如果你之前在 Android 上装过 Luckgram 的测试版，请先卸载：签名密钥不同的版本不能相互覆盖升级。请只从本页或本页链接的 GitHub 仓库下载 Luckgram。")}</p>
</div>'''
    page("/download/", t("Download Luckgram for Android, iOS and Windows", "下载 Luckgram（Android、iOS 和 Windows）"),
         t("Download the latest Luckgram builds for Android (APK), iOS (IPA) and Windows.", "下载最新版 Luckgram：Android（APK）、iOS（IPA）和 Windows。"), body, "download",
         crumb=t("Download", "下载"))



def privacy():
    body = f'''<article class="prose">
<h1>{t("Privacy Policy", "隐私政策")}</h1>
<p class="meta">{t("Last updated", "最后更新：")}{"" if chinese() else " "}{t(*PRIVACY_UPDATED)}</p>

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
         t("How Luckgram handles your information.", "Luckgram 如何处理你的信息。"), body, langs=LEGAL_LANGS, crumb=t("Privacy Policy", "隐私政策"))


def terms():
    body = f'''<article class="prose">
<h1>{t("Terms of Use", "使用条款")}</h1>
<p class="meta">{t("Last updated", "最后更新：")}{"" if chinese() else " "}{t(*UPDATED)}</p>

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
         t("The terms for using Luckgram.", "使用 Luckgram 的条款。"), body, langs=LEGAL_LANGS, crumb=t("Terms of Use", "使用条款"))




# Feature page: (slug, short name, title, status, body, help path); text pairs are (English, Chinese)
FEATURES_JSON = os.path.join(ROOT, "data", "features.json")
STATUS_CLASS = {"live": "ok", "telegram": "ok", "pro": "pro", "wip": "wip"}


def load_features():
    """data/features.json is the single feature list shared with wiki.luckgram.cc (issue specs#103)."""
    with open(FEATURES_JSON, encoding="utf-8") as f:
        return json.load(f)


def web_line(f):
    """The feature in the web app (field "web" of features.json): a line for the features page, or nothing."""
    if f.get("web") != "live":
        return ""
    note = f.get("web_note")
    text = t("Also in the web app.", "网页版也可用。") + (" " + t(note["en"], note["zh"]) if note else "")
    return f'<p class="feat-web"><span class="tag ok">{t("Web", "网页版")}</span> {text} <a href="{WEB_APP}" target="_blank" rel="noopener">{t("Open the web app", "打开网页版")}</a></p>'


def feature_groups():
    """[((group en, zh), [(slug, short, title, (css class, label), body, wiki path, has video, web line)])] from features.json.
    features.json keeps Chinese and English (the Help Center copies it); t() finds the other languages by the English."""
    data = load_features()
    pair = lambda d: (d["en"], d["zh"])
    out = []
    for g in data["groups"]:
        items = [(f["id"], pair(f["name"]), pair(f["title"]), (STATUS_CLASS[f["status"]], pair(data["statuses"][f["status"]])),
                  pair(f["description"]), f["wiki"], f["video"], web_line(f))
                 for f in data["features"] if f["group"] == g["id"]]
        out.append((pair(g["name"]), items))
    return out


def features():
    toc, sections, names = [], [], []
    for group, items in feature_groups():
        toc.append(f'<li class="toc-group">{t(*group)}</li>')
        for slug, short, title, (key, label), body, help_path, has_video, web in items:
            title = t(*title)
            names.append((slug, title))
            toc.append(f'<li><a href="#{slug}">{t(*short)}</a></li>')
            demo = video(slug, title) if has_video else ""
            sections.append(f'''<section class="feat{"" if has_video else " novid"}" id="{slug}">
  {demo}
  <div class="feat-text">
    <span class="tag {key}">{t(*label)}</span>
    <h2>{title}</h2>
    <p>{t(*body)}</p>
    {web}
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
    <div class="btns" data-smart>
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
    listing = {"@type": "ItemList", "@id": SITE + u("/features/") + "#list", "name": t("Luckgram features", "Luckgram 功能"),
               "numberOfItems": len(names), "itemListElement": [
                   {"@type": "ListItem", "position": i + 1, "name": plain(name), "url": SITE + u("/features/") + "#" + slug}
                   for i, (slug, name) in enumerate(names)]}
    page("/features/", t("Luckgram features: everything it adds to Telegram", "Luckgram 功能：在 Telegram 之上增加了什么"),
         t("Every feature Luckgram adds to Telegram, with its status: available for everyone or part of Luckgram Pro.",
           "Luckgram 在 Telegram 之上增加的全部功能及状态：所有人可用，或属于 Luckgram Pro。"),
         body, "features", ld=[listing], crumb=t("Features", "功能"))


# ---- MCP documentation and the Skill market ----

MCP_CONFIG = """{
  "mcpServers": {
    "luckgram": {
      "type": "http",
      "url": "http://127.0.0.1:28765/mcp",
      "headers": { "Authorization": "Bearer &lt;TOKEN&gt;" }
    }
  }
}"""

MCP_CLOUD_CONFIG = """{
  "mcpServers": {
    "luckgram-cloud": {
      "type": "http",
      "url": "https://mcp.luckgram.cc/mcp",
      "headers": { "Authorization": "Bearer lgc_..." }
    }
  }
}"""

MCP_CLAUDE = """claude mcp add --transport http luckgram http://127.0.0.1:28765/mcp \\
  --header "Authorization: Bearer &lt;TOKEN&gt;\""""

MCP_KIRO = """{
  "mcpServers": {
    "luckgram": {
      "url": "http://127.0.0.1:28765/mcp",
      "headers": { "Authorization": "Bearer &lt;TOKEN&gt;" }
    }
  }
}"""

MCP_CODEX = """export LUCKGRAM_MCP_TOKEN="&lt;TOKEN&gt;"
codex mcp add luckgram --url http://127.0.0.1:28765/mcp \\
  --bearer-token-env-var LUCKGRAM_MCP_TOKEN"""

MCP_CODEX_TOML = """[mcp_servers.luckgram]
url = "http://127.0.0.1:28765/mcp"
bearer_token_env_var = "LUCKGRAM_MCP_TOKEN\""""

MCP_OPENCODE = """opencode mcp add luckgram --url http://127.0.0.1:28765/mcp \\
  --header "Authorization=Bearer &lt;TOKEN&gt;\""""

MCP_SSH = "ssh -N -L 28765:127.0.0.1:28765 user@computer-with-luckgram"

MCP_CALL = """POST /mcp
Authorization: Bearer &lt;TOKEN&gt;
Content-Type: application/json

{"jsonrpc":"2.0","id":1,"method":"tools/call",
 "params":{"name":"list_chats","arguments":{"account":"7943234085","unread_only":true}}}"""

SKILL_CLI_INSTALL = """curl -LO https://luckgram.cc/skills/luckgram/luckgram-skill.zip
unzip luckgram-skill.zip -d ~/.claude/skills/
node ~/.claude/skills/luckgram/bin/luckgram config --local --token-stdin"""

# Copy buttons on code blocks, the tabs of "Connect your AI tool", the current section in the
# side list and the filter of the Skill market. Everything works without it: the code is
# selectable, every tab's panel is shown, every skill is listed.
DOC_SCRIPT = """<script>
(function () {
  var copy = __COPY__, copied = __COPIED__;
  document.querySelectorAll('.doc pre').forEach(function (pre) {
    if (!navigator.clipboard) return;
    var b = document.createElement('button'); b.type = 'button'; b.className = 'copy'; b.textContent = copy;
    b.addEventListener('click', function () {
      navigator.clipboard.writeText(pre.querySelector('code').innerText).then(function () {
        b.textContent = copied; setTimeout(function () { b.textContent = copy; }, 1600); });
    });
    pre.appendChild(b);
  });
  document.querySelectorAll('.tabs').forEach(function (tabs) {
    var buttons = tabs.querySelectorAll('[role=tab]'), panels = tabs.querySelectorAll('[role=tabpanel]');
    function show(i) {
      buttons.forEach(function (b, n) { b.setAttribute('aria-selected', n === i ? 'true' : 'false'); b.tabIndex = n === i ? 0 : -1; });
      panels.forEach(function (p, n) { p.hidden = n !== i; });
    }
    buttons.forEach(function (b, i) {
      b.addEventListener('click', function () { show(i); });
      b.addEventListener('keydown', function (e) {
        var d = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0; if (!d) return;
        var n = (i + d + buttons.length) % buttons.length; show(n); buttons[n].focus();
      });
    });
    tabs.classList.add('on'); show(0);
  });
  var links = {}; document.querySelectorAll('.doc-nav a').forEach(function (a) { links[a.getAttribute('href').slice(1)] = a; });
  if ('IntersectionObserver' in window && Object.keys(links).length) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (!e.isIntersecting || !links[e.target.id]) return;
        document.querySelectorAll('.doc-nav a.on').forEach(function (x) { x.classList.remove('on'); }); links[e.target.id].classList.add('on'); });
    }, {rootMargin: '-20% 0px -70% 0px'});
    Object.keys(links).forEach(function (id) { var el = document.getElementById(id); if (el) io.observe(el); });
  }
  var chips = document.querySelectorAll('.sk-filter button');
  chips.forEach(function (c) {
    c.addEventListener('click', function () {
      chips.forEach(function (x) { x.setAttribute('aria-pressed', x === c ? 'true' : 'false'); });
      var kind = c.getAttribute('data-kind');
      document.querySelectorAll('.sk-card').forEach(function (card) {
        card.hidden = kind !== 'all' && card.getAttribute('data-kind') !== kind;
      });
    });
  });
})();
</script>"""


def doc_script():
    return DOC_SCRIPT.replace("__COPY__", json.dumps(t("Copy", "复制"))).replace("__COPIED__", json.dumps(t("Copied", "已复制")))


def skill_logo(skill, size=""):
    """A skill's own logo: its mark on a tile in its own colour."""
    return (f'<span class="sk-logo{" " + size if size else ""}" style="--h:{skill["hue"]}" aria-hidden="true">'
            f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{skill["icon"]}</svg></span>')


def skill_kind(skill):
    return {"always": t("Always on", "始终开启"), "read": t("Read only", "只读"),
            "write": t("Changes the account", "会改动账号")}[skill["kind"]]


def skill_limit(skill):
    """The tightest limit of the skill's tools, for the card."""
    limits = [tool[4] for tool in skill["tools"] if tool[4]]
    return t(*limits[0]) if limits else t("No limit", "不限次数")


def mcp():
    sections = [
        ("start", t("Quick start", "快速开始")),
        ("connect", t("Connect your AI tool", "连接你的 AI 工具")),
        ("skills", t("Skills", "Skill")),
        ("cloud", t("Cloud", "云端")),
        ("api", t("Calling it directly", "直接调用")),
        ("security", t("Security", "安全")),
        ("trouble", t("Troubleshooting", "排查问题")),
    ]
    nav = "".join(f'<li><a href="#{key}">{label}</a></li>' for key, label in sections)
    tabs = [
        ("Claude Code", f"""<pre><code>{MCP_CLAUDE}</code></pre>
<p>{t("Check with <code>claude mcp list</code>: the line for <code>luckgram</code> ends with <b>Connected</b>.", "用 <code>claude mcp list</code> 检查：<code>luckgram</code> 那一行末尾显示 <b>Connected</b>。")}</p>"""),
        ("Kiro", f"""<p>{t("Put this in <code>.kiro/settings/mcp.json</code> in your project, or in <code>~/.kiro/settings/mcp.json</code> for every project:", "把下面的内容写到项目里的 <code>.kiro/settings/mcp.json</code>；想对所有项目生效，就写到 <code>~/.kiro/settings/mcp.json</code>：")}</p>
<pre><code>{MCP_KIRO}</code></pre>
<p>{t("Then ask Kiro to call <code>list_accounts</code>.", "然后让 Kiro 调用 <code>list_accounts</code> 试一下。")}</p>"""),
        ("Codex", f"""<p>{t("Codex reads the token from an environment variable, so it is not written into its config file:", "Codex 从环境变量读取令牌，令牌不会写进它的配置文件：")}</p>
<pre><code>{MCP_CODEX}</code></pre>
<p>{t('On Windows set the variable with <code>setx LUCKGRAM_MCP_TOKEN "&lt;TOKEN&gt;"</code> and open a new terminal. The command writes this to <code>~/.codex/config.toml</code>:', 'Windows 上用 <code>setx LUCKGRAM_MCP_TOKEN "&lt;TOKEN&gt;"</code> 设置变量，然后重新打开终端。上面的命令会在 <code>~/.codex/config.toml</code> 里写入：')}</p>
<pre><code>{MCP_CODEX_TOML}</code></pre>"""),
        ("opencode", f"""<pre><code>{MCP_OPENCODE}</code></pre>
<p>{t("The header is written as <code>name=value</code>. Check with <code>opencode mcp list</code>: it shows <b>connected</b>. Right after adding it may still say pending; run it again a few seconds later.", "请求头的写法是 <code>名称=值</code>。用 <code>opencode mcp list</code> 检查，显示 <b>connected</b> 即可。刚添加完可能还显示 pending，过几秒再运行一次。")}</p>"""),
        (t("Other tools", "其他工具"), f"""<p>{t("Any MCP client that speaks HTTP works. Most accept this JSON:", "任何支持 HTTP 传输的 MCP 客户端都能用。大多数接受下面这段 JSON：")}</p>
<pre><code>{MCP_CONFIG}</code></pre>"""),
    ]
    tab_buttons = "".join(f'<button type="button" role="tab" id="tab-{i}" aria-controls="panel-{i}">{name}</button>' for i, (name, _) in enumerate(tabs))
    tab_panels = "".join(f'<div role="tabpanel" id="panel-{i}" aria-labelledby="tab-{i}"><h3>{name}</h3>{body}</div>' for i, (name, body) in enumerate(tabs))
    skill_rows = "".join(
        f'<a class="sk-row" href="{u("/skills/" + sk["key"] + "/")}">{skill_logo(sk, "s")}<span><b>{t(*sk["name"])}</b><i>{t(*sk["tagline"])}</i></span><em>{skill_kind(sk)}</em></a>'
        for sk in SKILLS)
    trouble = [
        (t("The tool cannot connect", "工具连不上"),
         t("Luckgram Desktop has to be open, with <b>Local MCP server</b> switched on. The page shows the address in use: when port 28765 is taken, the next free one is used.", "Luckgram 桌面版要开着，并且打开了<b>本机 MCP 接口</b>。设置页会显示实际使用的地址：28765 端口被占用时会顺延到下一个空闲端口。")),
        (t("401, “Missing or wrong access token”", "401，“Missing or wrong access token”"),
         t("The token in your tool is not the current one. Copy it again; after <b>Regenerate access token</b> the old one stops working.", "工具里的令牌不是当前的令牌。重新复制一次；点过<b>重新生成访问令牌</b>后旧令牌就失效了。")),
        (t("“The … skill is off for account …”", "“The … skill is off for account …”"),
         t("That skill is not switched on for that account. Switch it on in the same settings page, under the account's name.", "这个账号没有开启这个 Skill。在同一个设置页里，到该账号名下把它打开。")),
        (t("“Rate limit … Try again in N seconds”", "“Rate limit … Try again in N seconds”"),
         t("The per-account limit of that tool was reached. Wait the stated time. The limits cannot be switched off.", "这个工具在该账号上达到了频率上限。等待提示的时间即可。上限不能关闭。")),
        (t("“Luckgram Desktop is locked with a passcode”", "“Luckgram Desktop is locked with a passcode”"),
         t("Unlock the app on the computer. While it is locked nothing is listed and nothing runs.", "到电脑上解锁应用。锁定期间不列出任何账号，也不执行任何操作。")),
        (t("The cloud says no computer is online", "云端提示没有电脑在线"),
         t("Open Luckgram Desktop on that computer and check that <b>Connect through the cloud</b> is on and says “Connected”. Where <code>luckgram.cc</code> is blocked the app switches to the backup address by itself; your AI tool needs the backup address too.", "在那台电脑上打开 Luckgram 桌面版，确认<b>通过云端连接</b>已打开并显示“已连接”。<code>luckgram.cc</code> 被屏蔽的网络里应用会自己切到备用地址，AI 工具那边也要换成备用地址。")),
    ]
    trouble_rows = "".join(f"<tr><td>{q}</td><td>{a}</td></tr>" for q, a in trouble)
    body = f"""<section class="doc-head">
  <div class="wrap">
    <p class="crumbs"><a href="{u("/")}">Luckgram</a> / MCP</p>
    <h1>Luckgram MCP</h1>
    <p class="lede">{t("Luckgram Desktop has an MCP server built in. Your AI tool lists the Telegram accounts on your computer, switches between them, and uses the skills you allow for each account.", "Luckgram 桌面版内置 MCP 接口。你的 AI 工具可以列出电脑上的 Telegram 账号、在账号之间切换，并使用你为每个账号开启的 Skill。")}</p>
    <ul class="doc-facts">
      <li><b>{t("Off by default", "默认关闭")}</b>{t("The server, the cloud and every skill of every account are switched on by you.", "接口、云端、每个账号的每个 Skill，都要你亲手打开。")}</li>
      <li><b>{t("Local first", "本机优先")}</b>{t("Listens on 127.0.0.1 only. The cloud is optional.", "只监听 127.0.0.1。云端是可选的。")}</li>
      <li><b>{t("Limits built in", "内置上限")}</b>{t("Everything that changes an account is rate limited per account.", "所有会改动账号的操作都按账号限制频率。")}</li>
    </ul>
  </div>
</section>
<div class="wrap doc-layout">
  <nav class="doc-nav" aria-label="{t("On this page", "本页内容")}"><ul>{nav}</ul></nav>
  <article class="doc">

<h2 id="start">{t("Quick start", "快速开始")}</h2>
<ol class="steps">
<li>{t(f'Install <a href="{u("/download/")}">Luckgram Desktop</a> for Windows and sign in to your accounts.', f'安装 Windows 版 <a href="{u("/download/")}">Luckgram 桌面版</a>并登录账号。')}</li>
<li>{t("Open Settings → Luckgram → <b>Local MCP server</b> and switch it on.", "打开 设置 → Luckgram 功能 → <b>本机 MCP 接口</b>，把开关打开。")}</li>
<li>{t("Click the row and use <b>Copy client config</b> or <b>Copy access token</b>.", "点进这一行，使用<b>复制客户端配置</b>或<b>复制访问令牌</b>。")}</li>
<li>{t("Connect your AI tool (next section) and ask it: “Which Telegram accounts am I logged in to?”", "连接你的 AI 工具（见下一节），然后问它：“我登录了哪些 Telegram 账号？”")}</li>
</ol>

<h2 id="connect">{t("Connect your AI tool", "连接你的 AI 工具")}</h2>
<p>{t("<code>&lt;TOKEN&gt;</code> is the access token from the settings page. For the cloud, use <code>https://mcp.luckgram.cc/mcp</code> as the address and the cloud key as the token; everything else is the same.", "<code>&lt;TOKEN&gt;</code> 是设置页里的访问令牌。接云端时，把地址换成 <code>https://mcp.luckgram.cc/mcp</code>、令牌换成云端密钥，其余步骤相同。")}</p>
<div class="tabs">
  <div class="tab-list" role="tablist" aria-label="{t("AI tool", "AI 工具")}">{tab_buttons}</div>
  {tab_panels}
</div>
<p class="fine">{t("Tested with Claude Code 2.1, Kiro CLI 2.31, Codex CLI 0.144 and opencode 2.0, against the local and the cloud address.", "已在 Claude Code 2.1、Kiro CLI 2.31、Codex CLI 0.144、opencode 2.0 上用本机地址和云端地址测试。")}</p>

<h2 id="skills">{t("Skills", "Skill")}</h2>
<p>{t(f'What a tool may do is decided per account. Until you switch a skill on for an account, the tool can only list accounts and switch between them. Each skill has its own page in the <a href="{u("/skills/")}">Skill market</a>.', f'工具能做什么，是按账号决定的。在你为某个账号开启 Skill 之前，工具只能列出账号和切换账号。每个 Skill 在 <a href="{u("/skills/")}">Skill 市场</a>里都有自己的页面。')}</p>
<div class="sk-rows">{skill_rows}</div>

<h2 id="cloud">{t("Cloud: all your computers at one address", "云端：一个地址管理所有电脑")}</h2>
<p>{t("The local server works on one computer. With the cloud on, Luckgram Desktop connects out to <code>mcp.luckgram.cc</code>, so your AI tool reaches it from anywhere and several computers share one address. No public IP, no port forwarding.", "本机接口只能在一台电脑上用。打开云端后，桌面版会主动连到 <code>mcp.luckgram.cc</code>，AI 工具从任何地方都能连上，多台电脑共用一个地址。不需要公网 IP，也不需要端口转发。")}</p>
<ol class="steps">
<li>{t("On the first computer: the same settings page → switch on <b>Connect through the cloud</b>. A cloud key is made on your computer.", "在第一台电脑上：同一个设置页 → 打开<b>通过云端连接</b>。云端密钥在你的电脑上生成。")}</li>
<li>{t("Click <b>Copy cloud client config</b> and paste it into your AI tool:", "点<b>复制云端客户端配置</b>，粘贴到 AI 工具里：")}
<pre><code>{MCP_CLOUD_CONFIG}</code></pre></li>
<li>{t("On every other computer: <b>Use the cloud key of another computer</b>, paste the key, then switch on <b>Connect through the cloud</b>.", "在其他每台电脑上：点<b>使用另一台电脑的云端密钥</b>，粘贴密钥，再打开<b>通过云端连接</b>。")}</li>
</ol>
<ul>
<li>{t("The tools are the same, each with one more argument, <code>device</code>. <code>list_devices</code> shows your computers and which are online.", "工具和本机版相同，每个工具多一个 <code>device</code> 参数。<code>list_devices</code> 列出你的电脑和在线状态。")}</li>
<li>{t("Skills stay per account and are switched on in the app on each computer. Rate limits are counted on each computer too.", "Skill 仍然按账号开启，在每台电脑各自的应用里设置。频率上限也在每台电脑上各自计数。")}</li>
<li>{t("<code>list_recent_calls</code> shows the last 200 calls that went through the cloud: time, tool, computer, account, failed or not.", "<code>list_recent_calls</code> 可以查看最近 200 次经过云端的调用：时间、工具、电脑、账号、是否失败。")}</li>
<li>{t("If <code>luckgram.cc</code> does not open on your network, use the backup address <code>https://lg-mcp.cat158.com/mcp</code>. It is the same service with the same computers, and Luckgram Desktop switches to it by itself.", "如果你的网络打不开 <code>luckgram.cc</code>，把地址换成备用地址 <code>https://lg-mcp.cat158.com/mcp</code>。它是同一个服务、同一批电脑，桌面版会自己切换过去。")}</li>
</ul>

<h2 id="api">{t("Calling it directly", "直接调用")}</h2>
<p>{t("The server speaks MCP over HTTP: one <code>POST</code> per JSON-RPC message, a JSON answer. No session, no stream. A tool call looks like this:", "接口使用 MCP 的 HTTP 传输：每条 JSON-RPC 消息一个 <code>POST</code>，返回 JSON。没有会话，也没有流。一次工具调用是这样的：")}</p>
<pre><code>{MCP_CALL}</code></pre>
<p>{t("The answer has the result twice: as text in <code>content</code> and as JSON in <code>structuredContent</code>. A tool that could not do what was asked answers with <code>isError: true</code> and says why in plain words.", "返回里结果有两份：<code>content</code> 里的文字和 <code>structuredContent</code> 里的 JSON。工具没能完成时返回 <code>isError: true</code>，并用一句话说明原因。")}</p>
<p>{t("From another computer without the cloud, forward the port over SSH:", "不用云端、从另一台电脑调用时，用 SSH 转发端口：")}</p>
<pre><code>{MCP_SSH}</code></pre>

<h2 id="security">{t("Security", "安全")}</h2>
<ul>
<li>{t("The local server listens on <code>127.0.0.1</code> only. It cannot be reached from your network or the internet.", "本机接口只监听 <code>127.0.0.1</code>，局域网和外网都连不上。")}</li>
<li>{t("Every request needs the access token. It is generated on your computer, kept in the system credential store, and can be regenerated at any time.", "每个请求都要带访问令牌。令牌在你的电脑上生成，保存在系统凭据库里，随时可以重新生成。")}</li>
<li>{t("Requests from web pages are refused, so a site you visit cannot call it through your browser.", "来自网页的请求会被拒绝，你访问的网站无法借浏览器调用它。")}</li>
<li>{t("The cloud only passes requests on. It does not store arguments, results or chats, and it does not store the cloud key itself.", "云端只转发请求：不保存参数和结果，不保存聊天内容，也不保存云端密钥本身。")}</li>
<li>{t("Whoever has the access token or the cloud key can use what you switched on. If one leaks, regenerate it: the old one stops working at once.", "拿到访问令牌或云端密钥的人，可以使用你已开启的功能。泄露后请立即重新生成，旧的立刻失效。")}</li>
<li>{t("What a skill returns goes to your AI tool and its model. Switch on reading messages only for accounts whose chats you are willing to share with it.", "Skill 返回的内容会交给你的 AI 工具和它背后的模型。只给你愿意让它看聊天内容的账号开启读消息。")}</li>
</ul>

<h2 id="trouble">{t("Troubleshooting", "排查问题")}</h2>
<div class="tbl"><table>
<thead><tr><th>{t("What you see", "现象")}</th><th>{t("What to do", "怎么办")}</th></tr></thead>
<tbody>{trouble_rows}</tbody>
</table></div>

<p class="note">{t("Luckgram is an independent client that uses the Telegram API. It is not an official Telegram app. Use automation within Telegram's Terms of Service.", "Luckgram 是使用 Telegram API 的第三方客户端，不是 Telegram 官方应用。请在 Telegram 服务条款允许的范围内使用自动化功能。")}</p>
  </article>
</div>
{doc_script()}"""
    page("/mcp/", t("Luckgram MCP – connect AI tools to your Telegram accounts", "Luckgram MCP – 让 AI 工具操作你的 Telegram 账号"),
         t("Luckgram Desktop has an MCP server built in: AI tools list your accounts, switch between them and use the skills you allow for each account.",
           "Luckgram 桌面版内置 MCP 接口：AI 工具可以列出账号、切换账号，并使用你为每个账号开启的 Skill。"),
         body, "mcp", crumb="MCP")


def switchboard():
    """The picture of the idea: every account has its own switches."""
    shown = [BY_KEY[k] for k in ("friends", "chats", "messages", "messages_send", "groups")]
    rows = [
        (t("Work", "工作号"), "@li_work", (1, 1, 1, 1, 0)),
        (t("Support", "客服号"), "@acme_support", (1, 1, 1, 0, 0)),
        (t("Personal", "个人号"), "@li_wei", (0, 1, 0, 0, 0)),
    ]
    head = "".join(f'<th scope="col" title="{t(*sk["name"])}">{skill_logo(sk, "xs")}<span class="sr">{t(*sk["name"])}</span></th>' for sk in shown)
    body = "".join(
        f'<tr><th scope="row"><b>{name}</b><i>{user}</i></th>'
        + "".join(f'<td><span class="sw{" on" if on else ""}" style="--h:{sk["hue"]}"><span class="sr">{t("on", "开") if on else t("off", "关")}</span></span></td>'
                  for sk, on in zip(shown, states)) + "</tr>"
        for name, user, states in rows)
    return f"""<figure class="board">
  <table>
    <thead><tr><td></td>{head}</tr></thead>
    <tbody>{body}</tbody>
  </table>
  <figcaption>{t("Each account has its own switches. All are off until you turn them on.", "每个账号各有各的开关，在你打开之前全部是关的。")}</figcaption>
</figure>"""


def skills():
    cards = "".join(f"""<a class="sk-card" href="{u("/skills/" + sk["key"] + "/")}" data-kind="{sk["kind"]}">
  {skill_logo(sk)}
  <h3>{t(*sk["name"])}</h3>
  <p>{t(*sk["tagline"])}</p>
  <dl>
    <div><dt>{t("Type", "类型")}</dt><dd class="k-{sk["kind"]}">{skill_kind(sk)}</dd></div>
    <div><dt>{t("Tools", "工具")}</dt><dd>{len(sk["tools"])}</dd></div>
    <div><dt>{t("Limit per account", "每账号上限")}</dt><dd>{skill_limit(sk)}</dd></div>
  </dl>
</a>""" for sk in SKILLS)
    counts = {k: sum(1 for sk in SKILLS if sk["kind"] == k) for k in ("always", "read", "write")}
    body = f"""<section class="market-head">
  <div class="wrap">
    <div>
      <p class="crumbs"><a href="{u("/")}">Luckgram</a> / Skill</p>
      <h1>{t("Skill market", "Skill 市场")}</h1>
      <p class="lede">{t("A skill is one thing your AI tool may do with one of your Telegram accounts. Pick the ones you need and switch them on, account by account.", "一个 Skill，就是你的 AI 工具可以对你某个 Telegram 账号做的一件事。挑你需要的，按账号逐个打开。")}</p>
      <div class="btns">
        <a class="btn primary" href="{u("/mcp/")}#start">{t("Set up Luckgram MCP", "开始配置 Luckgram MCP")}</a>
        <a class="btn" href="#agent-skill">{t("Get the agent skill", "获取 Agent Skill")}</a>
      </div>
    </div>
    {switchboard()}
  </div>
</section>
<section class="wrap market">
  <div class="sk-filter" role="group" aria-label="{t("Show", "筛选")}">
    <button type="button" data-kind="all" aria-pressed="true">{t("All", "全部")} <span>{len(SKILLS)}</span></button>
    <button type="button" data-kind="read" aria-pressed="false">{t("Read only", "只读")} <span>{counts["read"]}</span></button>
    <button type="button" data-kind="write" aria-pressed="false">{t("Changes the account", "会改动账号")} <span>{counts["write"]}</span></button>
  </div>
  <div class="sk-grid">{cards}</div>
</section>
<section class="wrap market-how">
  <h2>{t("How a skill gets switched on", "Skill 是怎么打开的")}</h2>
  <ol>
    <li><b>{t("Turn on the MCP server", "打开 MCP 接口")}</b>{t("In Luckgram Desktop: Settings → Luckgram → Local MCP server.", "在 Luckgram 桌面版里：设置 → Luckgram 功能 → 本机 MCP 接口。")}</li>
    <li><b>{t("Switch skills on per account", "按账号打开 Skill")}</b>{t("On the same page, under each account's name. A skill that changes the account asks you to confirm once.", "在同一页里，每个账号名下各有一组开关。会改动账号的 Skill 要你确认一次。")}</li>
    <li><b>{t("Connect your AI tool", "连接 AI 工具")}</b>{t(f'Claude Code, Kiro, Codex, opencode or any MCP client. <a href="{u("/mcp/")}#connect">See how</a>.', f'Claude Code、Kiro、Codex、opencode 或任何 MCP 客户端。<a href="{u("/mcp/")}#connect">查看接法</a>。')}</li>
  </ol>
</section>
<section class="wrap market-agent doc" id="agent-skill">
  <div>
    <h2>{t("The luckgram skill for agents", "给 Agent 用的 luckgram Skill")}</h2>
    <p>{t("A command-line tool and instructions for agents that load skills, such as Claude Code. One command covers every skill above; the access token is read from standard input, stored with owner-only permissions and never printed.", "一个命令行工具，加上给 Agent 的使用说明，适用于 Claude Code 等会加载 Skill 的 Agent。一个命令覆盖上面所有 Skill；访问令牌从标准输入读取，以仅本人可读的权限保存，不会被输出。")}</p>
    <ul>
      <li>{t("<code>luckgram accounts</code>, <code>chats list</code>, <code>messages get</code>, <code>messages send</code>, <code>friends add</code> and the rest", "<code>luckgram accounts</code>、<code>chats list</code>、<code>messages get</code>、<code>messages send</code>、<code>friends add</code> 等命令")}</li>
      <li>{t("Works with the local server and the cloud; Node 18 or later, no dependencies", "本机接口和云端都能用；需要 Node 18 或更高版本，没有其他依赖")}</li>
      <li>{t("Rules for the agent: start from the account list, respect the limits, show a message before sending it", "给 Agent 的规则：先看账号列表、遵守频率上限、发送前先给你看")}</li>
    </ul>
    <p><a class="btn" href="/skills/luckgram/luckgram-skill.zip" download>{t("Download luckgram-skill.zip", "下载 luckgram-skill.zip")}</a> <a class="plain" href="/skills/luckgram/SKILL.md">{t("Read SKILL.md", "查看 SKILL.md")}</a></p>
  </div>
  <div>
    <p class="fine">{t("Install for Claude Code:", "为 Claude Code 安装：")}</p>
    <pre><code>{SKILL_CLI_INSTALL}</code></pre>
    <p class="fine">{t("Paste the access token when the last command waits, then press Enter and Ctrl-D.", "最后一条命令等待输入时粘贴访问令牌，然后按回车和 Ctrl-D。")}</p>
  </div>
</section>
{doc_script()}"""
    page("/skills/", t("Luckgram Skill market – what AI tools can do with each account", "Luckgram Skill 市场 – AI 工具能对每个账号做什么"),
         t("The skills of Luckgram MCP: accounts, friends, chats, messages, groups, profile. Each one is switched on per account.",
           "Luckgram MCP 的 Skill：账号、好友、会话、消息、群组、资料。每个 Skill 按账号单独开启。"),
         body, "skills", crumb="Skill")


def skill_page(sk):
    name = t(*sk["name"])
    here = "/skills/" + sk["key"] + "/"
    tools = "".join(
        f'<tr><td><code>{tool}</code></td><td>{t(*what)}</td><td>{t(*args)}</td><td>{t(*returns)}</td><td>{t(*limit) if limit else "–"}</td></tr>'
        for tool, what, args, returns, limit in sk["tools"])
    can = "".join(f"<li>{t(*c)}</li>" for c in sk["can"])
    prompts = "".join(f"<li>{t(*q)}</li>" for q in sk["prompts"])
    notes = "".join(f"<li>{t(*n)}</li>" for n in sk["notes"])
    cli = "\n".join(esc(line) for line in sk["cli"])
    related = "".join(
        f'<a class="sk-row" href="{u("/skills/" + r + "/")}">{skill_logo(BY_KEY[r], "s")}<span><b>{t(*BY_KEY[r]["name"])}</b><i>{t(*BY_KEY[r]["tagline"])}</i></span><em>{skill_kind(BY_KEY[r])}</em></a>'
        for r in sk["related"])
    if sk["kind"] == "always":
        turn_on = f'<p>{t("Nothing to switch on: it works as soon as the MCP server is on.", "不需要单独打开：MCP 接口开着它就可用。")}</p>'
    else:
        confirm = t(" Luckgram asks you to confirm, once for this account.", " Luckgram 会让你确认一次，每个账号只确认一次。") if sk["kind"] == "write" else ""
        turn_on = f"""<ol class="steps">
<li>{t("In Luckgram Desktop open Settings → Luckgram → <b>Local MCP server</b>.", "在 Luckgram 桌面版里打开 设置 → Luckgram 功能 → <b>本机 MCP 接口</b>。")}</li>
<li>{t("Under <b>Skills of each account</b>, find the account.", "在<b>每个账号的 Skill</b> 下面找到那个账号。")}</li>
<li>{t(f"Switch on <b>{sk['name'][0]}</b>.", f"打开<b>{sk['name'][1]}</b>。")}{confirm}</li>
</ol>"""
    limits = [(tool[0], tool[4]) for tool in sk["tools"] if tool[4]]
    limit_facts = "".join(f"<div><dt><code>{tool}</code></dt><dd>{t(*limit)}</dd></div>" for tool, limit in limits) \
        or f'<div><dt>{t("Limit", "上限")}</dt><dd>{t("None: it changes nothing", "无：它不改动任何东西")}</dd></div>'
    body = f"""<section class="skill-head" style="--h:{sk["hue"]}">
  <div class="wrap">
    <p class="crumbs"><a href="{u("/")}">Luckgram</a> / <a href="{u("/skills/")}">{t("Skill market", "Skill 市场")}</a> / {name}</p>
    <div class="skill-title">
      {skill_logo(sk, "l")}
      <div>
        <h1>{name}</h1>
        <p class="lede">{t(*sk["tagline"])}</p>
      </div>
    </div>
  </div>
</section>
<div class="wrap skill-layout">
  <article class="doc">
<p class="about">{t(*sk["about"])}</p>

<h2>{t("What it can do", "能做什么")}</h2>
<ul>{can}</ul>

<h2>{t("Ask your AI tool", "对 AI 工具这样说")}</h2>
<ul class="prompts">{prompts}</ul>

<h2>{t("Switch it on", "怎么打开")}</h2>
{turn_on}

<h2>{t("Tools", "工具")}</h2>
<div class="tbl"><table>
<thead><tr><th>{t("Tool", "工具")}</th><th>{t("What it does", "作用")}</th><th>{t("Arguments", "参数")}</th><th>{t("Returns", "返回")}</th><th>{t("Limit per account", "每账号上限")}</th></tr></thead>
<tbody>{tools}</tbody>
</table></div>
<p class="fine">{t("<code>account</code> is the <code>id</code> from <code>list_accounts</code>; without it the active account is used. On the cloud every tool also takes <code>device</code>.", "<code>account</code> 是 <code>list_accounts</code> 返回的 <code>id</code>，不填就是当前账号。在云端，每个工具还可以带 <code>device</code>。")}</p>

<h2>{t("From the command line", "命令行")}</h2>
<pre><code>{cli}</code></pre>
<p class="fine">{t(f'With the <a href="{u("/skills/")}#agent-skill">luckgram skill for agents</a>.', f'需要安装<a href="{u("/skills/")}#agent-skill">给 Agent 用的 luckgram Skill</a>。')}</p>

<h2>{t("Good to know", "注意事项")}</h2>
<ul>{notes}</ul>

<h2>{t("Works well with", "搭配使用")}</h2>
<div class="sk-rows">{related}</div>
  </article>
  <aside class="skill-facts" aria-label="{t("About this skill", "关于这个 Skill")}">
    <dl>
      <div><dt>{t("Skill key", "Skill 标识")}</dt><dd><code>{sk["key"]}</code></dd></div>
      <div><dt>{t("Type", "类型")}</dt><dd class="k-{sk["kind"]}">{skill_kind(sk)}</dd></div>
      <div><dt>{t("Switched on", "开启方式")}</dt><dd>{t("Per account, off at first", "按账号，默认关闭") if sk["kind"] != "always" else t("With the MCP server", "随 MCP 接口")}</dd></div>
      <div><dt>{t("Works on", "可用于")}</dt><dd>{t("Local and cloud", "本机和云端")}</dd></div>
      <div><dt>{t("Needs", "需要")}</dt><dd>{t("Luckgram Desktop for Windows", "Windows 版 Luckgram 桌面版")}</dd></div>
      {limit_facts}
    </dl>
    <a class="btn primary" href="{u("/mcp/")}#start">{t("Set up Luckgram MCP", "开始配置 Luckgram MCP")}</a>
  </aside>
</div>
{doc_script()}"""
    page(here, t(f"{sk['name'][0]} – Luckgram Skill", f"{sk['name'][1]} – Luckgram Skill"),
         plain(t(*sk["tagline"]) + " " + t(*sk["about"])), body, "skills", crumb=name)


def not_found():
    """GitHub Pages serves this one page for every address that does not exist, in any language."""
    links = "".join(f'<li><a href="{u("/", c)}" hreflang="{tag(c)}" lang="{tag(c)}">{LANGUAGES[c][2]}</a></li>' for c in LANGS)
    body = f"""<article class="prose">
<h1>{t("Page not found", "页面不存在")}</h1>
<p>{t(f'This page does not exist. Go to the <a href="{u("/")}">home page</a> or the <a href="{u("/download/")}">downloads</a>.',
      f'这个页面不存在。去<a href="{u("/")}">首页</a>或<a href="{u("/download/")}">下载页</a>看看吧。')}</p>
<ul class="langs-list">{links}</ul>
</article>"""
    page("/404.html", t("Page not found – Luckgram", "页面不存在 – Luckgram"), t("Page not found.", "页面不存在。"), body, langs=[LANG], index=False)


def redirect(path, target):
    out = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(f"""<!doctype html>
<html lang="{tag()}"><head><meta charset="utf-8">
<title>Luckgram</title>
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url={target}">
<link rel="canonical" href="{target}">
</head><body><p><a href="{target}">{target}</a></p></body></html>
""")


def write(path, text):
    with open(os.path.join(ROOT, path), "w", encoding="utf-8") as f:
        f.write(text)


def sitemap():
    """Every indexable page in every language it exists in, each naming the others (hreflang)."""
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for here, langs in PAGES:
        alternates = "".join(f'<xhtml:link rel="alternate" hreflang="{tag(c)}" href="{SITE}{u(here, c)}"/>' for c in langs)
        alternates += f'<xhtml:link rel="alternate" hreflang="x-default" href="{SITE}{u(here, X_DEFAULT)}"/>'
        for c in langs:
            out.append(f"<url><loc>{SITE}{u(here, c)}</loc><lastmod>{MODIFIED}</lastmod>{alternates}</url>")
    out.append("</urlset>")
    write("sitemap.xml", "\n".join(out) + "\n")


def robots():
    write("robots.txt", f"""# luckgram.cc: everything here is public and may be read by search engines and AI assistants.
User-agent: *
Allow: /

Sitemap: {SITE}/sitemap.xml
""")


def llms():
    """llms.txt: the site in plain Markdown for AI assistants, from the same texts as the pages (English)."""
    global LANG
    LANG = "en"
    groups = feature_groups()
    lines = ["# Luckgram", "",
             "> Luckgram is an independent, open-source Telegram client for iPhone, iPad, Android and Windows. People sign in with their existing Telegram account and get everything Telegram has, plus extras such as more accounts in one app, hidden chats, free translation and AI tools. Luckgram is not made by, affiliated with, or endorsed by Telegram.", "",
             "## Facts", ""]
    lines += [f"- {k}: {plain(v)}" for k, v in facts()]
    lines += [f"- Languages of this website: {', '.join(LANGUAGES[c][2] for c in LANGS)}",
              "- Contact: support@luckgram.cc", "",
              "## Pages", "",
              f"- [Home]({SITE}/en/): what Luckgram is and what it adds to Telegram",
              f"- [Download]({SITE}/en/download/): the latest builds for Android (APK), iPhone and iPad (IPA or direct install) and Windows",
              f"- [Features]({SITE}/en/features/): every feature Luckgram adds, with its status",
              f"- [Help Center]({WIKI_HOST}/en/): installation, accounts and a guide to each feature",
              f"- [Luckgram MCP]({SITE}/en/mcp/): the MCP server built into Luckgram Desktop - setup, connecting Claude Code, Kiro, Codex and opencode, the cloud, security",
              f"- [Skill market]({SITE}/en/skills/): what an AI tool may do with each Telegram account - " + ", ".join(sk["name"][0] for sk in SKILLS),
              f"- [Privacy Policy]({SITE}/en/privacy-policy/)",
              f"- [Terms of Use]({SITE}/en/terms-of-use/)",
              f"- [Full text for AI assistants]({SITE}/llms-full.txt)", "",
              "## Source code", "", f"- [Luckgram for iOS]({IOS_REPO})", f"- [Luckgram for Android]({ANDROID_REPO})", ""]
    write("llms.txt", "\n".join(lines))
    full = lines[:lines.index("## Pages")]
    full += ["## What works from Telegram", ""] + [f"- {a}: {plain(d)}" for a, d in available()] + [""]
    full += ["## Features Luckgram adds", "",
             "Status: Available = free for everyone; Pro = needs Luckgram Pro; In development = not released yet.", ""]
    for group, items in groups:
        full += [f"### {group[0]}", ""]
        for slug, short, title, (_, label), body, help_path, _, web in items:
            full += [f"- {title[0]} ({label[0]}). {plain(body[0])}{' Also in the web app (web.luckgram.cc).' if web else ''} More: {WIKI_HOST}/en{help_path}"]
        full += [""]
    full += ["## Questions and answers", ""]
    for q, a in faq():
        full += [f"### {plain(q)}", "", plain(a), ""]
    write("llms-full.txt", "\n".join(full))


def export():
    """locales/source.json: every text there is to translate, English -> Chinese."""
    os.makedirs(LOCALES_DIR, exist_ok=True)
    with open(os.path.join(LOCALES_DIR, "source.json"), "w", encoding="utf-8") as f:
        json.dump(SOURCE, f, ensure_ascii=False, indent=1)
        f.write("\n")


if __name__ == "__main__":
    load_catalogs()
    for LANG in LANGS:
        home()
        download()
        features()
        mcp()
        skills()
        for skill in SKILLS:
            skill_page(skill)
        if LANG in LEGAL_LANGS:
            RECORD = False
            privacy()
            terms()
            RECORD = True
        if LANG == "zh":
            not_found()
        # Paths referenced by the Help Center.
        redirect((prefix() + "/faq/index.html").lstrip("/"), wiki("/help/"))
        redirect((prefix() + "/hub/index.html").lstrip("/"), wiki("/features/ai.html"))
    sitemap()
    robots()
    llms()
    if "--export" in sys.argv:
        export()
    for code, texts in sorted(MISSING.items()):
        print(f"{code}: {len(texts)} texts are not translated and are shown in English")
        if "--missing" in sys.argv:
            for text in sorted(texts):
                print("   ", text[:110])
    print(f"built {len(LANGS)} languages: {', '.join(LANGS)}")
    if MISSING and "--strict" in sys.argv:
        sys.exit(1)
