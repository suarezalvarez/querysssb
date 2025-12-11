# querysssb
This project automatically logs into SSSB (Stockholm Studentbostäder), scrapes all available apartments, stores them in a CSV, and generates a 7-day queue-days trend plot.

It is built with:

- Python + uv

- Selenium for automated browsing

- BeautifulSoup for HTML parsing

- plotnine for visualization


## Installation

You can install the necessary libraries doing:

```bash
uv sync
```
You need to have google chrome installed. 

Then you should create a file named `.env` in the root of the directory. Here you are going to store two environment variables that have
your credentials for SSSB:

```bash
USERNAME=your_sssb_username
PASSWORD=your_sssb_password
```

>[!NOTE]  
>It's important that you use exactly the same name for these variables


You can run directly the `doit.sh` script in two ways:

```bash
# make it executable 
chmod u+x doit.sh

# or run it with bash

bash runit.sh
```


This will scrap SSSB and show you the plot in PDF, that is stored in `storage`. 

# Project structure

```
├── automate.py
├── config
│   └── settings.py
├── doit.sh
├── main.py
├── pyproject.toml
├── README.md
├── report
│   └── plotandmail.py
├── scraper
│   └── listings.py
├── storage
│   ├── apartment_queue.pdf
│   └── apartments.csv
└── uv.lock
```