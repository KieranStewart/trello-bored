import * as vscode from 'vscode';
import * as https from 'https';
import * as http from 'http';
import * as fs from 'fs';
import * as path from 'path';

export class SidebarProvider implements vscode.WebviewViewProvider {
    private _view?: vscode.WebviewView;
    private _pollingInterval?: NodeJS.Timeout;

    constructor(private readonly _extensionUri: vscode.Uri) {}

    resolveWebviewView(webviewView: vscode.WebviewView) {
        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };

        webviewView.webview.html = this._getHtmlContent();

        webviewView.webview.onDidReceiveMessage(async message => {
            switch (message.command) {
                case 'fetchChanges':
                    await this._fetchAndDisplayChanges();
                    break;
                case 'saveSettings':
                    await this._saveSettings(message.serverUrl, message.username, message.sessionId);
                    break;
                case 'loadSettings':
                    this._loadSettings();
                    break;
                case 'loadView':
                    this._loadViewContent(message.view, message.data);
                    break;
                case 'startPolling':
                    this._startPolling(message.interval);
                    break;
                case 'stopPolling':
                    this._stopPolling();
                    break;
                case 'acceptChange':
                    await this._handleChange(message.changeId, true);
                    break;
                case 'declineChange':
                    await this._handleChange(message.changeId, false);
                    break;
                case 'createSession':
                    await this._createSession();
                    break;
                case 'confirmChange':
                    await this._confirmChange(message.taskId, message.confirm);
                    break;
                case 'fetchTodoTasks':
                    await this._fetchTodoTasks();
                    break;

            }
        });

        webviewView.onDidDispose(() => this._stopPolling());
    }

    private async _fetchTodoTasks() {
    try {
        const config = vscode.workspace.getConfiguration('trelloboredextension');
        const serverUrl = config.get<string>('serverUrl', 'http://localhost:8080');
        const data = await this._httpGetWithHeaders(`${serverUrl}/tasks`, {});
        const parsed = JSON.parse(data);

        this._view?.webview.postMessage({
            command: 'updateTodoTasks',
            data: parsed
        });
    } catch (error) {
        this._view?.webview.postMessage({
            command: 'error',
            message: String(error)
        });
    }
}

    private async _saveSettings(serverUrl: string, username: string, sessionId: string) {
        const config = vscode.workspace.getConfiguration('trelloboredextension');
        await config.update('serverUrl', serverUrl, vscode.ConfigurationTarget.Global);
        await config.update('username', username, vscode.ConfigurationTarget.Global);
        await config.update('sessionId', sessionId, vscode.ConfigurationTarget.Global);
        vscode.window.showInformationMessage('Settings saved!');
    }

    private _loadSettings() {
        const config = vscode.workspace.getConfiguration('trelloboredextension');
        const serverUrl = config.get<string>('serverUrl', 'http://localhost:8080');
        const username = config.get<string>('username', '');
        const sessionId = config.get<string>('sessionId', '');
        this._view?.webview.postMessage({ command: 'settingsLoaded', serverUrl, username, sessionId });
    }

    private async _createSession() {
        try {
            const config = vscode.workspace.getConfiguration('trelloboredextension');
            const serverUrl = config.get<string>('serverUrl', 'http://localhost:8080');
            const sessionId = config.get<string>('sessionId', '');
            
            const response = await this._httpPostWithHeaders(`${serverUrl}/init`, { 'session-id': sessionId });
            const newSessionId = response.headers['session-id'];
            
            if (newSessionId) {
                await config.update('sessionId', newSessionId, vscode.ConfigurationTarget.Global);
                this._view?.webview.postMessage({ command: 'settingsLoaded', serverUrl, username: config.get<string>('username', ''), sessionId: newSessionId });
                vscode.window.showInformationMessage(`Session created: ${newSessionId}`);
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to create session: ${error}`);
        }
    }

    private _loadViewContent(view: string, data?: any) {
        const htmlPath = path.join(this._extensionUri.fsPath, 'src', 'views', `${view}.html`);
        let html = fs.readFileSync(htmlPath, 'utf8');

        const approveCssUri = this._view?.webview.asWebviewUri(
            vscode.Uri.joinPath(this._extensionUri, 'src', 'style', 'approve.css')
        ).toString() ?? '';
        const historicalCssUri = this._view?.webview.asWebviewUri(
            vscode.Uri.joinPath(this._extensionUri, 'src', 'style', 'historical.css')
        ).toString() ?? '';
        const todoCssUri = this._view?.webview.asWebviewUri(
            vscode.Uri.joinPath(this._extensionUri, 'src', 'style', 'todo.css')
        ).toString() ?? '';
        const approveJsUri = this._view?.webview.asWebviewUri(
            vscode.Uri.joinPath(this._extensionUri, 'src', 'script', 'approve.js')
        ).toString() ?? '';
        const historicalJsUri = this._view?.webview.asWebviewUri(
            vscode.Uri.joinPath(this._extensionUri, 'src', 'script', 'historical.js')
        ).toString() ?? '';
        const todoJsUri = this._view?.webview.asWebviewUri(
            vscode.Uri.joinPath(this._extensionUri, 'src', 'script', 'todo.js')
        ).toString() ?? '';

        html = html
            .replace(/\.\.\/style\/approve\.css/g, approveCssUri)
            .replace(/\.\.\/style\/historical\.css/g, historicalCssUri)
            .replace(/\.\.\/style\/todo\.css/g, todoCssUri)
            .replace(/\.\.\/script\/approve\.js/g, approveJsUri)
            .replace(/\.\.\/script\/historical\.js/g, historicalJsUri)
            .replace(/\.\.\/script\/todo\.js/g, todoJsUri);
        
        if (view === 'approve' && data) {
            html = html.replace('{{CONTENT}}', this._renderApproveItems(data));
        } else if (view === 'historical' && data) {
            html = html.replace('{{CONTENT}}', this._renderHistoricalItems(data));
        } else if (view === 'approve' || view === 'historical') {
            html = html.replace('{{CONTENT}}', '<p>No data available</p>');
        } else if (view === 'todo' && data) {
            html = html.replace('{{CONTENT}}', this._renderTodoItems(data));
        } else if (view === 'todo') {
            html = html.replace('{{CONTENT}}', '<p>No to-do items.</p>');
        }
        
        this._view?.webview.postMessage({ command: 'renderView', html });
    }

    private _renderApproveItems(data: any[]): string {
        if (!data || data.length === 0) {
            return '<p>No pending requests</p>';
        }
        
        return data.map(change => 
            `<div class="change-item">
                <strong>${change.type || 'Update'}</strong>: ${change.description || ''}
                <br><small>${change.timestamp || ''}</small>
                <div class="change-actions">
                    <button class="accept-btn" onclick="acceptChange('${change.task_id || change.id}')">Accept</button>
                    <button class="decline-btn" onclick="declineChange('${change.task_id || change.id}')">Decline</button>
                </div>
            </div>`
        ).join('');
    }

    private _renderHistoricalItems(data: any[]): string {
        if (!data || data.length === 0) {
            return '<p>No historical data</p>';
        }
        
        return data.map(change => 
            `<div class="change-item">
                <strong>${change.type || 'Update'}</strong>: ${change.description || ''}
                <br><small>${change.timestamp || ''}</small>
            </div>`
        ).join('');
    }

    private _renderTodoItems(data: any[]): string {
        if (!data || data.length === 0) {
            return '<p>No tasks available</p>';
        }
        return data.map(task =>
            `<div class="change-item">
            <strong>Task #${task.number ?? "?"}</strong>: ${task.title || "Untitled"}
            <br><small>${task.state || ""}</small>
            </div>`).join('');
    }   

    private _startPolling(interval: number = 5000) {
        this._stopPolling();
        this._pollingInterval = setInterval(() => this._fetchAndDisplayChanges(), interval);
    }

    private _stopPolling() {
        if (this._pollingInterval) {
            clearInterval(this._pollingInterval);
            this._pollingInterval = undefined;
        }
    }

    private async _fetchAndDisplayChanges() {
        try {
            const config = vscode.workspace.getConfiguration('trelloboredextension');
            const serverUrl = config.get<string>('serverUrl', 'http://localhost:8080');
            const sessionId = config.get<string>('sessionId', '');
            
            const data = await this._httpGetWithHeaders(`${serverUrl}/confirm`, { 'session-id': sessionId });
            this._view?.webview.postMessage({ command: 'updateChanges', data: JSON.parse(data) });
        } catch (error) {
            this._view?.webview.postMessage({ command: 'error', message: String(error) });
        }
    }

    private async _handleChange(changeId: string, accepted: boolean) {
        try {
            const config = vscode.workspace.getConfiguration('trelloboredextension');
            const serverUrl = config.get<string>('serverUrl', 'http://localhost:8080');
            const apiUrl = `${serverUrl}/api/changes/${changeId}/${accepted ? 'accept' : 'decline'}`;
            await this._httpPost(apiUrl);
            vscode.window.showInformationMessage(`Change ${accepted ? 'accepted' : 'declined'}`);
            await this._fetchAndDisplayChanges();
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to ${accepted ? 'accept' : 'decline'} change: ${error}`);
        }
    }

    private async _confirmChange(taskId: string, confirm: boolean) {
        try {
            const config = vscode.workspace.getConfiguration('trelloboredextension');
            const serverUrl = config.get<string>('serverUrl', 'http://localhost:8080');
            const sessionId = config.get<string>('sessionId', '');
            
            await this._httpPostJson(`${serverUrl}/confirm`, { task_id: taskId, confirm }, { 'session-id': sessionId });
            vscode.window.showInformationMessage(`Change ${confirm ? 'approved' : 'rejected'}`);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to ${confirm ? 'approve' : 'reject'} change: ${error}`);
        }
    }

    private _httpGetWithHeaders(url: string, headers: Record<string, string>): Promise<string> {
        return new Promise((resolve, reject) => {
            const urlObj = new URL(url);
            const client = url.startsWith('https') ? https : http;
            const options = {
                hostname: urlObj.hostname,
                port: urlObj.port,
                path: urlObj.pathname + urlObj.search,
                method: 'GET',
                headers
            };
            
            client.get(options, (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => resolve(data));
            }).on('error', reject);
        });
    }

    private _httpPostWithHeaders(url: string, headers: Record<string, string>): Promise<{headers: Record<string, string>}> {
        return new Promise((resolve, reject) => {
            const urlObj = new URL(url);
            const client = url.startsWith('https') ? https : http;
            const req = client.request({
                hostname: urlObj.hostname,
                port: urlObj.port,
                path: urlObj.pathname,
                method: 'POST',
                headers
            }, (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => resolve({ headers: res.headers as Record<string, string> }));
            });
            req.on('error', reject);
            req.end();
        });
    }

    private _httpPostJson(url: string, body: any, headers: Record<string, string> = {}): Promise<void> {
        return new Promise((resolve, reject) => {
            const urlObj = new URL(url);
            const client = url.startsWith('https') ? https : http;
            const data = JSON.stringify(body);
            const req = client.request({
                hostname: urlObj.hostname,
                port: urlObj.port,
                path: urlObj.pathname,
                method: 'POST',
                headers: { ...headers, 'Content-Type': 'application/json', 'Content-Length': data.length }
            }, (res) => {
                res.on('end', () => resolve());
            });
            req.on('error', reject);
            req.write(data);
            req.end();
        });
    }

    private _httpPost(url: string): Promise<void> {
        return new Promise((resolve, reject) => {
            const urlObj = new URL(url);
            const client = url.startsWith('https') ? https : http;
            const req = client.request({
                hostname: urlObj.hostname,
                port: urlObj.port,
                path: urlObj.pathname,
                method: 'POST'
            }, (res) => {
                res.on('end', () => resolve());
            });
            req.on('error', reject);
            req.end();
        });
    }

    private _getHtmlContent() {
    const htmlPath = path.join(this._extensionUri.fsPath, 'src', 'sidebar.html');

    const sidebarCssUri = this._view?.webview.asWebviewUri(
        vscode.Uri.joinPath(this._extensionUri, 'src', 'style', 'sidebar.css')
        ).toString() ?? '';

    const sidebarJsUri = this._view?.webview.asWebviewUri(
        vscode.Uri.joinPath(this._extensionUri, 'src', 'script', 'sidebar.js')
        ).toString() ?? '';

    const html = fs.readFileSync(htmlPath, 'utf8');
    return html
        .replace('./style/sidebar.css', sidebarCssUri)
        .replace('./script/sidebar.js', sidebarJsUri);
    }
}
