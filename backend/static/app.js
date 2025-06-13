async function loginToGitlab() {
  const url = document.getElementById("gitlab-url").value;
  const token = document.getElementById("gitlab-token").value;
  const statusMsg = document.getElementById("login-status");
  console.log("Logging in with URL:", url, "and Token:", token);

  const res = await fetch("/api/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, token }),
  });

  const result = await res.json();
  console.log("Login result:", result);

  if (result.status === "success") {
    statusMsg.textContent = "";
    document.getElementById("login-section").style.display = "none";
    document.getElementById("main-app").style.display = "block";
    console.log("Login successful, loading trainees...");
    loadTrainees();
  } else {
    statusMsg.textContent = result.message;
    console.log("Login failed:", result.message);
  }
}

const traineeSelect = document.getElementById("trainees");
const traineeDetailsDiv = document.getElementById("trainee-details");
const outputPre = document.getElementById("output");
let traineeData = {};

const choices = new Choices(traineeSelect, {
  removeItemButton: true,
  placeholderValue: "Select Trainees",
  searchPlaceholderValue: "Search...",
  itemSelectText: "",
});

async function loadTrainees() {
  console.log("Fetching trainees...");
  const res = await fetch("/api/trainees");
  const data = await res.json();
  traineeData = data;

  console.log("Trainees fetched:", data);

  const traineeOptions = Object.entries(data).map(([id, obj]) => ({
    value: id,
    label: obj.name,
  }));

  choices.setChoices(traineeOptions, "value", "label", true);
  console.log("Trainee options set in Choices");
}

traineeSelect.addEventListener("change", async function () {
  const selectedIds = Array.from(traineeSelect.selectedOptions).map(
    (opt) => opt.value
  );

  console.log("Selected trainee IDs:", selectedIds);

  const existingBlocks = Array.from(traineeDetailsDiv.children);
  existingBlocks.forEach((block) => {
    const pid = block.dataset.projectId;
    if (!selectedIds.includes(pid)) {
      console.log("Removing block for project:", pid);
      block.remove();
    }
  });

  for (const id of selectedIds) {
    if (document.querySelector(`[data-project-id="${id}"]`)) {
      console.log("Skipping already rendered project ID:", id);
      continue;
    }

    console.log("Fetching branches for project:", id);
    const branches = await fetch(`/api/branches/${id}`).then((res) =>
      res.json()
    );
    console.log("Branches received for project", id, ":", branches);

    const branchSelect = document.createElement("select");
    branchSelect.name = `branch-${id}`;
    branchSelect.dataset.projectId = id;
    branchSelect.innerHTML = `<option disabled selected>Select Branch</option>`;
    branches.forEach((branch) => {
      const opt = document.createElement("option");
      opt.value = branch;
      opt.textContent = branch;
      branchSelect.appendChild(opt);
    });

    const fileContainer = document.createElement("div");
    fileContainer.id = `files-${id}`;

    const container = document.createElement("div");
    container.dataset.projectId = id;
    container.innerHTML = `<h3>${traineeData[id].project_name}</h3>`;
    container.appendChild(branchSelect);
    container.appendChild(fileContainer);
    traineeDetailsDiv.appendChild(container);

    branchSelect.addEventListener("change", async function () {
      const branchName = this.value;
      const projectId = this.dataset.projectId;
      console.log(`Branch selected: ${branchName} for project ${projectId}`);

      const files = await fetch(`/api/files/${projectId}/${branchName}`).then(
        (res) => res.json()
      );
      console.log(`Files for project ${projectId} on branch ${branchName}:`, files);

      const fileDiv = document.getElementById(`files-${projectId}`);
      fileDiv.innerHTML = files
        .map(
          (f) => `
          <label>
            <input type="checkbox" name="file-${projectId}" value="${f}" checked>
            ${f}
          </label><br/>
        `
        )
        .join("");
    });
  }
});

async function compareNow() {
  console.log("Starting comparison...");
  const selectedIds = Array.from(traineeSelect.selectedOptions).map(
    (opt) => opt.value
  );
  console.log("Selected trainee IDs for comparison:", selectedIds);

  const config = {};

  for (const id of selectedIds) {
    const branch = document.querySelector(`select[name="branch-${id}"]`)?.value;
    const files = Array.from(
      document.querySelectorAll(`input[name="file-${id}"]:checked`)
    ).map((input) => input.value);

    if (branch && files.length) {
      config[id] = {
        name: traineeData[id],
        Assignment: "Manual Selection",
        branch: branch,
        files: files,
      };
      console.log(`Config set for project ${id}:`, config[id]);
    } else {
      console.warn(`Skipping project ${id} due to missing branch or files.`);
    }
  }

  console.log("Final config to send:", config);

  const response = await fetch("/api/save-config", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config),
  });

  const result = await response.json();
  console.log("Comparison result received:", result);

  outputPre.innerHTML = "";

  result.forEach((entry) => {
    const block = document.createElement("div");
    block.className = "result-block";

    const heading = document.createElement("h3");
    heading.textContent = entry.pair;
    block.appendChild(heading);

    const percent = document.createElement("p");
    percent.textContent = `Similarity: ${entry.percentage}`;
    block.appendChild(percent);

    entry.matches.forEach((match, idx) => {
      const compareDiv = document.createElement("div");
      compareDiv.className = "code-compare";

      const code1 = document.createElement("div");
      code1.innerHTML = `<h4>Code 1</h4><pre>${match.code1}</pre>`;

      const code2 = document.createElement("div");
      code2.innerHTML = `<h4>Code 2</h4><pre>${match.code2}</pre>`;

      console.log(`Match ${idx + 1} for pair ${entry.pair}:`, match);

      compareDiv.appendChild(code1);
      compareDiv.appendChild(code2);
      block.appendChild(compareDiv);
    });

    outputPre.appendChild(block);
  });
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.innerText = text;
  return div.innerHTML;
}

window.compareNow = compareNow;
