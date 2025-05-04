# webprogramming

Music website where users can share their favorite songs and discuss them with others
- The user can log into their account
- The user can edit their profile and add their interests
- The user can create posts that others can comment on
- The user can search for songs by genre or instrument or any other relevant topic

# Instructions for using the app:
Make a folder called "test":
mdir test

Go to said folder:
cd test

Enable venv:
python3 -m venv venv

Change the source to venv:
source venv/bin/activate

Install flask:
pip install flask

Run the app:
flask run


UPDATE 30.3.2025:
The current state of the application is evolving. The application now has the feature to navigate from the front page to create a new thread where users can discuss music. From the front page, users can also navigate to browse already created threads or search for a new thread using a keyword. In the future, threads can be tagged based on music genre or instrument. However, this still needs to be implemented. Security is almost non-existent, and various bugs can be uncovered. A profile feature has not yet been created, but it is coming soon.

UPDATE 13.4.2025:
The current state is even better than last time. New functions, such as tags have been implemented. Users can tag posts by whichever they find suitable for the discussion. The promised profile feature has been added, and users can submit their own profile pictures and type out a little biography to let others know what's up. The app has an improved search, allowing users to find posts by their tags, poster or content. Still, some problems arise, such as cybersecurity and other malicious intent. The application is still very fragile, so better safety measures must be implemented. These security improvements will come soon, as soon as I find the other elements complete.

UPDATE 4.5.2025
This is the final update regarding the course. The app is finally in it's finished state. Added paging to the threads page, displaying only 8 threads per page. Edited the CSS to make the program more visually appealing. Fixed bugs. The app is complete. 
