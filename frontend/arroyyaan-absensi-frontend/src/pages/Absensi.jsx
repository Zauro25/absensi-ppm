import React, { useState } from "react";
import CameraCapture from "../components/CameraCapture";
import { recognizeAndAttend } from "../services/api";

export default function Absensi() {
  const [result, setResult] = useState(null);
  const [tanggal, setTanggal] = useState("");
  const [sesi, setSesi] = useState("Subuh");

  const startAbsensi = async () => {
    await fetch("http://localhost:8000/api/start-absensi/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Token " + localStorage.getItem("token"),
      },
      body: JSON.stringify({
        tanggal: tanggal || new Date().toISOString().slice(0, 10),
        sesi,
      }),
    });
    alert("Absensi dimulai");
  };

  const startTelat = async () => {
    await fetch("http://localhost:8000/api/start-telat/", {
      method: "POST",
      headers: { Authorization: "Token " + localStorage.getItem("token") },
    });
    alert("Hitung keterlambatan dimulai");
  };

  const handleCapture = async (dataURL) => {
    const res = await recognizeAndAttend(dataURL);
    setResult(res);
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-800">
      <div className="bg-gray-300 rounded-3xl shadow-lg p-6 w-[90%] max-w-4xl flex flex-col items-center">
        {/* Row utama */}
        <div className="flex w-full">
          {/* Kolom kiri */}
          <div className="flex flex-col gap-4 mr-6">
            <input
              type="date"
              value={tanggal}
              onChange={(e) => setTanggal(e.target.value)}
              className="px-4 py-3 rounded-lg border text-center font-bold text-white"
            />
            <select
              value={sesi}
              onChange={(e) => setSesi(e.target.value)}
              className="px-4 py-3 rounded-lg border text-center font-bold text-white"
            >
              <option value="Subuh">Subuh</option>
              <option value="Sore">Sore</option>
              <option value="Malam">Malam</option>
            </select>
          </div>

          {/* Kamera */}
          <div className="flex-1 flex items-center justify-center text-white rounded-lg text-3xl font-bold">
            {<CameraCapture onCapture={handleCapture}/>}
          </div>
        </div>

        {/* Tombol bawah */}
        <div className="flex gap-6 mt-6">
          <button
            onClick={startAbsensi}
            className="bg-green-700 text-white px-6 py-3 rounded-lg font-bold hover:bg-green-800 active:scale-95 transition-transform"
          >
            MULAI ABSENSI
          </button>
          <button
            onClick={startTelat}
            className="bg-red-700 text-white px-6 py-3 rounded-lg font-bold hover:bg-red-800 active:scale-95 transition-transform"
          >
            MULAI HITUNG TELAT
          </button>
        </div>

        {result && (
          <div className="mt-4 bg-white p-3 rounded-lg w-full text-center">
            {JSON.stringify(result)}
          </div>
        )}
      </div>
    </div>
  );
}
