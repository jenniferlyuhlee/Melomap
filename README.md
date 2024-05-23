# Capstone Project One: Melomap

## Deployed At: [Melomap](https://melomap.onrender.com/)

## Description:

Melomap is an AI-powered music searching app that allows users to upload their own photos and get back related song recommendations that are mapped to their photo. The app aims to provide an innovative and more personalized method for music exploration. Or, it'll help you find the perfect song for your next post.

## Features:

- User profiles - Personalization to the app that allows users to display their information, results, and bookmarked songs. Users can easily view other profiles to further explore music and build a community.
- Uploading image files - To further personalize the app and provide convenience, the app allows photo file uploads directly from the user's device.
- Sharing search results as posts - This sharing feature brings a social aspect to the app that enables more music exploration through eachother's results. Music is a community and the app is built around this community!
- Search bar - Allows further exploration of other users and all posts' song results (an intentional alternative to user-follows to drive away from metrics and encourage exploration beyond the familiar).
- Bookmarking songs - A feature that brings more functionality to the app, providing convenient access to songs that users may want to revisit, store for reference or share on their pages.

## User Flow:

- User registers an account | User logs in
- User greeted with homepage displaying 30 of the most recent searches, where they can find new music to listen to and profiles to browse
- User updates their own page by adding/editing profile information | User can update their password
- User uploads an image to do a new music search
- User receives results, which are automatically put to their page | User can delete their post, but still save the song results through bookmarking.
- User visits their own profile page, which displays posts (organized by most recent) and bookmarked songs (organized by artists name)
- User searches other users to browse profiles and posts | User searches songs to find more hidden music.

## Web-APIs:

- [Everypixel](https://labs.everypixel.com/docs): An image keywording API that uses AI to recognize objects, people, places and actions in images and turm them into keywords.
- [Spotify](https://developer.spotify.com/documentation/web-api/reference/search): Metadata from Spotify content. Keywords are sent to the search reference to make random track searches and retrieve data about the track.

## Tech-Stack:

- Front-End: HTML, CSS, JavaScript
- Back-End: Python/Flask, Jinja, WTForms, PostgreSQL, SQLAlchemy, RESTful APIs
- Deployment: ElephantSQL, Render
