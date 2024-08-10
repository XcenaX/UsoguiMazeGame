let mode = 'wall';

function setMode(newMode) {
    if (ready) return;
    mode = newMode;
    document.querySelectorAll('.controls .button').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`${newMode}-mode`).classList.add('active');
}

function handleCellClick(x, y) {
    if (ready) return;

    const cellContent = document.getElementById(`cell-content-${x}-${y}`);

    if (mode === 'entrance') {
        if (entrance && entrance.x === x && entrance.y === y) {
            entrance = null;
            cellContent.classList.remove('entrance');
        } else {
            if (exit && exit.x === x && exit.y === y) {
                exit = null;
                cellContent.classList.remove('exit');
            }
            if (entrance) {
                document.getElementById(`cell-content-${entrance.x}-${entrance.y}`).classList.remove('entrance');
            }
            entrance = { x, y };
            cellContent.classList.add('entrance');
        }
    } else if (mode === 'exit') {
        if (exit && exit.x === x && exit.y === y) {
            exit = null;
            cellContent.classList.remove('exit');
        } else {
            if (entrance && entrance.x === x && entrance.y === y) {
                entrance = null;
                cellContent.classList.remove('entrance');
            }
            if (exit) {
                document.getElementById(`cell-content-${exit.x}-${exit.y}`).classList.remove('exit');
            }
            exit = { x, y };
            cellContent.classList.add('exit');
        }
    }

    checkReady();
}


function placeWall(x, y, orientation) {
    if (ready) return;
    if (mode !== 'wall') return;
    const wallId = orientation === 'horizontal' ? `wall-horizontal-${x}-${y}` : `wall-vertical-${x}-${y}`;
    const wallElement = document.getElementById(wallId);
    
    if (!wallElement.classList.contains('active') && walls.length < maxWalls) {
        wallElement.classList.add('active');
        if (orientation === 'horizontal') {
            walls.push([x, y, x-1, y]);
        } else {
            walls.push([x, y, x, y-1]);
        }
    } else if (wallElement.classList.contains('active')) {
        wallElement.classList.remove('active');
        if (orientation === 'horizontal') {
            walls = walls.filter(wall => !(wall[0] === x && wall[1] === y && wall[2] === x-1 && wall[3] === y));
        } else {
            walls = walls.filter(wall => !(wall[0] === x && wall[1] === y && wall[2] === x && wall[3] === y-1));
        }
    }
    updateWallCount();
    checkReady();
}

function updateWallCount() {
    document.getElementById('wall-count').innerText = maxWalls - walls.length;
}

function clearBoard() {
    if (ready) return;
    walls.forEach(wall => {
        const [x, y, ,] = wall;
        var hor_wall = document.getElementById(`wall-horizontal-${x}-${y}`);
        var vert_wall = document.getElementById(`wall-vertical-${x}-${y}`);
        if(hor_wall) hor_wall.classList.remove('active');
        if(vert_wall) vert_wall.classList.remove('active');
    });
    walls = [];
    if (entrance) {
        document.getElementById(`cell-content-${entrance.x}-${entrance.y}`).classList.remove('entrance');
        entrance = null;
    }
    if (exit) {
        document.getElementById(`cell-content-${exit.x}-${exit.y}`).classList.remove('exit');
        exit = null;
    }
    updateWallCount();
    checkReady();
}

function getRandomWall() {
    let x, y, orientation;
    let wallExists = true;

    while (wallExists) {
        x = Math.floor(Math.random() * boardWidth);
        y = Math.floor(Math.random() * boardHeight);

        orientation = Math.random() > 0.5 ? 'horizontal' : 'vertical';

        if(x == 0){
            orientation = 'vertical'
        }
        else if(y == 0){
            orientation = 'horizontal'
        }
        if(x == 0 && y == 0){
            continue;
        }

        if (orientation === 'horizontal') {
            wallExists = walls.some(wall => wall[0] === x && wall[1] === y && wall[2] === x - 1 && wall[3] === y);
        } else {
            wallExists = walls.some(wall => wall[0] === x && wall[1] === y && wall[2] === x && wall[3] === y - 1);
        }
    }

    return { x, y, orientation };
}


function getRandomCoords() {
    let entranceCoords = {};
    let exitCoords = {};

    entranceCoords.x = Math.floor(Math.random() * boardWidth);
    entranceCoords.y = Math.floor(Math.random() * boardHeight);

    do {
        exitCoords.x = Math.floor(Math.random() * boardWidth);
        exitCoords.y = Math.floor(Math.random() * boardHeight);
    } while (entranceCoords.x === exitCoords.x && entranceCoords.y === exitCoords.y);

    return { entranceCoords, exitCoords };
}


function randomBoard() {
    clearBoard();

    setMode("wall");
    for (var i = 0; i < 20; i++) {
        var randomWall = getRandomWall();
        placeWall(randomWall.x, randomWall.y, randomWall.orientation);
    }

    setMode("entrance");
    var coords = getRandomCoords();
    handleCellClick(coords.entranceCoords.x, coords.entranceCoords.y);

    setMode("exit");
    handleCellClick(coords.exitCoords.x, coords.exitCoords.y);
    setMode("wall");
}


function checkReady() {
    if(ready) return;
    const submitButton = document.getElementById("submit-button");
    if (entrance && exit && walls.length === maxWalls) {
        submitButton.classList.add('active');
        submitButton.disabled = false;
    } else {
        submitButton.classList.remove('active');
        submitButton.disabled = true;
    }
}

function getCsrfToken() {
    return document.querySelector('#ready-form input[name="csrfmiddlewaretoken"]').value;
}

function submitBoard() {
    if(ready) return;
    fetch(updateGameStageUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCsrfToken()
        },
        body: JSON.stringify({
            entrance: entrance,
            exit: exit,
            walls: walls
        }),
        credentials: "same-origin"
    }).then(response => response.json())
      .then(data => {
        if (data.error) {
            for (let [key, value] of Object.entries(data.error)) {
                firstError = value[0];
                break;
            }
            Swal.fire({
                title: 'Error!',
                text: firstError,
                icon: 'error',
                confirmButtonText: 'OK'
            });
        }
        else{
            location.reload();
        }
    });
}

