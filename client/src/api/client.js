import axios from "axios";

const ACCESS_TOKEN_KEY = "mc_app_access";

export const getStoredToken = () => localStorage.getItem(ACCESS_TOKEN_KEY) || "";

export const setStoredToken = (token) => {
  if (token) {
    localStorage.setItem(ACCESS_TOKEN_KEY, token);
  } else {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
  }
};

export const apiClient = axios.create({
  baseURL: "/api",
  timeout: 10000
});

apiClient.interceptors.request.use((config) => {
  const token = getStoredToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      setStoredToken("");
    }
    return Promise.reject(err);
  }
);
