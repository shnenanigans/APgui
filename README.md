# APgui
Mime's all portals program but with a GUI

**Instructions:**

Make sure the AllPortals.exe and rings.png is in a nice little un-zipped folder

If you have a backups folder and you are not planning on using backups, delete it

Double click the exe to run it

If you are single monitor and you want the program to stay over minecraft, check 'always on top'. It will only work when minecraft is windowed (sorry).

It will prompt you to enter in the locations of your first 8 strongholds. You can use either f3 + c and then paste that in, or manually type the coords.

For exampe:

![image](https://github.com/user-attachments/assets/dbea3b8c-987c-43e8-a0f1-d43b6d77c199)

The input should look like that. Either a pasted f3+c or your x and z coordinates typed with only a space in between.

Press the lock button beside all the stronghold locations as you find them. This will make sure the image updates with your path. The image will show after you press "next" and pathfinding is done. It is VERY IMPORTANT that you lock the 8th ring stronghold LAST otherwise pathfinding will be messed up.

If you lock coordinates of a stronghold that does not match the ring, you will get a warning. Make sure you press "No" on the pop-up because it is not possible to edit if you accidentally press "Yes".

If you are unsure what ring your stronghold is in, press "check ring" and enter the overworld coordinates.

You will also have to enter in the nether coordinates of your portal on the roof near origin by pressing 'spawn coords'. If you forgot to check when you built it, just enter 0 0 and it will probably be close enough for the pathfinding, however your angles from origin may be slightly innacurate.

Once all 8 locations are locked, press next. This will cause the program to estimate the locations of the remaining strongholds and find the optimal path. It will take several seconds.

If you accidentally closed the program and need to use backups, press the 'use last backup' button. If it starts using the wrong backups file, delete all the backups files except the one you want and try again. It will open starting with the 9th stronghold so you will have to click "next" until you get to the one you were on. Also, the backups file is only created after you press 'next', not as you lock strongholds. If you accidentally close the program while finding the first 8 strongholds it will create an 'emegergency backup for stupid idiots' and you can find your coords in there. You will not be able to press 'use last backup' if you need the emergency backup because that's a lot of effort to code and at least this way you don't have to watch back your vod (you're welcome).

Now, the program should show a window with the next stronghold coords. The graph will be saved to 'output.png' which you can put into obs.

The first angle (towards stronghold 9) shows as N/A because it will not be correct especially if you had a very far blind.

Make sure you add the gui, graph, stronghold count, and fun facts to OBS. (very important)

The 'Find Portals' window is set up so that you can resize it to show only important information, since using the extra buttons is rare during a run.

![image](https://github.com/user-attachments/assets/98fb6b30-b502-4af1-90f3-3e6bb3e5f702)

![image](https://github.com/user-attachments/assets/bc8d110d-ecae-41e6-a7f9-a3a08f15c2a1)

This will also hide the messages showing when to leave your spawn behind and when to not set spawn at all. The spawn instructions are also colour coded in case they are hidden in window resizing.

Blue: set spawn at blind portal and break it after filling end portal and respawning

Purple: set spawn at blind portal and DO NOT break it after filling end portal and respawning

Green: do not set spawn at blind portal

When green comes after blue, you will respawn at world spawn. When green comes after purple, you will respawn at your last blind portal.

If you accidentally set your spawn when it takes you to origin, make a new bed to set spawn at and break it, then go through the end portal.

If you accidentally set spawn when you were supposed to leave it at the last stronghold, continue as if everything were blue and keep in mind that your next angle will be incorrect.

**Extra Buttons**

The 'Next SH Hotkey' button works as it sounds. It will allow you to hotkey instead of pressing 'next' on the gui. Just click it, enter a hotkey, and it should work. To remove a hotkey, set it to 'esc'. Also, it will not allow you to use q, k, or l as hotkeys because those close the portals graph (although only if you are tabbed into the graph, better safe than sorry ig). If you want arrow keys you can type "up" or "down" into the box. You can put official key names for any key I just don't know what they are except those ones.

The 'Check ring' button works as it sounds. You can enter coords or f3c, like the first 8 strongholds.

If you are wondering where the "empty" button is, it is gone because dealing with the empty sector is hard and I don't want to. If you find all the 8th ring strongholds before the empty sector, it will be up to you to skip the last one.

**How does it work?**

The problem with the previous All Portals program was that it didn't account for the fact that a player could simply not set their spawn and immediately teleport back to 0, 0. Not only that, but a player can leave their spawn at a previous stronghold. What this program does is, while creating the optimal route, it will look at the last and next strongholds and find out if the distance between them is shorter than the distance between your current stronghold and the next one. In this case, that stronghold will be set as one where you do not set spawn and the one before it will be set as one where you leave your spawn there.

For example:

![image](https://github.com/user-attachments/assets/96a9e5f8-5002-4e22-a0ba-c39f2626de57)

The old AP program would have told the player to go in order of the numbers and set spawn at every blind.

Instead, the program is telling the player to leave spawn at 2, go to 3, teleport to 2 when they go through the end portal, and then go to 4. This is because it has detected that the distance between 2 and 4 is shorter than the distance between 3 and 4.

![image](https://github.com/user-attachments/assets/1eac4f5b-3640-4a37-86b2-439c95585431)

Here is what it will look like if you don't set spawn at all. You don't set spawn at 1, and then you get to 2 from 0, 0. From there you continue to 3 as normal. 

It is important to have your nether roof portal near 0, 0 if you want the angles to be correct. They will be more and more inaccurate the further you are away so pay attention to your coordinates when getting to these strongholds.

**How do I read the graph?**

yellow dot = stronghold you are currently traveling to

green dot/line = normal path

blue dot/line = leave spawn

purple star = last stronghold

red line = get to stronghold from 0, 0


credit:
@thetalkingmime
@shnenanigans
@luvvlyjude
@Lincoln-LM
