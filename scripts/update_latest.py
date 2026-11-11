#!/usr/bin/env python3
"""Update download/latest.json after an app release (luckgram-specs#100).

Run by the iOS / Android CI (master only) after the GitHub release exists:

  python3 scripts/update_latest.py ios --repo limeng9088/luckgram-ios --tag ios-13.1.1-36129 \\
      --version 13.1.1 --build 36129 --commit fa7e35e --published-at 2026-11-03T06:33:10Z \\
      --file ipa=out/Luckgram-13.1.1-36129.ipa

  python3 scripts/update_latest.py android --repo limeng9088/luckgram-android --tag android-13.0.3-286 \\
      --version 13.0.3 --build 286 --commit 42470b9 --published-at ... \\
      --file arm64=out/luckgram-13.0.3-arm64-v8a.apk --file x86_64=out/luckgram-13.0.3-x86_64.apk

Only the given platform's entry is replaced; the other one is kept. With --url-base
(the CI passes https://dl.luckgram.cc after uploading the files there) URLs are
<url-base>/<platform>/<tag>/<file>; without it they are GitHub release-asset links. Prints "unchanged" when the file already has this release.
"""
import argparse, hashlib, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "download", "latest.json")


def asset(repo, tag, path, base=None, platform=None):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    name = os.path.basename(path)
    url = (f"{base.rstrip('/')}/{platform}/{tag}/{name}" if base
           else f"https://github.com/{repo}/releases/download/{tag}/{name}")
    return {"url": url,
            "sha256": h.hexdigest(), "size": os.path.getsize(path)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("platform", choices=["ios", "android"])
    for k in ("repo", "tag", "version", "build", "commit", "published-at"):
        ap.add_argument("--" + k, required=True)
    ap.add_argument("--url-base", help="download host the files were uploaded to, e.g. https://dl.luckgram.cc")
    ap.add_argument("--file", action="append", required=True, help="kind=path (ios: ipa; android: arm64, x86_64)")
    a = ap.parse_args()
    files = dict(f.split("=", 1) for f in a.file)

    entry = {"version": a.version, "build": int(a.build), "commit": a.commit[:7],
             "tag": a.tag, "published_at": a.published_at}
    if a.platform == "ios":
        entry.update(asset(a.repo, a.tag, files["ipa"], a.url_base, "ios"))
    else:
        if "arm64" not in files:
            sys.exit("android needs --file arm64=...")
        for kind in ("arm64", "x86_64"):
            if kind in files and os.path.exists(files[kind]):
                entry[kind] = asset(a.repo, a.tag, files[kind], a.url_base, "android")

    data = {}
    if os.path.exists(PATH):
        with open(PATH, encoding="utf-8") as f:
            data = json.load(f)
    old = data.get(a.platform)
    if old and int(old.get("build", 0)) > entry["build"]:
        print(f"skip: latest.json has a newer {a.platform} build ({old['build']} > {entry['build']})")
        return
    if old == entry:
        print("unchanged")
        return
    data[a.platform] = entry
    os.makedirs(os.path.dirname(PATH), exist_ok=True)
    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(dict(sorted(data.items())), f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"updated {a.platform}: {a.tag}")


if __name__ == "__main__":
    main()
