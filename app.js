var http = require('http');
var fs = require('fs');
var path = require('path');

const fs2 = require('fs');

//Create directoty for statistics of our server
var dir = './statistics';
if (!fs2.existsSync(dir)){
    fs2.mkdirSync(dir);
}



//Start write to new File
let writeStream = fs2.createWriteStream('statistics/results_'+ myCurrentDate() +'.csv');
writeStream.write('FilePath,DateTime\n');


var server = http.createServer(function (request, response) {

    var filePath = '.' + request.url;
    var datetimeRequestStart = myCurrentDate();



    if(filePath.includes(".mpd") === true){
      console.log('(manifest) : request starting... : ' + filePath + '\n');
    }
    else if ( filePath.includes("video_audio") === true){
        //console.log('(audio) : request starting... : ' + filePath + '\n');
    }
    else if ( filePath.includes("video") === true){
        console.log('(segment) : request starting... : ' + filePath + '\n');
        // write to a new line in file named secret.txt
        writeStream.write(filePath + ','+ myCurrentTime()  +  '\n');
    }



    if (filePath == './')
        filePath = './index.html';

    var extname = path.extname(filePath);
    var contentType = 'text/html';
    switch (extname) {
	     case '.m4s':
            contentType = 'dash/m4s';
            break;
       case '_dashinit.mp4':
            contentType = 'dashinit/mp4';
            break;
        case '.mpd':
            contentType = 'manifest/mpd';
            break;
        case '.mp4':
            contentType = 'video/mp4';
            break;
        case '.m4a':
            contentType = 'audio/m4a';
            break;
    }


    fs.readFile(filePath, function(error, content) {
       if (error) {
            if(error.code == 'ENOENT'){
                fs.readFile('./404.html', function(error, content) {
                    response.writeHead(404, {"Content-Type": "text/html"});
                    response.write("404 Not Found\n");
                    response.end(content, 'utf-8');
                });
            }
            else {
                response.writeHead(500);
                response.end('Sorry, check with the site admin for error: '+error.code+' ..\n');
                response.end();
            }
        }
       else {
            //response.setHeader('Cookie', ['filePath=' + filePath, 'resolution=' + myResolution(filePath)]);
            response.setHeader('Cookie', [ filePath, myResolution(filePath)]);
            response.writeHead(200, { 'Content-Type': contentType  });
            response.end(content, 'utf-8');
        }
    });
  }).listen(1337, '10.0.0.1');
 console.log('Server running at http://10.0.0.1:1337/');
//}).listen(1337, '127.0.0.1');
//console.log('Server running at http://127.0.0.1:1337/');


server.on('close', function() {
  // the finish event is emitted when all data has been flushed from the stream
  writeStream.on('finish', () => {
      console.log('Create a new file with statistics of the experiment.\n');
  });

  // close the stream
  writeStream.end();

  console.log('Server stopped.\n');
});

process.on('SIGINT', function() {
  console.log('User typed : ^C');
  server.close();
});

function myCurrentDate() {
  let date_ob = new Date();
  // current date
  // adjust 0 before single digit date
  let date = ("0" + date_ob.getDate()).slice(-2);
  // current month
  let month = ("0" + (date_ob.getMonth() + 1)).slice(-2);
  // current year
  let year = date_ob.getFullYear();
  // current hours
  let hours = date_ob.getHours();
  // current minutes
  let minutes = date_ob.getMinutes();
  // current seconds
  let seconds = date_ob.getSeconds();
  // current date of server in YYYYMMDD_HH:MM:SS format
  let myDate = year  + month  + date + "_" + hours + ":" + minutes + ":" + seconds

  return myDate;             // Function returns myDate
}

function myCurrentTime() {
  let date_ob = new Date();
  // current time
  // current hours
  let hours = date_ob.getHours();
  // current minutes
  let minutes = date_ob.getMinutes();
  // current seconds
  let seconds = date_ob.getSeconds();
  // current milliseconds
  let milliseconds = date_ob.getMilliseconds();
  // current date of server in HH:MM:SS format
  let myTime = hours + ":" + minutes + ":" + seconds + '.' + milliseconds

  return myTime;             // Function returns myTime
}

function myResolution(filePath){
  //Find data from: https://stackoverflow.com/questions/10003683/extract-get-a-number-from-a-string


  if(filePath.includes(".mpd") === true){
    return ''
  }
  else if ( filePath.includes("video_audio") === true){
    return ''
  }
  else if ( filePath.includes("video") === true){
    var myNum = filePath.replace(/^\D+|\D.*$/g, "");
    var myResolution = '1920 x 1080';
    if( myNum === '242')
      myResolution = '430 x 242';
    else if( myNum === '360')
      myResolution = '640 x 360';
    else if( myNum === '480')
      myResolution = '849 x 480';
    else if( myNum === '720')
      myResolution = '1280 x 720';
    else if( myNum === '1080')
      myResolution = '1920 x 1080';

      return myResolution
  }

}

var units = ["B", "kB", "MB", "TB"];
function simplifiedUnits(input) {
    var unit = units[0];
    var i = 0;
    while (input > 1024 && ++i) {
        unit = units[i];
        input /= 1024;
    }
    return Math.round(input) + " " + unit;
}


process.on('SIGINT', function() {
  console.log('User typed : ^C');
  server.close();
});

