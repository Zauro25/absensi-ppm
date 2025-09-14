import React, {useState} from "react";
import CameraCapture from "../components/CameraCapture";
import { recognizeAndAttend } from "../services/api";

export default function Absensi() {
  const [result, setResult] = useState(null);

  const startAbsensi = async () => {
    await fetch("http://localhost:8000/api/start-absensi/", {
      method:"POST",
      headers:{ "Content-Type":"application/json", "Authorization": "Token "+localStorage.getItem("token")},
      body: JSON.stringify({tanggal:new Date().toISOString().slice(0,10), sesi:"Subuh"})
    });
    alert("Absensi dimulai");
  };

  const startTelat = async () => {
    await fetch("http://localhost:8000/api/start-telat/", {
      method:"POST",
      headers:{ "Authorization": "Token "+localStorage.getItem("token")}
    });
    alert("Hitung keterlambatan dimulai");
  };

  const handleCapture = async (dataURL) => {
    const res = await recognizeAndAttend(dataURL);
    setResult(res);
  };

  return (
    <div className="container">
      <h3>Absensi</h3>
      <div className="mb-2">
        <button className="btn btn-primary me-2" onClick={startAbsensi}>Mulai Absensi</button>
        <button className="btn btn-warning" onClick={startTelat}>Hitung Keterlambatan</button>
      </div>
      <CameraCapture onCapture={handleCapture}/>
      {result && <div className="mt-3">{JSON.stringify(result)}</div>}
    </div>
  );
}
