import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function RegisterSantri() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    username: "",
    password: "",
    nama: "",
    asal_daerah: "",
    sektor: "kepuh",
    angkatan: "",
    jenis_kelamin: "L"
  });
  const [msg, setMsg] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch("http://127.0.0.1:8000/api/register-santri/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const data = await res.json();

      if (res.ok) {
        setMsg("✅ Registrasi berhasil, silakan login!");
        // redirect ke halaman login setelah 1.5 detik
        setTimeout(() => navigate("/"), 1500);
      } else {
        setMsg("❌ Gagal: " + (data.message || JSON.stringify(data)));
      }
    } catch (err) {
      setMsg("❌ Error: " + err.message);
    }
  };

  return (
    <div className="container">
      <h3>Register Akun Santri</h3>
      <form onSubmit={submit}>
        <input
          placeholder="Nama Lengkap"
          className="form-control mb-2"
          value={form.nama}
          onChange={(e) => setForm({ ...form, nama: e.target.value })}
        />
        <input
          placeholder="Asal Daerah"
          className="form-control mb-2"
          value={form.asal_daerah}
          onChange={(e) => setForm({ ...form, asal_daerah: e.target.value })}
        />
        <select
          className="form-select mb-2"
          value={form.sektor}
          onChange={(e) => setForm({ ...form, sektor: e.target.value })}
        >
          <option value="kepuh">Kepuh</option>
          <option value="sidobali">Sidobali</option>
        </select>
        <input
          placeholder="Angkatan"
          className="form-control mb-2"
          value={form.angkatan}
          onChange={(e) => setForm({ ...form, angkatan: e.target.value })}
        />
        <select
          className="form-select mb-2"
          value={form.jenis_kelamin}
          onChange={(e) =>
            setForm({ ...form, jenis_kelamin: e.target.value })
          }
        >
          <option value="L">Laki-laki</option>
          <option value="P">Perempuan</option>
        </select>
        <input
          placeholder="Username"
          className="form-control mb-2"
          value={form.username}
          onChange={(e) => setForm({ ...form, username: e.target.value })}
        />
        <input
          type="password"
          placeholder="Password"
          className="form-control mb-2"
          value={form.password}
          onChange={(e) => setForm({ ...form, password: e.target.value })}
        />
        <button className="btn btn-primary">Register</button>
      </form>
      <div className="mt-2 text-info">{msg}</div>
    </div>
  );
}
