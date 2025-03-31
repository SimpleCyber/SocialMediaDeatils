from flask import Flask, jsonify, request
import requests
import json
import os
import http.client
from io import BytesIO

app = Flask(__name__)

# ---------------------- Facebook Functions ----------------------
def facebook_user_profile_information(url, username):
    """
    Fetches the profile information from the given Facebook page URL
    and saves the selected details into a JSON file.
    """
    base_dir = os.path.join(os.getcwd(), username)
    os.makedirs(base_dir, exist_ok=True)

    profile_dir = os.path.join(base_dir, f"{username}_profile")
    os.makedirs(profile_dir, exist_ok=True)

    # API endpoint and headers
    api_url = "https://facebook-pages-scraper2.p.rapidapi.com/get_facebook_pages_details"
    querystring = {"link": url}
    headers = {
        "x-rapidapi-key": "15c4fd52c7msh07c0a2768c2bdd3p1f6b5djsn0f9257862e61",
        "x-rapidapi-host": "facebook-pages-scraper2.p.rapidapi.com"
    }

    # Make the API request
    response = requests.get(api_url, headers=headers, params=querystring)
    if response.status_code == 200:
        data = response.json()[0]  # Extract the first item if the response is a list
        
        # Extract required fields
        profile_info = {
            "SocialMediaPlatform": "Facebook",
            "Bio": ((data.get("bio") or "") + (data.get("about_me_text_content") or "") + (data.get("description") or "")),
            "Followers": data.get("followers_count"),
            "AccountPrivacy": data.get("status"),
            "creation_date": data.get("creation_date"),
            "user_id": data.get("user_id"),
            "Name": data.get("about_me_text"),
            "Username": username,
        }

        image_url = data.get("image")
        facebook_save_profile_image(image_url, username, profile_dir)

        # Save profile_data.json in the profile directory
        caption_path = os.path.join(profile_dir, "profile_data.json")
        with open(caption_path, "w") as captions_info_file:
            json.dump(profile_info, captions_info_file, indent=4)

    else:
        profile_info = {
            "error": f"Failed to fetch profile information. Status code: {response.status_code}"
        }

    return profile_info

def facebook_save_profile_image(image_url, username, profile_dir):
    """
    Saves the profile image from the given image URL to a file named 'profile_pic.jpg'.
    """
    if not image_url:
        return None
        
    response = requests.get(image_url, stream=True)
    if response.status_code == 200:
        image_path = os.path.join(profile_dir, "profile_pic.jpg")
        with open(image_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        return image_path
    return None

def facebook_fetch_user_posts(page_url, username):
    base_dir = os.path.join(os.getcwd(), username)
    os.makedirs(base_dir, exist_ok=True)

    post_dir = os.path.join(base_dir, f"{username}_posts")
    os.makedirs(post_dir, exist_ok=True)

    caption_dir = os.path.join(base_dir, f"{username}_captions")
    os.makedirs(caption_dir, exist_ok=True)

    """
    Fetch the latest posts from a Facebook page, extract text, image URI, and user name,
    and save the data into captions.json. Download images to the post_pics folder.
    """
    api_url = "https://facebook-pages-scraper2.p.rapidapi.com/get_facebook_posts_details"
    querystring = {"link": page_url, "timezone": "UTC"}

    headers = {
        "x-rapidapi-key": "15c4fd52c7msh07c0a2768c2bdd3p1f6b5djsn0f9257862e61",
        "x-rapidapi-host": "facebook-pages-scraper2.p.rapidapi.com"
    }

    try:
        response = requests.get(api_url, headers=headers, params=querystring)
        if response.status_code == 200:
            data = response.json().get("data", {}).get("posts", [])

            post_details = []

            for i, post in enumerate(data[:3]):  # Limit to 3 posts
                # Extract post text
                text = post.get("values", {}).get("text", "No caption available")

                # Extract image URI
                photo_image = post.get("values", {}).get("photo_image", None)
                photo_image_url = None

                if isinstance(photo_image, str):  # If photo_image is a string, parse it
                    try:
                        photo_image_data = json.loads(photo_image)
                        photo_image_url = photo_image_data.get("uri", None)
                    except json.JSONDecodeError:
                        pass
                elif isinstance(photo_image, dict):  # If it's already a dict
                    photo_image_url = photo_image.get("uri", None)

                # Extract user name
                user_name = post.get("details", {}).get("name", "Unknown User")

                # Store post details
                post_details.append({
                    "user_name": user_name,
                    "Caption": text,
                })

                # Download image if available
                if photo_image_url:
                    try:
                        image_response = requests.get(photo_image_url, stream=True)
                        if image_response.status_code == 200:
                            image_path = os.path.join(post_dir, f'{username}_post_{i}.jpg')
                            with open(image_path, "wb") as file:
                                for chunk in image_response.iter_content(1024):
                                    file.write(chunk)
                    except Exception as e:
                        print(f"Failed to download image: {e}")

            caption_path = os.path.join(caption_dir, "captions.json")
            with open(caption_path, "w") as captions_info_file:
                json.dump(post_details, captions_info_file, indent=4)

        else:
            post_details = [{"error": f"Failed to fetch posts. Status code: {response.status_code}"}]

    except Exception as e:
        post_details = [{"error": f"An error occurred: {e}"}]

    return post_details

def facebook_process(username):
    base_url = "https://www.facebook.com/"
    url = base_url + username

    profile_info = facebook_user_profile_information(url, username)  
    post_info = facebook_fetch_user_posts(url, username)  
    
    data = {
        "profile_info": profile_info,
        "post_info": post_info
    }
    
    base_dir = os.path.join(os.getcwd(), username)
    profile_dir = os.path.join(base_dir, f"{username}_profile")
    os.makedirs(profile_dir, exist_ok=True)
    
    data_path = os.path.join(profile_dir, "data.json")
    with open(data_path, "w") as data_file:
        json.dump(data, data_file, indent=4)
        
    return data

# ---------------------- Instagram Functions ----------------------
def instagram_get_user_data(username):
    url = "https://instagram-scraper-api2.p.rapidapi.com/v1/info"
    querystring = {"username_or_id_or_url": username}
    headers = {
        'x-rapidapi-key': "acdfe0df04msh7a4e8b244eca339p1a58c6jsn344dbffe049a",
        'x-rapidapi-host': "instagram-scraper-api2.p.rapidapi.com"
    }
    # fetching the data from the api
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=10)
        response.raise_for_status()
        data = response.json()
        if 'data' in data:
            return data
        else:
            return {"error": "Invalid response structure from API."}
    except requests.exceptions.RequestException as e:
        print(f"Error fetching user data: {e}")
        return None

def instagram_save_profile_picture(url, username):
    try:
        img_data = requests.get(url).content

        base_dir = os.path.join(os.getcwd(), username)
        os.makedirs(base_dir, exist_ok=True)

        profile_dir = os.path.join(base_dir, f"{username}_profile")
        os.makedirs(profile_dir, exist_ok=True)

        img_filename = 'profile_pic.jpg'
        img_path = os.path.join(profile_dir, img_filename) 

        with open(img_path,'wb') as file:
            file.write(img_data)
         
        return img_path
    except Exception as e:
        print(f"Error saving profile picture: {e}")
        return None

def instagram_save_post_picture(img_url, username, post_index):
    try:
        base_dir = os.path.join(os.getcwd(), username)
        os.makedirs(base_dir, exist_ok=True)
        post_dir = os.path.join(base_dir, f"{username}_posts")
        os.makedirs(post_dir, exist_ok=True)

        img_data = requests.get(img_url).content
        img_filename = f'{username}_post_{post_index + 1}.jpg'
        img_path = os.path.join(post_dir, img_filename)
        
        with open(img_path, 'wb') as file:
            file.write(img_data)
            
        return img_path
    except Exception as e:
        print(f"Error saving post picture: {e}")
        return None

def instagram_get_recent_posts(username):
    url = "https://instagram-scraper-api2.p.rapidapi.com/v1.2/posts"
    querystring = {"username_or_id_or_url": username}
    headers = {
        'x-rapidapi-key': "acdfe0df04msh7a4e8b244eca339p1a58c6jsn344dbffe049a",
        'x-rapidapi-host': "instagram-scraper-api2.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=10)
        response.raise_for_status()
        data = response.json()

        if 'data' in data and 'items' in data['data']:
            posts = data['data']['items'][:10]
            for post_index, post in enumerate(posts):
                # Process posts
                post['caption_text'] = post.get('caption', {}).get('text', 'No caption text available')
                post['created_at'] = post.get('created_at', 'Unknown time')
                image_versions = post.get('image_versions', {}).get('items', [])
                post['image_url'] = image_versions[0]['url'] if image_versions else None
                if post['image_url']:
                    post['image_path'] = instagram_save_post_picture(post['image_url'], username, post_index)
            return posts
        else:
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching recent posts: {e}")
        return []

def instagram_profile_pic(username):
    user_data = instagram_get_user_data(username)
    if user_data and 'data' in user_data:
        profile_pic_url = user_data['data']['profile_pic_url']
        username = user_data['data']['username']
        profile_pic_path = instagram_save_profile_picture(profile_pic_url, username)
        return profile_pic_path
    return None

def instagram_process(username):
    user_data = instagram_get_user_data(username)
    if not user_data or 'error' in user_data:
        return {"error": f"Unable to fetch data for username: {username}"}

    base_dir = os.path.join(os.getcwd(), username)
    os.makedirs(base_dir, exist_ok=True)
    # caption
    caption_dir = os.path.join(base_dir, f"{username}_captions")
    os.makedirs(caption_dir, exist_ok=True)
    # profile
    profile_dir = os.path.join(base_dir, f"{username}_profile")
    os.makedirs(profile_dir, exist_ok=True)

    data = user_data.get('data', {})
    user_info = {
        "Username": data.get("username", "N/A"),
        "Name": data.get("full_name", "N/A"),
        "Bio": data.get("biography", "N/A"),
        "Followers": data.get("follower_count", 0),
        "Following": data.get("following_count", 0),
        "NumberOfPosts": data.get("media_count", 0),
        "Verified": "Yes" if data.get("is_verified") else "No",
        "AccountPrivacy": "Private" if data.get("is_private") else "Public",
        "Profile Picture Path": instagram_profile_pic(username),
        "SocialMediaPlatform": "Instagram",
    }

    try:
        posts = instagram_get_recent_posts(username)
        captions = [
            {"PostNumber": i + 1, "Caption": post.get("caption_text", "No caption available"), "Upload Time": post.get("created_at", "Unknown time")}
            for i, post in enumerate(posts)
        ]
    except Exception as e:
        posts = []
        captions = [
            {"PostNumber": 0, "Caption": "No captions available [PRIVATE ACCOUNT]", "Upload Time": "00:00:00"}
        ]

    profile_info_path = os.path.join(profile_dir, "profile_data.json")
    with open(profile_info_path, "w") as profile_info_file:
        json.dump(user_info, profile_info_file, indent=4)

    captions_path = os.path.join(caption_dir, "captions.json")
    with open(captions_path, "w") as captions_file:
        json.dump(captions, captions_file, indent=4)

    limited_captions = captions[:4]
    data = {
        "ProfileInfo": user_info,
        "Captions": limited_captions,
    }

    data_path = os.path.join(profile_dir, "data.json")
    with open(data_path, "w") as data_file:
        json.dump(data, data_file, indent=4)

    return data

# ---------------------- LinkedIn Functions ----------------------
def linkedin_fetch_linkedin_data(user_input):
    url = "https://linkedin-data-api.p.rapidapi.com/get-profile-data-by-url"

    # Check if input starts with "http"
    if user_input.startswith("http"):
        querystring = {"url": user_input}  # Use URL if it starts with "http"
    else:
        querystring = {"url": f"https://www.linkedin.com/in/{user_input}"}  # Construct URL if it's a username

    headers = {
        "x-rapidapi-key": "d65eb81e02mshd8f1eca29ba52b7p17caeajsn661881ae5f2c",
        "x-rapidapi-host": "linkedin-data-api.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200:
        data = response.json()
        result = {
            "Username": data.get("username"),
            "Name": data.get("firstName"),
            "lastName": data.get("lastName"),
            "isCreator": data.get("isCreator"),
            "isOpenToWork": data.get("isOpenToWork"),
            "isHiring": data.get("isHiring"),
            "profilePicture": data.get("profilePicture"),
            "Bio": data.get("summary"),
            "headline": data.get("headline"),
            "Verified": data.get("geo", {}).get("full"),
            "education": [edu.get("fieldOfStudy") for edu in data.get("education", []) if "fieldOfStudy" in edu],
            "SocialMediaPlatform": "LinkedIn"
        }

        # Save profile picture and data
        username = data.get("username")
        linkedin_save_profile_data(username, result)
        linkedin_save_profile_picture(username, data.get("profilePicture"))

        # Fetch post details using the username
        posts_data = linkedin_fetch_linkedin_posts(username)
        linkedin_save_post_data(username, posts_data)

        # Combine data for response
        result["Posts"] = posts_data
        return result
    else:
        return {"error": f"Failed to fetch data. Status code: {response.status_code}"}

def linkedin_fetch_linkedin_posts(username):
    url = "https://linkedin-data-api.p.rapidapi.com/get-profile-posts"

    querystring = {"username": username}

    headers = {
        "x-rapidapi-key": "d65eb81e02mshd8f1eca29ba52b7p17caeajsn661881ae5f2c",
        "x-rapidapi-host": "linkedin-data-api.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200:
        posts = response.json().get("data", [])
        post_details = []

        for index, post in enumerate(posts):
            image_url = None
            # Handle image URL from the list
            if post.get("image") and isinstance(post["image"], list) and len(post["image"]) > 0:
                image_url = post["image"][0].get("url")

            post_info = {
                "Caption": post.get("text"),
                "totalReactionCount": post.get("totalReactionCount"),
                "likeCount": post.get("likeCount"),
                "commentsCount": post.get("commentsCount"),
                "repostsCount": post.get("repostsCount"),
                "postUrl": post.get("postUrl"),
                "postedDate": post.get("postedDate"),
                "imageUrl": image_url
            }
            post_details.append(post_info)

            # Save post image
            linkedin_save_post_image(username, index, image_url)

        return post_details
    else:
        return [{"error": f"Failed to fetch posts. Status code: {response.status_code}"}]

def linkedin_save_profile_data(username, profile_data):
    base_dir = os.path.join(os.getcwd(), username)
    os.makedirs(base_dir, exist_ok=True)
    profile_dir = os.path.join(base_dir, f"{username}_profile")
    os.makedirs(profile_dir, exist_ok=True)
    with open(os.path.join(profile_dir, "profile_data.json"), "w") as file:
        json.dump(profile_data, file, indent=4)

    with open(os.path.join(profile_dir, "data.json"), "w") as file:
        json.dump(profile_data, file, indent=4)

def linkedin_save_profile_picture(username, profile_picture_url):
    if profile_picture_url:
        base_dir = os.path.join(os.getcwd(), username)
        os.makedirs(base_dir, exist_ok=True)
        profile_dir = os.path.join(base_dir, f"{username}_profile")
        os.makedirs(profile_dir, exist_ok=True)
        response = requests.get(profile_picture_url)
        if response.status_code == 200:
            with open(os.path.join(profile_dir, "profile_pic.jpg"), "wb") as file:
                file.write(response.content)

def linkedin_save_post_data(username, posts_data):
    base_dir = os.path.join(os.getcwd(), username)
    os.makedirs(base_dir, exist_ok=True)
    captions_dir = os.path.join(base_dir, f"{username}_captions")
    os.makedirs(captions_dir, exist_ok=True)
    with open(os.path.join(captions_dir, "captions.json"), "w") as file:
        json.dump(posts_data, file, indent=4)

def linkedin_save_post_image(username, index, image_url):
    if image_url:
        base_dir = os.path.join(os.getcwd(), username)
        os.makedirs(base_dir, exist_ok=True)
        posts_dir = os.path.join(base_dir, f"{username}_posts")
        os.makedirs(posts_dir, exist_ok=True)
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(os.path.join(posts_dir, f"{username}_post_{index + 1}.jpg"), "wb") as file:
                file.write(response.content)

def linkedin_process(username):
    return linkedin_fetch_linkedin_data(username)

# ---------------------- Twitter/X Functions ----------------------
def twitter_create_directory(path):
    os.makedirs(path, exist_ok=True)
    return path

def twitter_download_profile_image(profile_image_url, username):
    try:
        if profile_image_url:
            profile_images_dir = twitter_create_directory(os.path.join(os.getcwd(), username, f"{username}_profile"))
            response = requests.get(profile_image_url)
            if response.status_code == 200:
                filepath = os.path.join(profile_images_dir, "profile_pic.jpg")
                with open(filepath, 'wb') as file:
                    file.write(response.content)
                return filepath
            else:
                print(f"Failed to download profile image. HTTP Status: {response.status_code}")
        else:
            print("No profile image URL provided.")
    except Exception as e:
        print(f"Error downloading profile image: {e}")
    return None

def twitter_download_post_images(tweets, username):
    try:
        tweets_images_dir = twitter_create_directory(os.path.join(os.getcwd(), username, f"{username}_posts"))
        image_paths = []

        for index, tweet in enumerate(tweets):
            media_urls = tweet.get("media", [])
            for media_index, img_url in enumerate(media_urls):
                try:
                    response = requests.get(img_url)
                    if response.status_code == 200:
                        filename = f"{username}_post_{index}.jpg"
                        filepath = os.path.join(tweets_images_dir, filename)
                        with open(filepath, 'wb') as file:
                            file.write(response.content)
                        image_paths.append(filepath)
                except Exception as e:
                    print(f"Error downloading tweet image {img_url}: {e}")
        return image_paths
    except Exception as e:
        print(f"Error downloading post images: {e}")
        return []

def twitter_save_post_captions_to_json(tweets, username):
    try:
        # Create the nested directory for captions
        captions_dir = twitter_create_directory(os.path.join(os.getcwd(), username, f'{username}_captions'))

        # Define the filepath for the JSON file
        captions_filepath = os.path.join(captions_dir, "captions.json")

        captions = [{"Caption": tweet.get("text", "No caption available")} for tweet in tweets]
        
        with open(captions_filepath, "w", encoding="utf-8") as json_file:
            json.dump(captions, json_file, indent=4, ensure_ascii=False)
        
        return captions
    except Exception as e:
        print(f"Error saving post captions to JSON: {e}")
        return []

def twitter_fetch_user_details(username):
    try:
        conn = http.client.HTTPSConnection("twitter-api47.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': "5d54c973b7msh2418c169d4909b0p1e5362jsn1123fc1cd8ae",
            'x-rapidapi-host': "twitter-api47.p.rapidapi.com"
        }
        
        conn.request("GET", f"/v2/user/by-username?username={username}", headers=headers)
        res = conn.getresponse()
        

        if res.status != 200:
            print(f"Error: Received status code {res.status}")
            return None, None

        data = json.loads(res.read().decode("utf-8"))
        selected_fields = {
            'Username': data['legacy'].get('name'),
            'Name': data['legacy'].get('screen_name'),
            'Bio': data['legacy'].get('description'),
            'Followers': data['legacy'].get('normal_followers_count'),
            'Following': data['legacy'].get('friends_count'),
            'Verified': data.get('is_blue_verified'),
            'AccountPrivacy': data['verification_info'].get('is_identity_verified'),
            'profile_banner_url': data['legacy'].get('profile_banner_url'),
            'NumberOfPosts': data['legacy'].get('media_count'),
            'SocialMediaPlatform': "Twitter/X",
        }
        profile_dir = twitter_create_directory(os.path.join(os.getcwd(), username, f"{username}_profile"))
        profile_filepath = os.path.join(profile_dir, "profile_data.json")

        with open(profile_filepath, "w", encoding="utf-8") as json_file:
            json.dump(selected_fields, json_file, indent=4)

        return data, selected_fields
    except Exception as e:
        print(f"Error fetching user details: {e}")
        return None, None

def twitter_fetch_user_tweets(username, user_id, count=10):
    try:
        conn = http.client.HTTPSConnection("twitter-api47.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': "5d54c973b7msh2418c169d4909b0p1e5362jsn1123fc1cd8ae",
            'x-rapidapi-host': "twitter-api47.p.rapidapi.com"
        }
        
        conn.request("GET", f"/v2/user/tweets?userId={user_id}&count={count}", headers=headers)
        res = conn.getresponse()

        if res.status != 200:
            print(f"Error: Received status code {res.status} when fetching tweets")
            return None

        return json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"Error fetching tweets: {e}")
        return None

def twitter_process_tweets(tweets_raw_data):
    try:
        extracted_tweets = []

        for tweet_entry in tweets_raw_data.get("tweets", []):
            tweet_content = tweet_entry.get("content", {}).get("itemContent", {}).get("tweet_results", {}).get("result", {})
            legacy = tweet_content.get("legacy", {})

            tweet_text = (
                legacy.get("full_text") or
                legacy.get("text") or
                legacy.get("extended_tweet", {}).get("full_text") or
                "No text available"
            )

            media = legacy.get("extended_entities", {}).get("media", [])
            media_urls = [item.get("media_url_https") for item in media if item.get("type") == "photo"]

            extracted_tweets.append({
                "text": tweet_text,
                "created_at": legacy.get("created_at"),
                "media": media_urls,
            })

        return extracted_tweets
    except Exception as e:
        print(f"Error processing tweets: {e}")
        return []

def twitter_process(username):
    try:
        username = username.strip()

        raw_user_details, processed_user_details = twitter_fetch_user_details(username)

        if raw_user_details and processed_user_details:
            final_report = {"ProfileInfo": processed_user_details}

            user_id = raw_user_details.get("rest_id", None)

            if user_id:
                tweets_raw = twitter_fetch_user_tweets(username, user_id, count=10)

                if tweets_raw:
                    processed_tweets = twitter_process_tweets(tweets_raw)
                    final_report["tweets"] = processed_tweets

                    # Download profile image
                    profile_img_path = twitter_download_profile_image(processed_user_details.get("profile_banner_url"), username)
                    if profile_img_path:
                        processed_user_details["profile_image_path"] = profile_img_path

                    # Download post images
                    image_paths = twitter_download_post_images(processed_tweets, username)
                    if image_paths:
                        final_report["post_image_paths"] = image_paths

                    # Save post captions
                    captions = twitter_save_post_captions_to_json(processed_tweets, username)
                    if captions:
                        final_report["captions"] = captions

            # Save user details JSON
            user_dir = twitter_create_directory(os.path.join(os.getcwd(), username, f"{username}_profile"))
            json_filepath = os.path.join(user_dir, "data.json")
            with open(json_filepath, "w", encoding="utf-8") as json_file:
                json.dump(final_report, json_file, indent=4, ensure_ascii=False)
            
            return final_report
        else:
            return {"error": "Failed to fetch user details."}

    except Exception as e:
        return {"error": f"Unexpected error in main process: {e}"}

# ---------------------- API Routes ----------------------
@app.route('/<platform>/<username>', methods=['GET'])
def get_social_media_info(platform, username):
    """
    Main API endpoint that fetches and returns social media user information.
    
    Parameters:
    - platform: The social media platform (facebook, instagram, linkedin, twitter or x)
    - username: The username to fetch information for
    
    Returns:
    - JSON response with user information
    """
    try:
        platform = platform.lower()
        
        if platform == 'facebook':
            data = facebook_process(username)
        elif platform == 'instagram':
            data = instagram_process(username)
        elif platform == 'linkedin':
            data = linkedin_process(username)
        elif platform in ['twitter', 'x']:
            data = twitter_process(username)
        else:
            return jsonify({
                "success": False,
                "error": f"Unsupported platform: {platform}. Supported platforms are: facebook, instagram, linkedin, twitter/x"
            }), 400

        if data and not data.get('error'):
            return jsonify({
                "success": True,
                "platform": platform,
                "username": username,
                "data": data
            })
        else:
            return jsonify({
                "success": False,
                "error": data.get('error', 'Failed to fetch data')
            }), 404

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500
    

if __name__ == '__main__':
    app.run(debug=True)
