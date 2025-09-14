import React, { useState } from "react";
import { login } from "../services/api";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [msg, setMsg] = useState("");
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    const res = await login(username, password);

    if (res.token) {
      // Simpan data user + token ke localStorage
      localStorage.setItem("user", JSON.stringify(res));
      localStorage.setItem("token", res.token);

      setMsg("✅ Login sukses!");

      // Redirect sesuai role
      if (res.role === "pengurus") {
        navigate("/dashboard");
      } else if (res.role === "santri") {
        navigate("/dashboard-santri");
      } else {
        navigate("/");
      }
    } else {
      setMsg("❌ Gagal login: " + (res.error || res.message || "Unknown error"));
    }
  };

  return (
    <div className="container mt-5" style={{ maxWidth: "400px" }}>
      <h3 className="mb-3">Login</h3>
      <form onSubmit={submit}>
        <div className="mb-2">
          <input
            className="form-control"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        </div>
        <div className="mb-2">
          <input
            type="password"
            className="form-control"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        <button className="btn btn-success w-100 mt-2" type="submit">
          Login
        </button>
      </form>

      <div className="mt-3 text-center">
        <button
          className="btn btn-link"
          onClick={() => navigate("/register")}
        >
          Belum punya akun? Daftar disini
        </button>
      </div>

      {msg && <div className="mt-3 alert alert-info">{msg}</div>}
    </div>
  );
}
