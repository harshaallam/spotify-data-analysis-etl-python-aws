# Spotify Data End-to-End Analysis using AWS and Python

This project guides you through a Data Engineering journey, involving the ETL (Extract, Transform, Load) process by utilizing the Spotify API as the data source. Python and various AWS services are employed to accomplish this task.

## Architecture
![Architecture](Architecture.jpeg)

## Technologies Used:
- **Programming Language:** Python

### AWS Cloud Services:
1. **AWS S3 Bucket**
2. **AWS Lambda Function**
3. **AWS CloudWatch**
4. **AWS Glue Crawler**
5. **AWS Athena**

To pull **Top 50 Indian Songs** data from the Spotify application, you need API keys (Client ID and Client Secret). Create an account on Spotify and obtain your API keys from the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).

Initially, the code was developed in Jupyter Notebook (`src="SpotifyData_ETL@jupy.ipynb"`), and later it was implemented as an AWS Lambda function.

### Lambda Function Details:
- The Lambda function does not have the built-in **Spotipy** package, so you need to add a layer by externally uploading the Spotipy package as a ZIP file.
- Similarly, the **Pandas** package is not available by default in Lambda, but it can be added as a layer in the AWS Layers section.

### Lambda Functions Created:
1. **spotify-data-extract**: This function extracts data from the Spotify API and stores it in an S3 bucket as JSON files.
2. **spotify-data-transform-load-s3**: This function transforms the extracted data and stores the filtered data in the respective folders in CSV format.
