# ImageIQ
REST API for photo share
The main functionality for the REST API is implemented on FastAPI

Authentication
1.	Create an authentication mechanism. We use JWT tokens.
2.	Users have three roles. A regular user, a moderator, and an administrator. The first user in the system is always the administrator. 
3.	To implement different levels of access (regular user, moderator, and administrator), we can use FastAPI decorators to validate the user's token and role.
4.	Users can reset the password via email. Users can also change the password.

Working with photos
1.	Users can upload photos with a description (POST).
2.	Users can delete photos (DELETE).
3.	Users can edit the description of the photo (PUT).
4.	Users can retrieve a photo by a unique link (GET).
5.	Ability to add up to 5 tags to a photo. Adding a tag is not required when uploading a photo.
6.	Tags are unique for the entire application. The tag is transmitted to the server by name. If such a tag does not exist, it is created, if it does exist, an existing tag with the same name is taken for the photo.
7.	Users can perform basic operations on photos that are allowed by the Cloudinary service. You can choose a limited set of transformations on photos for your application from Cloudinary.
8.	Users can create a link to the transformed image to view the photo in the form of a URL and a QR code. POST operation, since a separate link to the transformed image is created and stored in the database.
9.	The created links are stored on the server and we can scan the QR code and see the image via a mobile phone
10.	Administrators can do all CRUD operations with users' photos.

Commenting
1.	Under each photo, there is a block with comments. Users can comment on each other's photos.
2.	Users can edit their comments, but not delete them.
3.	Administrators and moderators can delete comments.
4.	For comments, it is mandatory to store the time of creation and the time of editing the comment in the database. To implement the functionality of comments, we can use a one-to-many relationship between photos and comments in the database. To temporarily mark comments, use the "created_at" and "updated_at" columns in the comments table.

Additional functionality
1.	Create a route for a user profile by its unique username. All information about the user should be returned. Name, when registered, number of uploaded photos, etc.
2.	The user can edit information about himself and see information about himself. These should be different routes with the user's profile. The profile is for all users, and the information for yourself is what can be edited.
3.	The administrator can make users inactive (ban). Inactive users cannot enter the application.
4.	The administrator can change the user's role. 

Additional functionality
1.	Implement a mechanism for users to log out of the application via logout. Access token should be added to the blacklist for the duration of its existence.
2.	Rating
- Users can rate a photo from 1 to 5 stars. The rating is calculated as the average of the ratings of all users. 
- You can rate a photo only once per user. 
- You cannot rate your own photos. 
- Moderators and administrators can view and delete user ratings.
3.	Search and filtering
- Users can search for photos by keyword or tag. After the search, the user can filter the results by rating or date of addition. 
- Moderators and administrators can search and filter by users who have added photos.
