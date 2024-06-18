# ArmoniK.Admin.CLI

This project is part of the [ArmoniK](https://github.com/aneoconsulting/ArmoniK) project.
In particular it is a consitutent of its [Core](https://github.com/aneoconsulting/ArmoniK.Core)
component which, among its main functionalities, implements several gRPC services aiming to
provide a user with a robust task scheduler for a high throughput computing application.

The .proto files in the directory [./Protos/V1](https://github.com/aneoconsulting/ArmoniK.Api/tree/main/Protos/V1) 
provide the core data model and functionalities for ArmoniK and are used to generate the different SDKs.

## Requirements

In order to install the ArmoniK CLI in an isolated environment, you must have python3-venv installed on your machine.

```bash
sudo apt install python3-venv
```

## Installation

### Prerequisites

- Python 3.10
- pip (Python package installer)

### Setting up a Virtual Environment

It's a good practice to use a virtual environment to isolate your project dependencies. Create a virtual environment using `venv`:

```bash
python3 -m venv .venv
```

Activate the virtual environment:

* On Windows:

```powershell
.\.venv\Scripts\activate
```

* On Unix or MacOS:

```bash
source .venv/bin/activate
```

### Installing the project using pip

Once the virtual environment is activated, you can install the project using pip.

```bash
pip install armonik_cli
```

This will install the project and its dependencies.

### Installing the project from sources

You can also intall the project from sources by cloning the repository.

```bash
git clone git@github.com:aneoconsulting/ArmoniK.Admin.CLI.git
```

Navigate to the project directory and run:

```bash
pip install .
```

For development, you might want to install additional packages for testing, linting, etc. Install the development dependencies using:

```bash
pip install -e .[dev,tests]
```



## Contributing

Contributions are always welcome!

See [CONTRIBUTING.md](CONTRIBUTING.md) for ways to get started.

## License

[Apache Software License 2.0](LICENSE)
