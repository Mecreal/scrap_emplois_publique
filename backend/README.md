# Web Scraper for Emploi Public

This project contains a Python script to scrape job listings from the Emploi Public website. The script runs every 6 hours and updates a JSON file with the latest job listings.

## Requirements

- Python 3.x
- `requests`
- `beautifulsoup4`
- `schedule`

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/emploi-public-scraper.git
   cd emploi-public-scraper
   ```

2. Install the required Python packages:
   ```sh
   pip install -r requirements.txt
   ```

## Usage

To run the scraper script:

```sh
python scraper.py
```

The script will run continuously and update the `something.json` file every 6 hours with new job listings from the Emploi Public website.

## Running the Script as a Background Process

### Using `screen` or `tmux`

1. Start a new session:
   ```sh
   screen -S scraper
   # or
   tmux new -s scraper
   ```

2. Run your script inside the session:
   ```sh
   python scraper.py
   ```

3. Detach from the session:
   ```sh
   Ctrl+A D  # for screen
   # or
   Ctrl+B D  # for tmux
   ```

### Using `nohup`

1. Run the script with `nohup` to keep it running after you log out:
   ```sh
   nohup python scraper.py &
   ```

### Using `systemd`

1. Create a service file `/etc/systemd/system/scraper.service`:
   ```ini
   [Unit]
   Description=Web Scraper

   [Service]
   ExecStart=/usr/bin/python /path/to/scraper.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

2. Enable and start the service:
   ```sh
   sudo systemctl enable scraper.service
   sudo systemctl start scraper.service
   ```

## Configuration

Ensure that your server has Python 3.x installed and the necessary permissions to run the script and create/update the `something.json` file.

### Dependencies

All dependencies are listed in the `requirements.txt` file. Install them using:
```sh
pip install -r requirements.txt
```

## License

This project is licensed under the MIT License.




