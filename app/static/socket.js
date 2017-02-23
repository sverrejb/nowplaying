$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect();

    //receive details from server
    socket.on('newnumber', function(msg) {
        console.log("Hello, world!" + msg);
        //do stuff

    });

});