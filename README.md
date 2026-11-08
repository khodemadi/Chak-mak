The Feed

A lightweight desktop application built with Rust, Tauri v2, and HTML/CSS/JavaScript, designed to retrieve and display feed data through a structured API contract.

The project follows a modular architecture that separates the desktop application, user interface, API integration, and backend communication.

Overview

The Feed is designed to provide a foundation for a desktop feed reader with a clear separation between frontend and backend components.

The project currently includes:

- A desktop application powered by Rust and Tauri v2.
- An HTML/CSS/JavaScript-based user interface.
- A Python-based mock API for development and testing.
- A shared JSON API contract.
- API validation utilities.
- A Rust-based API client using "reqwest".

Architecture

                  ┌──────────────────────┐
                  │      API Server      │
                  │   Mock / Real API    │
                  └──────────┬───────────┘
                             │
                        HTTP / JSON
                             │
                  ┌──────────▼───────────┐
                  │      Rust Backend    │
                  │      Tauri v2        │
                  │       reqwest        │
                  └──────────┬───────────┘
                             │
                  ┌──────────▼───────────┐
                  │     Desktop UI       │
                  │    HTML / CSS / JS   │
                  └──────────────────────┘

Project Structure

Chak-mak/
├── docs/
│   └── api-contract.md
│
├── mock-api/
│   ├── server.py
│   └── validate.py
│
├── src-tauri/
│   └── Rust / Tauri application
│
├── ui/
│   └── HTML / CSS / JavaScript interface
│
├── api-contract.md
└── README.md

Tech Stack

Technology| Purpose
Rust| Backend application logic
Tauri v2| Desktop application framework
HTML| UI structure
CSS| UI styling
JavaScript| Frontend interactions
Python| Mock API server
Flask| API development
Reqwest| HTTP communication
JSON| API communication format

Requirements

Before running the project, make sure the following tools are installed:

- Python 3
- Rust
- Cargo
- Tauri v2 system dependencies
- Git

For Tauri prerequisites, see the official documentation:

https://v2.tauri.app/start/prerequisites/

Getting Started

1. Clone the Repository

git clone https://github.com/khodemadi/Chak-mak.git

cd Chak-mak

2. Install Python Dependencies

pip install flask

3. Start the Mock API

Run the mock API server:

python mock-api/server.py

The mock API is expected to run on:

http://127.0.0.1:8000

Keep this terminal running.

4. Install Tauri CLI

Install Tauri CLI v2:

cargo install tauri-cli --version "^2"

5. Generate Application Icons

Navigate to the Tauri directory:

cd src-tauri

Generate the application icons:

cargo tauri icon path/to/any-square.png

Replace "path/to/any-square.png" with the path to your image.

6. Run the Desktop Application

cargo tauri dev

The desktop application should now launch.

Connecting to a Real API

The application can be configured to use a real API instead of the mock server.

THEFEED_API=http://host:port cargo tauri dev

Replace "http://host:port" with your actual API endpoint.

Testing

Rust Tests

Run the Rust tests:

cd src-tauri

cargo test

API Validation

Run the API validation script:

python mock-api/validate.py http://127.0.0.1:8000

This script checks the API against the expected contract.

API Contract

The API contract defines the expected JSON structure shared between the backend and the desktop application.

Reference:

docs/api-contract.md

The contract serves as a common reference for frontend and backend development.

Development

The project is structured to allow independent development of the desktop application and API.

- Frontend development can proceed using the mock API.
- Backend development can follow the shared API contract.
- API responses can be validated independently.
- The real API can replace the mock implementation without changing the overall development workflow.

Contributing

Contributions, bug reports, and suggestions are welcome.

When contributing:

1. Keep changes consistent with the existing architecture.
2. Follow the API contract when modifying API-related functionality.
3. Test changes before submitting a pull request.
4. Clearly document any changes to the API structure.

License

The license has not yet been specified.

Please check the repository for licensing information before redistributing or using the project commercially.
