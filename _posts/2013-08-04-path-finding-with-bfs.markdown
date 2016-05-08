---
layout: post
title: "Path finding with BFS"
date: 2013-08-04 19:21
comments: true
categories: [AI, breath first search, tanks war, algorithm]
---

So as a part of the programming challenge module I did last semester, we were supposed to build a game which is similar to the Nintendo Tank war game. This was a group project and [Tharindu](https://twitter.com/TharinduRusira) and I designed and build the game. What we had to do was to build a client who can communicate with a server. All together five clients can connect with the server simultaneously and the server sends global updates about the position of each clients, positions of coin piles, etc on each second. the clients has to process this global update and send its next move to the server before the next global update is arrived from the server. More details about the server specification is available [here](https://docs.google.com/file/d/0B0SvcTAspdLrNHdJalc5elpiM28/edit).

So the main objective of the game is to collect as many coin piles as possible. The game is played on a 2D cell matrix as you can see on the below image. So what we had to do first was to create a suitable data structure which can be used by the path finding algorithm efficiently.

{% img https://dl.dropboxusercontent.com/u/30358512/Untitled.jpg "Tanks War GUI" %}

<!-- more -->

So for each cell we created a class called "Cell". It has two constructors. A cell can be initialized either by giving its ID or it's x,y coordinates. It has a list of adjacent neighbor cells(up,down,left,right). A "parent" variable, which is used in path finding algorithm and boolean variables to set if the cell is an obstacle or a coin pile. The Constant "ConfigData.Map_size" is either the number of columns or number of rows in the square matrix.

{% codeblock %}

class Cell
    {
        // implements a cell in the terrain
        public int positionX { get; set; }
        public int positionY { get; set; }
        public int id { get; set; }                 //id of the Cell

        // INTITIALIZE CELL BY THE ID
        public Cell(int cellid)
        {
            this.id = cellid;
            //calculate positionX and positionY based on id and MAP_SIZE
            double X = Convert.ToDouble(id / ConfigData.MAP_SIZE);
            double Y = Convert.ToDouble(id % ConfigData.MAP_SIZE);
            this.positionX = (int)Math.Floor(X);
            this.positionY = (int)Math.Floor(Y);
        }
        //  INITIALIZE A CELL BY <X,Y> CO-ORDINTES
        public Cell(int x, int y)
        {
            this.positionX = x;
            this.positionY = y;
            this.id = x * ConfigData.MAP_SIZE + y;
        }
        public Cell parent { get; set; }					//parent cell
        public List<Cell> neighbours = new List<Cell>();    //Cell list of neighbours
        public bool is_water { get; set; }// true if water
        public bool is_stone { get; set; }       //true if stone
        public bool is_brick { get; set; }     //true if brick
        public bool is_coin { get; set; }      //true if coin pile is in the cell
 }
{% endcodeblock %}

And then we have a "World" class which is composed of "Cell" objects. In the constructor of the "World" class a 2D array of "Cell" objects is initialized and for each cell in the 2D array, the neighboring cell is added to the neighbor's list. We can get any cell in the 2D array either by its x,y coordinates or the cell ID.

{% codeblock %}

 class World
    {
        // GAME WILL BE PLAYED IN THIS MATRIX
        private Cell[,] map = new Cell[ConfigData.MAP_SIZE, ConfigData.MAP_SIZE];

        /*
         * 0 20 40 . . . 380
         * 1 21 41 . . . .
         * 2 22 42 .   . .
         * 3 23 43 .   . .
         * 4 24 44     . .
         * . . .       . .
         * . . .       . 398
         * . . .   . . . 399
         */
        public World() { 
            //INITIALIZE CELLS IN THE MAP
            for (int i = 0; i < ConfigData.MAP_SIZE; i++)
            {
                for (int j = 0; j < ConfigData.MAP_SIZE; j++)
                {
                    map[i, j] = new Cell(i*ConfigData.MAP_SIZE+j);                   
                } 
            }
            //adds the neighbor cells
            for (int k = 0; k < ConfigData.MAP_SIZE; k++)
            {
                for (int n = 0; n < ConfigData.MAP_SIZE; n++)
                {
                    if (n - 1 > 0)     //left neighbour
                        map[k, n].neighbours.Add(map[k, n - 1]);
                    if (k - 1 > 0) //up neighbour
                        map[k, n].neighbours.Add(map[k - 1, n]);
                    if (n + 1 < ConfigData.MAP_SIZE)   //right neighbour
                        map[k, n].neighbours.Add(map[k, n + 1]);
                    if (k + 1 < ConfigData.MAP_SIZE)   //down neighbour
                        map[k, n].neighbours.Add(map[k + 1, n]);
                }
            }
        }
        public Cell[,] getMap() { return map; }
        // GET A CELL BY ITS ID
        public Cell getCell(int cellid)
        {
            double X = Convert.ToDouble(cellid / ConfigData.MAP_SIZE);
            double Y = Convert.ToDouble(cellid % ConfigData.MAP_SIZE);
            int x = (int)Math.Floor(X);
            int y = (int)Math.Floor(Y);
            return map[x, y];
        }
        // GET A CELL BY ITS <X,Y> CO-ORDINATES
        public Cell getCell(int x, int y)
        {
            return map[x, y];
        }
	}
{% endcodeblock %}

Then comes the interesting part. We used Breath First Search algorithm to find the nearest cell which contains a coin pile. In the constructor of the class "BFS" a world object is initialized. findNextMove() method returns the ID of the next cell where the tank client should move. This method requires the cell ID of the current tank's position. Then the Cell object corresponding to that position from the world  object is assigned to the "start" variable.

The BFS algorithm works as follows. Until the queue which contains all the possible goal cells is empty, each cell in the queue is dequeued and scanned for it's neighboring cells. If those neighbors are obstacle cells(water,brick,stone) then those cells are marked as visited, but doesn't added to the queue. If a neighboring cell is not an obstacle and doesn't contain a coin pile either, then that cell is marked as visited, set its parent cell as the current cell and added to the queue. If a cell with a coin pile is found, then using the "parent" variable in each cell, a back tracking loop will return the ID of the next cell where the tank should move. If the queue is empty(i.e. no coin pile is found) then after while loop finishes, it will return -1, which is not a valid cell ID.

{% codeblock %}
class BFS
    {
        private World world;
        private int currentPos;
        private int mapSize = ConfigData.MAP_SIZE * ConfigData.MAP_SIZE;
        private Cell start;
        private int id =-1;

        public BFS(World w)
        {
            this.world = w;
        }

        public int findNextMove(int currP)
        {
            this.currentPos = currP;
            this.start = world.getCell(currentPos);

            //if the tank is on a coin pile then that coin pile will vanish
            start.is_coin = false;

            Queue<Cell> queue = new Queue<Cell>();
            bool[] mark = new bool[mapSize];        // boolean array to store if a cell is visited
            //enque the current position cell
            queue.Enqueue(start);
            // marks current position as visited
            mark[start.id] = true;

            bool found = false;
            
            //untill a path is found
            while (queue.Count != 0)
            {
                Cell current = queue.Dequeue();
                //scans all the neighbour cells of the current cell
                foreach (Cell neighbour in current.neighbours)
                {
                    // if a coin pile or life pack is found BFS algorithm will break and return that cell id
                    if (neighbour.is_coin|| neighbour.is_Life)
                    {
                        found = true;

                        Cell curr = neighbour;
                        //backtracks the cell id of next cell where the tank should move
                        while (curr.parent != start)
                        {
                            curr = curr.parent;
                        }
                        id = curr.id;
                        break;
                    } 
                    if (neighbour.is_brick || neighbour.is_stone || neighbour.is_water)
                    {
                        mark[neighbour.id] = true;
                    }
                    //if neighbour is not a blocked cell it will be added to the queue
                    if (!mark[neighbour.id])
                    {
                        mark[neighbour.id] = true;
                        neighbour.parent = current;
                        queue.Enqueue(neighbour);
                    }                   
                }
                // if a goal is found "while" loop will break 
                if (found)
                    break;
            }
            return id  
	}
 {% endcodeblock %}   
        
This algorithm is best suited when the search space(size of the "World" 2D array) is small (typically less than 2500 cells). BFS is guaranteed to  find the closest goal (if a goal exists). If there is no goal, BFS will go through the entire search space, thus the size of the queue will increase by 3 cells on each iteration (assuming there are no obstacles). This pitfall can be avoided by using AStar algorithm. But for a small search space BFS is more than enough. The full project can be downloaded from the [Bitbucket repository](https://bitbucket.org/elitecoders/tankgame).
