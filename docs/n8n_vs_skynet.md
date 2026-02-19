# Why We Don't Use n8n on Termux (Android)

## 1. Resource Consumption (RAM/CPU)
- **n8n**: Requires Node.js runtime, often consumes 500MB+ RAM just to idle. On a phone, this drains battery and kills background processes.
- **Skynet (Our Core)**: Written in pure Python. Consumes <50MB RAM. Designed specifically for mobile architecture.

## 2. Complexity vs Speed
- **n8n**: Great for visual workflows, but adds latency (overhead).
- **Skynet**: Hardcoded logic (`if battery < 20: stop`). Microsecond execution time.

## 3. The "God Mode" Philosophy
We want a single, self-contained executable (`python main.py`). Adding n8n introduces an external dependency that breaks the "One Click Run" philosophy.

**Verdict:**
Skynet **IS** your n8n, but evolved for Cyber Operations on Mobile.
