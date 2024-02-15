# baduk_sgf
Baduk SGF Viewer

I wrote this program to passively familiarize my son with baduk patterns in pro games, by having them continuously running on the side in the living room. I'm expecting this will ease the learning curve later on when he's old enough to seriously engage with me in the game; so we can have baduk as a fun thing we do together.

The program pulls sgf files from the "badukmovies-pro-collection" folder, and steps through all the stone-placements in each game one-by-one, with a few seconds between each move. At the end of each game, it shows a block of white stones or black stones to indicate the winner (as dictated by the sgf file). If no winner is indicated in the sgf, it shows a block of half-black, half-white, to indicate that the winner is unknown.

The program keeps track of which game it showed last, so if you turn it off and on again then it will start with the next game in the folder, after the one it most recently opened.

The folder has just a few sgf files in it, because of some upload limitations I'm too lazy to manage.

You can download the whole thing here: https://www.badukmovies.com/pro%5fgames . That has enough sgf files in it for about a year of continuous runtime, I think. But there's currently a bug where the program will begin to slow after a few days, and eventually stop. I'm running this at-startup on a raspberry pi, though, so my resources are very limited. Restarting the pi fixes the issue for me. Eventually I'll figure that out and fix it.

This program must be placed in the same directory as the "badukmovies-pro-collection" folder in order to work.
