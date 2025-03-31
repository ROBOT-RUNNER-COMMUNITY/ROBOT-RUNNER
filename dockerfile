FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install pyinstaller \
    && pyinstaller --noconfirm --onefile --windowed \
       --name RobotTestRunner \
       --add-data "style/style.qss:style" \
       --add-data "image copy.png:." \
       main.py

CMD ["./dist/RobotTestRunner"]