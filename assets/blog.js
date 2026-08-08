document.documentElement.classList.add("js");

const progress = document.querySelector(".reading-progress span");
const article = document.querySelector("main article");

if (progress && article) {
  const updateProgress = () => {
    const start = article.offsetTop;
    const distance = Math.max(article.offsetHeight - window.innerHeight, 1);
    const value = Math.min(Math.max((window.scrollY - start) / distance, 0), 1);
    progress.style.width = `${value * 100}%`;
  };

  updateProgress();
  window.addEventListener("scroll", updateProgress, { passive: true });
  window.addEventListener("resize", updateProgress);
}

const tocLinks = [...document.querySelectorAll('.article-toc a[href^="#"]')];
const sections = tocLinks
  .map((link) => document.querySelector(link.getAttribute("href")))
  .filter(Boolean);

if (tocLinks.length && sections.length && "IntersectionObserver" in window) {
  const linksById = new Map(
    tocLinks.map((link) => [link.getAttribute("href").slice(1), link]),
  );
  const observer = new IntersectionObserver(
    (entries) => {
      const current = entries.find((entry) => entry.isIntersecting);
      if (!current) return;
      for (const link of tocLinks) link.removeAttribute("aria-current");
      linksById.get(current.target.id)?.setAttribute("aria-current", "true");
    },
    { rootMargin: "-15% 0px -70%", threshold: 0 },
  );
  for (const section of sections) observer.observe(section);
}
