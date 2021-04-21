var DB_NAME = "precise-indexed-DB"
var DB_VERSION = 1;

var openDatabase = function() {
  return new Promise(function(resolve, reject) {
    // Make sure IndexedDB is supported before attempting to use it
    if (!self.indexedDB) {
      reject("IndexedDB not supported");
    }
    var request = self.indexedDB.open(DB_NAME, DB_VERSION);
    request.onerror = function(event) {
      reject("Database error: " + event.target.error);
    };

    request.onupgradeneeded = function(event) {
      var db = event.target.result;
      var upgradeTransaction = event.target.transaction;
      var reservationsStore;
      if (!db.objectStoreNames.contains("queue")) {
        reservationsStore = db.createObjectStore("queue",
          { autoIncrement: true }
        );
      } else {
        reservationsStore = upgradeTransaction.objectStore("queue");
      }

      if (!reservationsStore.indexNames.contains("idx_status")) {
        reservationsStore.createIndex("idx_status", "status", { unique: false });
      }
    };

    request.onsuccess = function(event) {
      resolve(event.target.result);
    };
  });
};

var openObjectStore = function(db, storeName, transactionMode) {
  return db
    .transaction(storeName, transactionMode)
    .objectStore(storeName);
};

var addToObjectStore = function(storeName, object) {
  return new Promise(function(resolve, reject) {
    openDatabase().then(function(db) {
      openObjectStore(db, storeName, "readwrite")
        .add(object).onsuccess = resolve;
    }).catch(function(errorMessage) {
      reject(errorMessage);
    });
  });
};

var updateInObjectStore = function(storeName, id, object) {
  return new Promise(function(resolve, reject) {
    openDatabase().then(function(db) {
      openObjectStore(db, storeName, "readwrite")
        .openCursor().onsuccess = function(event) {
          var cursor = event.target.result;
          if (!cursor) {
            reject("Queue not found in object store");
          }
//          console.log(`Primary key = ${cursor.primaryKey}, id = ${id}`);
          if (cursor.primaryKey == id) {
//            console.log("Found the object!");
            cursor.update(object).onsuccess = resolve;
            return;
          }
          cursor.continue();
        };
    }).catch(function(errorMessage) {
      reject(errorMessage);
    });
  });
};

var getQueue = function(indexName, indexValue) {
  return new Promise(function(resolve) {
    openDatabase().then(function(db) {
      var objectStore = openObjectStore(db, "queue");
      var reservations = [];
      var cursor;
      if (indexName && indexValue) {
        cursor = objectStore.index(indexName).openCursor(indexValue);
      } else {
        cursor = objectStore.openCursor();
      }
      cursor.onsuccess = function(event) {
        var cursor = event.target.result;
        if (cursor) {
          var name_object = cursor.value;
          name_object['id'] = cursor.primaryKey;
          reservations.push(name_object);
          cursor.continue();
        } else {
          if (reservations.length > 0) {
            resolve(reservations);
          } else {
            getQueueFromServer().then(function(reservations) {
              openDatabase().then(function(db) {
                var objectStore = openObjectStore(db, "queue", "readwrite");
                for (var i = 0; i < reservations.length; i++) {
                  objectStore.add(reservations[i]);
                }
                resolve(reservations);
              });
            });
          }
        }
      };
    }).catch(function() {
      getQueueFromServer.then(function(reservations) {
        resolve(reservations);
      });
    });
  });
};

var getQueueFromServer = function() {
  return new Promise(function(resolve) {
    if (self.$) {
      $.getJSON("/reservations.json", resolve);
    } else if (self.fetch) {
      fetch("/reservations.json").then(function(response) {
        return response.json();
      }).then(function(reservations) {
        resolve(reservations);
      });
    }
  });
};


var createNameUrl = function(nameDetails) {
    var nameUrl = new URL("http://localhost:5000/api/add");
    Object.keys(nameDetails).forEach(function(key) {
        nameUrl.searchParams.append(key, nameDetails[key]);
    });
    return nameUrl;
};

var syncNames = function() {
    return getQueue("idx_status", "Pending").then(function(names) {
        return Promise.all(
            names.map(function(name) {
                var nameUrl = createNameUrl(name);
                console.log(nameUrl);
                return fetch(nameUrl).then(function(response) {
                    return response.json();
                }).then(function(newName) {
                    var id = newName['id'];
                    delete newName['id'];
                    return updateInObjectStore(
                        "queue",
                        id,
                        newName
                    );
                });
            })
        );
    });
};