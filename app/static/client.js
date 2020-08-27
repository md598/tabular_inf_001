var el = x => document.getElementById(x);

function showPicker() {
  el("file-input").click();
  console.log('showPicker');
  el("upload-label").innerHTML = 'picked';
}

/*
function showPicked(input) {
  el("upload-label").innerHTML = input.files[0].name;
  var reader = new FileReader();
  reader.onload = function(e) {
    console.log('showPicked1');
    el("image-picked").src = e.target.result;
    el("image-picked").className = "";
    console.log('showPicked2');
  };
  reader.readAsDataURL(input.files[0]);
}
*/

/*
//download local csv
function download2(filename, url) {
  var alink = document.createElement('a');
  //alink.setAttribute('href', 'data:text/csv;charset=utf-8,' + encodeURIComponent(text));
  alink.setAttribute('href', url);
  alink.setAttribute('download', filename);

  alink.style.display = 'none';
  document.body.appendChild(alink);

  alink.click();

  document.body.removeChild(alink);
}
*/

//Tabular
function analyze(){
    var uploadFiles = el('file-input').files;
    if (uploadFiles.length < 1) alert('Please select 1 file to analyze!');
    el('analyze-button').innerHTML = 'Analyzing...';
    var xhr = new XMLHttpRequest();
    var loc = window.location;
    xhr.open("POST", '${loc.protocol}//${loc.hostname}:${loc.port}/analyze', true);
    xhr.onerror = function() {alert (xhr.responseText);}
    xhr.onload = function(e) {
        if (this.readyState === 4) {
          // wanting to send the user the csv file saved in 'analyze' in server.py
          el("result-label").innerHTML = `Result = File Accepted`;
          //el("result-label").innerHTML = '${loc.protocol}//${loc.hostname}/app/static/results.csv';
          //console.log('${loc.protocol}//${loc.hostname}/app/static/results.csv');
          //download('results.csv', 'results.csv');
          //download2('results.csv','${loc.protocol}//${loc.hostname}/app/static/results.csv');
          var path = loc.protocol + '//' +  loc.hostname + '/app/static/results.csv';
          console.log(path);
          //download2('results.csv',path);
          var alink = document.createElement('a');
          alink.setAttribute('href', path);
          alink.setAttribute('download', 'results.csv');
          alink.style.display = 'none';
          document.body.appendChild(alink);
          console.log(alink.innerHTML);
          console.log('waypoint2');
          alink.click();
          document.body.removeChild(alink);
          el("result-label").innerHTML = 'download';
          //xhr.send();
        }
        el("analyze-button").innerHTML = "Analyze";
      };
    console.log('waypoint3');
    var fileData = new FormData();
    fileData.append("file", uploadFiles[0]); 
    xhr.send(fileData);
}


/*Vision
function analyze() {
  var uploadFiles = el("file-input").files;
  if (uploadFiles.length !== 1) alert("Please select a file to analyze!");

  el("analyze-button").innerHTML = "Analyzing...";
  var xhr = new XMLHttpRequest();
  var loc = window.location;
  xhr.open("POST", `${loc.protocol}//${loc.hostname}:${loc.port}/analyze`,
    true);
  xhr.onerror = function() {
    alert(xhr.responseText);
  };
  xhr.onload = function(e) {
    if (this.readyState === 4) {
      var response = JSON.parse(e.target.responseText);
      el("result-label").innerHTML = `Result = ${response["result"]}`;
    }
    el("analyze-button").innerHTML = "Analyze";
  };

  var fileData = new FormData();
  fileData.append("file", uploadFiles[0]);
  xhr.send(fileData);
}
*/
