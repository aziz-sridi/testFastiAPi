from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Container App UI</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h2 { margin-top: 2em; }
            table, th, td { border: 1px solid #ccc; border-collapse: collapse; padding: 6px; }
            input, button { margin: 4px; }
        </style>
    </head>
    <body>
        <h1>Container App UI</h1>
        <h2>Users</h2>
        <div>
            <input id="name" placeholder="Name">
            <input id="email" placeholder="Email">
            <button onclick="addUser()">Add User</button>
        </div>
        <table id="usersTable">
            <thead>
                <tr><th>ID</th><th>Name</th><th>Email</th><th>Actions</th></tr>
            </thead>
            <tbody></tbody>
        </table>
        <h2>Upload JSON for Prediction</h2>
        <input type="file" id="jsonFile">
        <button onclick="uploadJson()">Upload & Predict</button>
        <div id="predictionResult"></div>
        <script>
            const api = location.origin;

            function fetchUsers() {
                fetch(api + "/users/")
                    .then(r => r.json())
                    .then(users => {
                        const tbody = document.querySelector("#usersTable tbody");
                        tbody.innerHTML = "";
                        users.forEach(u => {
                            tbody.innerHTML += `<tr>
                                <td>${u.id}</td>
                                <td><input value="${u.name}" id="name${u.id}"></td>
                                <td><input value="${u.email}" id="email${u.id}"></td>
                                <td>
                                    <button onclick="updateUser(${u.id})">Update</button>
                                    <button onclick="deleteUser(${u.id})">Delete</button>
                                </td>
                            </tr>`;
                        });
                    });
            }
            function addUser() {
                const name = document.getElementById("name").value;
                const email = document.getElementById("email").value;
                fetch(api + "/users", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ name, email })
                })
                .then(() => { fetchUsers(); });
            }
            function updateUser(id) {
                const name = document.getElementById("name" + id).value;
                const email = document.getElementById("email" + id).value;
                fetch(api + `/users/${id}?name=${encodeURIComponent(name)}&email=${encodeURIComponent(email)}`, {
                    method: "PUT"
                }).then(() => { fetchUsers(); });
            }
            function deleteUser(id) {
                fetch(api + `/users/${id}`, { method: "DELETE" })
                .then(() => { fetchUsers(); });
            }
            function uploadJson() {
                const fileInput = document.getElementById("jsonFile");
                if (!fileInput.files.length) return;
                const formData = new FormData();
                formData.append("file", fileInput.files[0]);
                fetch(api + "/read_json/", {
                    method: "POST",
                    body: formData
                })
                .then(r => r.json())
                .then(res => {
                    document.getElementById("predictionResult").innerText = 
                        "Prediction: " + (res.next_point_prediction ?? res.detail);
                });
            }
            fetchUsers();
        </script>
    </body>
    </html>
    """
