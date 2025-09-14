// frontend/src/components/CameraCapture.jsx
import React, { useRef, useEffect } from "react";

export default function CameraCapture({ onCapture }) {
  const videoRef = useRef();
  const canvasRef = useRef();

  useEffect(() => {
    async function init() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      } catch (e) {
        console.error(e);
        alert("Camera akses ditolak atau tidak tersedia");
      }
    }
    init();
    return () => {
      // stop tracks
      if (videoRef.current && videoRef.current.srcObject) {
        videoRef.current.srcObject.getTracks().forEach(t=>t.stop());
      }
    };
  }, []);

  const capture = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);
    const dataURL = canvas.toDataURL('image/jpeg');
    onCapture(dataURL);
  };

  return (
    <div>
      <div className="mb-2">
        <button className="kembali" onClick={() => window.history.back()}>&larr; Kembali</button>
      </div>
      <video ref={videoRef} style={{width:'100%', maxWidth: '480px'}} />
      <div className="mt-2">
        <button className="btn btn-primary" onClick={capture}>Scan Wajah & Absen</button>
      </div>
      <canvas ref={canvasRef} style={{display:'none'}} />
    </div>
  );
}
