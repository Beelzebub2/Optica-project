# To be changed 2.2
![Static Badge](https://img.shields.io/badge/Version-Beta%20v2.1-8ebff1?style=for-the-badge&logo=v)
![Static Badge](https://img.shields.io/badge/Language-python-3776ab?style=for-the-badge&logo=python)
![Static Badge](https://img.shields.io/badge/Made%20by-Ricardo%20Martins%20and%20Jo%C3%A3o%20Marcos-851ebc?style=for-the-badge)  
 

Program made in python with the purpose of detecting face dimensions and predicting how the glasses would stay on it 

## Preview

![Preview](https://i.imgur.com/ptDIh3F.png)


## Changes
```diff

Beta 2.2 5/08/2023 (Linux/Windows)

+   Tested and implemented better measeurement algorithm

Beta 2.2 30/06/2023 (Linux/Windows)

+   Fixed exception raised when width and/or height of glasses wasn't input by the user
+   Added a check to let the user know if the aruco marker wasn't detected
+   Linux notifications finished
+   Fixed result images getting saved in wrong folder on linux
+   Fixed results folder and add faces folder not opening on some linux distributions
+   Removed forgoten useless code
+   Updated get graphics card function on linux

Beta 2.2 29/06/2023 (Linux/Windows)

+   Reorganized code
+   Fixed bug where previous answers on information windows would afect other windows


Beta 2.2 28/06/2023 (Linux)

+   Added show file with error on error handler
+   Cleaned imports
+   Linux version created
+   Fixed Linux information windows not working
+   Fixed aruco marker not being detected on Linux
+   Fixed themes and languages not working on Linux
+   Fixed information window not being created on center of the screen
+   Fixed informtaion window not staying on toplevel
+   Fixed information window duplication
+   Fixed program not responding when a information window was opened
+   Fixed program not closing with exit uppon pressing <esc>

Beta 2.1 27/06/2023

!   Working on better measurement algorithm
!   Working on better mm to pixel ratio predictor 
+   Fixed minor issues with error handler
+   Fix minor bug with style selection
+   Rearranged send error to discord function
+   Added more data collection (gpu, processor, ram)
+   Fixed minor bug with program priority elevator


Beta 2.1 18/06/2023

+   Added a Warning window handler
+   Fixed bug where program would crash if a warning window was opened
+   Fixed warning window duplication
+   Added error log file

Beta 2.1 17/06/2023

+   Added the use of Threads for image processing
+   Added a progress bar to the GUI
+   Fixed some bugs that would crash the program
+   Added an error handler to decrease chances of crashing
+   Reorganized variable names
+   Optimized error handler
+   Added decorator for threading
+   Fixed bug where program would not close if a thread was still running
+   Rearranged Languages values


Beta 2.0 12/06/2023

+   Added autorestart to apply changes
+   Close settings window with "Esc" key
+   Added French/Spanish/German translations
+   Fixed Program crash while trying to move main window after clicking on about button

Beta 2.0 11/06/2023

+   Minor fixes for the config handler
+   Added custom Orange Theme
+   Code optimization
+   Fixed Optionmenu starting function before it's clicked
+   Window always appears on center of screen now works with multiple screens

Beta 2.0 10/11/2022

+   Changed program name

Beta 2.0 07/11/2022

+   Added Missing tooltips

Beta 2.0 03/11/2022

+   New tutorial video
+   Fixed not letting use glasses more than once

Beta 2.0 18/09/2022

!   Working on Creating an Sql database to collect useful data
+   Fixed Dark and Light style not getting saved after restart

Beta 2.0 10/09/2022

+   Fixed buttons showing up even when no image was selected
+   Fixed Long ass function to open a simple folder 
+   Fixed an error with string to float convertion
+   Changed code orientation
+   Fixed red theme issues

Beta 2.0 09/09/2022

!   Working on simpler autoupdate
+   Fixed program error (would not close after program end)
+   Fixed Loading time (from 15-18s to 1-5s)
+   Optimized some module imports
+   Fixed 3 minor bugs related to image processing
+   Added custom Red theme

Alpha 1.0 08/09/2022

!   Working on Optionmenu starting function before it's clicked
+   Settings window now goes to top if user tries to duplicate it
+   Optimized config handler
+   Added ability to change themes
+   Added Language changing
+   Added warning when trying to duplicate settings window
+   Fixed bug where people were able to duplicate settings window
+   Fixed "temp.png" not getting deleted  
+   Window always appears on center of screen

Alpha 1.0 05/09/2022

+   Settings button was added
+   Reorganized and optimized code
+   Config handler created
```
