# Capstone 1: Project Proposal

##### 1. What goal will your website be designed to achieve?

The goal will be for users to create arithmetic worksheets using randomly generated math problems coming from an API. They will be able to save their worksheets along with an answer key.

##### 2. What kind of users will visit your site? In other words, what is the demographic of your users?

Anyone who can use math worksheets, so mostly teachers and tutors.

##### 3. What data do you plan on using? You may have not picked your actual API yet, which is fine, just outline what kind of data you would like it to contain.

The [xMath API](https://x-math.herokuapp.com/) will be used to generate the random arithmetic problems.

##### 4. In brief, outline your approach to creating your project (knowing that you may not know everything in advance and that these details might change later). Answer questions like the ones below, but feel free to add more information:

###### a. What does your database schema look like?

The database will have:

##### Users

Users will have a username, password, and email address. The password will be stored as a hashed string.

##### Worksheets

Each worksheet will have the worksheet itself and an answer key sheet. Both worksheets and answer keys can be saved by a user as a PDF for later download. The type of operation (addition, subtraction, multiplication, division, or random) will also be saved, so users can filter by this.

###### b. What kinds of issues might you run into with your API?

I can't think of any at the moment. I've tried out the API a few times, and it seems pretty simple and straightforward.

###### c. Is there any sensitive information you need to secure?

Passwords and emails.

###### d. What functionality will your app include?

-   Users can specify what type of operations they want included in the worksheet, as well as later see and filter their saved worksheets by operation.
-   They can also specify the number of questions in the worksheet along with the min and max numbers allowed.
-   Users can download and possibly save the worksheet to some other service like Google Drive or email their sheets to someone else.

###### e. What will the user flow look like?

Users can generate but not save worksheets without signing up. To save and access their worksheets for later, the user will have to sign up and create an account. Users will be shown a form where they can specify parameters for their worksheets, and then the generated worksheet and answer key will be shown to them with buttons to save and download them. The user will have a profile page to see all of their saved sheets.

###### f. What features make your site more than CRUD? Do you have any stretch goals?

Again, I'd like users to be able to download and possibly save worksheets to some other service like Google Drive or email sheets to someone else. I'd also like to try implementing a password reset feature via email.
