import { StorageClient } from "../scripts/storage.js";
import { StateManager } from "../scripts/state.js";
import { APIClient } from "../scripts/api.js";

// Toggle Developer Mode manual token entry UI
const DEV_MODE = true;

// DOM Elements
const unauthSection = document.getElementById("unauth-section");
const authSection = document.getElementById("auth-section");
const devSection = document.getElementById("dev-section");
const loginBtn = document.getElementById("login-btn");
const jwtInput = document.getElementById("jwt-input");
const saveJwtBtn = document.getElementById("save-jwt-btn");
const userAvatar = document.getElementById("user-avatar");
const userName = document.getElementById("user-name");
const userEmail = document.getElementById("user-email");
const repoSelect = document.getElementById("repo-select");
const settingsBtn = document.getElementById("settings-btn");
const logoutBtn = document.getElementById("logout-btn");
const statusMsg = document.getElementById("status-msg");

// Active Problem Section DOM Elements
const problemHeaderLabel = document.getElementById("problem-header-label");
const problemTitle = document.getElementById("problem-title");
const problemDifficulty = document.getElementById("problem-difficulty");
const syncStatusRow = document.getElementById("sync-status-row");

// Latest Submission DOM Elements
const submissionCard = document.getElementById("submission-card");
const submissionTitle = document.getElementById("submission-title");
const submissionDifficulty = document.getElementById("submission-difficulty");
const submissionLang = document.getElementById("submission-lang");
const submissionId = document.getElementById("submission-id");
const submissionRuntime = document.getElementById("submission-runtime");
const submissionMemory = document.getElementById("submission-memory");
const submissionStatusText = document.getElementById("submission-status-text");

// Sync controls
const syncBtn = document.getElementById("sync-btn");
const syncResult = document.getElementById("sync-result");
const resultSha = document.getElementById("result-sha");
const resultPath = document.getElementById("result-path");
const resultTime = document.getElementById("result-time");
const resultLink = document.getElementById("result-link");

// History controls
const historyCard = document.getElementById("history-card");
const historyList = document.getElementById("history-list");

document.addEventListener("DOMContentLoaded", async () => {
  setupDevModeVisibility();
  await initPopupState();
  await renderActiveProblem();
  await renderLatestSubmission();
  await renderSyncHistory();
  setupEventListeners();
});

/**
 * Configure developer mode interface visibility.
 */
function setupDevModeVisibility() {
  if (DEV_MODE) {
    devSection.classList.remove("hidden");
  } else {
    devSection.classList.add("hidden");
  }
}

/**
 * Initialize popup state by reading saved tokens and verifying session validity.
 */
async function initPopupState() {
  showStatus("", "");
  const token = await StorageClient.getToken();
  
  if (!token) {
    showUnauthenticatedState();
    return;
  }

  try {
    // 1. Fetch authenticated user profile
    const profile = await APIClient.fetchProfile(token);
    await StorageClient.setUser(profile);

    // 2. Load user details into popup UI
    userAvatar.src = profile.github_avatar_url || "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100' fill='%236366f1'><circle cx='50' cy='50' r='50'/></svg>";
    userName.textContent = profile.github_username || "User Account";
    userEmail.textContent = profile.github_email || "No public email";

    // 3. Load available repositories
    await loadRepositories(token);
    
    showAuthenticatedState();
  } catch (error) {
    console.error("Popup verification failed:", error);
    // Invalid token or network error. Clear storage and force re-login
    await StorageClient.clearAll();
    showUnauthenticatedState();
    showStatus(error.message, "error");
  }
}

/**
 * Reads the active problem from storage and populates the popup interface.
 */
async function renderActiveProblem() {
  const data = await chrome.storage.local.get(["current_problem"]);
  const current = data.current_problem;

  if (!current) {
    problemHeaderLabel.textContent = "Current Problem";
    problemTitle.textContent = "No LeetCode problem detected";
    problemDifficulty.className = "badge-difficulty hidden";
    problemDifficulty.textContent = "";
    syncStatusRow.classList.add("hidden");
    return;
  }

  // Task 11 requirement: Show "Last Detected Problem" if the problem exists in storage
  problemHeaderLabel.textContent = "Last Detected Problem";
  problemTitle.textContent = current.title;

  // Render difficulty badge
  const diffClass = current.difficulty.toLowerCase(); // easy, medium, hard
  problemDifficulty.className = `badge-difficulty ${diffClass}`;
  problemDifficulty.textContent = current.difficulty.charAt(0).toUpperCase() + current.difficulty.slice(1);
  
  // Show "Ready for Sync" status indicator
  syncStatusRow.classList.remove("hidden");
}

/**
 * Reads the latest submission and sync states from storage and populates the popup interface.
 */
async function renderLatestSubmission() {
  const data = await chrome.storage.local.get([
    "latest_submission",
    "latest_sync",
    "last_sync",
    "token",
    "selectedRepositoryId"
  ]);
  const submission = data.latest_submission;
  const token = data.token;
  const repoId = data.selectedRepositoryId;
  const lastSync = data.last_sync;
  const latestSync = data.latest_sync;

  if (!submission) {
    submissionCard.classList.add("hidden");
    return;
  }

  submissionTitle.textContent = submission.problem_title;

  // Difficulty badge
  const diffClass = submission.difficulty.toLowerCase();
  submissionDifficulty.className = `badge-difficulty ${diffClass}`;
  submissionDifficulty.textContent = submission.difficulty.charAt(0).toUpperCase() + submission.difficulty.slice(1);

  // Metadata
  submissionLang.textContent = submission.language;
  submissionId.textContent = submission.submission_id;
  submissionRuntime.textContent = submission.runtime || "N/A";
  submissionMemory.textContent = submission.memory || "N/A";

  submissionCard.classList.remove("hidden");

  // Determine button state and label based on repository-aware duplicate check
  let isSynced = false;
  if (lastSync && lastSync.submission_id === submission.submission_id && lastSync.repository_id === repoId) {
    isSynced = true;
  }

  if (isSynced) {
    submissionStatusText.textContent = "Accepted \u2022 Synced";
    syncBtn.textContent = "Already Synced";
    syncBtn.disabled = true;
  } else {
    submissionStatusText.textContent = "Accepted \u2022 Ready for Sync";
    syncBtn.textContent = "Ready to Sync";
    // Enable only if token, repo, and submission are available
    syncBtn.disabled = !(token && repoId);
  }

  // Render Latest Sync Details if applicable
  if (latestSync && latestSync.status === "completed" && isSynced) {
    resultSha.textContent = latestSync.commit_sha ? latestSync.commit_sha.substring(0, 7) : "N/A";
    resultPath.textContent = latestSync.github_file_path || "N/A";
    resultTime.textContent = latestSync.synced_at ? new Date(latestSync.synced_at).toLocaleString() : "N/A";
    
    if (latestSync.commit_url) {
      resultLink.href = latestSync.commit_url;
      resultLink.classList.remove("hidden");
    } else {
      resultLink.classList.add("hidden");
    }
    syncResult.classList.remove("hidden");
  } else {
    syncResult.classList.add("hidden");
  }
}

/**
 * Retrieves the user's active repositories from the backend and populates the select box.
 * @param {string} token 
 */
async function loadRepositories(token) {
  try {
    const repos = await APIClient.fetchRepositories(token);
    
    // Clear existing dynamic options
    repoSelect.innerHTML = '<option value="" disabled>Select a repository...</option>';
    
    if (!repos || repos.length === 0) {
      const opt = document.createElement("option");
      opt.value = "";
      opt.text = "No provisioned repositories found";
      opt.disabled = true;
      repoSelect.appendChild(opt);
      return;
    }

    const savedRepoId = await StorageClient.getSelectedRepositoryId();
    let isSavedRepoStillValid = false;

    repos.forEach((repo) => {
      const option = document.createElement("option");
      option.value = repo.id;
      // Show full name and bootstrap status
      const statusLabel = repo.bootstrap_status ? `[${repo.bootstrap_status}]` : "";
      option.text = `${repo.repo_name} ${statusLabel}`;
      
      if (repo.id === savedRepoId) {
        option.selected = true;
        isSavedRepoStillValid = true;
      }
      repoSelect.appendChild(option);
    });

    // Fallback if the saved repository ID is no longer in the list
    if (!isSavedRepoStillValid && repos.length > 0) {
      repoSelect.selectedIndex = 0;
      await StorageClient.setSelectedRepositoryId(repoSelect.value);
    }
  } catch (error) {
    console.error("Failed to load repositories:", error);
    showStatus("Failed to retrieve repositories list.", "error");
  }
}

/**
 * Event Listeners configuration.
 */
function setupEventListeners() {
  // Login redirects user to GitHub login endpoint
  loginBtn.addEventListener("click", async () => {
    try {
      showStatus("Initiating GitHub login...", "");
      const response = await APIClient.request("GET", "/auth/github/login");
      if (response && response.authorization_url) {
        chrome.tabs.create({ url: response.authorization_url });
        showStatus("", "");
      } else {
        showStatus("Failed to retrieve GitHub login URL.", "error");
      }
    } catch (error) {
      showStatus(`Login error: ${error.message}`, "error");
    }
  });

  // Manual JWT entry handler (Developer mode)
  if (DEV_MODE) {
    saveJwtBtn.addEventListener("click", async () => {
      const jwtValue = jwtInput.value.trim();
      if (!jwtValue) {
        showStatus("Please enter a valid non-empty token.", "error");
        return;
      }
      
      try {
        showStatus("Validating token...", "");
        // Verify token with backend
        const profile = await APIClient.fetchProfile(jwtValue);
        
        // Save token and user details to storage
        await StorageClient.setToken(jwtValue);
        await StorageClient.setUser(profile);
        
        jwtInput.value = "";
        showStatus("Authentication successful!", "success");
        
        // Reload UI state
        await initPopupState();
        await renderSyncHistory();
      } catch (error) {
        showStatus(`Authentication failed: ${error.message}`, "error");
      }
    });
  }

  // Repository selection change event
  repoSelect.addEventListener("change", async (event) => {
    const selectedId = event.target.value;
    if (selectedId) {
      await StorageClient.setSelectedRepositoryId(selectedId);
      showStatus("Repository preference updated.", "success");
      // Update sync button state
      await renderLatestSubmission();
      setTimeout(() => showStatus("", ""), 1500);
    }
  });

  // Redirect to Options settings page
  settingsBtn.addEventListener("click", () => {
    if (chrome.runtime.openOptionsPage) {
      chrome.runtime.openOptionsPage();
    } else {
      window.open(chrome.runtime.getURL("options/options.html"));
    }
  });

  // Logout handler
  logoutBtn.addEventListener("click", async () => {
    const token = await StorageClient.getToken();
    if (token) {
      try {
        await APIClient.logout(token);
      } catch (e) {
        console.warn("API logout call failed, clearing local session anyway.", e);
      }
    }
    await StorageClient.clearAll();
    showUnauthenticatedState();
    showStatus("Logged out successfully.", "success");
  });

  // Sync button click event
  syncBtn.addEventListener("click", handleSyncClick);

  // Task 12 requirement: Subscribe to storage updates to update popup in real-time
  chrome.storage.onChanged.addListener(async (changes, namespace) => {
    if (namespace === "local") {
      if (changes.current_problem) {
        console.log("[Popup] Active problem changed in storage, re-rendering.");
        await renderActiveProblem();
      }
      if (changes.latest_submission) {
        console.log("[Popup] Latest submission changed in storage, re-rendering.");
        await renderLatestSubmission();
      }
      if (changes.latest_sync || changes.last_sync || changes.selectedRepositoryId || changes.token) {
        console.log("[Popup] Sync state changed in storage, re-rendering.");
        await renderLatestSubmission();
      }
      if (changes.sync_history_cache) {
        console.log("[Popup] Sync history cache changed, re-rendering.");
        await renderSyncHistory();
      }
    }
  });
}

/**
 * Handles the solution synchronization flow when Sync is clicked.
 */
async function handleSyncClick() {
  const data = await chrome.storage.local.get([
    "latest_submission",
    "selectedRepositoryId",
    "token"
  ]);
  const submission = data.latest_submission;
  const repoId = data.selectedRepositoryId;
  const token = data.token;

  if (!submission || !repoId || !token) {
    showStatus("Missing required fields for synchronization.", "error");
    return;
  }

  // Confirmation dialog
  const repoText = repoSelect.options[repoSelect.selectedIndex]?.text || "Selected Repository";
  const confirmMessage = `Sync this solution?\n\nProblem: ${submission.problem_title}\nLanguage: ${submission.language}\nRepository: ${repoText}`;
  if (!confirm(confirmMessage)) {
    return;
  }

  // Disable button and change state
  syncBtn.disabled = true;
  syncBtn.textContent = "Syncing...";
  showStatus("Sync in progress...", "");

  const payload = {
    repository_id: repoId,
    problem_title: submission.problem_title,
    problem_slug: submission.problem_slug,
    difficulty: submission.difficulty.toLowerCase(),
    language: submission.language,
    source_code: submission.source_code
  };

  try {
    const response = await APIClient.syncLeetCodeSubmission(token, payload);
    
    // Save to latest_sync and last_sync
    const now = Date.now();
    const latestSyncPayload = {
      sync_id: response.sync_id,
      status: response.status,
      commit_sha: response.commit_sha,
      commit_url: response.commit_url,
      github_file_path: response.github_file_path,
      synced_at: now
    };
    
    const lastSyncPayload = {
      submission_id: submission.submission_id,
      repository_id: repoId,
      synced_at: now
    };

    await chrome.storage.local.set({
      latest_sync: latestSyncPayload,
      last_sync: lastSyncPayload
    });

    syncBtn.textContent = "\u2713 Synced Successfully";
    showStatus("Solution synced successfully!", "success");

    // Force clear the history cache to trigger fresh fetch
    await chrome.storage.local.remove(["sync_history_cache"]);
    await renderSyncHistory();
  } catch (error) {
    console.error("Sync failed:", error);
    
    // Handle 409 Conflict specifically as "Already Synced"
    if (error.status === 409) {
      const now = Date.now();
      const lastSyncPayload = {
        submission_id: submission.submission_id,
        repository_id: repoId,
        synced_at: now
      };
      await chrome.storage.local.set({ last_sync: lastSyncPayload });
      
      syncBtn.textContent = "Already Synced";
      showStatus("This submission already exists in the selected repository.", "error");
    } else {
      syncBtn.textContent = "Sync Failed";
      showStatus(error.message || "Synchronization failed.", "error");
      // Enable sync button again so user can retry
      syncBtn.disabled = false;
    }
  }
}

/**
 * Fetches and renders user sync history list (caching retrieved history for 5 mins).
 */
async function renderSyncHistory() {
  const token = await StorageClient.getToken();
  if (!token) {
    historyCard.classList.add("hidden");
    return;
  }

  // Load from cache first
  const cacheData = await chrome.storage.local.get(["sync_history_cache"]);
  const cache = cacheData.sync_history_cache;
  const now = Date.now();
  const cacheDurationLimit = 5 * 60 * 1000; // 5 minutes

  let historyEntries = null;

  if (cache && (now - cache.fetchedAt < cacheDurationLimit)) {
    console.log("[Popup] Loading sync history from cache.");
    historyEntries = cache.entries;
  } else {
    console.log("[Popup] Fetching fresh sync history.");
    try {
      historyEntries = await APIClient.fetchSyncHistory(token);
      await chrome.storage.local.set({
        sync_history_cache: {
          entries: historyEntries,
          fetchedAt: now
        }
      });
    } catch (error) {
      console.warn("Failed to fetch sync history:", error);
      // If API call fails but we have stale cache, fallback to cache
      if (cache) {
        historyEntries = cache.entries;
      }
    }
  }

  if (!historyEntries || historyEntries.length === 0) {
    historyList.innerHTML = '<div class="history-empty">No recent synchronizations</div>';
    historyCard.classList.add("hidden");
    return;
  }

  // Render top 5
  const top5 = historyEntries.slice(0, 5);
  historyList.innerHTML = "";
  
  top5.forEach(item => {
    const itemEl = document.createElement("div");
    itemEl.className = "history-item";
    
    const formattedTime = new Date(item.created_at || item.updated_at).toLocaleString();
    const statusClass = item.sync_status.toLowerCase(); // completed, failed, running
    
    // Left section (details)
    const leftEl = document.createElement("div");
    leftEl.className = "history-left";
    
    const titleEl = document.createElement("div");
    titleEl.className = "history-title";
    titleEl.textContent = item.problem_title;
    
    const metaEl = document.createElement("div");
    metaEl.className = "history-meta";
    metaEl.textContent = `${item.language.toUpperCase()} \u2022 ${formattedTime}`;
    
    leftEl.appendChild(titleEl);
    leftEl.appendChild(metaEl);
    
    // Right section (status & link)
    const rightEl = document.createElement("div");
    rightEl.className = "history-right";
    
    const badgeEl = document.createElement("span");
    badgeEl.className = `history-status-badge ${statusClass}`;
    badgeEl.textContent = item.sync_status;
    
    rightEl.appendChild(badgeEl);
    
    if (item.commit_url) {
      const linkEl = document.createElement("a");
      linkEl.href = item.commit_url;
      linkEl.target = "_blank";
      linkEl.className = "history-link-icon";
      linkEl.innerHTML = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
          <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
          <polyline points="15 3 21 3 21 9"></polyline>
          <line x1="10" y1="14" x2="21" y2="3"></line>
        </svg>
      `;
      rightEl.appendChild(linkEl);
    }
    
    itemEl.appendChild(leftEl);
    itemEl.appendChild(rightEl);
    historyList.appendChild(itemEl);
  });

  historyCard.classList.remove("hidden");
}

function showUnauthenticatedState() {
  unauthSection.classList.remove("hidden");
  authSection.classList.add("hidden");
}

function showAuthenticatedState() {
  unauthSection.classList.add("hidden");
  authSection.classList.remove("hidden");
}

/**
 * Display a user-facing success or error message.
 * @param {string} msg 
 * @param {'success'|'error'|''} type 
 */
function showStatus(msg, type) {
  if (!msg) {
    statusMsg.className = "status-msg hidden";
    statusMsg.textContent = "";
    return;
  }
  statusMsg.className = `status-msg ${type}`;
  statusMsg.textContent = msg;
  statusMsg.classList.remove("hidden");
}
