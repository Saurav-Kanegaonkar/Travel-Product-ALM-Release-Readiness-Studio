const state = {
  data: null,
  activeView: "command",
  selectedCapabilityId: null,
  areaFilter: "All areas",
  storyDecisionFilter: "All decisions",
};

const formatNumber = new Intl.NumberFormat("en-US");
const formatMoney = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

function byId(id) {
  return document.getElementById(id);
}

function pct(value) {
  return `${Number(value).toFixed(1)}%`;
}

function score(value) {
  return Number(value).toFixed(1);
}

function riskClass(value) {
  const numeric = Number(value);
  if (numeric >= 62) return "risk-high";
  if (numeric >= 48) return "risk-watch";
  return "risk-low";
}

function statusClass(value) {
  if (value === "Block" || value === "Blocked" || value.includes("Hold")) return "risk-high";
  if (value === "Watch" || value.includes("trade-off") || value.includes("Validate") || value.includes("Refine")) return "risk-watch";
  return "risk-low";
}

function metric(label, value, context) {
  return `
    <article class="metric">
      <span>${label}</span>
      <strong>${value}</strong>
      <em>${context}</em>
    </article>
  `;
}

function renderMetrics() {
  const { summary } = state.data;
  byId("topDecision").textContent = summary.top_decision;
  byId("topCapability").textContent = summary.top_capability;
  byId("metricGrid").innerHTML = [
    metric("Capabilities", summary.capability_count, "release portfolio"),
    metric("Backlog items", summary.backlog_item_count, "Azure DevOps style"),
    metric("Blocked gates", summary.blocked_gate_count, `${summary.watch_gate_count} on watch`),
    metric("Open impact", formatMoney.format(summary.total_open_event_impact), "modeled events"),
    metric("Story readiness", pct(summary.avg_story_readiness), "portfolio average"),
    metric("Package readiness", pct(summary.avg_package_readiness), "ALM average"),
  ].join("");
}

function populateFilters() {
  const areas = ["All areas", ...new Set(state.data.capabilities.map((row) => row.product_area))];
  byId("areaFilter").innerHTML = areas.map((area) => `<option>${area}</option>`).join("");
  byId("areaFilter").value = state.areaFilter;

  const decisions = ["All decisions", ...new Set(state.data.backlog.map((row) => row.acceptance_decision))];
  byId("storyDecisionFilter").innerHTML = decisions.map((decision) => `<option>${decision}</option>`).join("");
  byId("storyDecisionFilter").value = state.storyDecisionFilter;
}

function getVisibleCapabilities() {
  return state.data.capabilities.filter((row) => state.areaFilter === "All areas" || row.product_area === state.areaFilter);
}

function renderCapabilityRows() {
  const rows = getVisibleCapabilities();
  if (!rows.some((row) => row.capability_id === state.selectedCapabilityId)) {
    state.selectedCapabilityId = rows[0]?.capability_id ?? state.data.capabilities[0].capability_id;
  }

  byId("capabilityRows").innerHTML = rows.slice(0, 14).map((row) => `
    <tr class="${row.capability_id === state.selectedCapabilityId ? "selected" : ""}" data-capability="${row.capability_id}">
      <td>
        <button type="button" class="link-button" data-capability="${row.capability_id}">${row.capability_name}</button>
        <span>${row.primary_user}</span>
      </td>
      <td>${row.product_area}</td>
      <td><strong>${score(row.priority_score)}</strong></td>
      <td><mark class="${riskClass(row.release_risk_score)}">${score(row.release_risk_score)}</mark></td>
      <td><mark class="${statusClass(row.decision_needed)}">${row.decision_needed}</mark></td>
    </tr>
  `).join("");
}

function progress(label, value, tone = "") {
  return `
    <div class="progress-row">
      <span>${label}</span>
      <b>${pct(value)}</b>
      <div class="bar"><i class="${tone}" style="width:${Math.max(6, Number(value))}%"></i></div>
    </div>
  `;
}

function selectedCapability() {
  return state.data.capabilities.find((row) => row.capability_id === state.selectedCapabilityId) ?? state.data.capabilities[0];
}

function renderCapabilityDetail() {
  const row = selectedCapability();
  const actions = state.data.actions.filter((item) => item.capability_id === row.capability_id);
  const gates = state.data.gates.filter((item) => item.capability_id === row.capability_id);
  const blocked = gates.filter((item) => item.gate_status !== "Pass");

  byId("capabilityDetail").innerHTML = `
    <p class="eyebrow">Selected capability</p>
    <h3>${row.capability_name}</h3>
    <p class="problem">${row.business_problem}</p>
    <dl class="detail-list">
      <div><dt>Target release</dt><dd>${row.target_release}</dd></div>
      <div><dt>Product goal</dt><dd>${row.product_goal}</dd></div>
      <div><dt>Owner group</dt><dd>${row.product_owner_group}</dd></div>
      <div><dt>Open event impact</dt><dd>${formatMoney.format(row.open_event_impact)}</dd></div>
    </dl>
    <div class="progress-pack">
      ${progress("Story readiness", row.story_readiness_pct)}
      ${progress("Package readiness", row.solution_package_readiness_pct)}
      ${progress("Rollout readiness", row.rollout_readiness_pct)}
      ${progress("Rollback confidence", row.rollback_confidence_pct)}
    </div>
    <h4>PO decision</h4>
    <p class="decision ${statusClass(row.decision_needed)}">${row.decision_needed}</p>
    <h4>Blocked or watch gates</h4>
    <ul class="compact-list">
      ${(blocked.length ? blocked : gates.slice(0, 2)).map((gate) => `<li><strong>${gate.gate_name}</strong><span>${gate.blocker}</span></li>`).join("")}
    </ul>
    <h4>Recommended next move</h4>
    <p>${actions[0]?.recommended_action ?? "Confirm acceptance evidence and release owner."}</p>
  `;
}

function renderCommand() {
  renderCapabilityRows();
  renderCapabilityDetail();
}

function renderBacklog() {
  const filtered = state.data.backlog
    .filter((row) => state.storyDecisionFilter === "All decisions" || row.acceptance_decision === state.storyDecisionFilter)
    .sort((a, b) => Number(a.story_readiness_pct) - Number(b.story_readiness_pct));

  byId("storyList").innerHTML = filtered.slice(0, 12).map((row) => `
    <article class="story-item">
      <div>
        <span>${row.story_id} · ${row.priority} · ${row.target_sprint}</span>
        <h4>${row.summary}</h4>
        <p>${row.dependency} dependency, ${row.acceptance_criteria_count} acceptance criteria, ${row.effort_points} points.</p>
      </div>
      <aside>
        <mark class="${statusClass(row.acceptance_decision)}">${row.acceptance_decision}</mark>
        <strong>${pct(row.story_readiness_pct)}</strong>
      </aside>
    </article>
  `).join("");

  const personaCounts = state.data.backlog.reduce((acc, row) => {
    acc[row.persona] = (acc[row.persona] ?? 0) + 1;
    return acc;
  }, {});
  byId("criteriaGrid").innerHTML = Object.entries(personaCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6)
    .map(([persona, count]) => `<article><span>${persona}</span><strong>${count}</strong><em>stories needing criteria</em></article>`)
    .join("");

  const sprintGroups = state.data.backlog.reduce((acc, row) => {
    if (!acc[row.target_sprint]) acc[row.target_sprint] = { count: 0, points: 0, ready: 0 };
    acc[row.target_sprint].count += 1;
    acc[row.target_sprint].points += Number(row.effort_points);
    if (Number(row.story_readiness_pct) >= 70) acc[row.target_sprint].ready += 1;
    return acc;
  }, {});
  byId("sprintList").innerHTML = Object.entries(sprintGroups)
    .sort((a, b) => a[0].localeCompare(b[0]))
    .map(([sprint, data]) => `
      <article class="sprint-item">
        <strong>${sprint}</strong>
        <span>${data.count} stories</span>
        <span>${data.points} points</span>
        <mark class="${data.ready / data.count > 0.65 ? "risk-low" : "risk-watch"}">${Math.round((data.ready / data.count) * 100)}% ready</mark>
      </article>
    `).join("");
}

function renderDeployment() {
  const gates = state.data.gates.filter((row) => row.gate_status !== "Pass").slice(0, 16);
  byId("gateBoard").innerHTML = gates.map((gate) => {
    const capability = state.data.capabilities.find((row) => row.capability_id === gate.capability_id);
    return `
      <article class="gate-item">
        <div>
          <span>${gate.gate_name} · ${gate.owner}</span>
          <strong>${capability.capability_name}</strong>
          <p>${gate.evidence_required}</p>
        </div>
        <mark class="${statusClass(gate.gate_status)}">${gate.gate_status}</mark>
      </article>
    `;
  }).join("");

  byId("packageList").innerHTML = state.data.packages
    .sort((a, b) => Number(b.deployment_risk_score) - Number(a.deployment_risk_score))
    .slice(0, 8)
    .map((pack) => {
      const capability = state.data.capabilities.find((row) => row.capability_id === pack.capability_id);
      return `
        <article class="package-item">
          <span>${pack.package_id} · ${pack.solution_type}</span>
          <h4>${capability.capability_name}</h4>
          ${progress("Deployment risk", pack.deployment_risk_score, "danger")}
          <p>${pack.rollback_plan} rollback plan, ${pack.release_window} release window.</p>
        </article>
      `;
    }).join("");

  byId("adoptionList").innerHTML = state.data.adoption
    .filter((row) => row.primary_adoption_blocker !== "None" || Number(row.training_readiness_pct) < 72)
    .sort((a, b) => Number(a.training_readiness_pct) - Number(b.training_readiness_pct))
    .slice(0, 10)
    .map((row) => {
      const capability = state.data.capabilities.find((item) => item.capability_id === row.capability_id);
      return `
        <article class="adoption-item">
          <span>${row.cohort}</span>
          <strong>${capability.capability_name}</strong>
          <p>${row.primary_adoption_blocker}</p>
          <mark class="${statusClass(row.support_handoff_status)}">${row.support_handoff_status}</mark>
        </article>
      `;
    }).join("");
}

function renderActiveView() {
  if (state.activeView === "command") renderCommand();
  if (state.activeView === "backlog") renderBacklog();
  if (state.activeView === "deployment") renderDeployment();
}

function bindEvents() {
  document.querySelectorAll(".tabs button").forEach((button) => {
    button.addEventListener("click", () => {
      state.activeView = button.dataset.view;
      document.querySelectorAll(".tabs button").forEach((item) => item.classList.toggle("active", item === button));
      document.querySelectorAll(".view").forEach((view) => view.classList.toggle("active", view.id === state.activeView));
      renderActiveView();
    });
  });

  byId("areaFilter").addEventListener("change", (event) => {
    state.areaFilter = event.target.value;
    renderCommand();
  });

  byId("storyDecisionFilter").addEventListener("change", (event) => {
    state.storyDecisionFilter = event.target.value;
    renderBacklog();
  });

  byId("capabilityRows").addEventListener("click", (event) => {
    const target = event.target.closest("[data-capability]");
    if (!target) return;
    state.selectedCapabilityId = target.dataset.capability;
    renderCommand();
  });
}

async function init() {
  const response = await fetch("analysis/outputs/app_payload.json");
  state.data = await response.json();
  state.selectedCapabilityId = state.data.capabilities[0].capability_id;
  renderMetrics();
  populateFilters();
  bindEvents();
  renderActiveView();
}

init();
