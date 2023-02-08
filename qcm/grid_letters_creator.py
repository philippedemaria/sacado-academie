import random
 
def determine_grid_size(my_words):
    som = 0
    for w in my_words :
        som +=len(w)
    if    som<=25 : n,m=10,10
    elif  som<=50 : n,m=15,15
    else : n,m=20,15
    return n,m

def create_grid(my_words):
    n,m = determine_grid_size(my_words)
    grid = list()
    for i in range(n):
        rows = list()
        for j in range(m):
            rows.append(0)
        grid.append(rows)
    return grid
  
def orientation():
    orient = ["right","down","obup","obdown"]
    o = random.randint(0,3)
    return orient[o]
 

def position(o,w,x,y):
    i = 0
    liste = list()
    for c in w:
        if o == "right" :liste.append((c,x,y+i))
        if o == "down"  :liste.append((c,x+i,y))
        if o == "obup"  :liste.append((c,x-i,y+i))
        if o == "obdown":liste.append((c,x+i,y+i))
        i+=1
    return liste


def test_grid(w,x,y,grid,o):
    som = 0
    try :
        if o == "right":
            for i in range(len(w)):
                if grid[x][y+i] != 0 :
                    som=1
                    break
        if o == "down":
            for i in range(len(w)):
                if grid[x+i][y] != 0 :
                    som=1
                    break
        if o == "obup":
            for i in range(len(w)):
                if grid[x-i][y+i] != 0 :
                    som=1
                    break
        if o == "obdown":
            for i in range(len(w)):
                if grid[x+i][y+i] != 0 :
                    som=1
                    break
    except :
        som = 5
    return som == 0
            
            
def place_word(w,grid):
    l = len(w)
    o = orientation()
    n , m = len(grid[0])-1, len(grid)-1
    test = False
    while not test:
        if  o == "right":
            x = random.randint(0,m)
            y = random.randint(0,n-l)
        elif  o == "down":
            x = random.randint(0,m-l)
            y = random.randint(0,n)
        elif  o == "obup":
            x = random.randint(m-l,m)
            y = random.randint(0,n-l)
        elif  o == "obdown":
            x = random.randint(0,m-l)
            y = random.randint(0,n-l)
        test = test_grid(w,x,y,grid,o)
    for pos in position(o,w,x,y):
        code = random.randint(10,20)
        grid[pos[1]][pos[2]] = "<td data-code="+str(code)+"  class='clickable'>"+pos[0].upper()+"</td>"

    return grid 
    

def create_final_grid(my_words,grid):

    letters  = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"] 
    n , m = len(grid), len(grid[0])
    for w in my_words :
        place_word(w,grid)
    
    for i in range(n):
        for j in range(m):
            k   = random.randint(0,25)
            cod = random.randint(21,50)
            if grid[i][j] == 0:
                grid[i][j] = "<td data-code="+str(cod)+" class='clickable' >"+letters[k]+"</td>" 
    return grid


def create_string_table(my_words):
    grid = create_grid(my_words)
    string_table = "<table id='grid'>"
    for row in create_final_grid(my_words,grid):
        string_table +="<tr>"
        for col in row :
            string_table += col
        string_table +="</tr>"
    string_table +="</table>"
    return string_table

 
