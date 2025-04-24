# Social Media Details

A simple API service that fetches user data from major social media platforms including Facebook, Instagram, LinkedIn, and Twitter/X.

## Overview

Social Media Details provides a unified API to retrieve user profiles, recent posts, images, and other public information from popular social media platforms. The service organizes the data in a structured format and saves media files locally.

## Features

- Fetch user profile information from Facebook, Instagram, LinkedIn, and Twitter/X
- Download profile pictures and post images
- Extract post captions and other metadata
- Organized data storage structure for each platform

## Live Demo

The API is deployed at: [https://socialmediadeatils.onrender.com](https://socialmediadeatils.onrender.com)

## Installation

Clone the repository:

```bash
git clone https://github.com/SimpleCyber/SocialMediaDeatils.git
cd SocialMediaDeatils
```

Install required dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python app.py
```

The server will start at `http://localhost:5000`.

## API Usage

### Endpoint Structure

```
GET /<platform>/<username>
```

Where:
- `platform` is one of: `facebook`, `instagram`, `linkedin`, `twitter`, or `x`
- `username` is the user's handle on the respective platform

### Example Requests

```
GET /facebook/zuck
GET /instagram/zuck
GET /linkedin/billgates
GET /twitter/elonmusk
GET /x/elonmusk
```

### Response Format

A successful response will have the following structure:

```json
{
  "success": true,
  "platform": "platform_name",
  "username": "requested_username",
  "data": {
    // Platform-specific data structure
  }
}
```

## Postman Testing

Here are examples for testing the API with Postman:

### 1. Facebook User Details

- **Method**: GET
- **URL**: `https://socialmediadeatils.onrender.com/facebook/zuck`
- **Headers**: None required

### 2. Instagram User Details

- **Method**: GET
- **URL**: `https://socialmediadeatils.onrender.com/instagram/zuck`
- **Headers**: None required

### 3. LinkedIn User Details

- **Method**: GET
- **URL**: `https://socialmediadeatils.onrender.com/linkedin/billgates`
- **Headers**: None required

### 4. Twitter/X User Details

- **Method**: GET
- **URL**: `https://socialmediadeatils.onrender.com/twitter/elonmusk`
- **Headers**: None required

Alternative for Twitter:
- **Method**: GET
- **URL**: `https://socialmediadeatils.onrender.com/x/elonmusk`
- **Headers**: None required

## Error Handling

If an error occurs, the API will return:

```json
{
  "success": false,
  "error": "Error message details"
}
```

## Repository

The source code is available on GitHub: [https://github.com/SimpleCyber/SocialMediaDeatils](https://github.com/SimpleCyber/SocialMediaDeatils)
