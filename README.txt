****** Before run the server activate django environment ****
# Goto project env url and excute below command
 => env\Scripts\activate

**** Run the server *****
 => python manage.py runserver

******* API Testing Guide Using Swagger UI ******
Step 1: Access API Documentation

   Open browser and go to: http://127.0.0.1:8000/api/docs/
   You will see interactive Swagger documentation

Step 2: Authenticate

   1. Click "Authorize" button
   2. First, get a token by testing the login endpoint:

   => Scroll down to "Auth" section
   => Click on "POST /api/auth/login/"
   => Click "Try it out"
   => Enter your credentials:
   json{
     "username": "your_username",
     "password": "your_password"
    }

   => Click "Execute"
   => Copy the access token from the response
   3. Go back to "Authorize" and enter:
   => Bearer YOUR_ACCESS_TOKEN_HERE

Step 3: Test Each Endpoint
 Now you can test all endpoints directly in the browser:

 1. Projects:

   => Create project: POST /api/projects/
   => List projects: GET /api/projects/
   => Get project details: GET /api/projects/{id}/

 2. Bugs:

   => Create bug: POST /api/bugs/
   => List bugs: GET /api/bugs/
   => Filter bugs: GET /api/bugs/?status=open

3. Comments:

   => Add comment: POST /api/comments/
   => List comments: GET /api/comments/

***** Redis Setup *******
   => Download & install on windows Redis-x64-5.0.14.1.msi 
   => Add the installation path in windows variable path

****** Test Websocket ********
   => Run the test_websocket.py file in project environment

******* API Testing Guide using python script automation ******
   # Run the test_api_complete.py file in project environment
