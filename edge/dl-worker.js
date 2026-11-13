// dl.luckgram.cc: app downloads served from Cloudflare's cache, origin is a private
// S3 bucket (aws-sg, ap-southeast-1). The bucket only answers requests that carry the
// ORIGIN_REFERER value (bucket policy), so files can't be pulled from S3 directly.
// Paths are versioned (/<platform>/<tag>/<file>) and never change, so they are cached
// for a year. Bindings: ORIGIN_BASE (plain text), ORIGIN_REFERER (secret).
const PATH = /^\/(android|ios|windows|macos)\/[A-Za-z0-9._-]+\/[A-Za-z0-9._-]+\.(apk|ipa|exe|zip|dmg)$/;
const TYPES = {
  apk: "application/vnd.android.package-archive", ipa: "application/octet-stream",
  exe: "application/vnd.microsoft.portable-executable", zip: "application/zip", dmg: "application/x-apple-diskimage",
};

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/" ) return Response.redirect("https://luckgram.cc/download/", 302);
    if (request.method !== "GET" && request.method !== "HEAD") return new Response("Method not allowed", { status: 405 });
    const m = url.pathname.match(PATH);
    if (!m) return new Response("Not found", { status: 404 });

    const headers = new Headers({ Referer: env.ORIGIN_REFERER });
    const range = request.headers.get("Range");
    if (range) headers.set("Range", range);
    const origin = await fetch(env.ORIGIN_BASE + url.pathname, {
      method: request.method, headers,
      cf: { cacheEverything: true, cacheTtl: 31536000, cacheTtlByStatus: { "200-299": 31536000, "400-599": 0 } },
    });
    if (origin.status === 403 || origin.status === 404) return new Response("Not found", { status: 404 });

    const out = new Response(origin.body, origin);
    for (const h of [...out.headers.keys()]) if (h.startsWith("x-amz-")) out.headers.delete(h);
    out.headers.set("Content-Type", TYPES[m[2]]);
    out.headers.set("Content-Disposition", `attachment; filename="${url.pathname.split("/").pop()}"`);
    out.headers.set("Cache-Control", "public, max-age=31536000, immutable");
    out.headers.set("Access-Control-Allow-Origin", "*");
    return out;
  },
};
