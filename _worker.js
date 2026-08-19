const verificationPath = "/google939576fea7c9232c.html";
const verificationContent = "google-site-verification: google939576fea7c9232c.html\n";
const bingVerificationPath = "/BingSiteAuth.xml";
const bingVerificationContent = "<?xml version=\"1.0\"?>\n<users>\n\t<user>DC4AB582C527A7A168FC391B84B8995E</user>\n</users>\n";
const indexNowPath = "/8533992191f84fd89569e65989a804c7.txt";
const indexNowContent = "8533992191f84fd89569e65989a804c7\n";

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
    if (url.pathname === bingVerificationPath) {
      return new Response(bingVerificationContent, {
        status: 200,
        headers: {
          "content-type": "application/xml; charset=UTF-8",
          "cache-control": "no-store"
        }
      });
    }
    if (url.pathname === indexNowPath) {
      return new Response(indexNowContent, {
        status: 200,
        headers: {
          "content-type": "text/plain; charset=UTF-8",
          "cache-control": "no-store"
        }
      });
    }
    return env.ASSETS.fetch(request);
  }
};
