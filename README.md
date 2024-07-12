# Log Analysis Of Vigitoon

## Overview

This tool processes and analyzes Nginx log files. It parses log entries, cleans the data, stores it in a MySQL database, and provides various visualizations for insights.

## Features

- **Log Parsing**: Extracts components from log entries.
- **Data Cleaning**: Removes duplicates and invalid entries.
- **Database Integration**: Stores parsed data into a MySQL database.
- **Visualizations**: Provides insights through various plots.

## Requirements

- Python 3.x
- Required Libraries:
  - `re`
  - `json`
  - `seaborn`
  - `pandas`
  - `matplotlib`
  - `datetime`
  - `sklearn`
  - `MySQL (Optional)`

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/SMMH1999/vigitoon.git
    cd vigitoon
    ```

2. Install the required Python libraries:
    ```bash
    pip install -r requirements.txt
    ```

3. Configure MySQL connection in `MySQL.py`.

## Usage

1. **Parse and Clean Logs:**
    ```python
    data = read_and_parse_logs()
    data = clean_data(data)
    ```

2. **Setup Database:**
    Uncomment the following lines in the main section:
    ```python
    setup_database()
    save_data_to_db(data)
    ```

3. **Visualizations:**
    Uncomment the desired visualization functions in the main section:
    ```python
    visualize_requests_per_ip(data)
    visualize_unique_urls_per_ip(data)
    visualize_status_code_distribution(data)
    visualize_http_method_distribution(data)
    visualize_requests_per_hour(data)
    visualize_transferred_bytes_by_status(data)
    ```

4. **Run the Script:**
    ```bash
    python log_analysis.py
    ```

## Visualizations

- **Requests per IP Address**: Bar plot showing the number of requests per IP.
- **Unique URLs per IP**: Bar plot showing the number of unique URLs requested by each IP.
- **Status Code Distribution**: Count plot showing the distribution of HTTP status codes.
- **HTTP Method Distribution**: Count plot showing the distribution of HTTP methods.
- **Requests per Hour**: Count plot showing the number of requests per hour.
- **Transferred Bytes by Status Code**: Bar plot showing the sum of transferred bytes by status code.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes or improvements.
