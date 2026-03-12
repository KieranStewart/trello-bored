const vscode = acquireVsCodeApi();

function fetchTodoTasks() {
  vscode.postMessage({ command: "fetchTodoTasks" });
}
console.log("Todo script loaded, fetching tasks...");

window.addEventListener("message", (event) => {
  const message = event.data;

  if (message.command === "updateTodoTasks") {
    const tasks = Array.isArray(message.data) ? message.data : (message.data?.tasks || []);
    const list = document.getElementById("todoList");

    if (!tasks.length) {
      list.innerHTML = "<p>No to-do items.</p>";
      return;
    }

    list.innerHTML = tasks.map(task =>
    `<div class="change-item">
        <strong>Task #${task.number ?? "?"}</strong>: ${task.title || "Untitled"}
        <br><small>${task.state || ""}</small>
    </div>`
    ).join("");
  }

  if (message.command === "error") {
    document.getElementById("todoList").innerHTML = `<p>Error: ${message.message}</p>`;
  }
});

fetchTodoTasks();