import { StorageClient } from "./storage.js";

/**
 * APIClient communicates with the CodeSync Backend API.
 * Automatically fetches the API base URL from StorageClient settings.
 */
export const APIClient = {
  /**
   * Performs an HTTP request to the backend with authentication header injection.
   * Handles 401 Unauthorized, invalid JSON responses, and network failures.
   * @param {string} method - HTTP Verb (GET, POST, etc.)
   * @param {string} path - Target API route path (e.g. '/auth/me')
   * @param {string|null} token - JWT Access Token
   * @param {object|null} body - Request body payload
   * @returns {Promise<any>}
   */
  async request(method, path, token = null, body = null) {
    const baseUrl = await StorageClient.getApiBaseUrl();
    const cleanPath = path.startsWith("/") ? path : `/${path}`;
    const url = `${baseUrl}${cleanPath}`;

    const headers = {
      "Accept": "application/json"
    };

    if (body) {
      headers["Content-Type"] = "application/json";
    }

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const options = {
      method,
      headers
    };

    if (body) {
      options.body = JSON.stringify(body);
    }

    try {
      const response = await fetch(url, options);

      // Handle 401 Unauthorized automatically by wiping storage
      if (response.status === 401) {
        await StorageClient.clearAll();
        throw new Error("Session expired or unauthorized. Please log in again.");
      }

      const text = await response.text();
      let data = null;

      if (text) {
        try {
          data = JSON.parse(text);
        } catch (e) {
          throw new Error("Server returned an invalid JSON response.");
        }
      }

      if (!response.ok) {
        const detail = data && (data.detail || data.message);
        throw new Error(detail || `Server request failed with status code ${response.status}.`);
      }

      return data;
    } catch (error) {
      // Differentiate network failures from parsed server errors
      if (error.name === "TypeError" && error.message.includes("fetch")) {
        throw new Error("Unable to connect to the CodeSync backend. Check your network or API Base URL settings.");
      }
      throw error;
    }
  },

  /**
   * Fetches the current user profile from /auth/me
   * @param {string} token 
   * @returns {Promise<object>}
   */
  async fetchProfile(token) {
    return await this.request("GET", "/auth/me", token);
  },

  /**
   * Fetches the list of user repositories from /repositories
   * @param {string} token 
   * @returns {Promise<Array>}
   */
  async fetchRepositories(token) {
    return await this.request("GET", "/repositories", token);
  },

  /**
   * Requests logout and token invalidation on backend
   * @param {string} token 
   * @returns {Promise<object>}
   */
  async logout(token) {
    return await this.request("POST", "/auth/logout", token);
  }
};
