# User Management System
This is a project to implement a user management system.

The architecture is as follow:\
**Browser -> Frontend -> Backend -> Database**

Features:
1. User login system
2. User register system
3. Logged-in only protected route
4. Expirable acccess Token (cryptographically protected) for browser session

Security Measures:
1. Token are generated with SHA256 algorithm and only will be validated from \
backend server
2. Salted user passwords are hashed and stored in the database (passwords are \
not writen to any storage in the entire chain)
3. API Key to restrict only the frontend server can request through REST API

With the security measures implemented as above, this should make\
this system robust for majority of the use case against session thief,\
cookie tampering, guess password (brute force), unauthorized API requests \
and etc.