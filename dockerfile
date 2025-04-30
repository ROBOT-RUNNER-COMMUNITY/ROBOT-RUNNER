FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install pyinstaller \
    && pyinstaller --noconfirm --onefile --windowed \
       --name RobotTestRunner \
       --add-data "robotframework-4.0.3-py3.11.egg:." \
       --add-data "robotframework-seleniumlibrary-5.1.3-py3.11.egg:." \
       --add-data "robotframework-selenium2library-3.0.0-py3.11.egg:." \
       --add-data "robotframework-requests-0.9.0-py3.11.egg:." \
       --add-data "robotframework-httplibrary-3.0.0-py3.11.egg:." \
       --add-data "robotframework-selenium2library-3.0.0-py3.11.egg:." \
       --add-data "robotframework-seleniumlibrary-5.1.3-py3.11.egg:." \
       --add-data "robotframework-requests-0.9.0-py3.11.egg:." \
       --add-data "robotframework-httplibrary-3.0.0-py3.11.egg:." \
       --add-data "robotframework-4.0.3-py3.11.egg:." \
       --add-data "robotframework-seleniumlibrary-5.1.3-py3.11.egg:." \
       --add-data "robotframework-selenium2library-3.0.0-py3.11.egg:." \
       --add-data "robotframework-requests-0.9.0-py3.11.egg:." \
       --add-data "robotframework-httplibrary-3.0.0-py3.11.egg:." \
       --add-data "robotframework-selenium2library-3.0.0-py3.11.egg:." \
       --add-data "robotframework-seleniumlibrary-5.1.3-py3.11.egg:." \
       --add-data "robotframework-requests-0.9.0-py3.11.egg:." \
       --add-data "robotframework-httplibrary-3.0.0-py3.11.egg:." \
       --add-data "robotframework-selenium2library-3.0.0-py3.11.egg:." \
       --add-data "robotframework-seleniumlibrary-5.1.3-py3.11.egg:." \
       --add-data "robotframework-requests-0.9.0-py3.11.egg:." \
       --add-data "robotframework-httplibrary-3.0.0-py3.11.egg:." \
       --add-data "style/style.qss:style" \
       --add-data "image copy.png:." \
       main.py

CMD ["./dist/RobotTestRunner"]