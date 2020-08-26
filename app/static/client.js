var el = x => document.getElementById(x);

function showPicker() {
  el("file-input").click();
  console.log("waypoint-1");
}

function showPicked(input) {
  el("upload-label").innerHTML = input.files[0].name;
  var reader = new FileReader();
  console.log("waypoint0");
  reader.onload = function(e) {
    el("image-picked").src = e.target.result;
    el("image-picked").className = "";
  };
  reader.readAsDataURL(input.files[0]);
}

//Tabular
function analyze(){
    var uploadFiles = el('file-input').files;
    if (uploadFiles.length < 1) alert('Please select 1 file to analyze!');

    el('analyze-button').innerHTML = 'Analyzing...';
    var xhr = new XMLHttpRequest();
    var loc = window.location;
    console.log("Pre-POST"); 
    xhr.open("POST", `${loc.protocol}//${loc.hostname}:${loc.port}/analyze`, true);
    console.log("Post-POST"); 
    xhr.onerror = function() {alert (xhr.responseText);}
    console.log("waypoint1"); 
    xhr.onload = function(e) {
        if (this.readyState === 4) {
          el("result-label").innerHTML = `Result = File Accepted`;
          console.log("waypoint2");
          download('results.csv', 'results.csv');
          console.log("waypoint3");
          xhr.send();
        }
        el("analyze-button").innerHTML = "Analyze";
        console.log("waypoint4");
      };

      var fileData = new FormData();
      console.log("waypoint5");
      fileData.append("file", uploadFiles[0]);
      console.log("waypoint6");
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
