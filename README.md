# ImageIQ

## REST API for ImageIQ.
The main functionality for the REST API is implemented on FastAPI

## Links:

## General description:

### Authentication

- created an authentication mechanism. We use JWT tokens.
- users have three roles. A regular user, a moderator, and an administrator. The first user in the system is always the
  administrator.
- implemented different levels of access (regular user, moderator, and administrator), we can use FastAPI decorators to
  validate the user's token and role.
- users can reset the password via email. Users can also change the password.

### Working with photos

- users can upload photos with a description (POST).
- users can delete photos (DELETE).
- users can edit the description of the photo (PUT).
- users can retrieve a photo by a unique link (GET).
- ability to add up to 5 tags to a photo. Adding a tag is not required when uploading a photo.
- tags are unique for the entire application. The tag is transmitted to the server by name. If such a tag does not
  exist, it is created, if it does exist, an existing tag with the same name is taken for the photo.
- users can perform basic operations on photos that are allowed by the Cloudinary service. You can choose a limited set
  of transformations on photos for your application from Cloudinary.
- users can create a link to the transformed image to view the photo in the form of a URL and a QR code. POST operation,
  since a separate link to the transformed image is created and stored in the database.
- the created links are stored on the server and we can scan the QR code and see the image via a mobile phone
- administrators can do all CRUD operations with users' photos.

### Commenting

- under each photo, there is a block with comments. Users can comment on each other's photos.
- users can edit their comments, but not delete them.
- administrators and moderators can delete comments.
- for comments, it is mandatory to store the time of creation and the time of editing the comment in the database. To
  implement the functionality of comments, we can use a one-to-many relationship between photos and comments in the
  database. To temporarily mark comments, use the "created_at" and "updated_at" columns in the comments table.

### Additional functionality

- created a route for a user profile by its unique username. It returns information about the user: name, when
  registered, number of uploaded photos, etc.
- user can edit information about himself and see information about himself. These should be different routes with the
  user's profile. The profile is for all users, and the information for yourself is what can be edited.
- administrator can make users inactive (ban). Inactive users cannot enter the application.
- administrator can change the user's role.
- implement a mechanism for users to log out of the application via logout. .
- users can rate a photo from 1 to 5 stars. The rating is calculated as the average of the ratings of all users.
- you can rate a photo only once per user.
- you cannot rate your own photos.
- moderators and administrators can view and delete user ratings.
- users can search for photos by keyword or tag. After the search, the user can filter the results by rating or date of
  addition. 
