# 🤖 Voice Assistant with Emotion Detection

An intelligent voice assistant developed in Python that integrates speech recognition, command processing, and emotion detection using machine learning models.

---

## 🚀 Features

* 🎙️ Voice command recognition
* 🧠 Natural language processing
* 😊 Emotion classification from user input
* ⚡ Real-time interaction
* 🗂️ Modular and scalable architecture

---

## 🛠️ Technologies Used

* Python
* Machine Learning (Scikit-learn / custom models)
* Speech Recognition libraries
* JSON for data storage

---

## 📦 Project Structure

```
├── main.py              # Main execution file
├── voz.py               # Voice processing
├── comandos.py          # Command handling
├── funciones.py         # Core functions
├── emociones.py         # Emotion detection logic
├── modelo_emociones.pkl # Trained ML model
├── encoder_emociones.pkl
├── scaler_emociones.pkl
├── interfaz.py          # User interface
├── historial.json       # Interaction history
├── entrenar.py          # Model training script
```

---

## ⚙️ Installation

1. Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ Usage

Run the assistant with:

```bash
python main.py
```

---

## 🧪 Model Training

To retrain the emotion detection model:

```bash
python entrenar.py
```

---

## 📌 Future Improvements

* Improve NLP capabilities
* Add GUI enhancements
* Integrate APIs for extended functionality
* Optimize emotion detection accuracy

---

## 👨‍💻 Author

Developed by Benjamín Palazzo

---

## 📄 License

This project is open-source and available under the MIT License.
