# https://twelvedata.com/docs#income_statement

import csv
import requests
import json

# File paths
input_file_path = r"C:\Users\Wanderer\Documents\OSU to STANFORD\CS361\CS-361\pqrInput.csv"
output_file_path = r"C:\Users\Wanderer\Documents\OSU to STANFORD\CS361\CS-361\pqrOutput.csv"

# Polygon API Information
api_key = "8sJLC5HFPZM3Nq68mKGInCVToyXiOxpt"
api_endpoint_template = "https://api.polygon.io/vX/reference/financials?ticker={stock}&apiKey={api_key}"

# List of stocks to query API
stocks = []

# Read stock tickers from the input CSV, stocks must be in first column
with open(input_file_path, mode='r') as csv_file:
    csv_reader = csv.reader(csv_file)
    for row in csv_reader:
        # Stop if an empty row is encountered in the first column

        if not row[0]:
            break
        stocks.append(row[0])

headers = []

# Write to the output CSV
with open(output_file_path, mode='w', newline='') as csv_output:
    csv_writer = csv.writer(csv_output)

    for stock in stocks:
        # Now we insert the stock variable into the API endpoint
        api_endpoint = api_endpoint_template.format(stock=stock, api_key=api_key)
        try:
            response = requests.get(api_endpoint)
            response.raise_for_status()
            data = response.json()

            # Check and extract the most recent income statement
            most_recent_income_statement = None
            if 'results' in data and data['results']:
                sorted_financials = sorted(data['results'], key=lambda x: x['end_date'], reverse=True)
                most_recent_income_statement = next(
                    (item for item in sorted_financials if item['financials'].get('income_statement')), None
                )

            # Check if headers are not set and if there's a recent income statement
            if not headers and most_recent_income_statement:
                # Write the headers based on the keys of the income statement
                headers = ['ticker'] + list(most_recent_income_statement['financials']['income_statement'].keys())
                csv_writer.writerow(headers)

            # Write the row for the current stock
            if most_recent_income_statement:
                # Use .get method to avoid KeyError, provide a default value if key does not exist
                row = [stock] + [most_recent_income_statement['financials']['income_statement'].get(key, {}).get('value', 'No Data') for key in headers if key != 'ticker']
                csv_writer.writerow(row)
            else:
                # If no income statement is present for the most recent year, write "No Data"
                csv_writer.writerow([stock] + ["No Data"] * (len(headers) - 1))

        except requests.RequestException as e:
            # If there's an API error, write that instead of financial data
            csv_writer.writerow([stock] + ["API Error"] * (len(headers) - 1))
            print(f"API Error for {stock}: {e}")

print("CSV saved to", output_file_path)