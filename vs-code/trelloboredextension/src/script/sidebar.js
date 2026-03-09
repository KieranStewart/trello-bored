const vscode = acquireVsCodeApi();
        let currentView = 'approve';
        let currentData = null;
        
        vscode.postMessage({ command: 'loadSettings' });
        
        function saveSettings() {
            const serverUrl = document.getElementById('serverUrl').value;
            const username = document.getElementById('username').value;
            const sessionId = document.getElementById('sessionId').value;
            vscode.postMessage({ command: 'saveSettings', serverUrl, username, sessionId });
        }

        function createSession() {
            vscode.postMessage({ command: 'createSession' });
        }
        
        function showView(view) {
            currentView = view;
            document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            if (view === 'approve' || view === 'historical') {
                fetchChanges();
            } else {
                vscode.postMessage({ command: 'loadView', view });
            }
        }
        
        function fetchChanges() {
            document.getElementById('content').innerHTML = '<p class="loading">Loading...</p>';
            vscode.postMessage({ command: 'fetchChanges' });
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
                    break;
                case 'renderView':
                    document.getElementById('content').innerHTML = message.html;
                    break;
                case 'updateChanges':
                    currentData = message.data;
                    vscode.postMessage({ command: 'loadView', view: currentView, data: currentData });
                    break;
                case 'error':
                    document.getElementById('content').innerHTML = '<p class="error">Error: ' + message.message + '</p>';
                    break;
            }
        });
        
        showView('approve');
        vscode.postMessage({ command: 'startPolling', interval: 5000 });