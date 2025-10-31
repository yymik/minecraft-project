import React from "react";
import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

const ProtectedRoute = ({ redirect = "/login" }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <p>로딩 중...</p>;
  }

  return isAuthenticated ? <Outlet /> : <Navigate to={redirect} replace />;
};

export default ProtectedRoute;
