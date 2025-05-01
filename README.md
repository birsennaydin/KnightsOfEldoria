# KnightsOfEldoria
# 🏰 Knights of Eldoria – AI Grid Simulation

**Knights of Eldoria** is a grid-based AI simulation written in Python. The simulation models a fantasy world where **Hunters**, **Knights**, **Treasures**, **Hideouts**, and **Garrisons** interact with each other through autonomous decision-making.

---

## 📂 Project Structure

---

## 🚀 How to Run

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/KnightsOfEldoria.git
cd KnightsOfEldoria
```

### 2. Set Up Virtual Environment (Recommended)

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 3. Run the Simulation

```bash
python view/main.py
```
This launches the GUI and starts the simulation loop.

### 🎮 Simulation Rules

| Entity        | Description                                                  |
|---------------|--------------------------------------------------------------|
| 🧍‍♂️ Hunter     | Roams the grid, collects treasures, and returns to hideouts. |
| 🤺 Knight      | Patrols the area, detects and detains hunters.              |
| 💰 Treasure    | Decays over time. Hunters prioritize high-value treasures.  |
| 🏚️ Hideout     | Stores hunters and treasures. Used for resting and recruitment. |
| 🏰 Garrison    | Provides energy recovery to knights.                        |

### 🔍 Features
✅ A* pathfinding for strategic movement

✅ Intelligent hunter and knight controllers

✅ Treasure decay and replacement logic

✅ Simulation ends when all treasures are depleted or all hunters die

✅ Optional sentiment analysis with TextBlob (disabled by default)

### 🧠AI Logging with Sentiment Analysis
To enable emotional logs based on hunter actions:

Install TextBlob:

```bash
pip install textblob
python -m textblob.download_corpora
```

Enable and use analyze_sentiment() from nlp/sentiment_analyzer.py inside hunter_controller.py.

### 🧪 Testing
Tests are located under the tests/ folder and follow standard Python unittest or pytest conventions.

### 🛠️ Customization
You can tweak simulation parameters for faster or slower execution in simulation_controller.py, such as:

Grid size

Number of entities

Decay rate of treasures

Energy/stamina drain and recovery rates

GUI render delay (time.sleep())

### 📜 License
MIT License – you are free to use, modify, and share this project.