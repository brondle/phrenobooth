let express = require('express');
var app = express();
let fs = require("fs");

var bodyParser = require('body-parser');
var multer  = require('multer');

app.use(express.static('public'));
app.use(bodyParser.urlencoded({ extended: false }));


var upload = multer({ dest: './img/'});


// File input field name is simply 'file'
app.post('/file_upload', upload.single('file'), function(req, res) {
  /** When using the "single"
      data come in "req.file" regardless of the attribute "name". **/
  console.log('req: ', req);
  var tmp_path = req.file.path;

  /** The original name of the uploaded file
      stored in the variable "originalname". **/
  var target_path = 'img/' + req.file.originalname;

  /** A better way to copy the uploaded file. **/
  var src = fs.createReadStream(tmp_path);
  var dest = fs.createWriteStream(target_path);
  src.pipe(dest);
  src.on('end', function() {
    res.send('complete');
  });
  src.on('error', function(err) { res.send('error: ', err); });
});

app.listen(3030);
