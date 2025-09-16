import React, { useState } from "react";

export default function UploadFotoSantri() {
  const [file, setFile] = useState(null);
  const [msg, setMsg] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setMsg("Pilih file foto dulu!");
      return;
    }

    const formData = new FormData();
    formData.append("foto", file);

    const userData = JSON.parse(localStorage.getItem("user"));
    const token = userData?.token;

    const res = await fetch("http://127.0.0.1:8000/api/santri/upload-foto/", {
      method: "POST",
      headers: {
        Authorization: "Token " + token,
      },
      body: formData,
    });

    const data = await res.json();
    if (res.ok) {
      setMsg("✅ Foto berhasil diupload & wajah terdeteksi!");
    } else {
      setMsg("❌ Gagal: " + (data.message || "Terjadi error"));
    }
  };

  return (
    <div className="container">
      <h3>Upload Foto Wajah Santri</h3>
      <form onSubmit={handleSubmit}>
        <input
          type="file"
          accept="image/*"
          className="form-control mb-2"
          onChange={(e) => setFile(e.target.files[0])}
        />
        <button className="btn btn-primary">Upload Foto</button>
      </form>
      {msg && <div className="mt-3">{msg}</div>}
    </div>
  );
}
