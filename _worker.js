const verificationPath = "/google939576fea7c9232c.html";
const verificationContent = "google-site-verification: google939576fea7c9232c.html\n";

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === verificationPath) {
      return new Response(verificationContent, {
        status: 200,
        headers: {
          "content-type": "text/html; charset=UTF-8",
          "cache-control": "no-store"
        }
      });
    }
    return env.ASSETS.fetch(request);
  }
};
