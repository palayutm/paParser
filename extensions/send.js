var ws = new WebSocket("ws://localhost:12358/parse");

ws.onopen = function() {
    var msg = JSON.stringify({
        url: window.location.href,
        data: document.body.innerHTML
    })
    ws.send(msg);
};

ws.onmessage = function(evt) {
    var msg = evt.data;
    alert(msg)
};

ws.onerror = function(event) {
    alert('Connect paParser daemon failed. ');
    console.error("WebSocket error observed:", event);
}


