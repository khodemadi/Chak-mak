# Chak-mak

A lightweight, extensible desktop application built with **Rust, Tauri v2, and HTML/CSS/JavaScript**, designed to fetch and display feed data through a structured API.

---

## About the Project

Chak-mak is a foundation for building a desktop application with a modular architecture, where the user interface, application logic, and API communication are kept separate.

### Features

- Desktop app development with Rust and Tauri v2
- UI based on HTML, CSS, and JavaScript
- Python-based mock API for development and testing
- Shared JSON-based API contract
- API validation tools
- HTTP communication via the Reqwest library
- Extensible, with support for connecting to a real API

---

## Architecture

```text
                ┌─────────────────────┐
                │      API Server     │
                │    Mock / Real API  │
                └──────────┬──────────┘
                           │
                      HTTP / JSON
                           │
                ┌──────────▼──────────┐
                │    Rust Backend    │
                │      Tauri v2      │
                │       Reqwest      │
                └──────────┬──────────┘
                           │
                ┌──────────▼──────────┐
                │     Desktop UI     │
                │   HTML / CSS / JS  │
                └────────────────────┘
```

---

## Project Structure

```text
Chak-mak/
├── docs/
│   └── api-contract.md
├── mock-api/
│   ├── server.py
│   └── validate.py
├── src-tauri/
├── ui/
├── api-contract.md
└── README.md
```

---

## Technologies Used

| Technology | Purpose |
|---|---|
| Rust | Application logic |
| Tauri v2 | Building the desktop app |
| HTML | UI structure |
| CSS | UI styling |
| JavaScript | Client-side interactions |
| Python | Mock API development |
| Flask | API implementation |
| Reqwest | HTTP communication |
| JSON | Data exchange format |

---

## Prerequisites

| Tool | Description |
|---|---|
| Python 3 | Running the mock API |
| Rust | Core application development |
| Cargo | Rust dependency management |
| Tauri v2 Dependencies | Required dependencies |
| Git | Version control |

[Official Tauri documentation](https://v2.tauri.app/start/prerequisites/)

---

## Installation and Setup

### 1. Get the project

```bash
git clone https://github.com/khodemadi/Chak-mak.git
cd Chak-mak
```

### 2. Install Python dependencies

```bash
pip install flask
```

### 3. Run the mock API

```bash
python mock-api/server.py
```

API address:

```text
http://127.0.0.1:8000
```

### 4. Install the Tauri CLI

```bash
cargo install tauri-cli --version "^2"
```

### 5. Generate the app icon

```bash
cd src-tauri
cargo tauri icon path/to/any-square.png
```

### 6. Run the app

```bash
cargo tauri dev
```

---

## Connecting to a Real API

```bash
THEFEED_API=http://host:port cargo tauri dev
```

Replace `http://host:port` with the address of the real API.

---

## Testing and Validation

### Run Rust tests

```bash
cd src-tauri
cargo test
```

### Validate the API

```bash
python mock-api/validate.py http://127.0.0.1:8000
```

---

## API Contract

| File | Description |
|---|---|
| `docs/api-contract.md` | API contract documentation |
| `api-contract.md` | API structure reference |

---

## Development

- Develop the UI against the mock API
- Develop the Rust side based on the API contract
- Independently validate API responses
- Replace the mock API with the real API
- Develop application components modularly

---

## Contributing

Bug reports, suggestions, and developer contributions are welcome.

1. Preserve the project's architectural structure.
2. Make API changes in accordance with the contract.
3. Run the tests before submitting changes.
4. Document any structural API changes.
5. Submit changes via Pull Request.

---

## License

The project's official license has not yet been determined.

Check the project's license status before commercial use or redistribution.
