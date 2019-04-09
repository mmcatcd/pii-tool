# PII Detection Tool

Since the introduction of the General Data Protection Regulation (GDPR) by the European Union in 2018, companies and individuals alike have been looking for solutions to combat data privacy vulnerabilities in their data sources. This tool aims to  be a completely open-source, flexible, and scalable service to identify and act upon Personally Identifiable Information found in your data.

## Getting Started

Currently supported Data Sources:

* JSON
* MySQL Database
* CSV

### Prerequisites

* Python 3.5+ and it's associated package manager, 'pip'

  * Check python version in Linux/Windows/MacOS: `python -V`
  * Install python : [https://www.python.org/downloads/]()

### Installing

Clone or download the repo:

```
git clone https://github.com/mmcatcd/pii-tool.git
```

cd into the repo:

```
cd path/to/the/repo/pii-tool
```

Install the project dependencies:

```
pip install -r requirements.txt
```



## Usage
For CSV and JSON files make sure the file is in the same directory as the main pii_tool.py file.

Example usage:

Add some rules to the rules.txt file in the pii_tool folder (Create your own or use some from the provided European RegEx.csv), making sure that they reflect the data in YOUR source and then: 

```
python3 pii_tool.py -i tests/employees.json
```

```
python3 pii_tool.py -i tests/people.csv
```

```
python3 pii_tool.y -d hostname username database tablename
```



## Contributing

All contributions welcome, make sure to update the README with any relevant and significant changes to the interface/usage.

## License

This project is licensed under the MIT License - see the LICENCE file for details.

