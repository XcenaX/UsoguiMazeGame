document.addEventListener("DOMContentLoaded", function() {
    const chatForm = document.getElementById('chat-form');
    const chatMessages = document.getElementById('chat-messages');
    chatMessages.scrollTop = chatMessages.scrollHeight;

    const chatSocket = new WebSocket(
        'ws://' + window.location.host + '/ws/game/' + gameId + '/'
    );

    chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const message = data.message;
    const message_type = data.type;

    console.log("DATA", data);

    if (data.exit) {
        if(data.should_delete_game==true){
            Swal.fire({
                title: 'Warning!',
                text: "Your opponent has left the game. You will be redirected to main page",
                icon: 'error',
                confirmButtonText: 'OK'
            });
            window.location.href = '/'; // Адрес главной страницы
            return;
        }
        const player = document.getElementById("player-opponent");
        player.children[1].textContent = "Waiting...";
        Swal.fire({
            title: 'Warning!',
            text: "Your opponent has left the game",
            timer: 3000,
            timerProgressBar: true,
            icon: 'warning',
            showConfirmButton: false,
            showCancelButton: false,
            showCloseButton: false
        });        

    } else if (data.opponent_position){
        updatePlayerPosition(data.opponent_position, me=true);
        if (data.can_go){
            initializeCanGo(data.can_go);
        }
        if (data.turn_ended === true){
            SwitchPlayersTurn();
        }
        if (data.visited_cells){
            ClearPaths(false);
            CreatePaths(data.visited_cells, false);
        }
    } else if(data.game_started){
        window.location.reload();
    } else if(data.opponent_came == true){
        const player = document.getElementById("player-opponent");
        player.children[1].textContent = data.opponent;
    } else if(data.opponent_ready == true){
        const player = document.getElementById("player-opponent");
        player.classList.add('ready');       
    } else if(data.game_ended == true){
        window.location.reload();
    } 

    if(message && message_type == "chat_message"){
        const lastMessageGroup = chatMessages.lastElementChild;
        const lastMessage = lastMessageGroup ? lastMessageGroup.querySelector('.chat-message') : null;
        const lastTimestamp = lastMessage ? new Date(lastMessage.querySelector('.chat-time').getAttribute('data-timestamp')) : null;
        const messageTimestamp = new Date(message.created_at);
        const lastUser = lastMessage ? lastMessage.querySelector('.chat-user').dataset.sessionKey : null;
        const messageUser = message.session_key ? message.session_key : message.user;

        console.log(lastMessage, lastUser, message);
    
        const formattedTime = messageTimestamp.getHours().toString().padStart(2, '0') + ':' + messageTimestamp.getMinutes().toString().padStart(2, '0');
    
        if (lastTimestamp && (messageTimestamp - lastTimestamp) / 1000 <= 60 && lastUser === messageUser) {
            // Добавляем новое сообщение в последнюю группу
            const newMessageText = document.createElement('span');
            newMessageText.classList.add('chat-text');
            newMessageText.textContent = message.text;
            lastMessage.appendChild(newMessageText);
            // Обновляем временную метку группы сообщений
            lastMessage.querySelector('.chat-time').textContent = formattedTime;
        } else {
            // Создаем новую группу сообщений
            const newMessageGroup = document.createElement('div');
            newMessageGroup.classList.add('chat-message-group');
            const newMessage = document.createElement('div');
            newMessage.classList.add('chat-message');
            if (message.session_key === sessionKey) {
                newMessage.classList.add('self');
            }
            if (message.text == "activateSVIN"){
                newMessage.innerHTML = `
                    <span class="chat-user" data-session-key="${message.session_key}">${message.user}</span>
                    <span class="chat-time" data-timestamp="${message.created_at}">${formattedTime}</span>
                    <div class="chat-image"></div>
                `;
            } else{
                newMessage.innerHTML = `
                    <span class="chat-user" data-session-key="${message.session_key}">${message.user}</span>
                    <span class="chat-time" data-timestamp="${message.created_at}">${formattedTime}</span>
                    <span class="chat-text">${message.text}</span>
                `;
            }
            newMessageGroup.appendChild(newMessage);
            chatMessages.appendChild(newMessageGroup);
        }
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }    
};

    chatSocket.onclose = function(e) {
        console.error('Chat socket closed unexpectedly. Reloading page...');
        window.location.reload();
    };

    chatForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const messageInputDom = document.getElementById('chat-text');
        const message = messageInputDom.value;
        chatSocket.send(JSON.stringify({
            'message': {
                'user': username,
                'text': message,
                'created_at': new Date().toISOString()
            }
        }));
        messageInputDom.value = '';
    });

    // Convert timestamps to local time
    const timestamps = chatMessages.getElementsByClassName("chat-time");
    for (let i = 0; i < timestamps.length; i++) {
        const timestamp = timestamps[i];
        const date = new Date(timestamp.getAttribute("data-timestamp"));
        const formattedTime = date.getHours().toString().padStart(2, '0') + ':' + date.getMinutes().toString().padStart(2, '0');
        timestamp.textContent = formattedTime;
    }   
});