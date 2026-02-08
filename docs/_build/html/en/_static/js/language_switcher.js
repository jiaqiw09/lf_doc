document.addEventListener("DOMContentLoaded", function () {
  // Only inject if not already injected
  if (document.querySelector(".language-selector")) return;

  var navSearch = document.querySelector(".wy-side-nav-search");
  if (!navSearch) return;

  // Create container
  var langContainer = document.createElement("div");
  langContainer.className = "language-selector";
  langContainer.style.marginTop = "10px";
  langContainer.style.textAlign = "center";
  langContainer.style.color = "#d9d9d9";

  // Check current path
  var path = window.location.pathname;
  // Handle paths like /docs/_build/html/zh/index.html or /zh/index.html
  // We want to detect if we are in /zh/ or /en/
  
  // Normalize path to remove local dev prefixes if any, though usually relative links work best.
  // Strategy: 
  // 1. Determine if current page is 'zh' or 'en'
  // 2. Generate the other link by replacing the segment.

  var isZh = path.includes("/zh/");
  var isEn = path.includes("/en/");
  
  // If neither (e.g. root index.html redirect), do nothing
  if (!isZh && !isEn) return;

  // Create links
  var zhLink = document.createElement("a");
  zhLink.textContent = "中文";
  zhLink.style.margin = "0 10px";
  zhLink.style.color = isZh ? "#fff" : "#ccc";
  zhLink.style.fontWeight = isZh ? "bold" : "normal";
  zhLink.style.textDecoration = "none";
  zhLink.style.cursor = "pointer";

  var enLink = document.createElement("a");
  enLink.textContent = "English";
  enLink.style.margin = "0 10px";
  enLink.style.color = isEn ? "#fff" : "#ccc";
  enLink.style.fontWeight = isEn ? "bold" : "normal";
  enLink.style.textDecoration = "none";
  enLink.style.cursor = "pointer";

  // Build target URLs
  // Assumption: structure is .../zh/... and .../en/...
  var targetZh = path.replace("/en/", "/zh/");
  var targetEn = path.replace("/zh/", "/en/");

  zhLink.href = targetZh;
  enLink.href = targetEn;

  langContainer.appendChild(zhLink);
  langContainer.appendChild(document.createTextNode("|"));
  langContainer.appendChild(enLink);

  // Append to sidebar
  navSearch.appendChild(langContainer);
});
