# shopify-challenge-winter-2022

An image repository with authentication and file permissions!

## Building + Running

To build, run

```
docker-compose build
```

To run, 

```
docker-compose up
```

## Usage

Example queries are all in Postman! If you want to create/delete users, add images, etc. Each query has
specific example parameters and tests with it! An admin can create users with its own REST calls and then
supply the access token to the user. All authentication is done via the token header, as shown in postman.

To use postman, import all the files in `/postman` to get the necessary collections and global environment variables.    
\*Note: You must set your Postman working directory to be this repository so it can view `/test_data`, which contains the images used in the example requests.
![Postman Import Demo](https://github.com/CalderWhite/shopify-challenge-winter-2022/raw/master/demo_videos/postman_import_demo.gif)

Some of the features include...    

Uploading and getting public images:
![Public Demo](https://github.com/CalderWhite/shopify-challenge-winter-2022/raw/master/demo_videos/public_demo.gif)

Creating private images that only you can access:
![Private Demo](https://github.com/CalderWhite/shopify-challenge-winter-2022/raw/master/demo_videos/private_demo.gif)



## Testing

All tests are built into Postman! Just click run on the "Admin Actions" and "Image Management" collections!

![Testing Demo](https://github.com/CalderWhite/shopify-challenge-winter-2022/raw/master/demo_videos/test_demo.gif)

