const roomName = JSON.parse(document.getElementById('json-roomname').textContent);
const userName = JSON.parse(document.getElementById('json-username').textContent);
const Token = JSON.parse(document.getElementById('json-token').textContent);
const chatSocket = new WebSocket('ws://' + window.location.host + '/ws/chat/' + roomName + '/?token=' + Token);

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    if (data.message) {
        let html;
        if (data.username === userName) {
            html = '<div class="flex justify-end mb-2">';
            html += '<div class="bg-sky-500 text-black p-4 rounded-xl">';
        } else {
            html = '<div class="flex mb-2">';
            html += '<div class="bg-gray-200 text-black p-4 rounded-xl">';
        }
        html += '<p class="font-semibold">' + data.username + '</p>';
        html += '<p>' + data.message + '</p></div></div>';
        document.querySelector('#chat-messages').innerHTML += html;
        scrollToBottom();
    }
}

chatSocket.onclose = function(e) {
    console.log("Bye!");
}

document.querySelector('#chat-message-submit').onclick = function(e){
    e.preventDefault();
    const messageInputDom = document.querySelector('#chat-message-input');
    const message = messageInputDom.value;
    chatSocket.send(JSON.stringify({
        'message': message,
        'username': userName,
        'room': roomName
    }));
    messageInputDom.value = '';
    return false;
}

function scrollToBottom() {
    const objDiv = document.querySelector('#chat-messages');
    objDiv.scrollTop = objDiv.scrollHeight;
}

window.onload = function() {
    scrollToBottom();
};
