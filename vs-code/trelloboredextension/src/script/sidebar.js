const vscode = acquireVsCodeApi();
        let currentView = 'approve';
        let currentData = null;
        
        vscode.postMessage({ command: 'loadSettings' });
        
        function saveSettings() {
            const serverUrl = document.getElementById('serverUrl').value;
            const username = document.getElementById('username').value;
            const sessionId = document.getElementById('sessionId').value;
            const userId = document.getElementById('userId').value;
            vscode.postMessage({ command: 'saveSettings', serverUrl, username, sessionId, userId });
        }

        function createSession() {
            vscode.postMessage({ command: 'createSession' });
        }
        
        function showView(view) {
            currentView = view;
            document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');

            if (view === 'approve') {
                fetchChanges();
            } else if (view === 'historical') {
                document.getElementById('content').innerHTML = '<p class="loading">Loading...</p>';
                vscode.postMessage({ command: 'fetchHistoricalTasks' });
            } else if (view === 'todo') {
                document.getElementById('content').innerHTML = '<p class="loading">Loading...</p>';
                vscode.postMessage({ command: 'fetchTodoTasks' });
            } else {
                vscode.postMessage({ command: 'loadView', view });
            }
        }
        
        function fetchChanges() {
            document.getElementById('content').innerHTML = '<p class="loading">Loading...</p>';
            vscode.postMessage({ command: 'fetchChanges' });
        }

        let approveChanges = [];
        let selectedIndex = null;

        function renderApproveView(data) {
            approveChanges = data || [];
            const content = document.getElementById('content');
            if (!approveChanges.length) {
                content.innerHTML = '<p>No pending requests</p>';
                return;
            }
            let html = '<div id="changeTypeHeader" class="change-type-header">Select a Ticket</div>';
            html += '<div id="ticketList">';
            approveChanges.forEach((change, index) => {
                html += `<div class="ticket" onclick="selectApproveChange(${index})">${change.type}: ${change.description}</div>`;
            });
            html += '</div>';
            html += '<div id="details" style="display:none"><div id="approveDescription"></div>';
            html += '<div class="actions"><button class="action-btn" onclick="approveChange()">✔</button><button class="action-btn" onclick="rejectChange()">✖</button></div></div>';
            content.innerHTML = html;
            selectedIndex = null;
        }

        function selectApproveChange(index) {
            selectedIndex = index;
            document.querySelectorAll('.ticket').forEach(t => t.classList.remove('selected'));
            document.querySelectorAll('.ticket')[index].classList.add('selected');
            document.getElementById('approveDescription').textContent = approveChanges[index].description;
            document.getElementById('details').style.display = 'block';
        }

        function approveChange() {
            if (selectedIndex === null) { return; }
            const change = approveChanges[selectedIndex];
            vscode.postMessage({ command: 'confirmChange', taskId: change.task_id, confirm: true });
            approveChanges.splice(selectedIndex, 1);
            selectedIndex = null;
            renderApproveView(approveChanges);
        }

        function rejectChange() {
            if (selectedIndex === null) { return; }
            const change = approveChanges[selectedIndex];
            vscode.postMessage({ command: 'confirmChange', taskId: change.task_id, confirm: false });
            approveChanges.splice(selectedIndex, 1);
            selectedIndex = null;
            renderApproveView(approveChanges);
        }

        function acceptChange(changeId) {
            vscode.postMessage({ command: 'acceptChange', changeId });
        }

        function declineChange(changeId) {
            vscode.postMessage({ command: 'declineChange', changeId });
        }
        
        window.addEventListener('message', event => {
            const message = event.data;
            
            switch (message.command) {
                case 'settingsLoaded':
                    document.getElementById('serverUrl').value = message.serverUrl;
                    document.getElementById('username').value = message.username;
                    document.getElementById('sessionId').value = message.sessionId;
                    document.getElementById('userId').value = message.userId || '';
                    break;
                case 'renderView':
                    document.getElementById('content').innerHTML = message.html;
                    break;
                case 'updateChanges':
                    currentData = message.data;
                    if (currentView === 'approve') {
                        renderApproveView(currentData);
                    } else {
                        vscode.postMessage({ command: 'loadView', view: currentView, data: currentData });
                    }
                    break;
                case 'updateTodoTasks':
                    currentData = Array.isArray(message.data) ? message.data : (message.data?.tasks || []);
                    vscode.postMessage({ command: 'loadView', view: currentView, data: currentData });
                    break;
                case 'updateHistoricalTasks':
                    currentData = Array.isArray(message.data) ? message.data : (message.data?.tasks || []);
                    vscode.postMessage({ command: 'loadView', view: currentView, data: currentData });
                    break;
                case 'error':
                    document.getElementById('content').innerHTML = '<p class="error">Error: ' + message.message + '</p>';
                    break;
            }
        });
        
        showView('approve');
        vscode.postMessage({ command: 'startPolling', interval: 5000 });