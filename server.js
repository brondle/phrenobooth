let express = require('express');
let http = require('http');
let app = express();
let server = app.listen(3030);
let io = require('socket.io').listen(server);
let fs = require("fs");
let path = require('path');

var bodyParser = require('body-parser');
var multer  = require('multer');

app.use(express.static(__dirname));
app.use(bodyParser.urlencoded({ extended: false }));


var upload = multer({ dest: './img/'});
app.get('/', function(req, res) {
    res.sendFile(path.join(__dirname + '/index.html'));
});

io.on('connection', function(socket){
  console.log('a user connected');
});

let i = 0;
// File input field name is simply 'file'
app.post('/file_upload', upload.single('file'), function(req, res) {
  /** When using the "single"
      data come in "req.file" regardless of the attribute "name". **/
  var tmp_path = req.file.path;

  /** The original name of the uploaded file
      stored in the variable "originalname". **/
  var target_path = 'img/' + i + '_' + req.file.originalname;
  i++;

  /** A better way to copy the uploaded file. **/
  var src = fs.createReadStream(tmp_path);
  var dest = fs.createWriteStream(target_path);
  src.pipe(dest);
  src.on('end', function() {
    io.emit('new_image', {filepath: target_path});
    res.send('complete');
  });
  src.on('error', function(err) { res.send('error: ', err); });
});

