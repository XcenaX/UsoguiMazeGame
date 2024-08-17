function clearCanGo() {
    const cells = document.querySelectorAll('.cell-content.can-go');
    cells.forEach(cell => {
        cell.classList.remove('can-go');
        cell.onclick = null;
    });
}

function addCanGo(cells) {
    cells.forEach(cell => {
        const cellElement = document.getElementById(`opponent-cell-content-${cell.x}-${cell.y}`);
        if (cellElement) {
            cellElement.classList.add('can-go');
            cellElement.onclick = function(){
                makeMove(cell.x, cell.y)
            };
        }
    });
}

function initializeCanGo(cells) {
    clearCanGo();
    addCanGo(cells);
}

function updateWalls(spottedWalls) {
    const horizontalWalls = document.querySelectorAll('.wall-horizontal.opponent.active');
    horizontalWalls.forEach(wall => wall.classList.remove('active'));

    const verticalWalls = document.querySelectorAll('.wall-vertical.opponent.active');
    verticalWalls.forEach(wall => wall.classList.remove('active'));

    spottedWalls.forEach(wall => {
        const [x1, y1, x2, y2] = wall;
        // 1 1 1 0
        if (x1 === x2) {
            const wallElement = document.getElementById(`opponent-wall-vertical-${x1}-${Math.max(y1, y2)}`);
            if (wallElement) {
                wallElement.classList.add('active');
            }
        } else if (y1 === y2) {
            const wallElement = document.getElementById(`opponent-wall-horizontal-${Math.max(x1, x2)}-${y1}`);
            if (wallElement) {
                wallElement.classList.add('active');
            }
        }
    });
}

function updatePlayerPosition(playerPosition, me=false) {
    playerClass = "me";
    if(me == false){
        playerClass = "opponent";
    }
    const currentPlayerCell = document.querySelector('.player.'+playerClass);
    if (currentPlayerCell) {
        currentPlayerCell.classList.remove('player');
        currentPlayerCell.classList.remove(playerClass);
    }
    
    
    if (me === false){
        if ((playerPosition["x"] == opponent_entrance["x"] && playerPosition["y"] == opponent_entrance["y"])
            || (playerPosition["x"] == opponent_exit["x"] && playerPosition["y"] == opponent_exit["y"])){
          return;
        }
    } else if (me === true){
        if ((playerPosition["x"] == entrance["x"] && playerPosition["y"] == entrance["y"])
            ||  (playerPosition["x"] == exit["x"] && playerPosition["y"] == exit["y"])){
            return;
        } 
    }
    

    const newPlayerCell = document.getElementById(`${playerClass}-cell-content-${playerPosition.x}-${playerPosition.y}`);
    if (newPlayerCell) {
        newPlayerCell.classList.add('player');
        newPlayerCell.classList.add(playerClass);
    }
}

function makeMove(x, y) {
    fetch(makeMoveUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            wanted_position: {x: x, y: y}
        })
    })
    .then(response => response.json())
    .then(data => {
        if(data.success == true){
            updatePlayerPosition(data.player_position, me=false);
            initializeCanGo(data.can_go);
            ClearPaths();
            CreatePaths(data.visited_cells);
        }
        else{
            updateWalls(data.spotted_walls);
            clearCanGo();
            SwitchPlayersTurn();
        }
        if(data.game_ended == true){
            window.location.reload();
        }
    })
    .catch(error => console.error('Error:', error));
}

document.addEventListener("DOMContentLoaded", function() {
    initializeCanGo(can_go);
    CreatePaths(visitedCells);
});

function SwitchPlayersTurn(){
    let players = document.querySelectorAll('.player-block'); 
    if (players[0].classList.contains('ready')) {
        players[0].classList.remove('ready');
        players[1].classList.add('ready');
    } else{
        players[1].classList.remove('ready');
        players[0].classList.add('ready');
    }
}

function removeRedundantCells(visitedCells) {
    const optimizedCells = [];
    
    for (let i = 0; i < visitedCells.length - 1; i++) {
        const currentCell = visitedCells[i];
        const nextCell = visitedCells[i + 1];

        // Если текущая клетка и следующая клетка совпадают, пропускаем текущую
        if (!(currentCell[0] === nextCell[0] && currentCell[1] === nextCell[1])) {
            optimizedCells.push(currentCell);
        }
    }

    // Не забываем добавить последнюю клетку, так как она не будет проверена в цикле
    optimizedCells.push(visitedCells[visitedCells.length - 1]);

    return optimizedCells;
}


function getPath(directions) {
    const path = {};

    // Функция для определения направления между двумя клетками
    function getDirection(from, to) {
        if (from[0] > to[0]) return 'bottom';
        if (from[0] < to[0]) return 'top';
        if (from[1] > to[1]) return 'right';
        if (from[1] < to[1]) return 'left';
        return '';
    }

    // Основной цикл
    for (let i = 0; i < directions.length; i++) {
        const current = directions[i];
        const key = `${current[0]}-${current[1]}`;

        // Если ключ уже существует, значит, мы добавляем направления к уже существующим
        let directionsSet = new Set(path[key] ? path[key].split(' ') : []);

        // Проверяем предыдущую клетку
        if (i > 0) {
            const prev = directions[i - 1];
            const directionFromPrev = getDirection(prev, current);
            console.log(`From ${prev} to ${current}: ${directionFromPrev}`); // вывод промежуточных значений
            directionsSet.add(directionFromPrev);
        }

        // Проверяем следующую клетку
        if (i < directions.length - 1) {
            const next = directions[i + 1];
            const directionToNext = getDirection(next, current);
            console.log(`From ${current} to ${next}: ${directionToNext}`); // вывод промежуточных значений
            directionsSet.add(directionToNext);
        }

        // Обновляем направления для текущей клетки
        path[key] = Array.from(directionsSet).join(' ');
    }

    return path;
}


function ClearPaths(opponent=true) {
    // Найти все элементы .path-img на доске соперника и удалить их
    let pathImgs = [];
    if(opponent === true){
        pathImgs = document.querySelectorAll('.opponent-board .board-cell .cell-content .path-img');
    } else{
        pathImgs = document.querySelectorAll('.my-board .board-cell .cell-content .path-img');
    }

    pathImgs.forEach(pathImg => {
        pathImg.remove(); // Удаляет элемент .path-img
    });
}



function CreatePaths(paths, opponent=true) {
    // Расчет CSS классов для клеток на основе посещенных путей
    const optimizedPaths = removeRedundantCells(paths);
    const pathClasses = getPath(optimizedPaths);

    let user = "opponent";
    if(!opponent){
        user = "me";
    }

    console.log(pathClasses);

    // Применение CSS классов к элементам .path-img на доске соперника
    for (const cell in pathClasses) {
        let [x, y] = cell.split('-');
        let directions = pathClasses[cell].split(' ');

        const cellElement = document.querySelector(`#${user}-cell-content-${x}-${y}`);

        // Проверка на наличие классов .exit, .entrance, или .player
        if (cellElement && !(cellElement.classList.contains('exit') || cellElement.classList.contains('entrance') || cellElement.classList.contains('player'))) {
            // Создание нового элемента .path-img
            directions.forEach(direction => {
                const pathImgElement = document.createElement('div');
                pathImgElement.classList.add('path-img', direction);
                cellElement.appendChild(pathImgElement);
            });
        }
    }
}


