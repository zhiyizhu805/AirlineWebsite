# Webapp

Public system:
Routes and functions overview

>>Homepage (route("/")) return HTML page containing ((route"/ArrDep")) for the user to search arrival and departure flights from a selected(user input) airport and (route"/bookaflight")) for the user to book a flight and route("/signin") for users to sign up their account and route("/register") for users to register an account.

>>route"/signin": sign()function return HTML page - user input data on HTML page send to route("/mypage") .mypage() function process data and match with the database. If matched return the user account HTML page. If not matched, return signin HTML page.

>>route("/register"): register()function return register HTML page to gather user data and send it to route("/register/checkvalid").register_checkvalid() function will match user data with database data to check if it has existed in the database. If not, insert new user data into the databse, otherwise, prompt the user to access the route("signin")

>>route("ArrDep"): firstly return arrival and departure HTML page to get airport info from the user. User data will be sent to route("/ArrDep/process") to process by match() function. The match function will get related airport info from the database and return it to users.

>>route("/bookaflight"): 
If the user is not logged in, prompt users to access route("/siginin) to log in or access route("/register") to register an account and then log in.
If the user is logged in,bookaflight() function first returns available flights to the user and then gets the user-selected flight information and sends it to route("/bookbutton"). bookbutton()function will process data and get the flight booking done for users.

---
* assumption and design decisions: 
 Bookaflight()function return bookaflight HTML page with the Current time + 7 days flight schedules to users.Because we don't want to show the flight information that has already happened to the user, but when the user selects the flights of today, he will still see the flight information that has already been taken which cannot be booked. Asking the user to enter the time is not user-friendly.
 My compromise plan is: when the user selects today's flight, the function defaults to filtering flights before the current time by assigning the current time (2022-11-11 11:00:00) to the variable to replace the current date(2022-11-11).

* assumption and design decisions: 
To book a flight for a user, my idea is to first extract all the flight ID-passenger ID arrays in the passenger flight table. Putting these arrays into a list is used to check whether the flight combination booked by the new passenger is in the existing combination to avoid double booking.

After the user clicks book to book a flight, my original idea is to let the user stay on the book flight page to continue booking the flight and at the same time display a message of success or failure of the previous booking.

But since I don't know of any other way to display this "notice" while keeping it on the same page besides repeating render the same template with putting in a new variable. 

My final compromise decision is to bring users back to "my booking page" because less repeating code is needed to get this page worked with a notice sentence displayed.

--
* assumption and design decisions: 
About user login(1): User login is required to book a flight. My original idea was that after a user logs in, user info will be sent to a route through "<form>".Then a function will pass this user info into the flight booking template HTML page. when the user clicks "book" on the flight booking page for a specific flight, the user info and selected flight info will be passed to the method route and a function will deal with these data.
However, I finally decided to use the session to store user data. Whenever a user logs in, user data is stored in the session. Whenever a user logs out, the user data in the session will be cleared. I think this is a better approach than repeating passing variable information on each page.




              Administration system for staff
Routes and functions overview:

>>Administration system contains two main routes which are route("/admin/staff page/passenger") route("/admin/staffpage/flights") 

>>route("/admin/staffpage/passenger") will return Passenger List which can be filtered by their Lastname:user input last name data will be sent to route("/admin/staffpage/passenger/process") to be processed by passengerProcess()function.
In this route., administrators can be directed to individual passenger pages (route("/admin/staffpage/passenger/each")) to check their bookings (route("/admin/staffpage/passenger/booking")) and edit their details (route("/admin/staffpage/passenger/edit")).
In the individual passenger management page, administrators are allowed to cancel(/admin/staffpage/passenger/booking/cancel) and add new flights/ or reschedule flights(route("/admin/staffpage/passenger/booking/addPassengerflightProcess"))for them.


>>in this part, the reschedule function and the add flights function can be nested.related data will be sent to the same route(route("/admin/staffpage/passenger/booking/addPassengerflightProcess")).
First addPassengerflightsProcess() function will add the selected flight for both add and reschedule request, then if the user request to reschedule, the function will delete the original booking(passengerID-flightID)from the database to complete the reschedule process. 


>>route("/admin/staffpage/flights") will return a filtered Flight List HTML page in which Administrators can be directed to individual flight pages (route("/admin/staffpage/flights/each")).On the individual flight page, a passenger list of the selected flight will be displayed and the flight details can be edited.
The passenger list of individual flights page allows administrators to edit each passenger's details by the manager(/admin/staffpage/editflights/process) or other staff(route("/admin/staffpage/editflights/process/class0")) and manage their bookings.


* assumption and design decisions: 
for the flight filter function, What I have designed is that the user selection can be preserved on the input box after filtering so that the user can see his selection.

I get user input in the backend and put user input as value into each input or select tag 


* assumption and design decisions: 
In these two main routes. Many functions and pages overlap. For example, the individual passenger management page can be accessed from both the passenger list page("/admin/staffpage/passenger") and the individual flight management page(route("/admin/staffpage/flights/each")).
My idea is that there is no need to write two similar pages, just send parameters when entering from different endpoints. Then on the HTML page, it is determined from which endpoint it is entered by judging the parameters received, to display different information to users.
I believe it's important to be able to bring administrators back to the last page. After booking a flight for a passenger, the function should be able to bring administrators back to the same passenger management page for further management.
I use <input type="hide">in <form> to send related parameters. Then in HTML, use jinja {%%} if statement to judge in which stage, what information and function to display. To book flights for passengers, the flight List page can be used by showing available seats and the book button when the administrator clicks the '+ add flights' button from the passenger management page. 


>>For adding flights function. Administrators can access route("/admin/staffpage/addAflight") and route("/admin/staffpage/addflights") by clicking the 'add flights' dropdown button.





* assumption and design decisions: 
About user login(2): 
I use the same approach by storing user data in session["data]. However, I encountered a problem which is that I would like to display user login info on every page so I get the logged user info from the session and render them into nearly every template. However, I found if I clear the browser history, my web will not work because session["data"] of logged user info cannot be found(I render them in every page template). The only two pages I could access normally are route("/signin") and route("/register") because I didn't assign session['data'] to these two pages.

I will need to write an if statement to define if the session['data'] is lost/does not exist, and prompt users to re-login.

The final decision regarding this issue is to add a "try-except" statement to every page. If a page encounters a session value missing situation will be directed back to the HomePage or Login page.
