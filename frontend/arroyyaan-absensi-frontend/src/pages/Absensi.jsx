import React, { useRef, useEffect, useState } from "react";
import api from "../services/api";

export default function Absensi({ tanggal, sesi }) {
  const videoRef = useRef();
  const [lastScan, setLastScan] = useState(null);

  useEffect(() => {
    let stream;
    let intervalId;

    async function init() {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        videoRef.current.srcObject = stream;
        await videoRef.current.play();

        // Scan otomatis tiap 2 detik
        intervalId = setInterval(capture, 2000);
      } catch (err) {
        console.error(err);
        alert("Gagal akses kamera");
      }
    }
    init();

    return () => {
      if (stream) stream.getTracks().forEach((t) => t.stop());
      if (intervalId) clearInterval(intervalId);
    };
  }, []);

  const capture = async () => {
    const video = videoRef.current;
    if (!video) return;

    // Snapshot dari kamera
    const hiddenCanvas = document.createElement("canvas");
    hiddenCanvas.width = video.videoWidth;
    hiddenCanvas.height = video.videoHeight;
    const hctx = hiddenCanvas.getContext("2d");
    hctx.drawImage(video, 0, 0);
    const dataURL = hiddenCanvas.toDataURL("image/jpeg");

    try {
      const res = await api.post("/api/recognize-and-attend/", {
        image: dataURL,
        tanggal,
        sesi,
      });

      if (res.data && res.data.ok) {
        // Simpan hasil scan terakhir
        setLastScan({
          nama: res.data.santri.nama,
          status: res.data.status,
        });
      }
    } catch (err) {
      console.error("Scan error:", err);
    }
  };

  return (
    <div className="flex flex-row items-start gap-6">
      {/* Kamera */}
      <div>
        <video
          ref={videoRef}
          style={{ width: "480px", borderRadius: "10px" }}
        />
      </div>

      {/* Kotak informasi scan terakhir */}
      <div className="bg-gray-100 p-4 rounded w-64 h-[200px] flex items-center justify-center">
        {lastScan ? (
          <div className="text-center">
            <h3 className="font-bold text-lg">{lastScan.nama}</h3>
            <p
              className={`mt-2 text-xl font-bold ${
                lastScan.status === "Hadir"
                  ? "text-green-600"
                  : lastScan.status === "T1"
                  ? "text-yellow-500"
                  : lastScan.status === "T2"
                  ? "text-orange-500"
                  : "text-red-600"
              }`}
            >
              {lastScan.status}
            </p>
          </div>
        ) : (
          <p className="text-gray-500">Belum ada wajah terdeteksi</p>
        )}
      </div>
    </div>
  );
}
