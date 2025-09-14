import React, { useEffect, useState } from "react";
import { listSantri } from "../services/api";
import { useNavigate } from "react-router-dom";

export default function Dashboard() {
  const [santris, setSantris] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    // cek user dari localStorage
    const user = JSON.parse(localStorage.getItem("user"));
    if (!user) {
      navigate("/"); // kalau belum login, balikin ke login
    }

    // load daftar santri
    fetchSantri();
  }, []);

  async function fetchSantri() {
    const res = await listSantri();
    if (res.ok) {
      setSantris(res.data);
    }
  }

  return (
    <div className="container">
      <h2>Dashboard Pengurus</h2>
      <p>Selamat datang, {JSON.parse(localStorage.getItem("user"))?.username} 👋</p>
      <div className="list-group">
  <a href="/registrasi" className="list-group-item">📋 Registrasi Santri</a>
  <a href="/absensi" className="list-group-item">✅ Absensi</a>
  <a href="/izin" className="list-group-item">📝 Surat Izin</a>
  <a href="/rekap" className="list-group-item">📊 Rekap Absensi</a>
</div>
      <div className="mb-3">
        <button
          className="btn btn-danger"
          onClick={() => {
            localStorage.removeItem("user");
            navigate("/");
          }}
        >
          Logout
        </button>
      </div>

      <h4>Daftar Santri</h4>
      <table className="table table-striped">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nama</th>
          </tr>
        </thead>
        <tbody>
          {santris.map((s) => (
            <tr key={s.id}>
              <td>{s.santri_id}</td>
              <td>{s.nama}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
