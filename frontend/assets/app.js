const state = {
  apiBase: localStorage.getItem("asa_api_base") || "/api",
  token: localStorage.getItem("asa_token") || "",
  user: null,
  orders: [],
  documents: [],
  lastRun: null,
};

const viewTitles = {
  workspace: "Agent 工作台",
  orders: "订单查询",
  knowledge: "知识库检索",
  documents: "知识库文档",
  approvals: "审批中心",
  runs: "运行记录",
};

const promptTemplates = {
  normal: {
    orderNo: "10086",
    message: "订单 10086 已经签收两天了，用户不满意，想申请退款，可以直接退吗？",
  },
  high: {
    orderNo: "10087",
    message: "订单 10087 是高金额耳机订单，客户说不满意想退款，需要主管审批吗？",
  },
  virtual: {
    orderNo: "10088",
    message: "订单 10088 是会员兑换码，已经交付了，客户想无理由退款，可以处理吗？",
  },
};

function $(selector, root = document) {
  return root.querySelector(selector);
}

function $all(selector, root = document) {
  return Array.from(root.querySelectorAll(selector));
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatDate(value) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "-";
  return new Intl.DateTimeFormat("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

function formatMoney(value) {
  const amount = Number(value ?? 0);
  return new Intl.NumberFormat("zh-CN", {
    style: "currency",
    currency: "CNY",
    minimumFractionDigits: 2,
  }).format(Number.isFinite(amount) ? amount : 0);
}

function sleep(ms) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

function statusBadge(status) {
  const normalized = String(status || "unknown");
  const labelMap = {
    pending_payment: "待支付",
    paid: "已支付",
    shipped: "已发货",
    delivered: "已签收",
    cancelled: "已取消",
    refunded: "已退款",
    partially_refunded: "部分退款",
    processing: "处理中",
    ready: "可检索",
    failed: "失败",
    uploaded: "已上传",
  };
  const toneMap = {
    delivered: "success",
    paid: "info",
    shipped: "info",
    ready: "success",
    processing: "warning",
    pending_payment: "warning",
    failed: "danger",
    cancelled: "neutral",
    refunded: "neutral",
    partially_refunded: "warning",
  };
  const tone = toneMap[normalized] || "neutral";
  return `<span class="badge ${tone}">${escapeHtml(labelMap[normalized] || normalized)}</span>`;
}

function setRunStatus(text) {
  $("#runStatusDot").textContent = text;
}

function showToast(title, message = "", type = "info") {
  const stack = $("#toastStack");
  const toast = document.createElement("div");
  toast.className = `toast ${type === "error" ? "is-error" : ""}`;
  toast.innerHTML = `<strong>${escapeHtml(title)}</strong><span>${escapeHtml(message)}</span>`;
  stack.appendChild(toast);
  window.setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(8px)";
    window.setTimeout(() => toast.remove(), 180);
  }, 3600);
}

function getApiUrl(path) {
  const base = state.apiBase.trim().replace(/\/+$/, "") || "/api";
  const suffix = path.startsWith("/") ? path : `/${path}`;
  return `${base}${suffix}`;
}

async function request(path, options = {}) {
  const headers = new Headers(options.headers || {});
  let body = options.body;

  if (state.token) {
    headers.set("Authorization", `Bearer ${state.token}`);
  }

  if (body && !(body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
    body = JSON.stringify(body);
  }

  const response = await fetch(getApiUrl(path), {
    ...options,
    headers,
    body,
  });

  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json")
    ? await response.json().catch(() => null)
    : await response.text().catch(() => "");

  if (!response.ok) {
    const detail = payload && typeof payload === "object" ? payload.detail : payload;
    throw new Error(detail || `Request failed: ${response.status}`);
  }

  return payload;
}

function updateApiDisplay() {
  $("#apiBaseInput").value = state.apiBase;
  $("#apiBaseLabel").textContent = state.apiBase;
}

function setAuthenticated(isAuthenticated) {
  $("#authGate").classList.toggle("is-hidden", isAuthenticated);
  $("#contentShell").classList.toggle("is-hidden", !isAuthenticated);
  $("#logoutButton").classList.toggle("is-hidden", !isAuthenticated);

  const pill = $("#sessionPill");
  if (isAuthenticated && state.user) {
    pill.textContent = `${state.user.email} · ${state.user.role}`;
  } else {
    pill.textContent = "未登录";
  }
}

function logout(showMessage = true) {
  state.token = "";
  state.user = null;
  state.orders = [];
  state.documents = [];
  localStorage.removeItem("asa_token");
  setAuthenticated(false);
  renderOrders();
  renderDocuments();
  if (showMessage) showToast("已退出", "本地 token 已清除。");
}

async function loadMe() {
  state.user = await request("/auth/me");
  setAuthenticated(true);
}

async function handleLogin(event) {
  event.preventDefault();
  const formData = new FormData(event.currentTarget);
  const payload = {
    email: formData.get("email"),
    password: formData.get("password"),
  };

  try {
    const token = await request("/auth/login", {
      method: "POST",
      body: payload,
    });
    state.token = token.access_token;
    localStorage.setItem("asa_token", state.token);
    await loadMe();
    await Promise.allSettled([loadOrders(), loadDocuments()]);
    showToast("登录成功", "工作台已经连接后端。");
  } catch (error) {
    showToast("登录失败", error.message, "error");
  }
}

async function handleRegister(event) {
  event.preventDefault();
  const formData = new FormData(event.currentTarget);
  const payload = {
    email: formData.get("email"),
    password: formData.get("password"),
  };

  try {
    await request("/auth/register", {
      method: "POST",
      body: payload,
    });
    showToast("注册成功", "正在自动登录。");
    const loginForm = $("#loginForm");
    loginForm.email.value = payload.email;
    loginForm.password.value = payload.password;
    await handleLogin({ preventDefault() {}, currentTarget: loginForm });
  } catch (error) {
    showToast("注册失败", error.message, "error");
  }
}

function switchAuthTab(tab) {
  $all("[data-auth-tab]").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.authTab === tab);
  });
  $all("[data-auth-form]").forEach((form) => {
    form.classList.toggle("is-hidden", form.dataset.authForm !== tab);
  });
}

function switchView(view) {
  const apply = () => {
    $all(".nav-item").forEach((button) => {
      button.classList.toggle("is-active", button.dataset.view === view);
    });
    $all("[data-view-panel]").forEach((panel) => {
      panel.classList.toggle("is-active", panel.dataset.viewPanel === view);
    });
    $("#viewTitle").textContent = viewTitles[view] || "AfterSaleAgent";
    $("#sidebar").classList.remove("is-open");
  };

  if (document.startViewTransition) {
    document.startViewTransition(apply);
  } else {
    apply();
  }
}

async function loadOrders() {
  try {
    state.orders = await request("/orders/");
    renderOrders();
  } catch (error) {
    renderOrders();
    showToast("订单加载失败", error.message, "error");
  }
}

function renderOrders() {
  const tbody = $("#ordersTableBody");
  const query = ($("#orderSearchInput")?.value || "").trim().toLowerCase();
  const orders = state.orders.filter((order) => {
    const haystack = `${order.order_no} ${order.status} ${order.customer_id}`.toLowerCase();
    return !query || haystack.includes(query);
  });

  if (!orders.length) {
    tbody.innerHTML = `<tr><td colspan="5" class="muted-cell">暂无匹配订单。</td></tr>`;
    return;
  }

  tbody.innerHTML = orders
    .map(
      (order) => `
        <tr data-order-no="${escapeHtml(order.order_no)}">
          <td><span class="row-action">${escapeHtml(order.order_no)}</span></td>
          <td>#${escapeHtml(order.customer_id)}</td>
          <td>${statusBadge(order.status)}</td>
          <td>${formatMoney(order.total_amount)}</td>
          <td>${formatDate(order.created_at)}</td>
        </tr>
      `,
    )
    .join("");

  $all("[data-order-no]", tbody).forEach((row) => {
    row.addEventListener("click", () => selectOrder(row.dataset.orderNo));
  });
}

async function selectOrder(orderNo) {
  const pane = $("#orderDetailPane");
  pane.className = "detail-empty";
  pane.textContent = "正在加载订单详情...";

  try {
    const [order, payment, shipment] = await Promise.all([
      request(`/orders/${encodeURIComponent(orderNo)}`),
      request(`/orders/${encodeURIComponent(orderNo)}/payment`),
      request(`/orders/${encodeURIComponent(orderNo)}/shipment`),
    ]);
    pane.className = "detail-stack";
    pane.innerHTML = renderOrderDetail(order, payment, shipment);
  } catch (error) {
    pane.className = "detail-empty";
    pane.textContent = error.message;
  }
}

function renderOrderDetail(order, payment, shipment) {
  const items = (order.items || [])
    .map(
      (item) => `
        <div class="kv">
          <span>商品 #${escapeHtml(item.product_id)}</span>
          <strong>${escapeHtml(item.quantity)} 件 · ${formatMoney(item.unit_price)}</strong>
        </div>
      `,
    )
    .join("");

  return `
    <div class="detail-block">
      <h4>订单 ${escapeHtml(order.order_no)}</h4>
      <div class="key-values">
        <div class="kv"><span>状态</span><strong>${statusBadge(order.status)}</strong></div>
        <div class="kv"><span>金额</span><strong>${formatMoney(order.total_amount)}</strong></div>
        <div class="kv"><span>客户</span><strong>#${escapeHtml(order.customer_id)}</strong></div>
        <div class="kv"><span>支付时间</span><strong>${formatDate(order.paid_at)}</strong></div>
      </div>
    </div>
    <div class="detail-block">
      <h4>商品明细</h4>
      <div class="key-values">${items || "<div class='kv'><span>暂无</span><strong>-</strong></div>"}</div>
    </div>
    <div class="detail-block">
      <h4>支付</h4>
      <div class="key-values">
        <div class="kv"><span>状态</span><strong>${statusBadge(payment.status)}</strong></div>
        <div class="kv"><span>金额</span><strong>${formatMoney(payment.amount)}</strong></div>
        <div class="kv"><span>已退</span><strong>${formatMoney(payment.refunded_amount)}</strong></div>
        <div class="kv"><span>支付时间</span><strong>${formatDate(payment.paid_at)}</strong></div>
      </div>
    </div>
    <div class="detail-block">
      <h4>物流</h4>
      <div class="key-values">
        <div class="kv"><span>状态</span><strong>${statusBadge(shipment.status)}</strong></div>
        <div class="kv"><span>承运商</span><strong>${escapeHtml(shipment.carrier || "-")}</strong></div>
        <div class="kv"><span>运单号</span><strong>${escapeHtml(shipment.tracking_no || "-")}</strong></div>
        <div class="kv"><span>签收</span><strong>${formatDate(shipment.delivered_at)}</strong></div>
      </div>
    </div>
  `;
}

async function searchKnowledge(event) {
  event.preventDefault();
  const formData = new FormData(event.currentTarget);
  const query = String(formData.get("query") || "").trim();
  const topK = Number(formData.get("top_k") || 5);
  const list = $("#knowledgeResults");
  list.innerHTML = `<div class="empty-state">正在检索...</div>`;

  try {
    const response = await request("/knowledge/search", {
      method: "POST",
      body: {
        query,
        top_k: topK,
      },
    });
    renderKnowledgeResults(response.results || []);
  } catch (error) {
    list.innerHTML = `<div class="empty-state">${escapeHtml(error.message)}</div>`;
    showToast("检索失败", error.message, "error");
  }
}

function renderKnowledgeResults(results, target = $("#knowledgeResults")) {
  if (!results.length) {
    target.innerHTML = `<div class="empty-state">没有匹配到政策片段。</div>`;
    return;
  }

  target.innerHTML = results
    .map(
      (item) => `
        <article class="result-card">
          <div class="result-meta">
            <span>chunk #${escapeHtml(item.chunk_id)}</span>
            <span>document #${escapeHtml(item.document_id)}</span>
            <span>score ${Number(item.score || 0).toFixed(2)}</span>
          </div>
          <p>${escapeHtml(item.content)}</p>
        </article>
      `,
    )
    .join("");
}

async function loadDocuments() {
  try {
    state.documents = await request("/documents/");
    renderDocuments();
  } catch (error) {
    renderDocuments();
    showToast("文档加载失败", error.message, "error");
  }
}

function renderDocuments() {
  const tbody = $("#documentsTableBody");
  if (!state.documents.length) {
    tbody.innerHTML = `<tr><td colspan="5" class="muted-cell">暂无文档。</td></tr>`;
    return;
  }

  tbody.innerHTML = state.documents
    .map(
      (doc) => `
        <tr>
          <td>#${escapeHtml(doc.id)}</td>
          <td>${escapeHtml(doc.title)}</td>
          <td>${statusBadge(doc.status)}</td>
          <td>#${escapeHtml(doc.uploaded_by)}</td>
          <td><button class="ghost-button" data-ingest-document="${escapeHtml(doc.id)}" type="button">入库</button></td>
        </tr>
      `,
    )
    .join("");

  $all("[data-ingest-document]", tbody).forEach((button) => {
    button.addEventListener("click", () => ingestDocument(button.dataset.ingestDocument));
  });
}

async function uploadDocument(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const formData = new FormData(form);
  const file = formData.get("file");
  const title = String(formData.get("title") || file?.name || "document").trim();

  if (!file || !file.name) {
    showToast("请选择文件", "只支持 .txt 和 .md。", "error");
    return;
  }

  const payload = new FormData();
  payload.append("file", file);

  try {
    await request(`/documents/?title=${encodeURIComponent(title)}`, {
      method: "POST",
      body: payload,
    });
    form.reset();
    await loadDocuments();
    showToast("上传成功", "文档已经保存，可以继续执行入库。");
  } catch (error) {
    showToast("上传失败", error.message, "error");
  }
}

async function ingestDocument(documentId) {
  try {
    const result = await request(`/documents/${encodeURIComponent(documentId)}/ingest`, {
      method: "POST",
    });
    await loadDocuments();
    showToast("入库完成", `切块数量：${result.chunk_count ?? 0}`);
  } catch (error) {
    showToast("入库失败", error.message, "error");
  }
}

function extractOrderNo(message) {
  const match = String(message || "").match(/\d{4,}/);
  return match ? match[0] : "";
}

function resetTimeline() {
  $("#runTimeline").innerHTML = "";
}

function addTimelineItem(title, meta, status = "is-active") {
  const item = document.createElement("li");
  item.className = `timeline-item ${status}`;
  item.innerHTML = `
    <div class="timeline-title">${escapeHtml(title)}</div>
    <div class="timeline-meta">${escapeHtml(meta)}</div>
  `;
  $("#runTimeline").appendChild(item);
  item.scrollIntoView({ block: "nearest", behavior: "smooth" });
  return item;
}

function completeTimelineItem(item, status = "is-done", meta) {
  item.className = `timeline-item ${status}`;
  if (meta) {
    $(".timeline-meta", item).textContent = meta;
  }
}

function assessDecision(order, shipment, message) {
  const amount = Number(order.total_amount || 0);
  const lowered = String(message || "").toLowerCase();
  const isVirtual = order.order_no === "10088" || lowered.includes("virtual") || message.includes("虚拟");

  if (isVirtual) {
    return {
      tone: "danger",
      risk: "medium",
      action: "reject_refund",
      title: "暂不支持直接退款",
      answer: `订单 ${order.order_no} 疑似虚拟商品或已完成数字交付，建议先按政策拒绝无理由退款，并确认是否存在服务故障。`,
    };
  }

  if (shipment.status !== "delivered") {
    return {
      tone: "warning",
      risk: "medium",
      action: "ask_for_more_info",
      title: "需要补充签收状态",
      answer: `订单 ${order.order_no} 当前物流状态不是已签收，建议先确认物流节点后再判断退款路径。`,
    };
  }

  if (amount >= 500) {
    return {
      tone: "warning",
      risk: "high",
      action: "create_approval",
      title: "需要主管审批",
      answer: `订单 ${order.order_no} 金额为 ${formatMoney(amount)}，达到高金额退款阈值，建议创建审批单后再处理退款。`,
    };
  }

  return {
    tone: "success",
    risk: "low",
    action: "create_refund",
    title: "可直接进入退款流程",
    answer: `订单 ${order.order_no} 金额较低且已签收，若商品未使用且不影响二次销售，可以进入普通退款处理。`,
  };
}

function renderAgentContext({ order, payment, shipment, policies, decision }) {
  const policyList = (policies || [])
    .slice(0, 2)
    .map(
      (item) => `
        <div class="result-card">
          <div class="result-meta"><span>score ${Number(item.score || 0).toFixed(2)}</span></div>
          <p>${escapeHtml(item.content)}</p>
        </div>
      `,
    )
    .join("");

  $("#agentContext").innerHTML = `
    <div class="context-block">
      <h4>判断结论</h4>
      <span class="badge ${decision.tone}">${escapeHtml(decision.title)}</span>
      <p class="timeline-meta">${escapeHtml(decision.answer)}</p>
    </div>
    <div class="context-block">
      <h4>订单上下文</h4>
      <div class="key-values">
        <div class="kv"><span>订单号</span><strong>${escapeHtml(order.order_no)}</strong></div>
        <div class="kv"><span>金额</span><strong>${formatMoney(order.total_amount)}</strong></div>
        <div class="kv"><span>订单状态</span><strong>${statusBadge(order.status)}</strong></div>
        <div class="kv"><span>风险</span><strong>${escapeHtml(decision.risk)}</strong></div>
      </div>
    </div>
    <div class="context-block">
      <h4>支付与物流</h4>
      <div class="key-values">
        <div class="kv"><span>支付</span><strong>${statusBadge(payment.status)}</strong></div>
        <div class="kv"><span>已退金额</span><strong>${formatMoney(payment.refunded_amount)}</strong></div>
        <div class="kv"><span>物流</span><strong>${statusBadge(shipment.status)}</strong></div>
        <div class="kv"><span>签收时间</span><strong>${formatDate(shipment.delivered_at)}</strong></div>
      </div>
    </div>
    <div class="context-block">
      <h4>政策片段</h4>
      <div class="result-list">${policyList || "<div class='empty-state'>暂无匹配政策。</div>"}</div>
    </div>
  `;
}

function renderRunHistory() {
  const pane = $("#runHistoryPane");
  if (!state.lastRun) {
    pane.className = "empty-state";
    pane.textContent = "完成一次 Agent 判断后，这里会显示最近一次运行摘要。";
    return;
  }

  pane.className = "detail-stack";
  pane.innerHTML = `
    <div class="detail-block">
      <h4>${escapeHtml(state.lastRun.id)}</h4>
      <div class="key-values">
        <div class="kv"><span>订单号</span><strong>${escapeHtml(state.lastRun.orderNo)}</strong></div>
        <div class="kv"><span>意图</span><strong>${escapeHtml(state.lastRun.intent)}</strong></div>
        <div class="kv"><span>风险</span><strong>${escapeHtml(state.lastRun.risk)}</strong></div>
        <div class="kv"><span>动作</span><strong>${escapeHtml(state.lastRun.action)}</strong></div>
      </div>
    </div>
    <div class="detail-block">
      <h4>最终回复</h4>
      <p class="timeline-meta">${escapeHtml(state.lastRun.answer)}</p>
    </div>
  `;
}

async function runAgentDemo() {
  if (!state.token) {
    showToast("请先登录", "Agent 工作台需要携带 JWT 调用后端接口。", "error");
    return;
  }

  const button = $("#runAgentButton");
  const message = $("#agentMessageInput").value.trim();
  const inputOrderNo = $("#agentOrderNoInput").value.trim();
  const orderNo = inputOrderNo || extractOrderNo(message);

  button.disabled = true;
  setRunStatus("Running");
  resetTimeline();
  $("#agentContext").innerHTML = `<div class="empty-state">正在构建上下文...</div>`;

  const receiveStep = addTimelineItem("接收客服诉求", message || "暂无消息");
  await sleep(260);
  completeTimelineItem(receiveStep, "is-done", "诉求已进入前端演示流程。");

  const parseStep = addTimelineItem("解析意图和订单号", "提取退款意图、订单号和风险线索。");
  await sleep(320);

  if (!orderNo) {
    completeTimelineItem(parseStep, "is-warning", "没有识别到订单号。");
    const askStep = addTimelineItem("生成回复", "暂时无法判断，请补充有效订单号。", "is-warning");
    completeTimelineItem(askStep, "is-warning");
    setRunStatus("Need info");
    button.disabled = false;
    return;
  }

  completeTimelineItem(parseStep, "is-done", `识别到订单 ${orderNo}，意图 refund_request。`);

  try {
    const orderStep = addTimelineItem("查询订单", `GET /orders/${orderNo}`);
    await sleep(260);
    const order = await request(`/orders/${encodeURIComponent(orderNo)}`);
    completeTimelineItem(orderStep, "is-done", `订单状态 ${order.status}，金额 ${formatMoney(order.total_amount)}。`);

    const toolStep = addTimelineItem("查询支付和物流", "并发调用 payment 与 shipment 接口。");
    await sleep(260);
    const [payment, shipment] = await Promise.all([
      request(`/orders/${encodeURIComponent(orderNo)}/payment`),
      request(`/orders/${encodeURIComponent(orderNo)}/shipment`),
    ]);
    completeTimelineItem(toolStep, "is-done", `支付 ${payment.status}，物流 ${shipment.status}。`);

    const policyStep = addTimelineItem("检索售后政策", "调用 POST /knowledge/search 获取政策片段。");
    await sleep(260);
    let policies = [];
    try {
      const policyResponse = await request("/knowledge/search", {
        method: "POST",
        body: {
          query: `${message || "退款政策"} 订单 ${orderNo}`,
          top_k: 5,
        },
      });
      policies = policyResponse.results || [];
      completeTimelineItem(policyStep, "is-done", `命中 ${policies.length} 条政策片段。`);
    } catch (error) {
      completeTimelineItem(policyStep, "is-warning", `政策检索暂不可用：${error.message}`);
    }

    const riskStep = addTimelineItem("评估风险", "根据金额、商品线索和物流状态执行确定性规则。");
    await sleep(320);
    const decision = assessDecision(order, shipment, message);
    const riskClass = decision.tone === "success" ? "is-done" : "is-warning";
    completeTimelineItem(riskStep, riskClass, `${decision.title}，动作 ${decision.action}。`);

    const finalStep = addTimelineItem("生成客服回复", decision.answer);
    await sleep(260);
    completeTimelineItem(finalStep, "is-done");

    renderAgentContext({ order, payment, shipment, policies, decision });
    state.lastRun = {
      id: `demo-run-${Date.now()}`,
      orderNo,
      intent: "refund_request",
      risk: decision.risk,
      action: decision.action,
      answer: decision.answer,
    };
    renderRunHistory();
    setRunStatus("Completed");
    showToast("判断完成", decision.title);
  } catch (error) {
    const errorStep = addTimelineItem("流程失败", error.message, "is-error");
    completeTimelineItem(errorStep, "is-error");
    $("#agentContext").innerHTML = `<div class="empty-state">${escapeHtml(error.message)}</div>`;
    setRunStatus("Failed");
    showToast("Agent 演示失败", error.message, "error");
  } finally {
    button.disabled = false;
  }
}

function fillTemplate(type) {
  const template = promptTemplates[type] || promptTemplates.normal;
  $("#agentOrderNoInput").value = template.orderNo;
  $("#agentMessageInput").value = template.message;
}

function initEvents() {
  $("#saveApiBaseButton").addEventListener("click", () => {
    state.apiBase = $("#apiBaseInput").value.trim() || "/api";
    localStorage.setItem("asa_api_base", state.apiBase);
    updateApiDisplay();
    showToast("API Base 已更新", state.apiBase);
  });

  $("#logoutButton").addEventListener("click", () => logout(true));
  $("#sidebarToggle").addEventListener("click", () => $("#sidebar").classList.toggle("is-open"));
  $("#loginForm").addEventListener("submit", handleLogin);
  $("#registerForm").addEventListener("submit", handleRegister);
  $("#refreshOrdersButton").addEventListener("click", loadOrders);
  $("#refreshDocumentsButton").addEventListener("click", loadDocuments);
  $("#orderSearchInput").addEventListener("input", renderOrders);
  $("#knowledgeSearchForm").addEventListener("submit", searchKnowledge);
  $("#documentUploadForm").addEventListener("submit", uploadDocument);
  $("#runAgentButton").addEventListener("click", runAgentDemo);
  $("#loadDemoButton").addEventListener("click", () => fillTemplate("normal"));

  $all(".nav-item").forEach((button) => {
    button.addEventListener("click", () => switchView(button.dataset.view));
  });

  $all("[data-auth-tab]").forEach((button) => {
    button.addEventListener("click", () => switchAuthTab(button.dataset.authTab));
  });

  $all("[data-template]").forEach((button) => {
    button.addEventListener("click", () => fillTemplate(button.dataset.template));
  });
}

async function bootstrap() {
  updateApiDisplay();
  initEvents();
  fillTemplate("normal");
  setAuthenticated(false);

  if (!state.token) return;

  try {
    await loadMe();
    await Promise.allSettled([loadOrders(), loadDocuments()]);
  } catch (error) {
    logout(false);
    showToast("登录已失效", "请重新登录。", "error");
  }
}

bootstrap();
