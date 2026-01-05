# 🛡️ Iron Dome: AI-Powered NIDS

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![License](https://img.shields.io/badge/License-GPL_v2-blue)
![Status](https://img.shields.io/badge/Status-Stable-red)

**A Next-Gen Network Intrusion Detection System utilizing Random Forest Classifiers to detect DDoS and Port Scan attacks in real-time.**

## 📖 Project Overview
Traditional firewalls rely on static rules. Iron Dome uses **Machine Learning** to analyze traffic behavior. By training on the **CIC-IDS2017** dataset, it learns to distinguish between benign user traffic and malicious patterns based on flow duration, packet counts, and payload size.

## 🚀 Features
*   **Hybrid Engine:** Switch between **Synthetic Simulation** (for demos) and **Real-World CSV Data**.
*   **Visual Diagnostics:** Real-time Confusion Matrix with automated layman explanations.
*   **Live Simulation:** "Inject" custom packets to test the AI's response.
*   **Report Generation:** One-click PDF export for security audits.
*   **Modern UI:** A custom-built, high-contrast Tkinter interface inspired by cyber-defense consoles.

## 🛠️ Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/YOUR_USERNAME/Iron-Dome-NIDS.git
    cd Iron-Dome-NIDS
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application**
    ```bash
    python src/main.py
    ```
## How to Use
1.  Launch the application.
2.  Use the sliders in the **Control Panel** to set your desired model parameters.
3.  Click **"Train Model Now"**. Wait for the status to change to "Model is Ready!".
4.  View the performance metrics and confusion matrix.

## 📊 Dataset
This project is compatible with the **CIC-IDS2017** dataset.
To use the "Real Data" feature:
1.  Download `Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv` from [Kaggle](https://www.kaggle.com/datasets/chethuhn/network-intrusion-dataset?select=Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv).
2.  Select "Real Dataset" in the Configuration panel and load the file.

## 📸 Screenshot: Initial User Interface Dashboard (GUI).
*(What it shows: The UI layout, the "SYSTEM STATUS: WAITING", and that the metrics are empty.)*
<img width="1920" height="1376" alt="NIDS- Iron Dome Prototype GUI" src="https://github.com/user-attachments/assets/a3e06dfb-da88-4e38-80d3-e553c4ed6f2f" />

## 📜 License
This project is open-source and licensed under the **GNU General Public License v2.0 (GPLv2)**. You are free to use, modify, and distribute this software in compliance with the license terms.
