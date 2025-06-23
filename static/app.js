function showSpinner() {
  document.getElementById("spinner").style.display = "flex";
}

function hideSpinner() {
  document.getElementById("spinner").style.display = "none";
}

async function loginToGitlab() {
  showSpinner();
  const url = document.getElementById("gitlab-url").value;
  const token = document.getElementById("gitlab-token").value;
  const statusMsg = document.getElementById("login-status");

  console.log("Logging in with URL:", url, "and Token:", token);

  const res = await fetch("/api/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, token }),
  });

  if (!res.ok) {
    const errorText = await res.text();
    console.error("Login failed:", errorText);
    statusMsg.textContent = "Login failed. See console for details.";
    return;
  }

  const result = await res.json();
  console.log("Login result:", result);

  if (result.success === true) {
    statusMsg.textContent = "";
    document.getElementById("login-section").style.display = "none";
    document.getElementById("main-app").style.display = "block";
    console.log("Login successful, loading trainees...");
    loadTrainees();
  } else {
    statusMsg.textContent = result.message;
    console.log("Login failed:", result.message);
  }
  hideSpinner();
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
  showSpinner();
  console.log("Fetching trainees...");
  const res = await fetch("/api/trainees", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });

  if (!res.ok) {
    const errorText = await res.text();
    console.error("Error loading trainees:", errorText);
    return;
  }

  const data = await res.json();
  traineeData = data;
  console.log("Trainees fetched:", data);

  const traineeOptions = Object.entries(data).map(([id, obj]) => ({
    value: id,
    label: obj.name,
  }));

  choices.setChoices(traineeOptions, "value", "label", true);
  console.log("Trainee options set in Choices");
  hideSpinner();
}

traineeSelect.addEventListener("change", async function () {
  showSpinner();
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
    hideSpinner();

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
      showSpinner();
      const branchName = encodeURIComponent(this.value);
      const projectId = this.dataset.projectId;
      console.log(`Branch selected: ${branchName} for project ${projectId}`);

      const files = await fetch(`/api/files/${projectId}/${branchName}`).then(
        (res) => res.json()
      );
      console.log(
        `Files for project ${projectId} on branch ${branchName}:`,
        files
      );

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
        hideSpinner();
    });
  }
});

async function compareNow() {
  showSpinner();
  try {
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

    if (!response.ok) {
      const err = await response.text();
      console.error("Similarity comparison failed:", err);
      return;
    }

    const result = await response.json();
    console.log("Comparison result received:", result);

    outputPre.innerHTML = "";

    // Build summary table
    const summaryTable = document.createElement("table");
    summaryTable.className = "summary-table";
    summaryTable.innerHTML = `
      <thead>
        <tr>
          <th>Project Pair</th>
          <th>Similarity</th>
          <th>Details</th>
        </tr>
      </thead>
      <tbody></tbody>
    `;
    const summaryBody = summaryTable.querySelector("tbody");

    result.forEach((entry, index) => {
      const row = document.createElement("tr");
      const id = `details-${index}`;

      // Project Pair
      const pairCell = document.createElement("td");
      pairCell.textContent = entry.pair;

      // Similarity %
      const percentCell = document.createElement("td");
      percentCell.textContent = entry.percentage;

      // View Details Button
      const viewCell = document.createElement("td");
      const toggleBtn = document.createElement("button");
      toggleBtn.textContent = "View Details ▼";
      toggleBtn.onclick = () => {
        const detailsDiv = document.getElementById(id);
        const isVisible = detailsDiv.style.display === "block";
        detailsDiv.style.display = isVisible ? "none" : "block";
        toggleBtn.textContent = isVisible ? "View Details ▼" : "Hide Details ▲";
      };
      viewCell.appendChild(toggleBtn);

      row.appendChild(pairCell);
      row.appendChild(percentCell);
      row.appendChild(viewCell);
      summaryBody.appendChild(row);

      // Code snippet details
      const detailsDiv = document.createElement("div");
      detailsDiv.id = id;
      detailsDiv.style.display = "none";
      detailsDiv.className = "details-block";

      entry.matches.forEach((match, idx) => {
        const compareDiv = document.createElement("div");
        compareDiv.className = "code-compare";

        const code1 = document.createElement("div");
        code1.innerHTML = `<h4>${match.file1 || "Code 1"}</h4><pre>${escapeHtml(match.code1)}</pre>`;

        const code2 = document.createElement("div");
        code2.innerHTML = `<h4>${match.file2 || "Code 2"}</h4><pre>${escapeHtml(match.code2)}</pre>`;

        compareDiv.appendChild(code1);
        compareDiv.appendChild(code2);
        detailsDiv.appendChild(compareDiv);
      });

      outputPre.appendChild(detailsDiv);
    });

    outputPre.prepend(summaryTable);
  } catch (err) {
    console.error("Error during comparison:", err);
  } finally {
    hideSpinner();
  }
}



function escapeHtml(text) {
  const div = document.createElement("div");
  div.innerText = text || '';
  return div.innerHTML;
}

window.compareNow = compareNow;
