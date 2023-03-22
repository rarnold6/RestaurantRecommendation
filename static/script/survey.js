function dateBorderCheck(id){
    var inputDate = document.getElementById(id);
    var datetime = inputDate.value;
    var datetimeString = datetime + ":00";
    var mindatetime = inputDate.min;
    var mindatetimeString = mindatetime + ":00";
    var maxdatetime = inputDate.max;
    var maxdatetimeString = maxdatetime + ":00";

    var dvalue = Date.parse(datetimeString);
    var dmin = Date.parse(mindatetimeString);
    var dmax = Date.parse(maxdatetimeString);

    var type = id.substring(0,id.length-1);
    
    var number = id.slice(-1);
    
    
    
    if(dvalue > dmax || dvalue < dmin){
        if(type === 'startTime'){
            inputDate.value = mindatetime;
        } else {
            inputDate.value = maxdatetime;
        }
        
    } else {
        
        if(type === 'startTime'){
            var endTime = document.getElementById('endTime'+number);
            endTime.min = datetime;
            
        } else {
            var startTime = document.getElementById('startTime'+number);
            startTime.max = datetime;
            
        }
    }
};

function dateConfirm(id){
    var checkBox = document.getElementById(id);
    var number = id.slice(-1);
    var startDate = document.getElementById('startTime'+number);
    var endDate = document.getElementById('endTime'+number);

    
    if(checkBox.checked){
        var otherCheckBox = document.getElementById('checkboxDelete'+number);
        otherCheckBox.checked = false;
        startDate.disabled = false;
        endDate.disabled = false;
        startDate.value = startDate.min;
        startDate.readOnly = true;
        endDate.value = endDate.max;
        endDate.readOnly = true;
    } else {
        startDate.readOnly = false;
        endDate.readOnly = false;
    }
    
}

function dateDelete(id){
    var checkBox = document.getElementById(id);
    
    var number = id.slice(-1);

    var startDate = document.getElementById('startTime'+number);
    var endDate = document.getElementById('endTime'+number);

    if(checkBox.checked){
        var otherCheckBox = document.getElementById('checkboxConfirm'+number);
        otherCheckBox.checked = false;
        startDate.readOnly = false;
        endDate.readOnly = false;
        startDate.disabled = true;
        endDate.disabled = true;
    } else {
        startDate.disabled = false;
        endDate.disabled = false;
    }
}

function locationCheck(){
    var checkBox = document.getElementById("checkboxGeoLocation");
    var addressDiv = document.getElementById("addressDiv");
    if(checkBox.checked){
        addressDiv.hidden = true;
        getLocation();
    } else {
        addressDiv.hidden = false;
    }
}

function getLocation() {
    var x = document.getElementById("x");
    var addressDiv = document.getElementById("addressDiv");
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(showPosition);

    } else { 
      x.innerHTML = "Geolocation is not supported by this browser.";
      addressDiv.hidden = false;
    }
  }

  function showPosition(position) {
    x.innerHTML = "Latitude: " + position.coords.latitude + 
    "<br>Longitude: " + position.coords.longitude;
  }

  function selectCategories(){
    const dropDown = document.getElementById("foodCategory");
    if(dropDown.value != "Select"){
        const div = document.getElementById("placeholderSelectedValues");

        const innerDiv = createInnerChild(dropDown.value);

        div.appendChild(innerDiv);
        dropDown.remove(dropDown.selectedIndex);
    }
  }

  function createInnerChild(category){
    const categoryDiv = document.createElement("div");
    categoryDiv.setAttribute("id","div" + category);
    const label = document.createElement("label");
    label.innerHTML = category;
    const button = document.createElement("button");
    button.setAttribute("type","button");
    button.setAttribute("onclick","takeBackSelection('" + categoryDiv.id + "');")
    button.innerHTML = "<i class='fa fa-trash'></i>";
    
    categoryDiv.appendChild(label);
    categoryDiv.appendChild(button);
    return categoryDiv;
  }

  function takeBackSelection(divid){
    console.log(divid);
    const categoryDiv = document.getElementById(divid);
    const div = document.getElementById("placeholderSelectedValues");

    console.log(categoryDiv);

    div.removeChild(categoryDiv);

    const dropDown = document.getElementById("foodCategory");

    const category = document.createElement("option");
    category.value = divid.substring(3);
    category.text = divid.substring(3);

    dropDown.add(category);
  }