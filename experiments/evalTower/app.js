global.__base = __dirname + '/';

var
    use_https     = true,
    argv          = require('minimist')(process.argv.slice(2)),
    https         = require('https'),
    fs            = require('fs'),
    app           = require('express')(),
    _             = require('lodash'),
    parser        = require('xmldom').DOMParser,
    XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest,
    sendPostRequest = require('request').post,
    cors          = require('cors');

////////// EXPERIMENT GLOBAL PARAMS //////////

var gameport;
var researchers = ['A4SSYO0HDVD4E', 'A9AHPCS83TFFE'];
var blockResearcher = false;

if(argv.gameport) {
  gameport = argv.gameport;
  console.log('using port ' + gameport);
} else {
  gameport = 8886;
  console.log('no gameport specified: using 8886\nUse the --gameport flag to change');
}

try {
  var privateKey  = fs.readFileSync('/etc/letsencrypt/live/cogtoolslab.org/privkey.pem'),
      certificate = fs.readFileSync('/etc/letsencrypt/live/cogtoolslab.org/cert.pem'),
      intermed    = fs.readFileSync('/etc/letsencrypt/live/cogtoolslab.org/chain.pem'),
      options     = {key: privateKey, cert: certificate, ca: intermed},
      server      = require('https').createServer(options,app).listen(gameport),
      io          = require('socket.io')(server);
} catch (err) {
  console.log("cannot find SSL certificates; falling back to http");
  var server      = app.listen(gameport),
      io          = require('socket.io')(server);
}

// serve stuff that the client requests
app.get('/*', (req, res) => {
  serveFile(req, res);
});

io.on('connection', function (socket) {

  // Recover query string information and set condition
  var gameid = UUID();
  var hs = socket.request;  
  var query = require('url').parse(hs.headers.referer, true).query;
  var id = query.workerId;
  var isResearcher = _.includes(researchers, id);

  var packet = {
    gameid: gameid,    
  };  

  if (!id || isResearcher && !blockResearcher){
    socket.emit('onConnected', packet); 
  } else if (!valid_id(id)) {
    console.log('invalid id, blocked');
  } else {
    checkPreviousParticipant(id, (exists) => {
      return exists ? handleDuplicate(socket) : initializeWithTrials(socket);
    });
  }

    // write data to db upon getting current data
    socket.on('currentData', function(data) {
	console.log('currentData received: ' + JSON.stringify(data));
	// Increment games list in mongo here
	writeDataToMongo(data);
    });

    // got request for stim
    socket.on('getStim', function(data) {
	console.log('got a stim request');
	sendStim(socket, data);
    });  

});

var serveFile = function(req, res) {
  var fileName = req.params[0];
  console.log('\t :: Express :: file requested: ' + fileName);
  return res.sendFile(fileName, {root: __dirname});
};

var handleDuplicate = function (socket) {
  console.log("duplicate id: blocking request");
  socket.emit('redirect', '/duplicate.html');
};

var valid_id = function (id) {
  return (id.length <= 15 && id.length >= 12) || id.length == 41;
};

var handleInvalidID = function (socket) {
  console.log("invalid id: blocking request");
  socket.emit('redirect', '/invalid.html');
};

function checkPreviousParticipant(workerId, callback) {
  var p = { 'workerId': workerId };
  var postData = {
    dbname: 'causaldraw',
    query: p,
    projection: { '_id': 1 }
  };
  sendPostRequest(
    'http://localhost:7000/db/exists',
    { json: postData },
    (error, res, body) => {
      try {
        if (!error && res.statusCode === 200) {
          console.log("success! Received data " + JSON.stringify(body));
          callback(body);
        } else {
          throw `${error}`;
        }
      }
      catch (err) {
        console.log(err);
        console.log('no database; allowing participant to continue');
        return callback(false);
      }
    }
  );
};

function sendStim(socket, data) {
  console.log('sending request to mongo')
  sendPostRequest('http://localhost:7000/db/getstims', {
    json: {
      dbname: 'stimuli',
      colname: 'curiotower_curiodrop',
      numTrials: 1,
      gameid: data.gameID
    }
  }, (error, res, body) => {
    if (!error && res.statusCode === 200) {
      socket.emit('stimulus', body);     
    } else {
      console.log(`error getting stims: ${error} ${body}`);
      console.log(`falling back to local stimList`);
      socket.emit('stimulus', _.sample(require('./example.json')));
    }
  });
} // 

var UUID = function() {
  var baseName = (Math.floor(Math.random() * 10) + '' +
        Math.floor(Math.random() * 10) + '' +
        Math.floor(Math.random() * 10) + '' +
        Math.floor(Math.random() * 10));
  var template = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx';
  var id = baseName + '-' + template.replace(/[xy]/g, function(c) {
    var r = Math.random()*16|0, v = c == 'x' ? r : (r&0x3|0x8);
    return v.toString(16);
  });
  return id;
};

var writeDataToMongo = function(data) {
  sendPostRequest(
    'http://localhost:7000/db/insert',
    { json: data },
    (error, res, body) => {
      if (!error && res.statusCode === 200) {
        console.log(`sent data to store`);
      } else {
	      console.log(`error sending data to store: ${error} ${body}`);
      }
    }
  );
};
