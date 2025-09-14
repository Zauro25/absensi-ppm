import React from "react";
import { useNavigate } from "react-router-dom";

export default function DashboardSantri() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user"));

  const logout = () => {
    localStorage.removeItem("user");
    localStorage.removeItem("token");
    navigate("/");
  };

  return (
    <div className="container">
      <div className="d-flex justify-content-between align-items-center mt-3 mb-4">
        <h3>Dashboard Santri</h3>
        <button className="btn btn-danger" onClick={logout}>
          Logout
        </button>
      </div>

      <p>Halo, <strong>{user?.username}</strong> 👋</p>

      <div className="list-group">
        <button
          className="list-group-item list-group-item-action"
          onClick={() => navigate("/upload-foto")}
        >
          📸 Upload Foto Wajah
        </button>

        <button
          className="list-group-item list-group-item-action"
          onClick={() => navigate("/izin")}
        >
          📝 Upload Surat Izin
        </button>
      </div>
    </div>
  );
}
