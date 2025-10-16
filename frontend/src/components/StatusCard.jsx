import React from "react";

const StatusCard = ({ fatigue, anomaly }) => {
  return (
    <div
      className={`p-4 rounded-2xl shadow-md text-white ${
        anomaly ? "bg-red-500" : "bg-green-600"
      }`}
    >
      <h3 className="text-lg font-semibold mb-1">
        {anomaly ? "⚠️ Anomaly Detected" : "✅ Normal Condition"}
      </h3>
      <p className="text-sm">Fatigue Index: {fatigue}</p>
    </div>
  );
};

export default StatusCard;
