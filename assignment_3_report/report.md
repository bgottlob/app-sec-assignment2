---
documentclass: extarticle
author: Brandon Gottlob
fontsize: 13pt
linestretch: 2 
geometry: margin=0.75in
indent: true
header-includes: |
    \usepackage{amsmath}
    \usepackage{amssymb}
    \usepackage{ifsym}
    \usepackage{fancyhdr}
    \pagestyle{fancy}
    \fancyhead[LO,LE]{Brandon Gottlob}
    \fancyhead[RO,RE]{Assignment 3 Report}
    \fancyfoot[LO,LE]{\today}
pagestyle: empty
lang: en-US
---

# Assignment 3

## Database Design

There are three tables in the database: User, AuthSession, and Submission.

The User table manages user data and credentials, and it contains the following columns:

- `id`: an auto-incrementing integer used as the primary key
- `username`: the string username, with a uniqueness constraint
- `password_hash`: a SHA512 hash of the user's password and salt
- `salt`: a string representation of 16 random bytes appended to the user's password before it is hashed
- `mfa`: the multi-factor authentication phone number

Notably, a numeric id is used as the primary key for users instead of the unique username column.
As will be seen in the other tables, the User.id column is used as a foreign key for joins.
Numeric values are more performant when used for joins compared to strings and are cheaper to store as foreign keys in other tables.
Additionally, using a numeric user id will allow for a user's username to be changed without the need to cascade changes to any other tables.
Changing usernames is not a feature in the application, but the schema allows it to be implemented easily.

As in the initial implementation with SQLite, the password is not stored directly.
Rather, the password is appended with a random salt string and is hashed.
Only the hash and the salt needed to verify the hash are stored in the database.

The Submission table manages spell check queries submitted by end users, and it contains the following columns:

- `id`: an auto-incrementing integer used as the primary key
- `text`: the submitted text that is spell-checked
- `result`: a string of comma-separated misspelled words
- `user_id`: foreign key to the `id` column of the User table, indicating which user submitted the query

The AuthSession table manages active user sessions and the logged times to support the login history functionality, and it contains the folowing columns:

- `id`: a randomly-generated UUID4 string to identify a single session, used as the primary key
- `valid`: a boolean flag indicating whether or not the session can still be used to authenticate user requests
- `login_datetime`: a UTC timestamp of when the session began, when the user logged in
- `logout_datetime`: a UTC timestamp of when the session ended, when the user logged out or when the session was invalidated
- `user_id`: foreign key to the `id` column of the User table, representing the user who is authenticated in this session

The most notable design decision is the use of a UUID string as the primary key, instead of an auto-incrementing integer as is for the User table primary key.
Because the session `id` value is sent in the cookie to users' browsers, it is very important that an attacker cannot guess the `id`.
If an attacker knew a user's username and correctly guessed the user's session `id`, the attacker could try to send it to the server in a spoofed cookie to hijack the user's session.
Even if the attacker had this information, the attacker would also need to know the Flask server's secret key to sign the spoofed cookie.
However, it is better to keep client-visible data as obscured and difficult to spoof as possible.
Additionally, since the UUIDs are in a primary key problem, the same UUID cannot be used for multiple sessions.
It is not particularly important for the User and Submission primary keys to be difficult-to-guess UUIDs because the numeric user `id` is never visible to end users and access to submission data is regulated by access control mechanisms.

The `valid` flag simply indicates whether the UUID for the given session can still be used to make authenticated requests for the given user.
As will be described in the next session, this is used to prevent session fixation attacks be verifying only one session can be used to make authenticated requests for each user.

The `valid` flag allows the AuthSession table to manage both active and historical session data.
Adding the login and logout timestamps directly to the AuthSession table made it possible to show active and historical sessions side-by-side in the login history page.
A `NULL` logout timestamp theoretically could indicate that a session is no longer valid, thus making the `valid` column redundant.
However, I separated the logout timestamp and the `valid` flag because they are semantically different concepts, as one is for logging history and the other is for managing the current state of the system.
Logically, it seemed cleaner to use two separate columns although it is redundant.
A single bit is a very low cost to pay in redundancy.

## Application Security Design Decisions
- No usage of string interpolation into SQL statements - strictly used the ORM query(), add(), and commit() methods to interact with the database

- logout_datetime - when the user logged out or when the session was invalidated
  - If the user logs in a second time, the first session is invalidated, and the logout time is set a the same time as the login time of the new session
  - Logging out will invalidate all sessions for the user, not just the current one
  - These measures prevent session fixation vulnerabilities

- Simple is_admin function - what if there are multiple admins?
  - Add an admin column to user table, rewrite is_admin to check if that username has 
