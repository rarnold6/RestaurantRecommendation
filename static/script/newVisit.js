function myFunction() {
    // Get the checkbox
    var checkBox = document.getElementById("checkboxDateDefined");
    var divDate = document.getElementById("divDateDefined");
    var divProposingDates = document.getElementById("divProDate");
    
    if (checkBox.checked == true){
        divDate.style.display = 'block';
        divProposingDates.style.display = 'none';
      } else {
        divDate.style.display = 'none';
        divProposingDates.style.display = 'block';
      }
}

var counter = 1
function addTimeslot (){
    //var div = document.getElementById("divProposedDate");
    if(counter > 10){
      alert("Maximum number of timeslots reached!")
      return null;
    }
    var parent = document.getElementById("divProposingDates");
    
    var oldinputFrom = document.getElementById("meeting-time-from"+counter);

    var now = oldinputFrom.getAttribute("value");
    var max = oldinputFrom.getAttribute("max");


    counter++;
    var div = document.createElement("div");
    div.setAttribute("id","divProposedDate"+counter);

    var labelFrom = document.createElement("label");
    labelFrom.innerHTML = 'From ';
    var inputFrom = document.createElement("input");
    inputFrom.setAttribute("type","datetime-local");
    inputFrom.setAttribute("id","meeting-time-from"+counter);
    inputFrom.setAttribute("name","meeting-time-from[]");
    inputFrom.setAttribute("value",now);
    inputFrom.setAttribute("min",now);
    inputFrom.setAttribute("max",max);
    inputFrom.setAttribute("onchange","dateChange("+counter+")");

    var labelUntil = document.createElement("label");
    labelUntil.innerHTML = ' until ';
    var inputUntil = document.createElement("input");
    inputUntil.setAttribute("value",now);
    inputUntil.setAttribute("min",now);
    inputUntil.setAttribute("max",max);
    inputUntil.setAttribute("type","datetime-local");
    inputUntil.setAttribute("name","meeting-time-until[]")
    inputUntil.setAttribute("id","meeting-time-until"+counter);

    var deleteButton = document.createElement("button");
    deleteButton.setAttribute("id","deleteButton"+counter);
    deleteButton.setAttribute("type","button");
    deleteButton.innerHTML = "Delete this timeslot";
    deleteButton.setAttribute("onclick","deleteTimeslot(" + counter + ")");


    var newLine = document.createElement("br");

    div.appendChild(labelFrom);
    div.appendChild(inputFrom);
    div.appendChild(labelUntil);
    div.appendChild(inputUntil);
    div.appendChild(deleteButton);
    div.appendChild(newLine);

    parent.appendChild(div);
  };

  function deleteTimeslot(index){
    var deletingDiv = document.getElementById("divProposedDate"+index);
    
    deletingDiv.remove();
    
    index++;
    while(index <= counter){
      
      var div = document.getElementById("divProposedDate"+index);
      div.setAttribute("id","divProposedDate"+(index-1));
      var inputFrom = document.getElementById("meeting-time-from"+index);
      inputFrom.setAttribute("id","meeting-time-from"+(index-1));
      inputFrom.setAttribute("onchange","dateChange("+(index-1)+")");
      var inputUntil = document.getElementById("meeting-time-until"+index);
      inputUntil.setAttribute("id","meeting-time-until"+(index-1));
      
      var deleteButto = document.getElementById("deleteButton"+index);
      deleteButto.setAttribute("onclick","deleteTimeslot(" + (index-1) + ")");
      deleteButto.setAttribute("id","deleteButton" + (index-1));
      index++;
    }
    counter--;


  };

function dateChange(index){
    var startDate = document.getElementById("meeting-time-from"+index);

    var endDate = document.getElementById("meeting-time-until"+index);

    var startingDate = startDate.value;

    endDate.value = startingDate;
    endDate.min = startingDate;
};
  