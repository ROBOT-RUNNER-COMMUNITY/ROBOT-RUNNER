
<h1 align="center">
  <br>
  <a href="ROBBOT RUNNER"><img src="images/Logo.png" width="300"></a>
  <br>
  ROBOT RUNNER
  <br>
</h1>
<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#download">Download</a> •
  <a href="#credits">Credits</a> •
</p>

## Table of Contents
- [Table of Contents](#table-of-contents)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Steps to Install](#steps-to-install)
- [Building the Application](#building-the-application)
  - [Steps to Build](#steps-to-build)
- [Building an Executable](#building-an-executable)
  - [Steps to Build the Executable using a pre-build script shell](#steps-to-build-the-executable-using-a-pre-build-script-shell)
  - [Steps to Build the Executable](#steps-to-build-the-executable)
- [Contributing](#contributing)

## Installation

### Prerequisites
Before you can run or contribute to the project, ensure you have the following installed:

- Python (version 3.6+)
- pip (Python package installer)
- Robot Framework
- PyQt6 (for GUI)
- pabot (optional, for parallel test execution)

### Steps to Install

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/robot-runner.git
    cd robot-runner
    ```

2. Create a virtual environment (optional but recommended):

    ```bash
    python -m venv venv
    ```

3. Activate the virtual environment:

    - **Windows**:
        ```bash
        venv\Scripts\activate
        ```
    - **macOS/Linux**:
        ```bash
        source venv/bin/activate
        ```

4. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

5. (Optional) Install Robot Framework and Pabot globally if you don't have them:

    ```bash
    pip install robotframework
    pip install pabot
    ```

## Building the Application

If you'd like to modify and build the application from source, follow these steps.

### Steps to Build

1. Install the required dependencies:

    Run the following command to ensure all dependencies are installed:

    ```bash
    pip install -r requirements.txt
    ```

2. Run the application:

    You can run the app directly with:

    ```bash
    python main.py
    ```

## Building an Executable

If you need to distribute the application to users without requiring them to install Python, you can build a standalone .exe file (for Windows) using PyInstaller.

### Steps to Build the Executable using a pre-build script shell
In order to generate the executable `exe` file you just need to run the script :

1. For Linux:
    ```bash
    sudo apt get bash
    bash ./build.sh
    ```
2. For windows:
    ```bash
    ./build.sh
    ```

### Steps to Build the Executable

1. Install PyInstaller:

    ```bash
    pip install pyinstaller
    ```

2. Create the executable:

    Run the following command in the project root directory to build the .exe file:

    ```bash
    pyinstaller --onefile --windowed main.py
    ```

    - `--onefile`: Bundles everything into a single executable file.
    - `--windowed`: Prevents a command prompt window from appearing when you run the app (for GUI apps).

    After building, you can find the `.exe` file in the `dist` folder.

3. (Optional) If you want to package the .exe with additional resources (e.g., icons, images), you can modify the PyInstaller command to include them:

    ```bash
    pyinstaller --onefile --windowed --add-data "./style/style.qss;style" --add-data "images/*;images" main.py
    ```

    Make sure to adjust paths as needed for your project structure.

## Contributing

We welcome contributions! Here’s how you can get involved:

1. **Fork the Repository**  
   Visit the repository and click the Fork button at the top-right of the page to create your own copy of the repository.

2. **Clone Your Fork**  
   ```bash
   git clone https://github.com/your-username/robot-runner.git
   cd robot-runner

3. **Create a Branch**  
   It’s best to create a new branch for the feature or bug fix you want to work on:
   ```bash
   git checkout -b feature/your-feature
4. **Make Your Changes**  
   Modify the code or add features. Be sure to write tests to validate your changes (if applicable).

5. **Commit Your Changes**  
   Commit your changes with a descriptive message:
   ```bash
   git add .
   git commit -m "Add new feature or fix bug"
6. **Push to Your Fork**  
   Push your changes back to your fork on GitHub:
   ```bash
   git push origin feature/your-feature
7. **Open a Pull Request**  
   Once your changes are pushed, go to the GitHub page for your fork and create a pull request. Provide a clear description of what your changes do and why.

8. **Review and Merge**  
   After the pull request is reviewed, we will merge it into the main branch.
