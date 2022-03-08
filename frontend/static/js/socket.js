/*var form = document.querySelector("form")
const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/post/'
);

chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    console.log(data)
};

chatSocket.onclose = function (e) {
    console.error('Chat socket closed unexpectedly');
};

form.onsubmit = (e) => {
    e.preventDefault();
    var message = e.target["post_text"].value
    chatSocket.send(JSON.stringify({
        'message': message
    }));
}*/
