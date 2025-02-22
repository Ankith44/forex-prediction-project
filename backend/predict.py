# predict.py
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from sklearn.preprocessing import MinMaxScaler
from config import MODEL_PATH, FEATURE_SCALER_PATH, TARGET_SCALER_PATH, DATA_PATH

# LSTM Model
class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size):
        super(LSTMModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out


def load_model_and_scalers():
    """Load LSTM model and scalers."""
    input_size = 10
    model = LSTMModel(input_size, hidden_size=64, num_layers=2, output_size=1)
    model.load_state_dict(torch.load(MODEL_PATH, weights_only=True))
    model.eval()

    feature_scaler = np.load(FEATURE_SCALER_PATH, allow_pickle=True).item()
    target_scaler = np.load(TARGET_SCALER_PATH, allow_pickle=True).item()

    return model, feature_scaler, target_scaler


def predict_close():
    """Predict next Close price using the latest 60 records."""
    df = pd.read_csv(DATA_PATH).tail(60)  # Last 60 records
    df = df.drop(columns=['date', 'Close'], errors='ignore')

    model, feature_scaler, target_scaler = load_model_and_scalers()

    input_features = feature_scaler.transform(df)
    input_tensor = torch.tensor(input_features, dtype=torch.float32).unsqueeze(0)

    with torch.no_grad():
        prediction = model(input_tensor).item()

    prediction = target_scaler.inverse_transform([[prediction]])[0][0]
    return prediction
