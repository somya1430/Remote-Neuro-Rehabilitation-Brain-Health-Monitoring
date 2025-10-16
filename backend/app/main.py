from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import asyncio
from scipy.signal import butter, lfilter
from sklearn.ensemble import IsolationForest
from datetime import datetime
import json

app = FastAPI(title="Neuro-Rehabilitation & Brain Health Monitoring API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def butter_bandpass(lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def bandpass_filter(data, lowcut=1.0, highcut=50.0, fs=256, order=4):
    b, a = butter_bandpass(lowcut, highcut, fs, order)
    y = lfilter(b, a, data)
    return y


# Generate simulated EEG data
def generate_eeg_signal(duration=1.0, fs=256):
    """
    Generate 1-second EEG-like signal with a mix of frequency components.
    """
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)

    # Base brain rhythms
    alpha = np.sin(2 * np.pi * 10 * t)       # 10 Hz (alpha)
    beta = np.sin(2 * np.pi * 20 * t)        # 20 Hz (beta)
    theta = np.sin(2 * np.pi * 6 * t)        # 6 Hz (theta)
    noise = np.random.normal(0, 0.5, len(t)) # random noise

    signal = alpha + 0.5 * beta + 0.3 * theta + noise
    signal = bandpass_filter(signal)
    return t, signal


# Feature extraction: compute band powers
def extract_features(signal, fs=256):
    freqs = np.fft.rfftfreq(len(signal), d=1/fs)
    fft_vals = np.abs(np.fft.rfft(signal))

    def band_power(low, high):
        idx = np.logical_and(freqs >= low, freqs <= high)
        return np.mean(fft_vals[idx])

    features = {
        "theta": band_power(4, 8),
        "alpha": band_power(8, 13),
        "beta": band_power(13, 30)
    }
    # Fatigue proxy metric
    features["fatigue_index"] = features["theta"] / (features["alpha"] + 1e-6)
    return features

# Pre-train a small Isolation Forest model on normal EEG features
def train_baseline_model(samples=200):
    normal_data = []
    for _ in range(samples):
        _, sig = generate_eeg_signal()
        f = extract_features(sig)
        normal_data.append(list(f.values()))
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(normal_data)
    return model


model = train_baseline_model()
print("[INFO] Baseline anomaly model trained.")

@app.websocket("/ws/eeg")
async def eeg_data_stream(websocket: WebSocket):
    await websocket.accept()
    print("[INFO] Client connected to EEG stream.")
    try:
        while True:
            # Simulate new EEG signal every 1 second
            _, eeg_signal = generate_eeg_signal()
            features = extract_features(eeg_signal)

            # Prepare input vector for model
            X = np.array(list(features.values())).reshape(1, -1)
            anomaly_flag = int(model.predict(X)[0] == -1)

            data_packet = {
                "timestamp": datetime.now().isoformat(),
                "features": features,
                "anomaly": anomaly_flag,
                "fatigue_level": round(features["fatigue_index"], 3),
                "raw_signal": eeg_signal.tolist()  # optional: for plotting
            }

            await websocket.send_text(json.dumps(data_packet))
            await asyncio.sleep(1)  # stream every 1s

    except WebSocketDisconnect:
        print("[INFO] EEG WebSocket disconnected.")


@app.get("/")
def root():
    return {"message": "Neuro-Rehabilitation & Brain Health Monitoring API is running"}
