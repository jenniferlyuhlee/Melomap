# Capstone Project 1 Proposal:
### Image-mapping Music Search
## Project Overview

|            | Description                                                                                                                                                                                                                                                                                                                                              | Fill in |
| ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| Tech Stack | What tech stack will you use for your final project? It is recommended to use the following technologies in this project: Python/Flask, PostgreSQL, SQLAlchemy, Heroku, Jinja, RESTful APIs, JavaScript, HTML, CSS. Depending on your idea, you might end up using WTForms and other technologies discussed in the course.|Front-End: HTML, CSS, JavScript <br> Back-End: Python/Flask, PostgreSQL, SQLAlchemy, RESTful APIs <br> Deployment: ElephantSQL, Render|
| Type       | Will this be a website? A mobile app? Something else? | Web app         |
| Goal       | What goal will your project be designed to achieve?  |Develop a web app that allows users to upload an image and receive a list of song recommendations in relation to the image utilizing AI image keywording technologies. Aims to provide an interesting exploration of music that is visual and feels more personal than just a simple search.|
| Users      | What kind of users will visit your app? In other words, what is the demographic of your users? | Any music lover looking to explore music randomly.|
| Data       | What data do you plan on using? How are you planning on collecting your data? You may have not picked your actual API yet, which is fine, just outline what kind of data you would like it to contain. You are welcome to create your own API and populate it with data. If you are using a Python/Flask stack, you are required to create your own API.                             |- Image file or url from user input <br> - (~5-10?) keywords obtained from AI image keyword generator API https://labs.everypixel.com/docs <br> - send keywords as part of query search to Spotify search API https://developer.spotify.com/documentation/web-api/reference/search <br> - return results to user|

## Project Breakdown


| Task Name                   | Description                                                                                                   | Labels                                                          |
| --------------------------- | ------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
|Identify functionality, features and components|Determine what will be necessary in the app to fulfill project objectives <br>- User authentication (login/signup) form <br>-User profile (basic information) <br>- Upload image form <br>- Display of song results where user can play song snippet <br>- A ‘listen later’ and favorites list where songs can be added(?)| Must have, Easy
| Design Database schema      | Determine the models and database schema required for your project.                                           | Must have, Hard |
| Source Your Data            | Determine where your data will come from. You may choose to use an existing API or create your own.           | Must have, Medium|
| User Flows                  | Determine user flow(s) - think about what you want a user’s experience to be like as they navigate your site. | Must have, Medium, Front-end |
| Set up backend and database | Configure the environmental variables on your framework of choice for development and set up database.        | Must have, Medium, Back-end |
| Set up frontend             | Set up frontend framework of choice and link it to the backend with a simple API call for example.            | Must have, Medium/Hard, Fullstack|
| User Authentication         | Fullstack feature - ability to authenticate (login and sign up) as a user                                     | Must have,Easy/Medium,Fullstack|
|Unit Testing|Run unit tests as I work to ensure components are working as expected, debugging any issues and handling errors|Must have, Easy/Medium,Back-end|
|Integrating Testing|Test that all components are working together, debugging any issues and handling errors|Must have, Medium/Hard, Fullstack|
|Deploy app|Deploy code with ElephantSQL and Render|Must have, Easy|

### Stretch Goals
* Connect to user’s spotify account so they can directly add to playlist
* Making the app more of a social platform where users can have followers, and share/like results
* Allowing video urls

### Potential Issues
* AI image keyword generators have limit on free tier
* Some keywords won’t have good “searchability” for Spotify search API
* Returning too many well-known and popular songs 
