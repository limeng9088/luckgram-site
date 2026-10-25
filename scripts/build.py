#!/usr/bin/env python3
"""Render the static pages of luckgram.cc in Chinese (default, at /) and English (at /en/).
Every piece of copy is written as t("English", "中文"). Edit the page bodies here, then run:
    python3 scripts/build.py
"""
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


def t(en, zh):
    return zh if LANG == "zh" else en


def u(path):
    """Site path in the current language: /download/ -> /en/download/ for English."""
    return path if LANG == "zh" else "/en" + path


def wiki(path="/"):
    """Help Center link in the current language (Chinese at /, English at /en/)."""
    return WIKI_HOST + (path if LANG == "zh" else "/en" + path)


def header(current, here):
    def link(href, label, key, cls=""):
        cur = ' aria-current="page"' if key == current else ""
        c = f' class="{cls}"' if cls else ""
        return f'<a href="{href}"{c}{cur}>{label}</a>'
    other = ("/en" + here) if LANG == "zh" else here
    switch = f'<a class="lang" href="{other}" hreflang="{"en" if LANG == "zh" else "zh-CN"}" lang="{"en" if LANG == "zh" else "zh-CN"}">{"EN" if LANG == "zh" else "中文"}</a>'
    return f'''<header class="site-header">
  <div class="wrap">
    <a class="logo" href="{u("/")}"><img src="/assets/icon-512.png" alt="" width="30" height="30"><span>Luckgram</span></a>
    <nav class="nav">
      {link(u("/features/"), t("Features", "功能"), "features")}
      {link(u("/download/"), t("Download", "下载"), "download")}
      {link(wiki(), t("Help", "帮助"), "help")}
      {link(u("/#faq"), t("FAQ", "常见问题"), "faq", "opt")}
      {switch}
    </nav>
  </div>
</header>'''


def footer():
    return f'''<footer class="site-footer">
  <div class="wrap">
    <div class="cols">
      <div><h4>Luckgram</h4><ul>
        <li><a href="{u("/download/")}">{t("Download", "下载")}</a></li>
        <li><a href="{u("/features/")}">{t("Features", "功能")}</a></li>
        <li><a href="{wiki()}">{t("Help Center", "帮助中心")}</a></li>
      </ul></div>
      <div><h4>{t("Source code", "源代码")}</h4><ul>
        <li><a href="{IOS_REPO}">{t("Luckgram for iOS", "Luckgram iOS 版")}</a></li>
        <li><a href="{ANDROID_REPO}">{t("Luckgram for Android", "Luckgram Android 版")}</a></li>
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
    <p class="disclaimer">{t("Luckgram is an independent app based on the open-source Telegram apps. It is not made by, affiliated with, or endorsed by Telegram. Telegram is a trademark of Telegram FZ-LLC.",
                             "Luckgram 是基于开源 Telegram 应用开发的独立应用，并非由 Telegram 制作，与 Telegram 没有关联，也未获其认可。Telegram 是 Telegram FZ-LLC 的商标。")}</p>
    <p>&copy; 2026 Luckgram</p>
  </div>
</footer>'''


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
<link rel="icon" href="/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="stylesheet" href="/assets/site.css">
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


def in_development():
    return [t(*x) for x in [
        ("More accounts in one app", "一个应用登录更多账号"), ("Account backup and transfer", "账号备份与迁移"),
        ("Double Bottom", "双重空间（Double Bottom）"), ("Hidden chats", "隐藏聊天"), ("Quick replies", "快捷回复"),
        ("Outgoing translation", "发送前翻译"), ("Free speech-to-text", "免费语音转文字"), ("Call recording", "通话录音"),
        ("Gallery video as round message", "相册视频转圆形视频消息"), ("Keyword folders", "关键词文件夹"),
        ("Show Telegram ID", "显示 Telegram ID"), ("AI Assistant", "AI 助手")]]


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


def home():
    cards = "\n".join(
        f'<div class="card"><span class="tag ok">{t("Available", "已上线")}</span><h3>{a}</h3><p>{d}</p></div>'
        for a, d in available())
    wip = "\n".join(f'<li>{x}<span class="tag wip">{t("In development", "开发中")}</span></li>' for x in in_development())
    qa = "\n".join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in faq())
    body = f'''<section class="hero">
  <div class="wrap">
    <div>
      <p class="eyebrow">{t("Independent Telegram client", "独立的 Telegram 客户端")}</p>
      <h1>{t("Luckgram: your Telegram, in a new app", "Luckgram：你的 Telegram，换一个新应用")}</h1>
      <p class="lede">{t("Luckgram is built on the open-source Telegram apps for iOS and Android. Sign in with your Telegram account and everything works as you know it. More tools are on the way.",
                         "Luckgram 基于开源的 Telegram iOS 和 Android 应用开发。用你的 Telegram 账号登录，一切用法照旧，更多工具正在路上。")}</p>
      <div class="btns">
        <a class="btn primary" href="{u("/download/")}">{t("Download Luckgram", "下载 Luckgram")}</a>
        <a class="btn" href="{u("/features/")}">{t("See the features", "查看功能")}</a>
      </div>
    </div>
    <div class="hero-art"><img src="/assets/icon-512.png" alt="{t("Luckgram app icon", "Luckgram 应用图标")}" width="512" height="512"></div>
  </div>
</section>

<section class="block" id="features">
  <div class="wrap">
    <h2>{t("What works today", "现在就能用")}</h2>
    <p class="sub">{t("Luckgram connects to the Telegram network, so the Telegram features you already use are all here.",
                      "Luckgram 连接的是 Telegram 网络，你平时用的 Telegram 功能这里都有。")}</p>
    <div class="grid">
{cards}
    </div>
  </div>
</section>

<section class="block">
  <div class="wrap">
    <h2>{t("In development", "开发中")}</h2>
    <p class="sub">{t("These Luckgram additions are being built. They are not in the app yet, and no release dates are promised.",
                      "这些是 Luckgram 正在开发的新功能，目前还没有加入应用，我们也不承诺上线时间。")}</p>
    <ul class="list-wip">
{wip}
    </ul>
    <p class="more"><a href="{u("/features/")}">{t("See every feature and its status &rarr;", "查看全部功能及状态 &rarr;")}</a></p>
  </div>
</section>

<section class="block">
  <div class="wrap">
    <h2>{t("Open source and transparent", "开源透明")}</h2>
    <p class="sub">{t("The complete source code for both apps is public, and every release is built by GitHub Actions from that code.",
                      "两个应用的完整源代码都已公开，每个版本都由 GitHub Actions 从这些代码构建。")}</p>
    <div class="grid">
      <div class="card"><h3>{t("Public source code", "公开的源代码")}</h3><p>{t(f'Read the code for <a href="{IOS_REPO}">iOS</a> and <a href="{ANDROID_REPO}">Android</a> on GitHub.', f'在 GitHub 上查看 <a href="{IOS_REPO}">iOS</a> 和 <a href="{ANDROID_REPO}">Android</a> 的代码。')}</p></div>
      <div class="card"><h3>{t("No Luckgram message servers", "没有 Luckgram 自己的消息服务器")}</h3><p>{t("Your messages go to Telegram's servers, as they would from any Telegram app. Luckgram does not run its own servers for them.", "你的消息和在任何 Telegram 应用里一样，发送到 Telegram 的服务器。Luckgram 不为消息设立自己的服务器。")}</p></div>
      <div class="card"><h3>{t("No added trackers", "不加追踪")}</h3><p>{t("Luckgram does not add analytics or advertising SDKs to the apps.", "Luckgram 没有在应用里加入任何统计或广告 SDK。")}</p></div>
    </div>
  </div>
</section>

<section class="block" id="download">
  <div class="wrap">
    <h2>{t("Get Luckgram", "获取 Luckgram")}</h2>
    <p class="sub">{t("Free for iOS and Android.", "iOS 和 Android 均可免费使用。")}</p>
    <div class="btns">
      <a class="btn primary" href="{u("/download/")}">{t("Go to downloads", "前往下载")}</a>
      <a class="btn" href="{wiki("/getting-started/install.html")}">{t("Install guide", "安装指南")}</a>
    </div>
  </div>
</section>

<section class="block" id="faq">
  <div class="wrap">
    <h2>{t("Frequently asked questions", "常见问题")}</h2>
    <p class="sub">{t(f'More answers in the <a href="{wiki()}">Help Center</a>.', f'更多解答请看<a href="{wiki()}">帮助中心</a>。')}</p>
{qa}
  </div>
</section>'''
    page("/", t("Luckgram – an independent Telegram client for iOS and Android", "Luckgram – 独立的 iOS 和 Android Telegram 客户端"),
         t("Luckgram is an independent, open-source Telegram client for iOS and Android. Sign in with your Telegram account and keep everything you use today.",
           "Luckgram 是独立、开源的 iOS 和 Android Telegram 客户端。用你的 Telegram 账号登录，现在用的一切都还在。"),
         body)


def download():
    body = f'''<section class="hero" style="padding-bottom:32px">
  <div class="wrap" style="grid-template-columns:1fr">
    <div>
      <p class="eyebrow">{t("Download", "下载")}</p>
      <h1>{t("Get Luckgram", "获取 Luckgram")}</h1>
      <p class="lede">{t("Luckgram is distributed through GitHub Releases. These links always open the latest build.",
                         "Luckgram 通过 GitHub Releases 发布，下面的链接始终指向最新版本。")}</p>
    </div>
  </div>
</section>
<section class="block" style="border-top:0;padding-top:0">
  <div class="wrap">
    <div class="dl">
      <div class="card">
        <h3>Android</h3>
        <ul>
          <li>{t("Signed APK for 64-bit ARM phones (arm64-v8a)", "已签名的 APK，适用于 64 位 ARM 手机（arm64-v8a）")}</li>
          <li>{t("Android 6.0 or later", "Android 6.0 及以上")}</li>
          <li>{t("Allow installs from your browser or file manager when asked", "安装时如有提示，请允许浏览器或文件管理器安装应用")}</li>
        </ul>
        <div class="btns"><a class="btn primary" href="{ANDROID_LATEST}">{t("Download APK", "下载 APK")}</a></div>
      </div>
      <div class="card">
        <h3>{t("iPhone and iPad", "iPhone 和 iPad")}</h3>
        <ul>
          <li>{t("Unsigned IPA", "未签名的 IPA")}</li>
          <li>{t("Sign it with Sideloadly, AltStore or your own certificate before installing", "安装前先用 Sideloadly、AltStore 或你自己的证书签名")}</li>
          <li>{t("iOS 15 or later", "iOS 15 及以上")}</li>
        </ul>
        <div class="btns"><a class="btn primary" href="{IOS_LATEST}">{t("Download IPA", "下载 IPA")}</a><a class="btn" href="{wiki("/getting-started/install.html")}">{t("Install guide", "安装指南")}</a></div>
      </div>
    </div>
    <p class="note" style="margin-top:24px">{t("If you previously installed a test build of Luckgram on Android, uninstall it first: builds signed with a different key cannot update each other. Only download Luckgram from this page or the GitHub repositories it links to.",
                                               "如果你之前在 Android 上装过 Luckgram 的测试版，请先卸载：签名密钥不同的版本不能相互覆盖升级。请只从本页或本页链接的 GitHub 仓库下载 Luckgram。")}</p>
  </div>
</section>'''
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
OK_TG = ("ok", ("Available · Telegram", "已上线 · Telegram 功能"))


# Feature page: (slug, short name, title, status, body, help path); text pairs are (English, Chinese)
def feature_groups():
    return [
    (("Accounts and privacy", "账号与隐私"), [
        ("accounts", ("More accounts", "更多账号"), ("More accounts in one app", "一个应用登录更多账号"), WIP,
         ("Today Luckgram follows Telegram's standard limit for accounts on one device. We are making room for many more, "
          "so personal, work and community accounts can sit side by side and you switch between them from Settings.",
          "目前 Luckgram 在一台设备上可登录的账号数与 Telegram 官方一致。我们正在让它容纳更多账号，"
          "个人、工作和社群账号可以并排放着，在设置里一点就能切换。"),
         "/getting-started/accounts.html"),
        ("backup", ("Account backup", "账号备份"), ("Back up your accounts and move them to a new phone", "备份账号，换手机时一起带走"), WIP,
         ("Choose the accounts you want and save them to one encrypted backup file. Restore it on a new phone or after "
          "reinstalling, without signing in to each account again.",
          "选择要备份的账号，保存成一个加密的备份文件。换新手机或重装应用后用它恢复，不用再逐个登录。"),
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
        ("voice-text", ("Voice to text", "语音转文字"), ("Read voice messages instead of playing them", "语音消息不用听，直接看"),
         ("part", ("Telegram Premium · free version in development", "Telegram Premium 功能 · 免费版开发中")),
         ("Turn a voice message into text with one tap, handy in a meeting or on a noisy train. Telegram offers this "
          "with Premium; a free version for Luckgram is being built.",
          "一点就把语音消息转成文字，开会时、在嘈杂的地铁上都方便。Telegram 的这个功能需要 Premium，Luckgram 正在开发免费版。"),
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
         ("Long-press a message and select everything that person wrote in the chat at once, ready to forward or delete.",
          "长按一条消息，就能一次选中这个人在聊天里发的所有消息，方便转发或删除。"),
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
        ("call-rec", ("Call recording", "通话录音"), ("Record calls and keep them in Saved Messages", "通话录音，自动存到收藏夹"), WIP,
         ("Record a call with one tap and find the recording in Saved Messages when you hang up. Recording laws differ "
          "by country; let the other person know before you record.",
          "一点就能录下通话，挂断后在收藏夹里找到录音。各国对录音的法律规定不同，录音前请先告知对方。"),
         "/features/media-and-calls.html"),
        ("cache", ("Storage", "存储空间"), ("See what takes up space and clear it", "看清空间被谁占用，按需清理"),
         ("part", ("Available · extra controls in development", "已上线 · 更多设置开发中")),
         ("Storage Usage shows how much space videos, photos, files and music take on your phone, and you clear the "
          "types you choose. More control over what is kept and for how long is on the way.",
          "“存储空间”会显示视频、照片、文件和音乐各占多少空间，你可以按类型清理。对保留哪些内容、保留多久的更多设置正在开发。"),
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
    ]),
    (("AI", "AI"), [
        ("ai-chat", ("AI assistant", "AI 助手"), ("An AI assistant inside your chats", "聊天里的 AI 助手"), WIP,
         ("Ask a question, get a topic explained, have a text rewritten or a problem worked through, in a chat like any "
          "other.",
          "像平常聊天一样提问：让它讲解一个话题、改写一段文字，或者一步步解一道题。"),
         "/features/ai.html"),
        ("ai-summary", ("Chat summary", "聊天总结"), ("Catch up on a busy chat with a summary", "用总结快速跟上热闹的群聊"), WIP,
         ("Coming back to hundreds of unread messages? Get the decisions, dates and open questions in a few lines "
          "before you scroll.",
          "回来发现几百条未读？先用几行字看清结论、日期和待解决的问题，再决定要不要往上翻。"),
         "/features/ai.html"),
        ("ai-reply", ("Reply drafts", "AI 回复"), ("Turn rough notes into a reply", "把随手写的几个字变成得体的回复"), WIP,
         ("Type what you mean, however quickly, and choose from polished replies that fit the conversation. Edit "
          "the one you pick before you send it.",
          "随手打下你想说的意思，从几条贴合对话的润色回复里挑一条，发送前还可以再改。"),
         "/features/ai.html"),
    ]),
    ]


def features():
    toc, sections = [], []
    sfx = "" if LANG == "en" else "-zh"   # Chinese pages use the videos with Chinese titles
    for group, items in feature_groups():
        toc.append(f'<li class="toc-group">{t(*group)}</li>')
        for slug, short, title, (key, label), body, help_path in items:
            title = t(*title)
            toc.append(f'<li><a href="#{slug}">{t(*short)}</a></li>')
            sections.append(f'''<section class="feat" id="{slug}">
  <video class="feat-video" muted loop playsinline preload="none" poster="/media/features/{slug}{sfx}.jpg" width="848" height="848" aria-label="{t("Animation", "演示动画")}: {title}">
    <source data-src="/media/features/{slug}{sfx}.webm" type="video/webm">
    <source data-src="/media/features/{slug}{sfx}.mp4" type="video/mp4">
  </video>
  <div class="feat-text">
    <span class="tag {key}">{t(*label)}</span>
    <h2>{title}</h2>
    <p>{t(*body)}</p>
    <p class="feat-more"><a href="{wiki(help_path)}">{t("Learn more in the Help Center &rarr;", "在帮助中心了解更多 &rarr;")}</a></p>
  </div>
</section>''')
    body = f'''<section class="feat-hero">
  <div class="wrap">
    <h1>{t("Luckgram features", "Luckgram 功能")}</h1>
    <p class="lede">{t("Everything you use in Telegram already works in Luckgram. Below are the extras we add, each marked with where it stands today. Features in development are not in the app yet, and no release dates are promised.",
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
<section class="block">
  <div class="wrap">
    <h2>{t("Built on Telegram, open to everyone", "基于 Telegram，向所有人开放")}</h2>
    <div class="grid">
      <div class="card"><h3>{t("The Telegram network", "Telegram 网络")}</h3><p>{t("Luckgram signs in to your Telegram account and follows Telegram's updates, so chats, channels, calls and bots work as you expect.", "Luckgram 登录的是你的 Telegram 账号，并跟进 Telegram 的更新，聊天、频道、通话和机器人都照常可用。")}</p></div>
      <div class="card"><h3>{t("Your messages stay with Telegram", "消息只在 Telegram")}</h3><p>{t("Messages are sent to and stored on Telegram's servers. Luckgram runs no message servers of its own.", "消息发送到并保存在 Telegram 的服务器上。Luckgram 没有自己的消息服务器。")}</p></div>
      <div class="card"><h3>{t("Open source", "开源")}</h3><p>{t(f'The code for <a href="{IOS_REPO}">iOS</a> and <a href="{ANDROID_REPO}">Android</a> is public, and every release is built from it by GitHub Actions.', f'<a href="{IOS_REPO}">iOS</a> 和 <a href="{ANDROID_REPO}">Android</a> 的代码都已公开，每个版本都由 GitHub Actions 从这些代码构建。')}</p></div>
    </div>
    <div class="btns" style="margin-top:32px"><a class="btn primary" href="{u("/download/")}">{t("Download Luckgram", "下载 Luckgram")}</a><a class="btn" href="{wiki("/features/")}">{t("Full status in the Help Center", "在帮助中心查看完整状态")}</a></div>
  </div>
</section>
<script>
// Load and play each feature video only while it is on screen.
(function () {{
  var vids = document.querySelectorAll('.feat-video');
  function load(v) {{ if (v.dataset.loaded) return; v.querySelectorAll('source').forEach(function (s) {{ s.src = s.dataset.src; }}); v.load(); v.dataset.loaded = 1; }}
  if (!('IntersectionObserver' in window)) {{ vids.forEach(load); return; }}
  var io = new IntersectionObserver(function (es) {{
    es.forEach(function (e) {{ var v = e.target; if (e.isIntersecting) {{ load(v); var p = v.play(); if (p) p.catch(function () {{}}); }} else v.pause(); }});
  }}, {{rootMargin: '200px 0px'}});
  vids.forEach(function (v) {{ io.observe(v); }});
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
