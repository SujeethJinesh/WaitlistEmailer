# WaitlistEmailer

Usage:

`source venv/bin/activate` to enter the virtual python environment,
`python main.py` to start running the script.

Inside of main.py, you can edit the link to point to the course page you want. For my use case I'm making it point to the number of available seats in a class, you can change that by selecting the right html element of the page.

This script runs continuously at whatever interval set in the main function, you would have to keep this running (likely on a server) so you can always be checking if a class opens up.

You will be missing a file called "credentials.py". Make this file, and put in the following with your credentials:

LOGIN="your_gmail@gmail.com"
PASSWORD="your_password_for_gmail"

You will also need to allow insecure apps to use your account here: https://myaccount.google.com/lesssecureapps

Don't forget to turn this back off when you're done with getting your class schedule.
