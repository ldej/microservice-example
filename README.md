TODO:
 - Some way to show the websockets potential.
     - Subscribe to a certain channel, with the websocket. A callback from another channel should post something back
       in the websocket channel. So like somebody is posting information, and you get a message of that via
       websocket.
     - Make a simple websocket webpage with input fields for: the service you want to call, the data you want to
       send. And a way to select which websocket channel you want to subscribe to. Maybe subscribe to more channels
       over the same websocket?

 - Add a way to send messages to other services.
 - Use marshmallow schema's for loading and dumping data at service calls.
 - Add a javascript way to use these schema's and invoke services.
 - Add an easy service call test thing.

