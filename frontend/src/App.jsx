import React, { useEffect, useState } from "react";
import EEGChart from "./components/EEGcharts.jsx";
import StatusCard from "./components/StatusCard.jsx";

function App() {
  const [signal, setSignal] = useState([]);
  const [fatigue, setFatigue] = useState(0);
  const [anomaly, setAnomaly] = useState(false);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket("ws://127.0.0.1:8000/ws/eeg");

    ws.onopen = () => {
      console.log("✅ Connected to EEG WebSocket");
      setConnected(true);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const raw = data.raw_signal.slice(0, 200).map((v, i) => ({ index: i, value: v }));
      setSignal(raw);
      setFatigue(data.fatigue_level);
      setAnomaly(data.anomaly === 1);
    };

    ws.onclose = () => {
      console.log("❌ Disconnected from EEG WebSocket");
      setConnected(false);
    };

    return () => ws.close();
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center p-6">
      <h1 className="text-3xl font-bold mb-4 text-indigo-700">
        🧠 Neuro-Rehabilitation & Brain Health Dashboard
      </h1>

      <div className="mb-4">
        <StatusCard fatigue={fatigue} anomaly={anomaly} />
      </div>

      <EEGChart data={signal} />

      <p className="mt-4 text-sm text-gray-600">
        Connection Status:{" "}
        <span className={connected ? "text-green-600" : "text-red-500"}>
          {connected ? "Connected" : "Disconnected"}
        </span>
      </p>
    </div>
  );
}

export default App;
