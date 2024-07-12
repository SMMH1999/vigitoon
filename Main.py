# Importing the libraries
import re
import json
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.cluster import KMeans
from MySQL import query_executor


def parse_log(log_line):
    """
    Function 2 parsing the logs
    """

    # Regular expression to match the log entry
    log_pattern = re.compile(
        r'(?P<ip>\d+\.\d+\.\d+\.\d+|NULL) - - \[(?P<timestamp>[^\]]+)\] "(?P<method>\w+) (?P<url>[^\s]+) HTTP/1.1" (?P<status>\d+) (?P<size>\d+|-)'
    )

    # Parsing the logs with RegEx
    match = log_pattern.match(log_line)

    # Checking the results returned from RegEx.match()
    if match:
        return match.groupdict()
    return None


def ReadParse():
    # Read and parse the log file
    log_entries = []

    # Read logs file
    with open('nginx_logs.txt', 'r') as file:

        # Scroll file line by line
        for line in file:

            # Parsing log
            parsed_line = parse_log(line)
            if parsed_line:
                log_entries.append(parsed_line)
            else:

                # For debugging
                print(line)

    # Convert to DataFrame for easier handling
    df = pd.DataFrame(log_entries)

    # Extract query parameters
    df['query_params'] = df['url'].apply(lambda x: dict(param.split(
        '=') for param in x.split('?')[1].split('&')) if '?' in x else {})

    # Save to CSV for further steps
    df.to_csv('parsed_log_Step_1.csv', index=False)

    return df


def Cleaner(df):
    # Convert query_params column to a string representation
    df['query_params'] = df['query_params'].apply(json.dumps)

    # Remove duplicates based on all columns except 'query_params'
    df.drop_duplicates(subset=['ip', 'timestamp', 'method',
                               'url', 'status', 'size', 'query_params'], inplace=True)

    # Convert invalid data to NaN
    df.replace(to_replace=r'(NULL|-)+', value=None, regex=True, inplace=True)

    # Drop invalid data (if any)
    df.dropna(axis=0, how='any', inplace=True)

    # Save to CSV for further steps (optional)
    df.to_csv('parsed_log_Step_2.csv', index=False)

    # Return cleaned data
    return df


def MakeDB():
    """
        This function is used to work with MySQL DB
    """

    # Making a DataBase
    result = query_executor(
        None,
        """
            CREATE DATABASE IF NOT EXISTS log_analysis
        """
    )

    # Making a Tabale
    result = query_executor(
        'log_analysis',
        """
            CREATE TABLE IF NOT EXISTS logs 
            (
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


def SaveData(df):

    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        try:
            # Extract data from the row
            ip = row['ip']
            timestamp = datetime.strptime(
                row['timestamp'], '%d/%b/%Y:%H:%M:%S %z')
            method = str(row['method'])
            url = str(row['url'])
            status = row['status']
            size = row['size']

            # Safely handle potential missing query_params column
            query_params = json.dumps(row.get('query_params', {}))
            # query_params = str(row['query_params'])
        except KeyError as e:
            # Handle missing columns gracefully (optional)
            print(f"Error: Missing column '{e.name}' in row {index}")

        try:
            result = query_executor(
                'log_analysis',
                """
                    INSERT INTO logs (ip, timestamp, method, url, status, size, query_params)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                ip,
                timestamp,
                method,
                url,
                status,
                size,
                query_params
            )
        except:
            print(
                f'Error:{result} \n\tinsert data({ip},{timestamp},{method},{url},{status},{size},{query_params}) was with problem')


def Vis_1(df):
    # Count the number of unique IP addresses
    num_ips = df['ip'].nunique()

    # Count the number of requests per IP address
    ip_counts = df['ip'].value_counts()

    # Create a bar plot
    plt.figure(figsize=(10, 6))
    ip_counts.plot(kind='bar')
    plt.title(f'Number of Requests per IP Address (Total IPs: {num_ips})')
    plt.xlabel('IP Address')
    plt.ylabel('Number of Requests')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()


def Vis_2(df):

    # Count the number of unique URLs requested per IP address
    ip_url_counts = df.groupby('ip')['url'].nunique()

    # Create a bar plot
    plt.figure(figsize=(10, 6))
    ip_url_counts.plot(kind='bar')
    plt.title('Number of Unique URLs Requested per IP Address')
    plt.xlabel('IP Address')
    plt.ylabel('Number of Unique URLs')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()


def Vis_3(df):
    # Distribution of Status Codes
    sns.countplot(x="status", data=df)
    plt.title("Distribution of Status Codes")
    plt.show()


def Vis_4(df):
    # Distribution of Methods
    sns.countplot(x="method", data=df)
    plt.title("Distribution of HTTP Methods")
    plt.show()


def Vis_5(df):

    data = []

    # Time Series - Requests per Hour
    for index, row in df.iterrows():
        data.append(datetime.strptime(
            row['timestamp'], '%d/%b/%Y:%H:%M:%S %z'))

    timeData = pd.DataFrame(data)

    timeData['hour'] = pd.to_datetime(timeData[0]).dt.hour
    sns.countplot(x="hour", data=timeData)
    plt.title("Number of Requests per Hour")
    plt.show()


def Vis_6(df):

    # Convert size column to numeric before plotting sum
    df['size'] = pd.to_numeric(df['size'].str.replace(
        ',', ''), errors='coerce')  # Handle commas and potential errors

    # Define conversion factor based on your preference (KB or MB)
    conversion_factor = 1024**2  # Change to 1024 for KB or 1024**2 for MB

    # Calculate sum of transferred bytes per status code in chosen units
    status_wise_sum = df.groupby('status')['size'].sum() / conversion_factor

    # Format labels with units (KB or MB)
    status_wise_sum = status_wise_sum.apply(
        lambda x: f"{x:.2f} {('KB' if conversion_factor == 1024 else 'MB')}")

    # Scatter plot to visualize sum of transferred bytes (formatted)
    # Use barplot for sum visualization
    sns.barplot(x=status_wise_sum.index, y=status_wise_sum.values)
    plt.xlabel("Status Code")
    plt.ylabel("Sum of Transferred Bytes")
    plt.title(
        f"Sum of Transferred Bytes by Status Code ({'in KB' if conversion_factor == 1024 else 'in MB'})")
    plt.show()


if __name__ == '__main__':
    data = ReadParse()
    data = Cleaner(data)
    # MakeDB()
    # SaveData(data)

    # Visualizing
    # Vis_1(data)
    # Vis_2(data)
    # Vis_3(data)
    # Vis_4(data)
    # Vis_5(data)
    # Vis_6(data)
