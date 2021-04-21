
// this has to go first so that there is a data-bind for knockout to put values into.
const template = `

                      <p style="float:left">Filter to submit:&nbsp; <p data-bind="text: fullName">!</p></p>
                      <form action="" method="POST" id="form-first" data-bind="submit: buildQuery">
                          <p>Patient Number: <br/><input class="myform" name="patientNum" data-bind="value: patientNum" style='width:100%'/></p>
                          <p>Filter Number: <br/><input class="myform" name="filterNum" data-bind="value: filterNum" style='width:100%'/></p>
                          <p>Date Received: <br/><input class="myform" type=date name="dateRec" data-bind="value: dateRec" style='width:100%'/></p>
                          <p>mL of Blood Received: <br/><input class="myform" type="number" step="0.25" min="1.00" max="10.00" name="mL" data-bind="value: mL" style='width:100%'/></p>
                          <p>Initials of Sender: <br/><input class="myform" name="initials" data-bind="value: initials" style='width:100%'/></p>
                          <p>Sending Institute: <br/><select class="myform" name="institutes" data-bind="options: institutes, selectedOptions: chosenInstitute" style='width:100%'>
                          </select></p>
                          </br>
                          <button type="submit">Submit</button>
                      </form>

                  `;

document.getElementById("form-content").innerHTML = template;

//Here's my data model
var ViewModel = function(pNum, fNum) {
    this.patientNum = ko.observable(pNum);
    this.filterNum = ko.observable(fNum);
    this.fullName = ko.pureComputed(function() {
        // Knockout tracks dependencies automatically. It knows that fullName depends on firstName and lastName, because these get called when evaluating fullName.
        return this.patientNum() + " " + this.filterNum();
    }, this);
    this.dateRec = ko.observable(moment().format('YYYY-MM-DD'));
    this.mL = ko.observable(9.00);
    this.initials = ko.observable("???");
    this.institutes = ko.observableArray(institutes);
    this.chosenInstitute = ko.observable([institutes[0]]);
    this.buildQuery = function() {
        var query = {
                    "patientNum":this.patientNum(),
                    "filterNum":this.filterNum(),
                    "dateRec": this.dateRec(),
                    "mL": this.mL(),
                    "initials": this.initials(),
                    "institutes": this.chosenInstitute()[0],
                    "status":"Pending"};
        var request = window.indexedDB.open("precise-indexed-DB", 1);
        request.onerror = function(event) {
            console.log("Database error: ", event.target.error);
        }
        request.onsuccess = function(event) {
            var db = event.target.result;
            // in additions-store.js

            addToObjectStore("queue", query);
            if ("serviceWorker" in navigator && "SyncManager" in window) {
                    navigator.serviceWorker.ready.then(function(registration) {
                        console.log("Registering names-sync!");
                        registration.sync.register("namesSync").catch(function(err) {
                            console.log(err);
                        });
                    });
            } else {
                var nameUrl = createNameUrl(query);
                console.log("Falling back to jquery")
                $.get(
                nameUrl,
                function(data) {
                    // todo call getQueueFromServer when that function is updated.
                    alert(data['firstname']);
                })

            };
        };
    }

};

ko.applyBindings(new ViewModel("P0100", "18AA0000"));