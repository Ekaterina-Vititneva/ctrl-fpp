# 1. Use a lightweight base image with Python
FROM python:3.11-slim

# 2. Create and switch to a working directory
WORKDIR /app

# 3. Copy your backend code
COPY . /app

# 4. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Expose the port FastAPI will run on
EXPOSE 8000

# 6. Run uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
