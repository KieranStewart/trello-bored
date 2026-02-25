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
                    await this._saveSettings(message.serverUrl, message.boardUrl);
                    break;
                case 'loadSettings':
                    this._loadSettings();
                    break;
                case 'loadView':
                    this._loadViewContent(message.view);
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
            }
        });

        webviewView.onDidDispose(() => this._stopPolling());
    }

    private async _saveSettings(serverUrl: string, boardUrl: string) {
        const config = vscode.workspace.getConfiguration('trelloboredextension');
        await config.update('serverUrl', serverUrl, vscode.ConfigurationTarget.Global);
        await config.update('boardUrl', boardUrl, vscode.ConfigurationTarget.Global);
        vscode.window.showInformationMessage('Settings saved!');
    }

    private _loadSettings() {
        const config = vscode.workspace.getConfiguration('trelloboredextension');
        const serverUrl = config.get<string>('serverUrl', 'http://localhost:3000');
        const boardUrl = config.get<string>('boardUrl', '');
        this._view?.webview.postMessage({ command: 'settingsLoaded', serverUrl, boardUrl });
    }

    private _loadViewContent(view: string) {
        const htmlPath = path.join(this._extensionUri.fsPath, 'src', 'views', `${view}.html`);
        const html = fs.readFileSync(htmlPath, 'utf8');
        this._view?.webview.postMessage({ command: 'renderView', html });
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
            const serverUrl = config.get<string>('serverUrl', 'http://localhost:3000');
            const boardUrl = config.get<string>('boardUrl', '');
            const apiUrl = `${serverUrl}/api/changes${boardUrl ? '?board=' + boardUrl : ''}`;
            const data = await this._httpGet(apiUrl);
            this._view?.webview.postMessage({ command: 'updateChanges', data: JSON.parse(data) });
        } catch (error) {
            this._view?.webview.postMessage({ command: 'error', message: String(error) });
        }
    }

    private async _handleChange(changeId: string, accepted: boolean) {
        try {
            const config = vscode.workspace.getConfiguration('trelloboredextension');
            const serverUrl = config.get<string>('serverUrl', 'http://localhost:3000');
            const apiUrl = `${serverUrl}/api/changes/${changeId}/${accepted ? 'accept' : 'decline'}`;
            await this._httpPost(apiUrl);
            vscode.window.showInformationMessage(`Change ${accepted ? 'accepted' : 'declined'}`);
            await this._fetchAndDisplayChanges();
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to ${accepted ? 'accept' : 'decline'} change: ${error}`);
        }
    }

    private _httpGet(url: string): Promise<string> {
        return new Promise((resolve, reject) => {
            const client = url.startsWith('https') ? https : http;
            client.get(url, (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => resolve(data));
            }).on('error', reject);
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
        return fs.readFileSync(htmlPath, 'utf8');
    }
}
