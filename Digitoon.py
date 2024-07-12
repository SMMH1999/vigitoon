import re
import json
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from MySQL import query_executor

def parse_log(log_line):
    """
    Parses a single log line into a dictionary of its components.
    """
    log_pattern = re.compile(
        r'(?P<ip>\d+\.\d+\.\d+\.\d+|NULL) - - \[(?P<timestamp>[^\]]+)\] "(?P<method>\w+) (?P<url>[^\s]+) HTTP/1.1" (?P<status>\d+) (?P<size>\d+|-)'
    )
    match = log_pattern.match(log_line)
    if match:
        return match.groupdict()
    return None

def read_and_parse_logs():
    """
    Reads and parses the log file into a DataFrame.
    """
    log_entries = []
    with open('nginx_logs.txt', 'r') as file:
        for line in file:
            parsed_line = parse_log(line)
            if parsed_line:
                log_entries.append(parsed_line)
            else:
                print(f"Failed to parse line: {line}")

    data = pd.DataFrame(log_entries)
    data['query_params'] = data['url'].apply(lambda x: dict(param.split('=') for param in x.split('?')[1].split('&')) if '?' in x else {})
    data.to_csv('parsed_log_step_1.csv', index=False)
    return data

def clean_data(data):
    """
    Cleans the parsed log DataFrame.
    """
    data['query_params'] = data['query_params'].apply(json.dumps)
    data.drop_duplicates(subset=['ip', 'timestamp', 'method', 'url', 'status', 'size', 'query_params'], inplace=True)
    data.replace(to_replace=r'(NULL|-)+', value=None, regex=True, inplace=True)
    data.dropna(axis=0, how='any', inplace=True)
    data.to_csv('parsed_log_step_2.csv', index=False)
    return data

def setup_database():
    """
    Sets up the MySQL database for storing log data.
    """
    query_executor(None, "CREATE DATABASE IF NOT EXISTS log_analysis")
    query_executor(
        'log_analysis',
        """
        CREATE TABLE IF NOT EXISTS logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ip VARCHAR(255),
            timestamp DATETIME,
            method VARCHAR(255),
            url TEXT,
            status INT,
            size INT,
            query_params JSON
        )
        """
    )

def save_data_to_db(data):
    """
    Saves the cleaned log data into the MySQL database.
    """
    for index, row in data.iterrows():
        try:
            ip = row['ip']
            timestamp = datetime.strptime(row['timestamp'], '%d/%b/%Y:%H:%M:%S %z')
            method = row['method']
            url = row['url']
            status = row['status']
            size = row['size']
            query_params = json.dumps(row.get('query_params', {}))

            query_executor(
                'log_analysis',
                """
                INSERT INTO logs (ip, timestamp, method, url, status, size, query_params)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                ip, timestamp, method, url, status, size, query_params
            )
        except Exception as e:
            print(f"Error saving row {index} to database: {e}")

def visualize_requests_per_ip(data):
    """
    Visualizes the number of requests per IP address.
    """
    ip_counts = data['ip'].value_counts()
    plt.figure(figsize=(10, 6))
    ip_counts.plot(kind='bar')
    plt.title(f'Number of Requests per IP Address (Total IPs: {data["ip"].nunique()})')
    plt.xlabel('IP Address')
    plt.ylabel('Number of Requests')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

def visualize_unique_urls_per_ip(data):
    """
    Visualizes the number of unique URLs requested per IP address.
    """
    ip_url_counts = data.groupby('ip')['url'].nunique()
    plt.figure(figsize=(10, 6))
    ip_url_counts.plot(kind='bar')
    plt.title('Number of Unique URLs Requested per IP Address')
    plt.xlabel('IP Address')
    plt.ylabel('Number of Unique URLs')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

def visualize_status_code_distribution(data):
    """
    Visualizes the distribution of status codes in the log data.
    """
    sns.countplot(x="status", data=data)
    plt.title("Distribution of Status Codes")
    plt.show()

def visualize_http_method_distribution(data):
    """
    Visualizes the distribution of HTTP methods in the log data.
    """
    sns.countplot(x="method", data=data)
    plt.title("Distribution of HTTP Methods")
    plt.show()

def visualize_requests_per_hour(data):
    """
    Visualizes the number of requests per hour.
    """
    data['timestamp'] = pd.to_datetime(data['timestamp'], format='%d/%b/%Y:%H:%M:%S %z')
    data['hour'] = data['timestamp'].dt.hour
    sns.countplot(x="hour", data=data)
    plt.title("Number of Requests per Hour")
    plt.show()

def visualize_transferred_bytes_by_status(data):
    """
    Visualizes the sum of transferred bytes by status code.
    """
    data['size'] = pd.to_numeric(data['size'], errors='coerce')
    status_wise_sum = data.groupby('status')['size'].sum() / (1024**2)  # in MB
    sns.barplot(x=status_wise_sum.index, y=status_wise_sum.values)
    plt.xlabel("Status Code")
    plt.ylabel("Sum of Transferred Bytes (MB)")
    plt.title("Sum of Transferred Bytes by Status Code (in MB)")
    plt.show()

if __name__ == '__main__':
    data = read_and_parse_logs()
    data = clean_data(data)
    # setup_database()
    # save_data_to_db(data)

    # Visualizing
    # visualize_requests_per_ip(data)
    # visualize_unique_urls_per_ip(data)
    # visualize_status_code_distribution(data)
    # visualize_http_method_distribution(data)
    # visualize_requests_per_hour(data)
    # visualize_transferred_bytes_by_status(data)
