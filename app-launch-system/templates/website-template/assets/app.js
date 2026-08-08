document.documentElement.classList.add("js");

for (const link of document.querySelectorAll('a[href^="#"]')) {
  link.addEventListener("click", () => {
    const target = document.querySelector(link.getAttribute("href"));
    if (target) target.setAttribute("tabindex", "-1");
  });
}
