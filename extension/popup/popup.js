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

document.addEventListener("DOMContentLoaded", async () => {
  setupDevModeVisibility();
  await initPopupState();
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
