import { StorageClient } from "../scripts/storage.js";
import { APIClient } from "../scripts/api.js";

// DOM Elements
const apiUrlInput = document.getElementById("api-url-input");
const saveSettingsBtn = document.getElementById("save-settings-btn");
const repoCard = document.getElementById("repo-card");
const repoSelect = document.getElementById("repo-select");
const accountCard = document.getElementById("account-card");
const userAvatar = document.getElementById("user-avatar");
const userName = document.getElementById("user-name");
const userEmail = document.getElementById("user-email");
const logoutBtn = document.getElementById("logout-btn");
const statusMsg = document.getElementById("status-msg");

document.addEventListener("DOMContentLoaded", async () => {
  await initOptionsState();
  setupEventListeners();
});

/**
 * Loads current configurations and configures cards based on authentication status.
 */
async function initOptionsState() {
  // Load saved API base URL
  const baseUrl = await StorageClient.getApiBaseUrl();
  apiUrlInput.value = baseUrl;

  const token = await StorageClient.getToken();
  if (!token) {
    hideAuthenticatedOptions();
    return;
  }

  try {
    const profile = await APIClient.fetchProfile(token);
    await StorageClient.setUser(profile);

    // Populate user profile information
    userAvatar.src = profile.github_avatar_url || "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100' fill='%236366f1'><circle cx='50' cy='50' r='50'/></svg>";
    userName.textContent = profile.github_username || "User Account";
    userEmail.textContent = profile.github_email || "No public email";

    // Load user repositories
    await loadRepositories(token);

    showAuthenticatedOptions();
  } catch (error) {
    console.error("Options session verification failed:", error);
    await StorageClient.clearAll();
    hideAuthenticatedOptions();
    showToast("Session expired. Please re-login via the extension popup.", "error");
  }
}

/**
 * Queries backend repositories and populates options dropdown list.
 * @param {string} token 
 */
async function loadRepositories(token) {
  try {
    const repos = await APIClient.fetchRepositories(token);
    
    // Clear select elements
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
      const statusLabel = repo.bootstrap_status ? `[${repo.bootstrap_status}]` : "";
      option.text = `${repo.repo_name} ${statusLabel}`;
      
      if (repo.id === savedRepoId) {
        option.selected = true;
        isSavedRepoStillValid = true;
      }
      repoSelect.appendChild(option);
    });

    if (!isSavedRepoStillValid && repos.length > 0) {
      repoSelect.selectedIndex = 0;
      await StorageClient.setSelectedRepositoryId(repoSelect.value);
    }
  } catch (error) {
    console.error("Options failed loading repositories:", error);
    showToast("Failed to load repositories.", "error");
  }
}

/**
 * Configure UI action listeners.
 */
function setupEventListeners() {
  // Save custom backend API base URL URL
  saveSettingsBtn.addEventListener("click", async () => {
    let urlValue = apiUrlInput.value.trim();
    if (!urlValue) {
      showToast("API Base URL cannot be empty.", "error");
      return;
    }

    // Clean trailing slashes
    if (urlValue.endsWith("/")) {
      urlValue = urlValue.slice(0, -1);
    }

    await StorageClient.setApiBaseUrl(urlValue);
    showToast("Connection settings updated successfully.", "success");
    
    // Re-verify session with new URL if token exists
    await initOptionsState();
  });

  // Save selected repository preference
  repoSelect.addEventListener("change", async (event) => {
    const selectedId = event.target.value;
    if (selectedId) {
      await StorageClient.setSelectedRepositoryId(selectedId);
      showToast("Active repository preference updated.", "success");
    }
  });

  // Log Out handler
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
    hideAuthenticatedOptions();
    showToast("Successfully logged out and session cleared.", "success");
  });
}

function showAuthenticatedOptions() {
  repoCard.classList.remove("hidden");
  accountCard.classList.remove("hidden");
}

function hideAuthenticatedOptions() {
  repoCard.classList.add("hidden");
  accountCard.classList.add("hidden");
}

/**
 * Displays a quick transient notification bubble.
 * @param {string} msg 
 * @param {'success'|'error'} type 
 */
function showToast(msg, type) {
  statusMsg.className = `status-msg ${type}`;
  statusMsg.textContent = msg;
  statusMsg.classList.remove("hidden");
  
  setTimeout(() => {
    statusMsg.classList.add("hidden");
  }, 3000);
}
