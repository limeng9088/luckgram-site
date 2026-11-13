// Mirror domains under cat158.com for networks that block luckgram.cc by name
// (luckgram-specs#160). Each mirror proxies its main host, so content updates
// on the main site show up here with no extra step:
//   lg-www.cat158.com  -> luckgram.cc        (GitHub Pages)
//   lg-wiki.cat158.com -> wiki.luckgram.cc   (GitHub Pages)
//   lg-dl.cat158.com   -> dl.luckgram.cc     (edge/dl-worker.js; same bytes, Range works)
// HTML gets its absolute luckgram.cc links (and redirects) pointed at the mirrors,
// keeps or gains a canonical link to the main host, and every response carries
// X-Robots-Tag: noindex so search engines index only the main domain.
// No bindings or secrets.

export const MIRRORS = {
  "lg-www.cat158.com": "luckgram.cc",
  "lg-wiki.cat158.com": "wiki.luckgram.cc",
  "lg-dl.cat158.com": "dl.luckgram.cc",
};
// Links-only: hosts with a backup entrance of their own that this Worker does not proxy.
// web.luckgram.cc is Cloudflare Pages project luckgram-web, which also answers on
// lgweb.cat158.com (luckgram-web release.yml; its relay and API backups are lgws/lg.cat158.com).
const TO_MIRROR = { "www.luckgram.cc": "lg-www.cat158.com", "web.luckgram.cc": "lgweb.cat158.com" };
for (const [m, h] of Object.entries(MIRRORS)) TO_MIRROR[h] = m;

// Request headers passed to the main host (everything else, cookies included, is dropped).
const PASS = ["Accept", "Accept-Language", "User-Agent", "Range", "If-Range", "If-None-Match", "If-Modified-Since"];

// mirrorURL points an absolute (or protocol-relative) URL on a main host at its mirror;
// anything else (relative paths, other hosts, mailto:) is returned unchanged.
export function mirrorURL(s) {
  const m = /^\s*(?:https?:)?\/\/([^/?#:\s]+)(?=[/?#]|\s*$)/i.exec(s);
  if (!m) return s;
  const host = TO_MIRROR[m[1].toLowerCase()];
  return host ? "https://" + host + s.slice(m[0].length) : s;
}

// mirrorRefresh rewrites the URL in a <meta http-equiv="refresh" content="0; url=…">.
export function mirrorRefresh(s) {
  return s.replace(/(url\s*=\s*['"]?)([^'"\s]+)/i, (_, pre, u) => pre + mirrorURL(u));
}

const ATTRS = [
  ["a[href], area[href]", "href"],
  ["img[src], script[src], iframe[src], embed[src], track[src], audio[src], video[src], source[src]", "src"],
  ["source[data-src]", "data-src"],
  ["video[poster]", "poster"],
  ["form[action]", "action"],
];

class Attr {
  constructor(name) { this.name = name; }
  element(el) {
    const v = el.getAttribute(this.name);
    const w = mirrorURL(v);
    if (w !== v) el.setAttribute(this.name, w);
  }
}

function rewriter(canonical) {
  let hasCanonical = false;
  const r = new HTMLRewriter();
  for (const [sel, name] of ATTRS) r.on(sel, new Attr(name));
  return r
    .on("link[href]", {
      element(el) {
        const rel = (el.getAttribute("rel") || "").toLowerCase().split(/\s+/);
        // canonical and hreflang alternates must keep naming the main host.
        if (rel.includes("canonical")) { hasCanonical = true; return; }
        if (rel.includes("alternate")) return;
        const v = el.getAttribute("href"), w = mirrorURL(v);
        if (w !== v) el.setAttribute("href", w);
      },
    })
    .on("meta[http-equiv]", {
      element(el) {
        if ((el.getAttribute("http-equiv") || "").toLowerCase() !== "refresh") return;
        el.setAttribute("content", mirrorRefresh(el.getAttribute("content") || ""));
      },
    })
    .on("head", {
      element(el) {
        el.onEndTag((end) => {
          if (!hasCanonical) end.before(`<link rel="canonical" href="${canonical.replace(/"/g, "&quot;")}">`, { html: true });
        });
      },
    });
}

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const main = MIRRORS[url.hostname];
    if (!main) return new Response("Not found", { status: 404 });
    if (request.method !== "GET" && request.method !== "HEAD") {
      return new Response("Method not allowed", { status: 405, headers: { Allow: "GET, HEAD" } });
    }
    const headers = new Headers();
    for (const h of PASS) {
      const v = request.headers.get(h);
      if (v) headers.set(h, v);
    }
    const res = await fetch("https://" + main + url.pathname + url.search, {
      method: request.method, headers, redirect: "manual",
    });

    let out = new Response(res.body, res);
    const type = out.headers.get("Content-Type") || "";
    if (main !== "dl.luckgram.cc" && res.status === 200 && request.method === "GET" && type.startsWith("text/html")) {
      out = rewriter("https://" + main + url.pathname).transform(out);
      // Same upstream bytes give the same output, but they are no longer the upstream bytes.
      const etag = out.headers.get("ETag");
      if (etag && !etag.startsWith("W/")) out.headers.set("ETag", "W/" + etag);
    }
    const loc = out.headers.get("Location");
    if (loc) out.headers.set("Location", mirrorURL(loc));
    out.headers.set("X-Robots-Tag", "noindex");
    return out;
  },
};
