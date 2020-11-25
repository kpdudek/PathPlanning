# PathPlanning
Implementation and visualizaton of the A* path planning algorithm on a 2D grid.

## Installation
### Windows 10
Download python >3.7 from the Microsoft Store and then use pip3 to install PyQt5 and numpy from PowerShell. Install git as described [here](https://git-scm.com/download/win)
```
git clone https://github.com/kpdudek/PathPlanning.git
pip3 install PyQt5 
pip3 install numpy
```

## Usage
Generate a graph by selecting the square dimension size, and then selecting Generate Graph. Random obstacles can be added by enabling Perlin noise.

Select the painting type from Environment Config. Draw a start and goal node by clicking a tile in the canvas. Staged changes are shaded on the canvas.

Select the Generate Roadmap button. The staged changes should now be solid colors.

Select the Find Path button to begin the graph search. The path will be shown with a blue line and the objects swept volume will be shown in dotted orange.
