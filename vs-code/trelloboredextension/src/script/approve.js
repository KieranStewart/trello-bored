const vscode = acquireVsCodeApi();

      let changes = [];
      let selectedIndex = null;

      vscode.postMessage({ command: "loadSettings" });

      function saveSettings() {
        const serverUrl = document.getElementById("serverUrl").value;
        const boardUrl = document.getElementById("boardUrl").value;
        vscode.postMessage({ command: "saveSettings", serverUrl, boardUrl });
      }

      function fetchChanges() {
        document.getElementById("ticketList").innerHTML =
          '<p class="loading">Loading...</p>';
        document.getElementById("details").style.display = "none";
        document.getElementById("changeTypeHeader").textContent = "Loading...";
        vscode.postMessage({ command: "fetchChanges" });
      }

      window.addEventListener("message", (event) => {
        const message = event.data;
        const content = document.getElementById("content");

        switch (message.command) {
          case "settingsLoaded":
            document.getElementById("serverUrl").value = message.serverUrl;
            document.getElementById("boardUrl").value = message.boardUrl;
            break;

          case "updateChanges":
            changes = message.data || [];
            renderTickets();
            break;

          case "error":
            content.innerHTML =
              '<p class="error">Error: ' + message.message + "</p>";
            break;
        }
      });

      function renderTickets() {
        const list = document.getElementById("ticketList");
        list.innerHTML = "";
        document.getElementById("changeTypeHeader").textContent =
          "Select a Ticket";

        if (!changes.length) {
          list.innerHTML = "<p>No tickets with new changes found</p>";
          return;
        }

        changes.forEach((change, index) => {
          const div = document.createElement("div");
          div.className = "ticket";
          div.textContent = change.name;
          div.onclick = () => selectChange(index, div);
          list.appendChild(div);
        });
      }

      function selectChange(index, element) {
        selectedIndex = index;
        const selectedChange = changes[index];

        document
          .querySelectorAll(".ticket.selected")
          .forEach((c) => c.classList.remove("selected"));
        element.classList.add("selected");

        document.getElementById("changeTypeHeader").textContent = selectedChange.type; // will be whichever api route is being called (depends on where the ticket will be moved)
        document.getElementById("description").textContent = selectedChange.description; // will describe where the ticket is being moved to and maybe other descriptors
        document.getElementById("details").style.display = "block";
      }

      function removeSelectedCard() {
        if (selectedIndex === null) {
            return;
        }

        changes.splice(selectedIndex, 1);
        selectedIndex = null;

        document.getElementById("details").style.display = "none";
        renderTickets();
      }

      async function approveChange() {
        if (selectedIndex === null) {return;}
        const change = changes[selectedIndex];
        vscode.postMessage({ command: "confirmChange", taskId: change.task_id || change.id, confirm: true });
        removeSelectedCard();
      }

      function rejectChange() {
        if (selectedIndex === null) {return;}
        const change = changes[selectedIndex];
        vscode.postMessage({ command: "confirmChange", taskId: change.task_id || change.id, confirm: false });
        removeSelectedCard();
      }

      fetchChanges();