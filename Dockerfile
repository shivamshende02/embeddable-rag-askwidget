# 1. Official Python slim image use karo
FROM python:3.10-slim

# 2. Container ke andar working directory set karo
WORKDIR /app

# 3. Apni requirements ya pyproject.toml copy karo
COPY pyproject.toml .

# 4. Dependencies install karo (agar aap pip use kar rahe hain)
RUN pip install --no-cache-dir .

# 5. Baaki ka saara project code copy karo
COPY . .

# 6. Port expose karo jo app use karegi
EXPOSE 8000

# 7. App run karne ki command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]