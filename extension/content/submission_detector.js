/**
 * CodeSync Content Script for LeetCode Submission Detection
 * Detects successful submissions ("Accepted"), extracts source code, language,
 * submission ID, runtime, and memory metrics, and relays them to the background worker.
 */

// Track last processed submission ID and metrics to prevent redundant dispatches
let lastProcessedSubmissionId = null;
let lastProcessedRuntime = "N/A";
let lastProcessedMemory = "N/A";

/**
 * Normalizes programming language strings to standardized extensions keys.
 * @param {string} lang 
 * @returns {string|null}
 */
function normalizeLanguage(lang) {
  const clean = lang.toLowerCase().trim();
  if (clean.includes("python")) return "python";
  if (clean.includes("javascript") || clean === "js") return "javascript";
  if (clean.includes("typescript") || clean === "ts") return "typescript";
  if (clean === "java") return "java";
  if (clean === "c++" || clean === "cpp") return "cpp";
  if (clean === "c" && clean.length === 1) return "c";
  if (clean === "go" || clean === "golang") return "go";
  if (clean === "rust") return "rust";
  if (clean === "c#" || clean === "csharp") return "csharp";
  return null;
}

/**
 * Extracts language preference from page selectors.
 * @returns {string|null}
 */
function getLanguage() {
  const elements = document.querySelectorAll("div, span, p, h1, h2, h3, button, a");
  
  // 1. Try matching "Code | Language" pattern (common on submissions page)
  for (const el of elements) {
    const text = el.textContent.trim();
    const match = text.match(/Code\s*\|\s*([a-zA-Z0-9#\+\-]+)/i);
    if (match) {
      const norm = normalizeLanguage(match[1]);
      if (norm) return norm;
    }
  }

  // 2. Try matching specific lang selectors
  const selectors = [
    "button[id^='lang-select']",
    "[class*='lang-select']",
    ".ant-select-selection-item",
    "div.text-sm.font-medium"
  ];

  for (const sel of selectors) {
    const el = document.querySelector(sel);
    if (el) {
      const text = el.textContent.trim();
      const norm = normalizeLanguage(text);
      if (norm) return norm;
    }
  }

  // 3. Fallback: Search elements with short text content matching language names
  for (const el of elements) {
    const text = el.textContent.trim();
    if (text.length > 0 && text.length < 15) {
      const norm = normalizeLanguage(text);
      if (norm) return norm;
    }
  }
  return null;
}

/**
 * Extracts code from Monaco Editor view lines or textareas.
 * Preserves formatting, line breaks, and indentation.
 * @returns {string|null}
 */
function extractSourceCode() {
  // Method 1: Check Monaco DOM lines (textContent)
  const lines = Array.from(document.querySelectorAll(".view-line"));
  if (lines.length > 0) {
    const code = lines.map(line => line.textContent).join("\n");
    if (code && code.trim().length > 5) {
      return code;
    }
    
    // Method 2: Monaco DOM lines (innerText)
    const codeInner = lines.map(line => line.innerText).join("\n");
    if (codeInner && codeInner.trim().length > 5) {
      return codeInner;
    }
  }

  // Method 3: Fallback to general read-only view code blocks
  const codeEl = document.querySelector("pre, code, textarea.inputarea");
  if (codeEl) {
    const code = codeEl.value || codeEl.textContent || codeEl.innerText;
    if (code && code.trim().length > 5) {
      return code;
    }
  }

  return null;
}

/**
 * Identifies the unique submission ID and constructs its URL.
 * @returns {{id: string, url: string}|null}
 */
function getSubmissionDetails() {
  // 1. Check URL pathname
  const path = window.location.pathname;
  const urlMatch = path.match(/\/submissions\/(?:detail\/)?(\d+)/);
  if (urlMatch) {
    return {
      id: urlMatch[1],
      url: window.location.href
    };
  }

  // 2. Fallback: Parse visible detail link elements
  const detailLink = document.querySelector('a[href*="/submissions/"]');
  if (detailLink) {
    const href = detailLink.getAttribute("href");
    const hrefMatch = href.match(/\/submissions\/(?:detail\/)?(\d+)/);
    if (hrefMatch) {
      const absoluteUrl = href.startsWith("http") ? href : `${window.location.origin}${href}`;
      return {
        id: hrefMatch[1],
        url: absoluteUrl
      };
    }
  }

  return null;
}

function getMetrics() {
  let runtime = "";
  let memory = "";

  const elements = Array.from(document.querySelectorAll("span, div, p, label"));
  
  // 1. Search parent containers of "Runtime" and "Memory" labels
  for (const el of elements) {
    const text = el.textContent.trim();
    if (text.length > 0 && text.length < 15 && (/^runtime$/i.test(text) || text === "Runtime")) {
      const parent = el.parentElement;
      if (parent) {
        const match = parent.textContent.match(/(\d+(?:\.\d+)?\s*(?:ms|seconds|sec|s))/i);
        if (match) {
          runtime = match[1];
          break;
        }
      }
    }
  }

  for (const el of elements) {
    const text = el.textContent.trim();
    if (text.length > 0 && text.length < 15 && (/^memory$/i.test(text) || text === "Memory")) {
      const parent = el.parentElement;
      if (parent) {
        const match = parent.textContent.match(/(\d+(?:\.\d+)?\s*(?:mb|kb|gb))/i);
        if (match) {
          memory = match[1];
          break;
        }
      }
    }
  }

  // 2. Fallback: Parse matching regex patterns from body text content
  if (!runtime) {
    const match = document.body.textContent.match(/Runtime\s*[:\s]*(\d+(?:\.\d+)?\s*(?:ms|seconds|sec|s))/i);
    if (match) runtime = match[1];
  }
  if (!memory) {
    const match = document.body.textContent.match(/Memory\s*[:\s]*(\d+(?:\.\d+)?\s*(?:mb|kb|gb))/i);
    if (match) memory = match[1];
  }

  return {
    runtime: runtime || "N/A",
    memory: memory || "N/A"
  };
}

/**
 * Fetches current challenge meta from chrome storage.
 * @returns {Promise<object|null>}
 */
function getSavedProblemMeta() {
  return new Promise((resolve) => {
    chrome.storage.local.get(["current_problem"], (result) => {
      resolve(result.current_problem || null);
    });
  });
}

/**
 * Searches the DOM for a successful "Accepted" status label.
 * @returns {boolean}
 */
function isAcceptedStatusVisible() {
  const selectors = [
    "[class*='text-success']",
    "[class*='text-green']",
    "[class*='text-emerald']",
    ".text-green-s",
    ".text-emerald-s",
    "[data-e2e-locator='submission-status']"
  ];

  for (const selector of selectors) {
    const elements = document.querySelectorAll(selector);
    for (const el of elements) {
      const txt = el.textContent.trim().toLowerCase();
      if (txt === "accepted" || txt.startsWith("accepted")) {
        return true;
      }
    }
  }

  // Fallback: search leaf nodes for exact or starts-with match
  const nodes = document.querySelectorAll("span, div, p, h1, h2, h3, a");
  for (const node of nodes) {
    if (node.children.length === 0) {
      const txt = node.textContent.trim().toLowerCase();
      if (txt === "accepted" || txt.startsWith("accepted")) {
        return true;
      }
    }
  }
  return false;
}

/**
 * Main parser: gathers all payload variables, validates them, and transmits to background.
 */
async function processSubmission() {
  try {
    const isAccepted = isAcceptedStatusVisible();
    const subDetails = getSubmissionDetails();

    console.log("[CodeSync Debug] Checking submission page:", {
      url: window.location.href,
      isAcceptedStatusVisible: isAccepted,
      submissionDetails: subDetails
    });

    // 1. Confirm "Accepted" text is present
    if (!isAccepted) return;

    // 2. Extract submission ID and details
    if (!subDetails) {
      console.log("[CodeSync Debug] No submission details extracted.");
      return;
    }

    // 3. Gather code, language, and performance metrics
    const sourceCode = extractSourceCode();
    const language = getLanguage();
    const { runtime, memory } = getMetrics();

    // Prevent duplicate runs on the same submission ID with identical metrics
    if (
      subDetails.id === lastProcessedSubmissionId &&
      runtime === lastProcessedRuntime &&
      memory === lastProcessedMemory
    ) {
      return;
    }

    // 4. Retrieve problem details (slug, title, difficulty)
    const problemMeta = await getSavedProblemMeta();

    console.log("[CodeSync Debug] Extracted payload parts:", {
      sourceCodeLength: sourceCode ? sourceCode.length : 0,
      language: language,
      runtime: runtime,
      memory: memory,
      problemMeta: problemMeta
    });

    if (!problemMeta) {
      console.log("[CodeSync Debug] No saved problem metadata found in storage.");
      return;
    }

    // 5. Validation Check: Reject incomplete payloads
    if (!sourceCode || sourceCode.length <= 5 || !language || !subDetails.id) {
      console.warn("[CodeSync Debug] Validation failed. Missing fields: " + JSON.stringify({
        hasSourceCode: !!sourceCode,
        sourceCodeLength: sourceCode ? sourceCode.length : 0,
        language: language,
        submissionId: subDetails.id
      }));
      return;
    }

    lastProcessedSubmissionId = subDetails.id;
    lastProcessedRuntime = runtime;
    lastProcessedMemory = memory;

    const payload = {
      type: "SUBMISSION_DETECTED",
      data: {
        platform: "leetcode",
        problem_title: problemMeta.title,
        problem_slug: problemMeta.slug,
        difficulty: problemMeta.difficulty,
        status: "accepted",
        language: language,
        source_code: sourceCode,
        submission_id: subDetails.id,
        submission_url: subDetails.url,
        runtime: runtime,
        memory: memory
      }
    };

    console.log("[CodeSync Submission Detector] Dispatching payload:", payload.data);
    chrome.runtime.sendMessage(payload);
  } catch (error) {
    console.error("[CodeSync Submission Detector] Error during submission processing:", error);
  }
}

// 1. Setup MutationObserver to watch result card states
const submissionObserver = new MutationObserver(() => {
  processSubmission();
});

submissionObserver.observe(document.body, {
  childList: true,
  subtree: true
});

// 2. Initial execution pass
processSubmission();

