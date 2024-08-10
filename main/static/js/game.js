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
        }
        else{
            updateWalls(data.spotted_walls);
            clearCanGo();
            SwitchPlayersTurn();
        }
        if(data.game_ended == true){
            clearCanGo();            
        }
    })
    .catch(error => console.error('Error:', error));
}

document.addEventListener("DOMContentLoaded", function() {
    initializeCanGo(can_go);
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