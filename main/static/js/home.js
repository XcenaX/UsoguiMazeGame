function JoinGame(game_code, password){
    fetch(`/game/${game_code}/join/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            password: password
        }),
        credentials: "same-origin"
    })
    .then(response => response.json())
    .then(data => {
        if(data.success === true){ 
            window.location.href = `${window.location.origin}/game/${game_code}/`;
        } else {
            Swal.fire({
                title: 'Error',
                text: data.error,
                icon: 'error',
                confirmButtonColor: '#3085d6',
                confirmButtonText: 'Ok'
            });
        }
    })
    .catch(error => console.error('Error:', error));
}

function LeaveGame(game_code){
    fetch(`/game/${game_code}/leave/`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        credentials: "same-origin"
    })
    .then(response => response.json())
    .then(data => {
        if(data.success === true){ 
            window.location.reload();
        } else {
            Swal.fire({
                title: 'Error',
                text: data.error,
                icon: 'error',
                confirmButtonColor: '#3085d6',
                confirmButtonText: 'Ok'
            });
        }
    })
    .catch(error => console.error('Error:', error));
}

function CreateGame(data) {
    fetch('/create-game/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            Swal.fire({
                title: 'Game Created',
                text: 'Your game has been created successfully!',
                icon: 'success'
            });
            window.location = data.redirect;
        } else {
            Swal.fire({
                title: 'Error',
                text: data.error,
                icon: 'error'
            });
        }
    })
    .catch(error => {
        Swal.fire({
            title: 'Error',
            text: 'An error occurred while creating the game.',
            icon: 'error'
        });
    });
}

