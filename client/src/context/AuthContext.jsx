import React, { createContext, useContext, useEffect, useState } from "react";
import jwtDecode from "jwt-decode";
import { apiClient, getStoredToken, setStoredToken } from "../api/client.js";

const AuthContext = createContext(null);

const parseToken = (token) => {
  if (!token) return null;
  try {
    const payload = jwtDecode(token);
    if (payload.exp && payload.exp * 1000 < Date.now()) {
      return null;
    }
    return {
      username: payload.username || payload.sub || "",
      email: payload.email || "",
      uuid: payload.minecraft_uuid || payload.uuid || ""
    };
  } catch (err) {
    console.warn("JWT decode failed", err);
    return null;
  }
};

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(getStoredToken());
  const [user, setUser] = useState(() => parseToken(getStoredToken()));
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setUser(parseToken(token));
    setStoredToken(token);
  }, [token]);

  const login = async (credentials) => {
    setLoading(true);
    try {
      const { data } = await apiClient.post("auth/login/", credentials);
      setToken(data.access);
      return { ok: true };
    } catch (error) {
      return {
        ok: false,
        message: error.response?.data?.detail || "로그인에 실패했습니다."
      };
    } finally {
      setLoading(false);
    }
  };

  const register = async (payload) => {
    setLoading(true);
    try {
      await apiClient.post("auth/register/", payload);
      return { ok: true };
    } catch (error) {
      return {
        ok: false,
        message: error.response?.data?.detail || "회원가입에 실패했습니다."
      };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setToken("");
  };

  const value = {
    token,
    user,
    loading,
    login,
    register,
    logout,
    isAuthenticated: Boolean(user)
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return ctx;
};
