# APgui
Mime's all portals program but with a GUI

Mime's original program: https://github.com/TheTalkingMime/AllPortals

Concord direct download [link](https://www.math.uwaterloo.ca/tsp/concorde/downloads/codes/win/concorde1.1.exe)

**Instructions:**

Make sure everything is in a nice little folder

Double click the program to run it

If you are single monitor and you want the program to stay over minecraft, check 'always on top'. It will only work if minecraft is windowed (sorry).

It will prompt you to enter in the locations of your first 8 strongholds. You can use either f3 + c and then paste that in, or manually type the coords.

For exampe:

![image](https://github.com/shnenanigans/APgui/assets/83895136/5932134a-5b23-4020-9751-a5c730dfe1cd)

The input should look like that. Either a pasted f3+c or your x and z coordinates typed with only a space in between.

Press the lock button beside all the stronghold locations as you find them. This will make sure the image updates with your path. The image will show after you press "next" and pathfinding is done.

If you lock coordinates of a stronghold that does not match the ring, you will get a warning. Make sure you press "No" on the pop-up because it is not possible to edit if you accidentally press "Yes"

Once all 8 locations are locked, press next. This will cause the program to estimate the locations of the remaining strongholds and save it to a file called strongholds.qs.

Double click the .qs file. If it does not open with concord, make sure you have it downloaded and select 'open with concord'.

![image](https://github.com/shnenanigans/APgui/assets/83895136/4ae2c2bb-c69b-418b-a35d-68b082c1ccdb)

![image](https://github.com/shnenanigans/APgui/assets/83895136/21e29f03-7d13-4086-a6cf-45af26e46652)

![image](https://github.com/shnenanigans/APgui/assets/83895136/0c7f649d-7314-402a-b13e-71a3114bfcc8)

Press the 'solve' tab, then 'ok' with the default parameters (as shown above). Then save it and CLOSE CONCORD. Bad things happen if you do not close concord.

Press 'ok' on the pop-up instruction box. The program will continually check for a saved strongholds.qs file and then update automatically.

If you accidentally closed the program and need to use backups, press the 'use last backups' button. Pretty self explanatory. Only problem with it is that the backups files are only created after you press 'next', not as you lock strongholds. If you accidentally close the program while finding the first 8 strongholds there is nothing I can do to help you.

Now, the program should show two windows. One with coords and one with the portals graph.

![image](https://github.com/shnenanigans/APgui/assets/83895136/cba38ec1-7373-477b-8de1-aa42521ed5cd)

Do not activate the Portal Graph window and press Q, K, or L. It will either close the window or mess up the graph and I have no idea why or how to stop it.

Make sure you add the gui, graph, stronghold count, and fun facts to OBS. (very important)

The 'Find Portals' window is set up so that you can resize it to show only important information, since using the extra buttons is rare during a run.

![image](https://github.com/shnenanigans/APgui/assets/83895136/f2eb3a2b-149d-40cd-b9a8-d15298c86051)

This will also hide the messages showing when you are at an 8th ring stronghold, when to leave your spawn behind, and when to not set spawn at all. At an 8th ring stronghold you will only see the 'empty' button (to press if you find the empty sector) and the spawn instructions are also colour coded in case they are hidden in window resizing.

Blue = set spawn normally

Purple = leave spawn at last strongold

Green = Do not set spawn at all

Here is an example of what the program would look like when getting to an 8th ring stronghold:

![image](https://github.com/shnenanigans/APgui/assets/83895136/0823261d-2beb-4e96-9bd3-e928a21863f7)

As you can see, all important information can still be found in a resized window if you remember the colour codes and that the 8th ring has an 'empty' button.

**Extra Buttons**

The 'Next SH Hotkey' button works as it sounds. It will allow you to hotkey instead of pressing 'next' on the gui. Just click it, enter a hotkey, and it should work. To remove a hotkey, set it to 'esc'. Also, it will not allow you to use q, k, or l as hotkeys because those close the portals graph (although only if you are tabbed into the graph, better safe than sorry ig)

The 'Check ring' button works as it sounds. You can enter coords or f3c, like the first 8 strongholds.

The 'Setspawn' button is kinda cosmetic. Basically, all the calculations to find if spawn is closer to your next stronghold or not are based on 0 0, so if you want to guarantee accuracy you can enter your actual spawn point coords.

You may have noticed there is no longer a 'Pathfind from coords' button. This is because it wasn't working and I tried to fix it but then it kept breaking and nothing worked and no one ever uses it anyway so just don't forget to set spawn.

**How does it work?**

The problem with the previous All Portals program was that it didn't account for the fact that a player could simply not set their spawn and immediately teleport back to 0, 0. Not only that, but a player can leave their spawn at a previous stronghold. What this program does is, on every stronghold, it will look at the next 3 ahead of it and see if the distance between the current stronhold and the one 2 ahead is shorter than the distance between that and the next one. In this case, the player would leave their spawn behind.

For example:

![image](https://github.com/shnenanigans/APgui/assets/83895136/6b05c38c-c2df-4bd2-9cd1-e46c4f1bfc90)

The old AP program would have told the player to go in order of the numbers and set spawn at every blind.

Instead, the program is telling the player to leave spawn at 2, go to 3, teleport to 2 when they go through the end portal, and then go to 4. This is because it has detected that the distance between 2 and 4 is shorter than the distance between 3 and 4.

![image](https://github.com/shnenanigans/APgui/assets/83895136/e36714b9-64a7-4595-aa5e-bbc4caaab14b)

Here is what it will look like if you don't set spawn at all. You don't set spawn at 2, teleport back to 0, 0 when you go through the end fountain, and travel to 3 from there because the distance from 3 to spawn is shorter than 3 to 2. The blue line simply indicates the next stronghold to go to.

**How do I read the graph?**

green = normal path

blue = next stronghold

purple = leave spawn behind

yellow = do not set spawn


credit:
@thetalkingmime
@shnenanigans
@machliah

