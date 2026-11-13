// node --test edge/mirror-worker.test.mjs   (Node 22+)
import { test } from "node:test";
import assert from "node:assert/strict";
import { mirrorURL, mirrorRefresh, MIRRORS } from "./mirror-worker.js";

test("main hosts map to their mirrors", () => {
  for (const [from, to] of [
    ["https://luckgram.cc/", "https://lg-www.cat158.com/"],
    ["https://luckgram.cc", "https://lg-www.cat158.com"],
    ["https://www.luckgram.cc/features/", "https://lg-www.cat158.com/features/"],
    ["http://wiki.luckgram.cc/getting-started/install.html", "https://lg-wiki.cat158.com/getting-started/install.html"],
    ["//wiki.luckgram.cc/en/#faq", "https://lg-wiki.cat158.com/en/#faq"],
    ["https://luckgram.cc/#faq", "https://lg-www.cat158.com/#faq"],
    ["https://luckgram.cc?x=1", "https://lg-www.cat158.com?x=1"],
    ["https://DL.luckgram.cc/android/android-13.0.3-383/luckgram-13.0.3-arm64-v8a.apk",
     "https://lg-dl.cat158.com/android/android-13.0.3-383/luckgram-13.0.3-arm64-v8a.apk"],
    ["https://web.luckgram.cc/", "https://lgweb.cat158.com/"],
  ]) assert.equal(mirrorURL(from), to, from);
});

test("everything else is left alone", () => {
  for (const s of [
    "/download/", "features/", "#faq", "", "mailto:support@luckgram.cc",
    "https://web-dev.luckgram.cc/", "https://api.luckgram.cc/v1/health",
    "https://luckgram.cc.evil.example/", "https://example-luckgram.cc/", "https://luckgram.cc:8443/",
    "https://github.com/limeng9088/luckgram-ios", "https://luckgram.evztet.cn/yx6sv23c",
  ]) assert.equal(mirrorURL(s), s, s);
});

test("meta refresh", () => {
  assert.equal(mirrorRefresh("0; url=https://luckgram.cc/en/"), "0; url=https://lg-www.cat158.com/en/");
  assert.equal(mirrorRefresh("0;URL='https://wiki.luckgram.cc/x'"), "0;URL='https://lg-wiki.cat158.com/x'");
  assert.equal(mirrorRefresh("0; url=/en/"), "0; url=/en/");
  assert.equal(mirrorRefresh("5"), "5");
});

test("mirror list", () => {
  assert.deepEqual(MIRRORS, {
    "lg-www.cat158.com": "luckgram.cc",
    "lg-wiki.cat158.com": "wiki.luckgram.cc",
    "lg-dl.cat158.com": "dl.luckgram.cc",
  });
});
