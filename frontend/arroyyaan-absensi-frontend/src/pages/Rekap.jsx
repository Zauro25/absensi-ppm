import React, {useState} from "react";
import { rekap, exportXLSX, exportPDF } from "../services/api";

export default function Rekap() {
  const [start, setStart] = useState('');
  const [end, setEnd] = useState('');
  const [data, setData] = useState(null);

  const doRekap = async () => {
    if(!start || !end) { alert('Pilih start & end'); return; }
    const res = await rekap(start, end);
    if(res.ok) setData(res);
    else alert(res.message || 'Gagal');
  };

  return (
    <div className="container">
      <h3>Rekap Absensi</h3>
      <div className="row mb-2">
        <div className="col-md-3"><input className="form-control" type="date" value={start} onChange={e=>setStart(e.target.value)} /></div>
        <div className="col-md-3"><input className="form-control" type="date" value={end} onChange={e=>setEnd(e.target.value)} /></div>
        <div className="col-md-6">
          <button className="btn btn-primary me-2" onClick={doRekap}>Tampilkan Rekap</button>
          <button className="btn btn-outline-primary me-2" onClick={()=>exportXLSX(start,end)}>Export XLSX</button>
          <button className="btn btn-outline-secondary" onClick={()=>exportPDF(start,end)}>Export PDF</button>
        </div>
      </div>

      {data && data.ok && (
        <div>
          <h5>Putra</h5>
          <table className="table table-sm">
            <thead>
              <tr>
                <th>Nama</th>
                {data.headers.map(h=> <th key={h.col_key}>{h.tanggal} {h.sesi}</th>)}
              </tr>
            </thead>
            <tbody>
              {data.putra.map(r => (
                <tr key={r.santri_id}>
                  <td>{r.nama}</td>
                  {data.headers.map(h => <td key={h.col_key}>{r[h.col_key]}</td>)}
                </tr>
              ))}
            </tbody>
          </table>

          <h5>Putri</h5>
          <table className="table table-sm">
            <thead>
              <tr>
                <th>Nama</th>
                {data.headers.map(h=> <th key={h.col_key}>{h.tanggal} {h.sesi}</th>)}
              </tr>
            </thead>
            <tbody>
              {data.putri.map(r => (
                <tr key={r.santri_id}>
                  <td>{r.nama}</td>
                  {data.headers.map(h => <td key={h.col_key}>{r[h.col_key]}</td>)}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
